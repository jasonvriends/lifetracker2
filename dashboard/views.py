from django.shortcuts import render


def dashboard_view(request):
    """View for the dashboard page."""
    if request.user.is_authenticated:
        # Authenticated user sees the dashboard
        context = {
            'cards': [
                {
                    'title': 'Total Progress',
                    'value': '75%',
                    'description': 'Your overall progress in tracking your life goals.',
                    'icon': 'fas fa-chart-line',
                    'color': 'blue'
                },
                {
                    'title': 'Tasks Completed',
                    'value': '24',
                    'description': 'Number of tasks you have completed this month.',
                    'icon': 'fas fa-tasks',
                    'color': 'green'
                },
                {
                    'title': 'Upcoming Events',
                    'value': '5',
                    'description': 'Events coming up in the next 7 days.',
                    'icon': 'fas fa-calendar',
                    'color': 'purple'
                }
            ]
        }
        return render(request, 'dashboard/dashboard.html', context)
    else:
        # Non-authenticated user sees the landing page
        return render(request, 'dashboard/landing.html')
