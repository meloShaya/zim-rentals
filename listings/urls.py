from django.urls import path
from . import views

app_name = 'listings'

urlpatterns = [
    path('', views.listing_list, name='listing_list'),
    path('search/', views.search, name='search'),
    path('<int:pk>/', views.ListingDetailView.as_view(), name='listing_detail'),
    path('create/', views.listing_create, name='listing_create'),
    path('<int:pk>/update/', views.listing_update, name='listing_update'),
    path('<int:pk>/delete/', views.listing_delete, name='listing_delete'),
    path('<int:pk>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('chat/<int:pk>/', views.chat, name='chat'),
    path('messages/', views.landlord_messages, name='landlord_messages'),
    path('messages/<int:listing_id>/read/', views.mark_messages_read, name='mark_messages_read'),
    path('message/<int:message_id>/delete/', views.delete_message, name='delete_message'),
    path('chat/<int:pk>/delete/', views.delete_chat, name='delete_chat'),
    
    # Roommate Finder URLs
    path('roommates/', views.roommate_list, name='roommate_list'),
    path('roommates/<int:pk>/', views.roommate_detail, name='roommate_detail'),
    path('roommates/create/', views.roommate_create, name='roommate_create'),
    path('roommates/<int:pk>/update/', views.roommate_update, name='roommate_update'),
    path('roommates/<int:pk>/delete/', views.roommate_delete, name='roommate_delete'),
    path('roommates/<int:pk>/chat/', views.roommate_chat, name='roommate_chat'),
    
    # Saved Search URLs
    path('saved-searches/', views.saved_search_list, name='saved_search_list'),
    path('saved-searches/create/', views.saved_search_create, name='saved_search_create'),
    path('saved-searches/<int:pk>/update/', views.saved_search_update, name='saved_search_update'),
    path('saved-searches/<int:pk>/delete/', views.saved_search_delete, name='saved_search_delete'),
    path('saved-searches/<int:pk>/results/', views.saved_search_results, name='saved_search_results'),
    path('saved-searches/<int:pk>/toggle/', views.toggle_saved_search_active, name='toggle_saved_search_active'),

    # Contact Us URL
    path('contact-us/', views.contact_us_view, name='contact_us'),
] 