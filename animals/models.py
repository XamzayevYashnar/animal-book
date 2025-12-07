from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from users.models import CustomUser as User

class BookAnimal(models.Model):
    ANIMAL_TYPES = [
        ('dog', 'Kuchuk'),
        ('cat', 'Mushuk'),
        ('bird', 'Qush'),
        ('rabbit', 'Quyon'),
        ('fish', 'Baliq'),
        ('rodent', 'Kemiruvchi'),
        ('reptile', 'Sudraluvchi'),
        ('other', 'Boshqa'),
    ]
    
    GENDER_CHOICES = [
        ('male', 'Erkak'),
        ('female', 'Urg\'ochi'),
        ('unknown', 'Noma\'lum'),
    ]
    
    STATUS_CHOICES = [
        ('available', 'Mavjud'),
        ('pending', 'Ko\'rib chiqilmoqda'),
        ('adopted', 'Asrab olingan'),
        ('sold', 'Sotilgan'),
        ('reserved', 'Band qilingan'),
    ]
    
    name = models.CharField(max_length=100, verbose_name="Nomi")
    animal_type = models.CharField(max_length=50, choices=ANIMAL_TYPES, verbose_name="Hayvon turi")
    breed = models.CharField(max_length=100, blank=True, null=True, verbose_name="Zoti")
    age = models.IntegerField(blank=True, null=True, verbose_name="Yoshi")
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True, verbose_name="Jinsi")
    description = models.TextField(blank=True, null=True, verbose_name="Tarif")
    location = models.CharField(max_length=200, verbose_name="Manzil")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Foydalanuvchi")
    is_for_sale = models.BooleanField(default=False, verbose_name="Sotiladi")
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Narxi")
    image = models.ImageField(upload_to='animal_images/', blank=True, null=True, verbose_name="Rasm")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available', verbose_name="Holati")
    vaccinated = models.BooleanField(default=False, verbose_name="Emlangan")
    sterilized = models.BooleanField(default=False, verbose_name="Sterilizatsiya qilingan")
    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefon raqam")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqt")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Yangilangan vaqt")
    
    def __str__(self):
        return f"{self.name} ({self.get_animal_type_display()})"
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Hayvon'
        verbose_name_plural = 'Hayvonlar'
    
    def get_status_color(self):
        colors = {
            'available': 'success',
            'pending': 'warning',
            'adopted': 'info',
            'sold': 'primary',
            'reserved': 'secondary'
        }
        return colors.get(self.status, 'secondary')


class Shelter(models.Model):
    SHELTER_TYPES = [
        ('state', 'Davlat'),
        ('private', 'Xususiy'),
        ('volunteer', 'Ko\'ngilli'),
        ('international', 'Xalqaro'),
    ]
    
    name = models.CharField(max_length=200, verbose_name="Boshpana nomi")
    shelter_type = models.CharField(max_length=50, choices=SHELTER_TYPES, verbose_name="Boshpana turi")
    description = models.TextField(verbose_name="Tarif")
    address = models.CharField(max_length=300, verbose_name="Manzil")
    phone_number = models.CharField(max_length=20, verbose_name="Telefon raqam")
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    website = models.URLField(blank=True, null=True, verbose_name="Veb-sayt")
    capacity = models.IntegerField(verbose_name="Sig'imi")
    current_animals = models.IntegerField(default=0, verbose_name="Joriy hayvonlar soni")
    director = models.CharField(max_length=100, verbose_name="Rahbar")
    founded_date = models.DateField(blank=True, null=True, verbose_name="Tashkil etilgan sana")
    image = models.ImageField(upload_to='shelter_images/', blank=True, null=True, verbose_name="Rasm")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True, verbose_name="Kenglik")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True, verbose_name="Uzunlik")
    is_active = models.BooleanField(default=True, verbose_name="Faol")
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0, 
                                 validators=[MinValueValidator(0), MaxValueValidator(5)], verbose_name="Reyting")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqt")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Yangilangan vaqt")
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Boshpana'
        verbose_name_plural = 'Boshpanalar'
    
    def available_space(self):
        return self.capacity - self.current_animals
    
    def occupancy_percentage(self):
        if self.capacity == 0:
            return 0
        return round((self.current_animals / self.capacity) * 100, 2)


