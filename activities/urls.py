from django.urls import path
from . import views

app_name = 'activities'

urlpatterns = [
    path('', views.activities_view, name='list'),
    path('', views.activities_view, name='activities'),
    path('create/', views.create_activity, name='create'),
    path('<int:pk>/', views.activity_detail, name='activity_detail'),
    path('<int:pk>/delete/', views.delete_activity, name='delete'),
    path('favorites/<str:category_slug>/', views.get_favorites, name='get_favorites'),
] 