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
    
    # Check if there's a default category in the query string
    default_category = request.GET.get('category', None)
    
    context = {
        'activities': activities,
        'categories': categories,
        'default_category': default_category,
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
                description = data.get('description', '')
                ingredients = data.get('ingredients', [])
                
                # Get existing consumption details
                existing_consumption = Consumption.objects.filter(activity=existing_favorite).first()
                
                if existing_consumption:
                    existing_description = existing_consumption.description or ''
                    existing_ingredients = [i.strip() for i in (existing_consumption.ingredients or '').split('\n') if i.strip()]
                    
                    # Only consider it a duplicate if name, description, and ingredients match
                    ingredients_match = set(ingredients) == set(existing_ingredients)
                    description_match = description.strip() == existing_description.strip()
                    
                    if not (ingredients_match and description_match):
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
    favorites = Activity.objects.filter(
        user=request.user,
        category__slug=category_slug,
        favorite=True
    ).values('id', 'name', 'description')
    
    return JsonResponse(list(favorites), safe=False) 