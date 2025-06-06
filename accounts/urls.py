from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('favorites/', views.favorites, name='favorites'),
    path('verification/', views.landlord_verification, name='landlord_verification'),
] 