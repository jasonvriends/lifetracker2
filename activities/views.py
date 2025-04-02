from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST
from datetime import datetime, timedelta
import json
from .models import Activity, ActivityCategory, Consumption
from django.db import models
from zoneinfo import ZoneInfo

@login_required
def activities_view(request):
    """View for activities page."""
    # Get all categories for the filter
    categories = ActivityCategory.objects.all()
    
    # Get all activities for the current user
    activities = Activity.objects.filter(user=request.user)
    
    # Handle date filtering
    date_str = request.GET.get('date')
    if date_str:
        try:
            # Convert the date string to a datetime object in the user's timezone
            naive_date = datetime.strptime(date_str, '%Y-%m-%d')
            
            # Get the user's timezone
            user_timezone = request.user.timezone
            
            # Create timezone-aware datetime objects for start and end of the day
            # Make sure to use the user's local timezone for the day boundaries
            start_date = timezone.make_aware(
                datetime.combine(naive_date.date(), datetime.min.time()),
                ZoneInfo(user_timezone)
            )
            
            end_date = timezone.make_aware(
                datetime.combine(naive_date.date(), datetime.max.time()),
                ZoneInfo(user_timezone)
            )
            
            print(f"Filtering activities for date: {date_str}")
            print(f"User timezone: {user_timezone}")
            print(f"Start date: {start_date} (UTC: {start_date.astimezone(ZoneInfo('UTC'))})")
            print(f"End date: {end_date} (UTC: {end_date.astimezone(ZoneInfo('UTC'))})")
            
            # Filter activities based on either created_at or consumed_at
            activities = Activity.objects.filter(
                models.Q(
                    user=request.user,
                    created_at__range=(start_date, end_date)
                ) |
                models.Q(
                    user=request.user,
                    category__slug='consume',
                    consumptions__consumed_at__range=(start_date, end_date)
                )
            ).distinct().order_by('-created_at')
            
        except ValueError:
            # If date parsing fails, return all activities
            pass
    
    # Add raw datetime values for debugging
    debug_info = {}
    for activity in activities:
        if activity.category.slug == 'consume':
            consumption = activity.consumptions.first()
            if consumption:
                debug_info[activity.id] = {
                    'raw_datetime': consumption.consumed_at.isoformat(),
                    'in_utc': consumption.consumed_at.astimezone(ZoneInfo('UTC')).isoformat(),
                    'in_toronto': consumption.consumed_at.astimezone(ZoneInfo('America/Toronto')).isoformat(),
                }
    
    context = {
        'activities': activities,
        'categories': categories,
        'user_timezone': request.user.timezone,
        'debug_info': debug_info,
    }
    
    # If it's an AJAX request, return only the activities list
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'activities/partials/activities_list.html', context)
    
    return render(request, 'activities/activities.html', context)

@login_required
def activity_detail(request, pk):
    """View for a single activity."""
    activity = get_object_or_404(Activity, pk=pk, user=request.user)
    
    # Return JSON for AJAX requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        activity_data = {
            'id': activity.id,
            'name': activity.name,
            'description': activity.description,
            'favorite': activity.favorite,
            'category': {
                'name': activity.category.name,
                'slug': activity.category.slug,
                'color': activity.category.color
            }
        }
        
        # Add consumption details if applicable
        if activity.category.slug == 'consume':
            consumption = activity.consumptions.first()
            if consumption:
                activity_data['consumptions'] = [{
                    'description': consumption.description,
                    'ingredients': consumption.ingredients.split('\n') if consumption.ingredients else [],
                    'consumed_at': consumption.consumed_at.isoformat() if consumption.consumed_at else None
                }]
        
        return JsonResponse(activity_data)
    
    # Return HTML for regular requests
    return render(request, 'activities/activity_detail.html', {'activity': activity})

