from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def activities_view(request):
    """View for activities page."""
    context = {
        'activities': [
            {
                'title': 'Morning Run',
                'description': 'Quick 5k run around the park',
                'date': '2025-03-30',
                'category': 'Exercise',
                'status': 'completed',
                'icon': 'fas fa-running',
                'color': 'green'
            },
            {
                'title': 'Project Meeting',
                'description': 'Weekly team sync with project updates',
                'date': '2025-03-31',
                'category': 'Work',
                'status': 'completed',
                'icon': 'fas fa-briefcase',
                'color': 'blue'
            },
            {
                'title': 'Yoga Session',
                'description': '1-hour yoga and meditation',
                'date': '2025-04-01',
                'category': 'Wellness',
                'status': 'planned',
                'icon': 'fas fa-spa',
                'color': 'purple'
            },
            {
                'title': 'Grocery Shopping',
                'description': 'Weekly grocery shopping',
                'date': '2025-04-02',
                'category': 'Errands',
                'status': 'planned',
                'icon': 'fas fa-shopping-cart',
                'color': 'yellow'
            },
        ]
    }
    return render(request, 'activities/activities.html', context) 