class Veterinarian(models.Model):
    CLINIC_TYPES = [
        ('clinic', 'Klinika'),
        ('hospital', 'Shifoxona'),
        ('mobile', 'Mobil xizmat'),
        ('specialized', 'Mutaxassislik klinikasi'),
    ]
    
    SERVICES = [
        ('general', 'Umumiy veterinariya'),
        ('surgery', 'Jarrohlik'),
        ('dental', 'Stomatologiya'),
        ('dermatology', 'Dermatologiya'),
        ('ophthalmology', 'Oftalmologiya'),
        ('emergency', 'Shoshilinch yordam'),
        ('vaccination', 'Emlash'),
        ('grooming', 'Grooming'),
    ]
    
    name = models.CharField(max_length=200, verbose_name="Nomi")
    clinic_type = models.CharField(max_length=50, choices=CLINIC_TYPES, verbose_name="Klinika turi")
    description = models.TextField(verbose_name="Tarif")
    address = models.CharField(max_length=300, verbose_name="Manzil")
    phone_number = models.CharField(max_length=20, verbose_name="Telefon raqam")
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    website = models.URLField(blank=True, null=True, verbose_name="Veb-sayt")
    services = models.CharField(max_length=200, verbose_name="Xizmatlar")
    working_hours = models.CharField(max_length=100, verbose_name="Ish soatlari")
    director = models.CharField(max_length=100, verbose_name="Rahbar")
    doctors_count = models.IntegerField(default=1, verbose_name="Shifokorlar soni")
    image = models.ImageField(upload_to='veterinarian_images/', blank=True, null=True, verbose_name="Rasm")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True, verbose_name="Kenglik")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True, verbose_name="Uzunlik")
    is_emergency = models.BooleanField(default=False, verbose_name="Shoshilinch xizmat")
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0,
                                 validators=[MinValueValidator(0), MaxValueValidator(5)], verbose_name="Reyting")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqt")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Yangilangan vaqt")
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Veterinariya'
        verbose_name_plural = 'Veterinariyalar'
    
    def get_services_list(self):
        return self.services.split(',') if self.services else []
    
    def is_open_now(self):
        # Bu yerda haqiqiy vaqtni tekshirish logikasi bo'lishi kerak
        # Oddiylik uchun doim ochiq deb qaytaramiz
        return True


class Donation(models.Model):
    DONATION_TYPES = [
        ('money', 'Pul'),
        ('food', 'Oziq-ovqat'),
        ('medicine', 'Dori-darmon'),
        ('equipment', 'Uskuna'),
        ('other', 'Boshqa'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Kutilmoqda'),
        ('confirmed', 'Tasdiqlangan'),
        ('delivered', 'Yetkazib berilgan'),
        ('cancelled', 'Bekor qilingan'),
    ]
    
    donor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                              related_name='donations', verbose_name="Xayriyachi")
    shelter = models.ForeignKey(Shelter, on_delete=models.CASCADE, related_name='donations', 
                                verbose_name="Boshpana")
    donation_type = models.CharField(max_length=50, choices=DONATION_TYPES, verbose_name="Xayriya turi")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Miqdor")
    description = models.TextField(blank=True, null=True, verbose_name="Tarif")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Holati")
    is_anonymous = models.BooleanField(default=False, verbose_name="Anonim")
    message = models.TextField(blank=True, null=True, verbose_name="Xabar")
    receipt_image = models.ImageField(upload_to='donation_receipts/', blank=True, null=True, 
                                      verbose_name="Chek rasmi")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqt")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Yangilangan vaqt")
    
    def __str__(self):
        return f"{self.donor.username if self.donor else 'Anonim'} - {self.amount} - {self.shelter.name}"
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Xayriya'
        verbose_name_plural = 'Xayriyalar'
    
    def get_donor_name(self):
        if self.is_anonymous:
            return "Anonim xayriyachi"
        return self.donor.username if self.donor else "Noma'lum"
    
    def get_status_color(self):
        colors = {
            'pending': 'warning',
            'confirmed': 'info',
            'delivered': 'success',
            'cancelled': 'danger'
        }
        return colors.get(self.status, 'secondary')