@require_POST
def create_activity(request):
    try:
        # Get request data
        data = json.loads(request.body)
        name = data.get('name')
        category_slug = data.get('category')
        is_favorite = data.get('favorite', False)
        
        # Basic validation
        if not name or not category_slug:
            return JsonResponse({'message': 'Name and category are required'}, status=400)
        
        # Get the category
        try:
            category = ActivityCategory.objects.get(slug=category_slug)
        except ActivityCategory.DoesNotExist:
            return JsonResponse({'message': f'Category {category_slug} does not exist'}, status=400)
            
        # For favorites, check if a similar favorite already exists
        if is_favorite:
            # Check if this user already has a favorite with this name in this category
            existing_favorite = Activity.objects.filter(
                user=request.user,
                name__iexact=name,
                category=category,
                favorite=True
            ).first()
            
            # For consumption activities, also check description and ingredients
            if existing_favorite and category_slug == 'consume':
                description = data.get('description', '').strip()
                ingredients = [i.strip() for i in data.get('ingredients', []) if i.strip()]
                
                # Get existing consumption details
                existing_consumption = Consumption.objects.filter(activity=existing_favorite).first()
                
                if existing_consumption:
                    existing_description = (existing_consumption.description or '').strip()
                    existing_ingredients = [i.strip() for i in (existing_consumption.ingredients or '').split('\n') if i.strip()]
                    
                    # Only consider it a duplicate if name, description, and ingredients match
                    # If either the new or existing activity has no description/ingredients, don't consider them in duplicate check
                    description_match = (not description and not existing_description) or description == existing_description
                    ingredients_match = (not ingredients and not existing_ingredients) or set(ingredients) == set(existing_ingredients)
                    
                    if not (description_match and ingredients_match):
                        # If details differ, it's not a true duplicate
                        existing_favorite = None
            
            if existing_favorite:
                return JsonResponse({'message': 'An identical favorite activity already exists'}, status=400)
        
        # Create the activity
        activity = Activity.objects.create(
            user=request.user,
            name=name,
            category=category,
            favorite=is_favorite
        )
        
        # Handle category-specific data
        if category_slug == 'consume':
            # Get consumption-specific data
            description = data.get('description', '')
            ingredients = data.get('ingredients', [])
            date_str = data.get('date')
            time_str = data.get('time')
            
            # Join ingredients as newline-separated string
            ingredients_str = '\n'.join(ingredients) if ingredients else ''
            
            # Parse date and time
            if date_str and time_str:
                try:
                    # Combine date and time strings
                    datetime_str = f"{date_str} {time_str}"
                    
                    # Parse the datetime as a naive datetime
                    naive_dt = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M')
                    
                    # Get the user's timezone
                    user_timezone = request.user.timezone
                    
                    # Make it timezone-aware using the user's timezone
                    # This correctly localizes the time
                    aware_dt = timezone.make_aware(naive_dt, ZoneInfo(user_timezone))
                    
                    # Convert to UTC for storage in the database
                    # This ensures consistent timezone storage
                    utc_dt = aware_dt.astimezone(ZoneInfo('UTC'))
                    
                    print(f"Input date/time: {date_str} {time_str}")
                    print(f"User timezone: {user_timezone}")
                    print(f"Naive datetime: {naive_dt}")
                    print(f"Aware datetime (user TZ): {aware_dt}")
                    print(f"UTC datetime: {utc_dt}")
                    
                except ValueError:
                    return JsonResponse({'message': 'Invalid date or time format'}, status=400)
            else:
                # Default to current time in user's timezone
                aware_dt = timezone.now()
                utc_dt = aware_dt.astimezone(ZoneInfo('UTC'))
            
            # Create consumption record with the timezone-aware datetime
            Consumption.objects.create(
                activity=activity,
                description=description,
                ingredients=ingredients_str,
                consumed_at=utc_dt  # Store as UTC
            )
        
        return JsonResponse({'message': 'Activity created successfully'})
    
    except json.JSONDecodeError:
        return JsonResponse({'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'message': str(e)}, status=400)

@login_required
def delete_activity(request, pk):
    """Delete an activity."""
    activity = get_object_or_404(Activity, pk=pk, user=request.user)
    
    if request.method == 'POST':
        activity_name = activity.name
        activity.delete()
        
        # Check if it's an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'message': f'Activity "{activity_name}" deleted successfully!'
            })
        
        # Regular form post - redirect
        return redirect('activities:list')
    
    # GET request
    return render(request, 'activities/delete_activity.html', {'activity': activity})

