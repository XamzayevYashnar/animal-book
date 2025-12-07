from django.urls import path
from . import views

urlpatterns = [
 
    path('', views.home_view, name='home'),
    
   
    path('animals/', views.animals_list_view, name='animals_list'),
    path('animals/my/', views.my_animals_view, name='my_animals'),
    path('animals/add/', views.add_animal_view, name='add_animal'),
    path('animals/<int:pk>/', views.animal_detail_view, name='animal_detail'),
    path('animals/<int:pk>/edit/', views.edit_animal_view, name='edit_animal'),
    path('animals/<int:pk>/delete/', views.delete_animal_view, name='delete_animal'),
    path('animals/<int:pk>/request-adoption/', views.request_adoption_view, name='request_adoption'),
    
    path('shelters/', views.shelters_list_view, name='shelters_list'),
    path('shelters/<int:pk>/', views.shelter_detail_view, name='shelter_detail'),
    path('shelters/<int:pk>/donate/', views.donate_to_shelter_view, name='donate_to_shelter'),
    
    path('veterinarians/', views.veterinarians_list_view, name='veterinarians_list'),
    path('veterinarians/<int:pk>/', views.veterinarian_detail_view, name='veterinarian_detail'),
    
    path('donations/', views.donations_list_view, name='donations_list'),
    path('donations/create/', views.create_donation_view, name='create_donation'),
    path('donations/<int:pk>/', views.donation_detail_view, name='donation_detail'),
    
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),
    path('faq/', views.faq_view, name='faq'),
    path('terms/', views.terms_view, name='terms'),
    path('privacy/', views.privacy_view, name='privacy'),
    
    path('profile/', views.profile_view, name='profile'),
    
    path('review/add/<str:model_type>/<int:pk>/', views.add_review_view, name='add_review'),
    path('adoption-request/<int:pk>/<str:action>/', views.manage_adoption_request_view, name='manage_adoption_request'),
    path('additional-info/', views.add_animal_view, name='add_animal_info'),
    path('shelters/', views.shelters_list_view, name='shelters_list'),
    path('shelters/create/', views.shelter_create_view, name='shelter_create'),
]