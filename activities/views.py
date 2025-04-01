from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST
from datetime import datetime, timedelta
import json
from .models import Activity, ActivityCategory, Consumption

@login_required
def activities_view(request):
    """View for activities page."""
    # Get all categories for the filter
    categories = ActivityCategory.objects.all()
    
    # Get all activities for the current user
    activities = Activity.objects.filter(user=request.user)
    
    context = {
        'activities': activities,
        'categories': categories,
    }
    return render(request, 'activities/activities.html', context)

@login_required
def activity_detail(request, pk):
    """View for a single activity."""
    activity = get_object_or_404(Activity, pk=pk, user=request.user)
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
            timezone_offset = data.get('timezone_offset', 0)
            
            # Join ingredients as newline-separated string
            ingredients_str = '\n'.join(ingredients) if ingredients else ''
            
            # Parse date and time
            if date_str and time_str:
                try:
                    # Combine date and time strings
                    datetime_str = f"{date_str} {time_str}"
                    local_dt = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M')
                    
                    # Adjust for timezone offset
                    utc_dt = local_dt + timedelta(minutes=timezone_offset)
                except ValueError:
                    return JsonResponse({'message': 'Invalid date or time format'}, status=400)
            else:
                # Default to current time
                utc_dt = timezone.now()
            
            # Create consumption record
            Consumption.objects.create(
                activity=activity,
                description=description,
                ingredients=ingredients_str,
                consumed_at=utc_dt
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