# Qo'shimcha model'lar
class AnimalImage(models.Model):
    animal = models.ForeignKey(BookAnimal, on_delete=models.CASCADE, related_name='images', 
                               verbose_name="Hayvon")
    image = models.ImageField(upload_to='animal_gallery/', verbose_name="Rasm")
    is_main = models.BooleanField(default=False, verbose_name="Asosiy rasm")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqt")
    
    class Meta:
        ordering = ['-is_main', '-created_at']
        verbose_name = 'Hayvon rasmi'
        verbose_name_plural = 'Hayvon rasmlari'
    
    def __str__(self):
        return f"{self.animal.name} rasmi"


class Review(models.Model):
    RATING_CHOICES = [
        (1, '1 - Juda yomon'),
        (2, '2 - Yomon'),
        (3, '3 - O\'rtacha'),
        (4, '4 - Yaxshi'),
        (5, '5 - Juda yaxshi'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews', 
                             verbose_name="Foydalanuvchi")
    veterinarian = models.ForeignKey(Veterinarian, on_delete=models.CASCADE, related_name='reviews', 
                                     blank=True, null=True, verbose_name="Veterinariya")
    shelter = models.ForeignKey(Shelter, on_delete=models.CASCADE, related_name='reviews', 
                                blank=True, null=True, verbose_name="Boshpana")
    rating = models.IntegerField(choices=RATING_CHOICES, verbose_name="Reyting")
    comment = models.TextField(verbose_name="Sharh")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqt")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Yangilangan vaqt")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Sharh'
        verbose_name_plural = 'Sharhlar'
        unique_together = [['user', 'veterinarian'], ['user', 'shelter']]
    
    def __str__(self):
        if self.veterinarian:
            return f"{self.user.username} - {self.veterinarian.name} ({self.rating})"
        else:
            return f"{self.user.username} - {self.shelter.name} ({self.rating})"


class AdoptionRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Kutilmoqda'),
        ('approved', 'Tasdiqlangan'),
        ('rejected', 'Rad etilgan'),
        ('completed', 'Yakunlangan'),
        ('cancelled', 'Bekor qilingan'),
    ]
    
    animal = models.ForeignKey(BookAnimal, on_delete=models.CASCADE, related_name='adoption_requests', 
                               verbose_name="Hayvon")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='adoption_requests', 
                             verbose_name="Foydalanuvchi")
    message = models.TextField(verbose_name="Xabar")
    phone_number = models.CharField(max_length=20, verbose_name="Telefon raqam")
    address = models.CharField(max_length=300, verbose_name="Manzil")
    experience = models.TextField(blank=True, null=True, verbose_name="Tajriba")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Holati")
    admin_notes = models.TextField(blank=True, null=True, verbose_name="Admin izohlari")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqt")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Yangilangan vaqt")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Asrab olish so\'rovi'
        verbose_name_plural = 'Asrab olish so\'rovlari'
    
    def __str__(self):
        return f"{self.user.username} - {self.animal.name}"
    
    def get_status_color(self):
        colors = {
            'pending': 'warning',
            'approved': 'info',
            'rejected': 'danger',
            'completed': 'success',
            'cancelled': 'secondary'
        }
        return colors.get(self.status, 'secondary')
    
from django.db import models

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
