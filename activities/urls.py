from django.urls import path
from . import views

urlpatterns = [
    path('', views.activities_view, name='activities'),
] 