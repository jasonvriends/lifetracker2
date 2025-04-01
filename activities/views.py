from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.urls import reverse
from django.utils import timezone
import json
from .models import Activity, Category, Consumption

@login_required
def activities_view(request):
    """View for activities page."""
    # Get all categories for the filter
    categories = Category.objects.all()
    
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

@login_required
def create_activity(request):
    """Create a new activity."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Get the category
            category_slug = data.get('category')
            category = get_object_or_404(Category, slug=category_slug)
            
            # Create the basic activity
            activity = Activity.objects.create(
                user=request.user,
                name=data.get('activity-name'),
                category=category,
                description=data.get('description', ''),
                favorite=data.get('save-favorite', False)
            )
            
            # Handle category-specific data
            if category_slug == 'consume':
                # Parse date and time
                date_str = data.get('consume-date')
                time_str = data.get('consume-time')
                
                try:
                    # Combine date and time
                    consumed_at = timezone.datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
                    
                    # Create the consumption
                    Consumption.objects.create(
                        activity=activity,
                        description=data.get('description', ''),
                        ingredients=data.get('ingredients', ''),
                        consumed_at=consumed_at
                    )
                except ValueError:
                    # Handle invalid date/time
                    return JsonResponse({'status': 'error', 'message': 'Invalid date or time format'}, status=400)
            
            return JsonResponse({
                'status': 'success', 
                'message': 'Activity created successfully',
                'redirect': reverse('activities:activity_detail', kwargs={'pk': activity.pk})
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    # Default - should be an AJAX POST request
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

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