@login_required
def get_favorites(request, category_slug):
    """Get favorite activities for a specific category."""
    # Get base favorites query
    favorites_query = Activity.objects.filter(
        user=request.user,
        category__slug=category_slug,
        favorite=True
    )
    
    # For consume category, include consumption details
    if category_slug == 'consume':
        favorites = []
        for activity in favorites_query:
            consumption = Consumption.objects.filter(activity=activity).first()
            favorite_data = {
                'id': activity.id,
                'name': activity.name,
                'description': consumption.description if consumption else None,
                'ingredients': consumption.ingredients.split('\n') if consumption and consumption.ingredients else []
            }
            favorites.append(favorite_data)
    else:
        # For other categories, just get basic info
        favorites = list(favorites_query.values('id', 'name', 'description'))
    
    # Remove duplicates based on name and description
    unique_favorites = []
    seen = set()
    for favorite in favorites:
        # For consume items, include ingredients in the uniqueness check
        if category_slug == 'consume':
            key = (
                favorite['name'].lower(),
                (favorite.get('description') or '').strip(),
                tuple(sorted(favorite.get('ingredients', [])))
            )
        else:
            key = (favorite['name'].lower(), (favorite.get('description') or '').strip())
            
        if key not in seen:
            seen.add(key)
            unique_favorites.append(favorite)
    
    return JsonResponse(unique_favorites, safe=False)

@login_required
@require_POST
def update_activity(request, pk):
    """Update an activity."""
    activity = get_object_or_404(Activity, pk=pk, user=request.user)
    
    try:
        # Validate required fields
        name = request.POST.get('name')
        if not name:
            return JsonResponse({
                'success': False,
                'error': 'Name is required'
            }, status=400)
        
        # Update basic activity fields
        activity.name = name
        activity.description = request.POST.get('description', '')
        activity.favorite = request.POST.get('favorite') == 'on'
        activity.save()
        
        # Handle consumption-specific fields
        if activity.category.slug == 'consume':
            consumption = activity.consumptions.first()
            if not consumption:
                consumption = Consumption(activity=activity)
            
            consumption.description = request.POST.get('consumption_description', '')
            consumption.ingredients = request.POST.get('ingredients', '')
            
            # Combine date and time for consumed_at
            consumed_date = request.POST.get('consumed_at_date')
            consumed_time = request.POST.get('consumed_at_time')
            if consumed_date and consumed_time:
                try:
                    # Parse the datetime as a naive datetime
                    naive_dt = datetime.strptime(f"{consumed_date} {consumed_time}", "%Y-%m-%d %H:%M")
                    
                    # Get the user's timezone
                    user_timezone = request.user.timezone
                    
                    # Make it timezone-aware using the user's timezone
                    aware_dt = timezone.make_aware(naive_dt, ZoneInfo(user_timezone))
                    
                    # Convert to UTC for storage in the database
                    utc_dt = aware_dt.astimezone(ZoneInfo('UTC'))
                    
                    # Store the UTC time in the database
                    consumption.consumed_at = utc_dt
                    
                    print(f"Update - Input date/time: {consumed_date} {consumed_time}")
                    print(f"Update - User timezone: {user_timezone}")
                    print(f"Update - Naive datetime: {naive_dt}")
                    print(f"Update - Aware datetime (user TZ): {aware_dt}")
                    print(f"Update - UTC datetime: {utc_dt}")
                    
                except ValueError as e:
                    return JsonResponse({
                        'success': False,
                        'error': f'Invalid date/time format: {str(e)}'
                    }, status=400)
            
            consumption.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Activity updated successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400) 