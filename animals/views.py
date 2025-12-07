from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum
from django.db import models
from django.core.paginator import Paginator
from .models import (
    BookAnimal, Shelter, Veterinarian, Donation,
    AnimalImage, Review, AdoptionRequest
)
from users.models import CustomUser

# ==================== ASOSIY VIEW'LAR ====================

# views.py

from django.shortcuts import render
from django.db.models import Q
from .models import BookAnimal, Shelter, Veterinarian, Donation

def home_view(request):
    """Asosiy sahifa"""
    # Filter parametrlarini olish
    category = request.GET.get('category', '')
    animal_type = request.GET.get('animal_type', '')
    search_query = request.GET.get('search', '')
    
    # Boshlang'ich queryset
    animals = BookAnimal.objects.filter(status='available')
    
    # Filterlar
    if category == 'free':
        animals = animals.filter(is_for_sale=False)
    elif category == 'paid':
        animals = animals.filter(is_for_sale=True)
    
    if animal_type:
        if animal_type == 'other':
            # "other" - dog va cat dan boshqa barcha hayvonlar
            animals = animals.exclude(animal_type__in=['dog', 'cat'])
        else:
            animals = animals.filter(animal_type=animal_type)
    
    if search_query:
        animals = animals.filter(
            Q(name__icontains=search_query) |
            Q(breed__icontains=search_query) |
            Q(location__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # So'nggi qo'shilgan hayvonlar (filtrlarsiz)
    latest_animals = BookAnimal.objects.filter(status='available').order_by('-created_at')[:6]
    
    # Statistikalar
    total_animals = BookAnimal.objects.filter(status='available').count()
    free_animals = BookAnimal.objects.filter(status='available', is_for_sale=False).count()
    paid_animals = BookAnimal.objects.filter(status='available', is_for_sale=True).count()
    
    # Hayvon turlari bo'yicha statistikalar
    dogs_count = BookAnimal.objects.filter(status='available', animal_type='dog').count()
    cats_count = BookAnimal.objects.filter(status='available', animal_type='cat').count()
    other_count = BookAnimal.objects.filter(status='available').exclude(animal_type__in=['dog', 'cat']).count()
    
    total_shelters = Shelter.objects.filter(is_active=True).count()
    total_donations = Donation.objects.filter(status__in=['confirmed', 'delivered']).count() if hasattr(Donation, 'status') else 0
    
    top_shelters = Shelter.objects.filter(is_active=True).order_by('-rating')[:3]
    top_veterinarians = Veterinarian.objects.all().order_by('-rating')[:3]
    
    context = {
        'animals': animals[:12],  # Faqat birinchi 12 ta hayvonni ko'rsat
        'latest_animals': latest_animals,
        'total_animals': total_animals,
        'free_animals': free_animals,
        'paid_animals': paid_animals,
        'dogs_count': dogs_count,
        'cats_count': cats_count,
        'other_count': other_count,
        'total_shelters': total_shelters,
        'total_donations': total_donations,
        'top_shelters': top_shelters,
        'top_veterinarians': top_veterinarians,
        'current_category': category,
        'current_animal_type': animal_type,
        'search_query': search_query,
    }
    return render(request, 'main_app/home.html', context)


# ==================== HAYVONLAR VIEW'LARI ====================

def animals_list_view(request):
    """Barcha hayvonlar ro'yxati"""
    # Filtrlarni olish
    category = request.GET.get('category', '')
    animal_type = request.GET.get('animal_type', '')
    search_query = request.GET.get('search', '')
    
    animals = BookAnimal.objects.filter(status='available').order_by('-created_at')
    
    if category:
        if category == 'free':
            animals = animals.filter(is_for_sale=False)
        elif category == 'paid':
            animals = animals.filter(is_for_sale=True)
    
    if animal_type:
        animals = animals.filter(animal_type=animal_type)
    
    if search_query:
        animals = animals.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(location__icontains=search_query) |
            Q(breed__icontains=search_query)
        )
    
    paginator = Paginator(animals, 12)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    total_count = animals.count()
    dogs_count = animals.filter(animal_type='dog').count()
    cats_count = animals.filter(animal_type='cat').count()
    other_count = animals.filter(animal_type='other').count()
    free_count = animals.filter(is_for_sale=False).count()
    paid_count = animals.filter(is_for_sale=True).count()
    
    context = {
        'animals': page_obj,
        'total_count': total_count,
        'dogs_count': dogs_count,
        'cats_count': cats_count,
        'other_count': other_count,
        'free_count': free_count,
        'paid_count': paid_count,
        'current_category': category,
        'current_animal_type': animal_type,
        'search_query': search_query,
        'page_obj': page_obj,
    }
    return render(request, 'main_app/animals/list.html', context)


def animal_detail_view(request, pk):
    """Hayvon tafsilotlari"""
    animal = get_object_or_404(BookAnimal, pk=pk)
    
    additional_images = AnimalImage.objects.filter(animal=animal)
    
    similar_animals = BookAnimal.objects.filter(
        animal_type=animal.animal_type,
        status='available'
    ).exclude(pk=pk).order_by('-created_at')[:4]
    
    # Asrab olish so'rovlari (faqat hayvon egasi ko'rishi mumkin)
    adoption_requests = None
    if request.user == animal.user:
        adoption_requests = AdoptionRequest.objects.filter(
            animal=animal
        ).order_by('-created_at')
    
    context = {
        'animal': animal,
        'additional_images': additional_images,
        'similar_animals': similar_animals,
        'adoption_requests': adoption_requests,
    }
    return render(request, 'main_app/animals/detail.html', context)


@login_required
def add_animal_view(request):
    """Yangi hayvon qo'shish"""
    if request.method == 'POST':
        try:
            # Asosiy ma'lumotlar
            animal = BookAnimal.objects.create(
                user=request.user,
                name=request.POST.get('name'),
                animal_type=request.POST.get('animal_type'),
                breed=request.POST.get('breed', ''),
                age=request.POST.get('age'),
                gender=request.POST.get('gender'),
                description=request.POST.get('description'),
                location=request.POST.get('location'),
                is_for_sale=request.POST.get('is_for_sale') == 'on',
                price=request.POST.get('price') if request.POST.get('is_for_sale') == 'on' else None,
                phone_number=request.POST.get('phone_number'),
                vaccinated=request.POST.get('vaccinated') == 'true',
                sterilized=request.POST.get('sterilized') == 'true',
                image=request.FILES.get('image')
            )
            
            # Qo'shimcha rasmlar
            additional_images = request.FILES.getlist('additional_images')
            for img in additional_images:
                AnimalImage.objects.create(animal=animal, image=img)
            
            messages.success(request, f"{animal.name} muvaffaqiyatli qo'shildi!")
            return redirect('animal_detail', pk=animal.pk)
            
        except Exception as e:
            messages.error(request, f"Xatolik yuz berdi: {str(e)}")
    
    return render(request, 'main_app/animals/add.html')


@login_required
def edit_animal_view(request, pk):
    """Hayvonni tahrirlash"""
    animal = get_object_or_404(BookAnimal, pk=pk)
    
    # Faqat egasi yoki admin tahrirlashi mumkin
    if animal.user != request.user and not request.user.is_staff:
        messages.error(request, "Siz faqat o'zingizning hayvonlaringizni tahrirlashingiz mumkin!")
        return redirect('animal_detail', pk=pk)
    
    if request.method == 'POST':
        try:
            # Asosiy ma'lumotlarni yangilash
            animal.name = request.POST.get('name')
            animal.animal_type = request.POST.get('animal_type')
            animal.breed = request.POST.get('breed', '')
            animal.age = request.POST.get('age')
            animal.gender = request.POST.get('gender')
            animal.description = request.POST.get('description')
            animal.location = request.POST.get('location')
            animal.is_for_sale = request.POST.get('is_for_sale') == 'on'
            animal.price = request.POST.get('price') if animal.is_for_sale else None
            animal.phone_number = request.POST.get('phone_number')
            animal.vaccinated = request.POST.get('vaccinated') == 'true'
            animal.sterilized = request.POST.get('sterilized') == 'true'
            animal.status = request.POST.get('status', 'available')
            
            # Asosiy rasm yangilash
            if request.FILES.get('image'):
                animal.image = request.FILES.get('image')
            
            animal.save()
            
            # Qo'shimcha rasmlar
            additional_images = request.FILES.getlist('additional_images')
            for img in additional_images:
                AnimalImage.objects.create(animal=animal, image=img)
            
            messages.success(request, f"{animal.name} muvaffaqiyatli yangilandi!")
            return redirect('animal_detail', pk=animal.pk)
            
        except Exception as e:
            messages.error(request, f"Xatolik yuz berdi: {str(e)}")
    
    context = {
        'animal': animal,
        'additional_images': AnimalImage.objects.filter(animal=animal),
    }
    return render(request, 'main_app/animals/edit.html', context)


@login_required
def delete_animal_view(request, pk):
    """Hayvonni o'chirish"""
    animal = get_object_or_404(BookAnimal, pk=pk)
    
    # Faqat egasi yoki admin o'chirishi mumkin
    if animal.user != request.user and not request.user.is_staff:
        messages.error(request, "Siz faqat o'zingizning hayvonlaringizni o'chirishingiz mumkin!")
        return redirect('animal_detail', pk=pk)
    
    if request.method == 'POST':
        animal_name = animal.name
        animal.delete()
        messages.success(request, f"{animal_name} muvaffaqiyatli o'chirildi!")
        return redirect('my_animals')
    
    context = {
        'animal': animal,
    }
    return render(request, 'main_app/animals/delete.html', context)


@login_required
def my_animals_view(request):
    """Foydalanuvchining hayvonlari"""
    animals = BookAnimal.objects.filter(user=request.user).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(animals, 12)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'animals': page_obj,
        'page_obj': page_obj,
    }
    return render(request, 'main_app/animals/my_animals.html', context)


