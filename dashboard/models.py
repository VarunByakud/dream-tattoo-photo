from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid

class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('Admin', 'Admin'),
        ('Staff', 'Staff'),
        ('Customer', 'Customer'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='Customer')
    mobile = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    instance.profile.save()

class Employee(models.Model):
    ROLE_CHOICES = (
        ('Photographer', 'Photographer'),
        ('Editor', 'Editor'),
        ('Designer', 'Designer'),
        ('Manager', 'Manager'),
    )
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    contact_number = models.CharField(max_length=15)
    status = models.CharField(max_length=10, choices=(('Active', 'Active'), ('Inactive', 'Inactive')), default='Active')

    def __str__(self):
        return f"{self.name} - {self.role}"

class Customer(models.Model):
    PAYMENT_STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Partial', 'Partial'),
        ('Paid', 'Paid'),
    )
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='customer_profile')
    name = models.CharField(max_length=100)
    mobile = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    event_date = models.DateField(blank=True, null=True)
    event_type = models.CharField(max_length=100, blank=True, null=True)
    payment_status = models.CharField(max_length=15, choices=PAYMENT_STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Expense(models.Model):
    CATEGORY_CHOICES = (
        ('Camera Purchase', 'Camera Purchase'),
        ('Lens Purchase', 'Lens Purchase'),
        ('Staff Salary', 'Staff Salary'),
        ('Travel Cost', 'Travel Cost'),
        ('Studio Rent', 'Studio Rent'),
        ('Electricity', 'Electricity'),
        ('Other', 'Other'),
    )
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.category} - ₹{self.amount} ({self.date})"

class AlbumDesign(models.Model):
    ALBUM_TYPE_CHOICES = (
        ('Regular Album', 'Regular Album'),
        ('Premium Album', 'Premium Album'),
        ('Luxury Album', 'Luxury Album'),
    )
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Designing', 'Designing'),
        ('Completed', 'Completed'),
        ('Delivered', 'Delivered'),
    )
    album_name = models.CharField(max_length=100)
    client_name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='albums')
    album_type = models.CharField(max_length=30, choices=ALBUM_TYPE_CHOICES)
    album_size = models.CharField(max_length=20, default='12x36')
    pages = models.IntegerField(default=30)
    sheets = models.IntegerField(default=15)
    cover_type = models.CharField(max_length=50, default='Regular Leather')
    extra_pages = models.IntegerField(default=0)
    base_price = models.DecimalField(max_digits=10, decimal_places=2, default=3000.00)
    per_page_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    sheet_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    design_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Calculate sheets as pages / 2, rounding up if odd (though pages should ideally be even)
        import math
        self.sheets = math.ceil(self.pages / 2)
        
        # Calculate total album cost based on formula:
        # Base Price + (Pages * Per Page Cost) + (Sheets * Sheet Cost)
        # We will also add (extra_pages * Per Page Cost) + (extra_pages/2 * Sheet Cost)
        total_pages = self.pages + self.extra_pages
        total_sheets = math.ceil(total_pages / 2)
        
        self.total_cost = self.base_price + (self.pages * self.per_page_cost) + (self.sheets * self.sheet_cost)
        if self.extra_pages > 0:
            extra_sheets = total_sheets - self.sheets
            self.total_cost += (self.extra_pages * self.per_page_cost) + (extra_sheets * self.sheet_cost)
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.album_name} - {self.client_name}"

class Invoice(models.Model):
    INVOICE_TYPE_CHOICES = (
        ('Photography', 'Photography'),
        ('Album', 'Album'),
        ('Combined', 'Combined'),
    )
    invoice_number = models.CharField(max_length=50, unique=True, blank=True)
    customer_name = models.CharField(max_length=100)
    customer_mobile = models.CharField(max_length=15)
    event_type = models.CharField(max_length=100, blank=True, null=True)
    event_date = models.DateField(blank=True, null=True)
    invoice_type = models.CharField(max_length=20, choices=INVOICE_TYPE_CHOICES, default='Photography')
    
    # Charges
    photography_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    videography_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    drone_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    led_wall_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    crane_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    live_streaming_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    photo_frame_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    travel_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    album_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    gst_rate = models.DecimalField(max_digits=5, decimal_places=2, default=18.00) # 18% GST default
    gst_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    balance_due = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payment_status = models.CharField(max_length=20, choices=(('Pending', 'Pending'), ('Partial', 'Partial'), ('Paid', 'Paid')), default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            # Generate Unique Invoice Number, e.g., DTP-YYYYMMDD-XXXX
            import datetime
            date_str = datetime.date.today().strftime('%Y%m%d')
            unique_id = str(uuid.uuid4().hex[:4]).upper()
            self.invoice_number = f"DTP-{date_str}-{unique_id}"
            
        # Calculate Subtotal
        total_charges = (
            self.photography_charge +
            self.videography_charge +
            self.drone_charge +
            self.led_wall_charge +
            self.crane_charge +
            self.live_streaming_charge +
            self.photo_frame_charge +
            self.travel_charge +
            self.album_charge
        )
        self.subtotal = total_charges - self.discount
        if self.subtotal < 0:
            self.subtotal = 0
            
        # GST Amount
        self.gst_amount = self.subtotal * (self.gst_rate / 100)
        self.grand_total = self.subtotal + self.gst_amount
        self.balance_due = self.grand_total - self.paid_amount
        
        if self.paid_amount >= self.grand_total:
            self.payment_status = 'Paid'
        elif self.paid_amount > 0:
            self.payment_status = 'Partial'
        else:
            self.payment_status = 'Pending'
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.invoice_number} - {self.customer_name}"
