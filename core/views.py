from django.shortcuts import render

# Create your views here.
def privacy_policy(request):
    return render(request, 'privacy-policy.html')

def terms_conditions(request):
    return render(request, 'terms-conditions.html')
