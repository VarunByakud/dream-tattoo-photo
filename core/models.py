from django.db import models
from django.contrib.auth.models import User
from dashboard.models import Employee

class Service(models.Model):
    CATEGORY_CHOICES = (
        ('Photography', 'Photography'),
        ('Tattoo', 'Tattoo'),
    )
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='Photography')
    description = models.TextField()
    starting_price = models.DecimalField(max_digits=10, decimal_places=2)
    icon_class = models.CharField(max_length=50, default='bi-camera', help_text="Bootstrap icon name (e.g. bi-camera, bi-heart-fill)")
    image = models.ImageField(upload_to='services/', blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.category})"

class GalleryItem(models.Model):
    CATEGORY_CHOICES = (
        ('Wedding', 'Wedding Gallery'),
        ('Pre-Wedding', 'Pre-Wedding Gallery'),
        ('Baby Shoot', 'Baby Shoot Gallery'),
        ('Birthday', 'Birthday Gallery'),
        ('Tattoo', 'Tattoo Gallery'),
    )
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='gallery/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.get_category_display()}"

class Booking(models.Model):
    PACKAGE_CHOICES = (
        ('Basic', 'Basic Package'),
        ('Premium', 'Premium Package'),
        ('Luxury', 'Luxury Package'),
        ('Custom', 'Custom Package'),
    )
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    )
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='bookings')
    customer_name = models.CharField(max_length=100)
    customer_mobile = models.CharField(max_length=15)
    customer_email = models.EmailField(blank=True, null=True)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='bookings')
    date = models.DateField()
    package = models.CharField(max_length=20, choices=PACKAGE_CHOICES, default='Basic')
    photographer = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='bookings')
    location = models.TextField()
    advance_payment = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer_name} - {self.service.name} ({self.date})"