@login_required
def request_adoption_view(request, pk):
    """Asrab olish so'rovi yuborish"""
    animal = get_object_or_404(BookAnimal, pk=pk, status='available')
    
    # O'z hayvoniga so'rov yuborish mumkin emas
    if animal.user == request.user:
        messages.error(request, "O'zingizning hayvoningizga asrab olish so'rovi yuborolmaysiz!")
        return redirect('animal_detail', pk=pk)
    
    # Oldin so'rov yuborilganmi tekshirish
    existing_request = AdoptionRequest.objects.filter(
        animal=animal, 
        user=request.user,
        status__in=['pending', 'approved']
    ).exists()
    
    if existing_request:
        messages.warning(request, "Siz allaqachon bu hayvon uchun so'rov yuborgansiz!")
        return redirect('animal_detail', pk=pk)
    
    if request.method == 'POST':
        try:
            adoption_request = AdoptionRequest.objects.create(
                animal=animal,
                user=request.user,
                message=request.POST.get('message'),
                phone_number=request.POST.get('phone_number'),
                address=request.POST.get('address'),
                experience=request.POST.get('experience', '')
            )
            
            messages.success(request, "Asrab olish so'rovi muvaffaqiyatli yuborildi!")
            return redirect('animal_detail', pk=pk)
            
        except Exception as e:
            messages.error(request, f"Xatolik yuz berdi: {str(e)}")
    
    context = {
        'animal': animal,
    }
    return render(request, 'main_app/animals/request_adoption.html', context)


