# main_app/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import (
    BookAnimal, Shelter, Veterinarian, Donation,
    AnimalImage, Review, AdoptionRequest
)

@admin.register(BookAnimal)
class BookAnimalAdmin(admin.ModelAdmin):
    list_display = ['name', 'animal_type', 'breed', 'user', 'status', 'created_at']
    list_filter = ['animal_type', 'status', 'is_for_sale', 'created_at']
    search_fields = ['name', 'breed', 'description', 'user__username']

@admin.register(Shelter)
class ShelterAdmin(admin.ModelAdmin):
    list_display = ['name', 'shelter_type', 'capacity', 'current_animals', 'rating', 'is_active']
    list_filter = ['shelter_type', 'is_active']
    search_fields = ['name', 'address', 'director']

@admin.register(Veterinarian)
class VeterinarianAdmin(admin.ModelAdmin):
    list_display = ['name', 'clinic_type', 'phone_number', 'rating', 'is_emergency']
    list_filter = ['clinic_type', 'is_emergency']
    search_fields = ['name', 'address', 'services']

@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ['get_donor_name', 'shelter', 'donation_type', 'amount', 'status', 'created_at']
    list_filter = ['donation_type', 'status', 'is_anonymous']
    search_fields = ['donor__username', 'shelter__name']

# Boshqa model'lar uchun ham admin sozlamalari...

admin.site.register(AnimalImage)
admin.site.register(Review)
admin.site.register(AdoptionRequest)