# ==================== BOSHPANALAR VIEW'LARI ====================

def shelters_list_view(request):
    """Barcha boshpanalar ro'yxati"""
    shelters = Shelter.objects.filter(is_active=True).order_by('-rating')
    
    # Filtrlash
    shelter_type = request.GET.get('type', '')
    search_query = request.GET.get('search', '')
    
    if shelter_type:
        shelters = shelters.filter(shelter_type=shelter_type)
    
    if search_query:
        shelters = shelters.filter(
            Q(name__icontains=search_query) |
            Q(address__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Statistikalar
    total_capacity = shelters.aggregate(total=models.Sum('capacity'))['total'] or 0
    total_current = shelters.aggregate(total=models.Sum('current_animals'))['total'] or 0
    total_available = total_capacity - total_current
    
    context = {
        'shelters': shelters,
        'current_type': shelter_type,
        'search_query': search_query,
        'shelter_types': Shelter.SHELTER_TYPES,
        'total_capacity': total_capacity,
        'total_current': total_current,
        'total_available': total_available,
    }
    return render(request, 'main_app/shelters/list.html', context)


def shelter_detail_view(request, pk):
    """Boshpana tafsilotlari"""
    shelter = get_object_or_404(Shelter, pk=pk, is_active=True)
    
    # Boshpanadagi hayvonlar
    animals_in_shelter = BookAnimal.objects.filter(
        Q(location__icontains=shelter.name) |
        Q(user__username__icontains='shelter')
    ).filter(status='available')[:6]
    
    # Boshpana uchun sharhlar
    reviews = Review.objects.filter(shelter=shelter).order_by('-created_at')[:5]
    
    # Oxirgi xayriyalar
    recent_donations = Donation.objects.filter(shelter=shelter).order_by('-created_at')[:10]
    
    # Xayriya statistikasi
    donation_stats = Donation.objects.filter(
        shelter=shelter,
        status__in=['confirmed', 'delivered']
    ).aggregate(
        total_amount=Sum('amount'),
        total_count=models.Count('id')
    )
    
    context = {
        'shelter': shelter,
        'animals': animals_in_shelter,
        'reviews': reviews,
        'recent_donations': recent_donations,
        'donation_stats': donation_stats,
        'occupancy_percentage': shelter.occupancy_percentage(),
        'available_space': shelter.available_space(),
    }
    return render(request, 'main_app/shelters/detail.html', context)


@login_required
def donate_to_shelter_view(request, pk):
    """Boshpanaga xayriya qilish"""
    shelter = get_object_or_404(Shelter, pk=pk, is_active=True)
    
    if request.method == 'POST':
        try:
            donation = Donation.objects.create(
                donor=request.user,
                shelter=shelter,
                donation_type=request.POST.get('donation_type'),
                amount=request.POST.get('amount'),
                description=request.POST.get('description', ''),
                is_anonymous=request.POST.get('is_anonymous') == 'on',
                message=request.POST.get('message', ''),
                receipt_image=request.FILES.get('receipt_image')
            )
            
            messages.success(request, f"{shelter.name} boshpanasiga xayriya muvaffaqiyatli amalga oshirildi!")
            return redirect('shelter_detail', pk=shelter.pk)
            
        except Exception as e:
            messages.error(request, f"Xatolik yuz berdi: {str(e)}")
    
    context = {
        'shelter': shelter,
        'donation_types': Donation.DONATION_TYPES,
    }
    return render(request, 'main_app/shelters/donate.html', context)


# ==================== VETERINARIYALAR VIEW'LARI ====================

# ==================== VETERINARIYALAR VIEW'LARI ====================

def veterinarians_list_view(request):
    """Barcha veterinariyalar ro'yxati"""
    vets = Veterinarian.objects.all().order_by('-rating')
    
    # Filtrlash
    clinic_type = request.GET.get('type', '')
    service = request.GET.get('service', '')
    search_query = request.GET.get('search', '')
    emergency = request.GET.get('emergency', '')
    
    if clinic_type:
        vets = vets.filter(clinic_type=clinic_type)
    
    if service:
        vets = vets.filter(services__icontains=service)
    
    if emergency == 'yes':
        vets = vets.filter(is_emergency=True)
    
    if search_query:
        vets = vets.filter(
            Q(name__icontains=search_query) |
            Q(address__icontains=search_query) |
            Q(services__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Xizmatlar ro'yxati (STATIC)
    SERVICES_CHOICES = [
        ('general', 'Umumiy veterinariya'),
        ('surgery', 'Jarrohlik'),
        ('dental', 'Stomatologiya'),
        ('dermatology', 'Dermatologiya'),
        ('ophthalmology', 'Oftalmologiya'),
        ('emergency', 'Shoshilinch yordam'),
        ('vaccination', 'Emlash'),
        ('grooming', 'Grooming'),
        ('radiology', 'Rentgenologiya'),
        ('laboratory', 'Laboratoriya tekshiruvlari'),
        ('boarding', 'Qarovxona'),
        ('training', 'Mashq qilish'),
    ]
    
    context = {
        'veterinarians': vets,
        'current_type': clinic_type,
        'current_service': service,
        'search_query': search_query,
        'clinic_types': Veterinarian.CLINIC_TYPES,
        'services': SERVICES_CHOICES,  # STATIC ro'yxat
        'emergency_filter': emergency,
    }
    return render(request, 'main_app/veterinarians/list.html', context)


def veterinarian_detail_view(request, pk):
    """Veterinariya tafsilotlari"""
    vet = get_object_or_404(Veterinarian, pk=pk)
    
    # Xizmatlar ro'yxati
    services_list = []
    SERVICE_CHOICES = [
        ('general', 'Umumiy veterinariya'),
        ('surgery', 'Jarrohlik'),
        ('dental', 'Stomatologiya'),
        ('dermatology', 'Dermatologiya'),
        ('ophthalmology', 'Oftalmologiya'),
        ('emergency', 'Shoshilinch yordam'),
        ('vaccination', 'Emlash'),
        ('grooming', 'Grooming'),
        ('radiology', 'Rentgenologiya'),
        ('laboratory', 'Laboratoriya tekshiruvlari'),
        ('boarding', 'Qarovxona'),
        ('training', 'Mashq qilish'),
    ]
    
    if vet.services:
        # Xizmatlarni ajratish
        service_codes = [s.strip() for s in vet.services.split(',') if s.strip()]
        for service_code in service_codes:
            for code, name in SERVICE_CHOICES:
                if code == service_code:
                    services_list.append({
                        'code': code,
                        'name': name
                    })
                    break
    
    # Sharhlar
    reviews = Review.objects.filter(veterinarian=vet).order_by('-created_at')
    
    # O'rtacha reyting
    avg_rating = reviews.aggregate(avg=models.Avg('rating'))['avg'] or 0
    
    # Yaqin atrofdagi veterinariyalar (tasodifiy 4ta)
    nearby_vets = Veterinarian.objects.exclude(pk=pk).order_by('?')[:4]
    
    # Ish vaqtini tekshirish
    is_open = True  # Hozircha har doim ochiq deb olaylik
    
    context = {
        'vet': vet,
        'services_list': services_list,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'nearby_vets': nearby_vets,
        'is_open_now': is_open,
    }
    return render(request, 'main_app/veterinarians/detail.html', context)


# ==================== XAYRIYALAR VIEW'LARI ====================

def donations_list_view(request):
    """Barcha xayriyalar ro'yxati"""
    donations = Donation.objects.all().order_by('-created_at')
    
    # Filtrlash
    donation_type = request.GET.get('type', '')
    status = request.GET.get('status', '')
    shelter_id = request.GET.get('shelter', '')
    
    if donation_type:
        donations = donations.filter(donation_type=donation_type)
    
    if status:
        donations = donations.filter(status=status)
    
    if shelter_id:
        donations = donations.filter(shelter_id=shelter_id)
    
    # Foydalanuvchining xayriyalari
    user_donations = None
    if request.user.is_authenticated:
        user_donations = Donation.objects.filter(donor=request.user).order_by('-created_at')
    
    # Boshpanalar ro'yxati
    shelters = Shelter.objects.filter(is_active=True)
    
    # Umumiy statistika
    total_stats = Donation.objects.filter(
        status__in=['confirmed', 'delivered']
    ).aggregate(
        total_amount=Sum('amount'),
        total_count=models.Count('id')
    )
    
    context = {
        'donations': donations[:50],
        'user_donations': user_donations,
        'shelters': shelters,
        'donation_types': Donation.DONATION_TYPES,
        'status_choices': Donation.STATUS_CHOICES,
        'current_type': donation_type,
        'current_status': status,
        'current_shelter': shelter_id,
        'total_stats': total_stats,
    }
    return render(request, 'main_app/donations/list.html', context)


@login_required
def create_donation_view(request):
    """Yangi xayriya yaratish"""
    shelters = Shelter.objects.filter(is_active=True)
    
    if request.method == 'POST':
        try:
            shelter = get_object_or_404(Shelter, pk=request.POST.get('shelter'))
            
            donation = Donation.objects.create(
                donor=request.user,
                shelter=shelter,
                donation_type=request.POST.get('donation_type'),
                amount=request.POST.get('amount'),
                description=request.POST.get('description', ''),
                is_anonymous=request.POST.get('is_anonymous') == 'on',
                message=request.POST.get('message', ''),
                receipt_image=request.FILES.get('receipt_image')
            )
            
            messages.success(request, f"{shelter.name} boshpanasiga xayriya muvaffaqiyatli amalga oshirildi!")
            return redirect('donation_detail', pk=donation.pk)
            
        except Exception as e:
            messages.error(request, f"Xatolik yuz berdi: {str(e)}")
    
    context = {
        'shelters': shelters,
        'donation_types': Donation.DONATION_TYPES,
    }
    return render(request, 'main_app/donations/create.html', context)


def donation_detail_view(request, pk):
    """Xayriya tafsilotlari"""
    donation = get_object_or_404(Donation, pk=pk)
    
    # Faqat donor yoki admin ko'ra olishi
    if not request.user.is_superuser and donation.donor != request.user and not donation.is_anonymous:
        messages.error(request, "Siz bu xayriya ma'lumotlarini ko'ra olmaysiz!")
        return redirect('donations_list')
    
    context = {
        'donation': donation,
    }
    return render(request, 'main_app/donations/detail.html', context)


# ==================== STATIK SAHIFALAR VIEW'LARI ====================

def about_view(request):
    """Biz haqimizda sahifasi"""
    # Statistikalar
    total_animals = BookAnimal.objects.filter(status='available').count()
    total_shelters = Shelter.objects.filter(is_active=True).count()
    total_veterinarians = Veterinarian.objects.count()
    total_donations = Donation.objects.filter(status__in=['confirmed', 'delivered']).count()
    
    # Xayriya summasi
    total_donation_amount = Donation.objects.filter(
        status__in=['confirmed', 'delivered']
    ).aggregate(total=models.Sum('amount'))['total'] or 0
    
    # Jamoa a'zolari (bu yerda real ma'lumotlar bo'lishi kerak)
    team_members = [
        {'name': 'Azizbek Ismoilov', 'position': 'Asoschi & Direktor', 'bio': 'Hayvonlarni sevuvchi va himoya qiluvchi'},
        {'name': 'Dilfuza Rahimova', 'position': 'Veterinariya mutaxassisi', 'bio': '10 yillik tajribaga ega veterinar'},
        {'name': 'Sanjar Yusupov', 'position': 'Texnik direktor', 'bio': 'Texnologiya va innovatsiyalar bo\'yicha mutaxassis'},
        {'name': 'Madina Karimova', 'position': 'Ijtimoiy mas\'ul', 'bio': 'Boshpanalar va xayriya loyihalari bo\'yicha mas\'ul'},
    ]
    
    context = {
        'total_animals': total_animals,
        'total_shelters': total_shelters,
        'total_veterinarians': total_veterinarians,
        'total_donations': total_donations,
        'total_donation_amount': total_donation_amount,
        'team_members': team_members,
    }
    return render(request, 'main_app/about.html', context)


def contact_view(request):
    """Aloqa sahifasi"""
    if request.method == 'POST':
        try:
            # Bu yerda contact formani qayta ishlash logikasi
            name = request.POST.get('name')
            email = request.POST.get('email')
            subject = request.POST.get('subject')
            message = request.POST.get('message')
            
            # Oddiy saqlash yoki email yuborish
            # Hozircha faqat xabar ko'rsatamiz
            messages.success(request, "Xabaringiz qabul qilindi! Tez orada siz bilan bog'lanamiz.")
            return redirect('contact')
            
        except Exception as e:
            messages.error(request, f"Xatolik yuz berdi: {str(e)}")
    
    return render(request, 'main_app/contact.html')


def faq_view(request):
    """Tez-tez so'raladigan savollar"""
    # FAQ ma'lumotlari
    faqs = [
        {
            'question': 'Platformadan qanday foydalansam bo\'ladi?',
            'answer': 'Ro\'yxatdan o\'tganingizdan so\'ng hayvon qo\'shishingiz, sotib olishingiz yoki asrab olishingiz mumkin. Bepul hayvonlarni ko\'rish uchun ro\'yxatdan o\'tish shart emas.'
        },
        {
            'question': 'Hayvon qo\'shish uchun to\'lov talab qilinadimi?',
            'answer': 'Yo\'q, hayvon qo\'shish mutlaqo bepul. Platforma hayvon egasi va yangi egalarni bog\'lashga yordam beradi.'
        },
        {
            'question': 'Xayriya qilish qanchalik ishonchli?',
            'answer': 'Barcha boshpanalarimiz tekshirilgan va ma\'lumotlari tasdiqlangan. Xayriyangiz to\'g\'ri yo\'naltirilishiga kafolat beramiz.'
        },
        {
            'question': 'Asrab olish jarayoni qanday amalga oshiriladi?',
            'answer': 'Hayvonni tanlang, asrab olish so\'rovi yuboring, hayvon egasi siz bilan bog\'lanadi, uchrashuv o\'tkazing va hayvonni asrab oling.'
        },
        {
            'question': 'Veterinariyalarni qanday topishim mumkin?',
            'answer': 'Veterinariyalar bo\'limida barcha klinikalar ro\'yxati mavjud. Siz filtrlash yordamida turi, xizmati yoki joylashuvi bo\'yicha qidirishingiz mumkin.'
        },
        {
            'question': 'Hayvonni platformada sotish qoidalari qanday?',
            'answer': 'Hayvon sog\'lom va emlangan bo\'lishi, haqiqiy ma\'lumotlar kiritilishi, yaxshi rasmlar joylashtirilishi kerak. Noqonuniy faoliyat taqiqlanadi.'
        },
        {
            'question': 'Platforma qanchalik xavfsiz?',
            'answer': 'Barcha shaxsiy ma\'lumotlar shifrlangan, to\'lovlar xavfsiz kanallar orqali, foydalanuvchilar tekshiriladi, monitoring tizimi mavjud.'
        },
        {
            'question': 'Qanday qilib o\'zimga mos hayvonni topishim mumkin?',
            'answer': 'Hayvon turi, yoshi, zoti, narxi, joylashuvi va nomi bo\'yicha filtrlardan foydalanishingiz mumkin.'
        },
        {
            'question': 'Qo\'shimcha savollarim bo\'lsa qayerga murojaat qilishim kerak?',
            'answer': 'Telefon, email, Telegram yoki aloqa formasi orqali biz bilan bog\'lanishingiz mumkin.'
        },
    ]
    
    context = {'faqs': faqs}
    return render(request, 'main_app/faq.html', context)


def terms_view(request):
    """Foydalanish shartlari"""
    return render(request, 'main_app/terms.html')


def privacy_view(request):
    """Maxfiylik siyosati"""
    return render(request, 'main_app/privacy.html')


# ==================== PROFIL VIEW'LARI ====================

@login_required
def profile_view(request):
    """Foydalanuvchi profili"""
    user = request.user
    
    if request.method == 'POST':
        try:
            # Profil ma'lumotlarini yangilash
            user.first_name = request.POST.get('first_name', '')
            user.last_name = request.POST.get('last_name', '')
            user.email = request.POST.get('email', '')
            user.phone_number = request.POST.get('phone_number', '')
            user.address = request.POST.get('address', '')
            
            if request.FILES.get('avatar'):
                user.avatar = request.FILES.get('avatar')
            
            user.save()
            messages.success(request, "Profil muvaffaqiyatli yangilandi!")
            return redirect('profile')
            
        except Exception as e:
            messages.error(request, f"Xatolik yuz berdi: {str(e)}")
    
    # Foydalanuvchi ma'lumotlari
    user_animals = BookAnimal.objects.filter(user=user).order_by('-created_at')[:5]
    user_donations = Donation.objects.filter(donor=user).order_by('-created_at')[:5]
    adoption_requests = AdoptionRequest.objects.filter(user=user).order_by('-created_at')[:5]
    
    # Statistikalar
    animals_count = BookAnimal.objects.filter(user=user).count()
    donations_count = Donation.objects.filter(donor=user).count()
    adoption_requests_count = AdoptionRequest.objects.filter(user=user).count()
    
    context = {
        'user_animals': user_animals,
        'user_donations': user_donations,
        'adoption_requests': adoption_requests,
        'animals_count': animals_count,
        'donations_count': donations_count,
        'adoption_requests_count': adoption_requests_count,
    }
    return render(request, 'main_app/profile.html', context)


# ==================== QO'SHIMCHA VIEW'LAR ====================

@login_required
def add_review_view(request, model_type, pk):
    """Sharh qo'shish (veterinariya yoki boshpana uchun)"""
    if model_type == 'veterinarian':
        obj = get_object_or_404(Veterinarian, pk=pk)
    elif model_type == 'shelter':
        obj = get_object_or_404(Shelter, pk=pk)
    else:
        messages.error(request, "Noto'g'ri obyekt turi!")
        return redirect('home')
    
    # Oldin sharh qo'shilganmi tekshirish
    existing_review = Review.objects.filter(
        user=request.user,
        **{f'{model_type}': obj}
    ).exists()
    
    if existing_review:
        messages.warning(request, "Siz allaqachon sharh qo'shgan ekansiz!")
        return redirect(f'{model_type}_detail', pk=pk)
    
    if request.method == 'POST':
        try:
            review = Review.objects.create(
                user=request.user,
                rating=request.POST.get('rating'),
                comment=request.POST.get('comment'),
                **{f'{model_type}': obj}
            )
            
            # Obyektning reytingini yangilash
            if model_type == 'veterinarian':
                avg_rating = Review.objects.filter(veterinarian=obj).aggregate(avg=models.Avg('rating'))['avg'] or 0
                obj.rating = avg_rating
                obj.save()
            elif model_type == 'shelter':
                avg_rating = Review.objects.filter(shelter=obj).aggregate(avg=models.Avg('rating'))['avg'] or 0
                obj.rating = avg_rating
                obj.save()
            
            messages.success(request, "Sharh muvaffaqiyatli qo'shildi!")
            return redirect(f'{model_type}_detail', pk=pk)
            
        except Exception as e:
            messages.error(request, f"Xatolik yuz berdi: {str(e)}")
    
    context = {
        'obj': obj,
        'model_type': model_type,
    }
    return render(request, 'main_app/add_review.html', context)


@login_required
def manage_adoption_request_view(request, pk, action):
    """Asrab olish so'rovini boshqarish"""
    adoption_request = get_object_or_404(AdoptionRequest, pk=pk)
    
    # Faqat hayvon egasi boshqarishi mumkin
    if adoption_request.animal.user != request.user:
        messages.error(request, "Siz faqat o'zingizning hayvoningiz so'rovlarini boshqarishingiz mumkin!")
        return redirect('animal_detail', pk=adoption_request.animal.pk)
    
    if action == 'approve':
        adoption_request.status = 'approved'
        adoption_request.save()
        messages.success(request, "Asrab olish so'rovi tasdiqlandi!")
        
    elif action == 'reject':
        adoption_request.status = 'rejected'
        adoption_request.admin_notes = request.POST.get('notes', '')
        adoption_request.save()
        messages.success(request, "Asrab olish so'rovi rad etildi!")
        
    elif action == 'complete':
        adoption_request.status = 'completed'
        adoption_request.animal.status = 'adopted'
        adoption_request.animal.save()
        adoption_request.save()
        messages.success(request, "Asrab olish jarayoni yakunlandi!")
    
    return redirect('animal_detail', pk=adoption_request.animal.pk)

# main_app/views.py

# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Shelter
from .forms import ShelterForm

def is_staff_user(user):
    return user.is_staff

@login_required
@user_passes_test(is_staff_user)
def shelter_create_view(request):
    """Yangi boshpana qo'shish"""
    if request.method == 'POST':
        form = ShelterForm(request.POST, request.FILES)
        if form.is_valid():
            shelter = form.save(commit=False)
            shelter.created_by = request.user
            shelter.save()
            
            # Qo'shimcha rasmlarni saqlash
            additional_images = request.FILES.getlist('additional_images')
            for image in additional_images:
                shelter.additional_images.create(image=image)
            
            messages.success(request, '✅ Boshpana muvaffaqiyatli yaratildi!')
            return redirect('shelters_list')
        else:
            messages.error(request, '❌ Formani to\'ldirishda xatoliklar mavjud.')
    else:
        form = ShelterForm()
    
    # Statistika ma'lumotlari
    context = {
        'form': form,
        'active_shelters': Shelter.objects.filter(is_active=True).count(),
        'total_animals': sum(s.animal_count for s in Shelter.objects.filter(is_active=True)),
        'available_capacity': sum(s.max_capacity - s.current_capacity for s in Shelter.objects.filter(is_active=True)),
    }
    
    return render(request, 'main_app/shelters/create.html', context)