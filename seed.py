import os
import django
import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dream_studio.settings')
django.setup()

from django.contrib.auth.models import User
from dashboard.models import UserProfile, Employee, Customer, Expense, AlbumDesign, Invoice
from core.models import Service, Booking, GalleryItem

def seed_db():
    print("Starting database seeding...")
    
    # 1. Create Admin Superuser
    if not User.objects.filter(username='admin').exists():
        admin_user = User.objects.create_superuser('admin', 'dreamoftatoo04@gmail.com', 'adminpassword123')
        # Create user profile
        profile = admin_user.profile
        profile.role = 'Admin'
        profile.mobile = '7338668173'
        profile.address = 'Dream Photography, Near police station, Mudalgi, Karnataka'
        profile.save()
        print("Admin user created successfully! (Username: admin, Password: adminpassword123)")
    else:
        print("Admin user already exists.")
        
    if not User.objects.filter(username='dreamstudio').exists():
        dream_user = User.objects.create_superuser('dreamstudio', 'dreamoftatoo04@gmail.com', 'varunchaitu@2026')
        profile = dream_user.profile
        profile.role = 'Admin'
        profile.mobile = '7338668173'
        profile.address = 'Dream Photography, Near police station, Mudalgi, Karnataka'
        profile.save()
        print("dreamstudio superuser created successfully! (Username: dreamstudio, Password: varunchaitu@2026)")
    else:
        print("dreamstudio superuser already exists.")
        
    # 2. Create Staff User
    if not User.objects.filter(username='staff').exists():
        staff_user = User.objects.create_user('staff', 'dreamoftatoo04@gmail.com', 'staffpassword123')
        profile = staff_user.profile
        profile.role = 'Staff'
        profile.mobile = '7338668173'
        profile.address = 'Dream Photography, Near police station, Mudalgi, Karnataka'
        profile.save()
        print("Staff user created! (Username: staff, Password: staffpassword123)")
        
    # 3. Create Services
    if Service.objects.count() == 0:
        services_seed = [
            {"name": "Wedding Photography", "category": "Photography", "starting_price": 45000.00, "icon_class": "bi-heart-fill", "description": "Full-day cover, candid shots, traditional poses, and post-processed album editing."},
            {"name": "Traditional Photography", "category": "Photography", "starting_price": 15000.00, "icon_class": "bi-camera-fill", "description": "Classic and structured event highlights capturing all family frames."},
            {"name": "Candid Photography", "category": "Photography", "starting_price": 20000.00, "icon_class": "bi-emoji-smile-fill", "description": "Spontaneous, authentic emotions and interactions captured creatively without posing."},
            {"name": "Drone Photography", "category": "Photography", "starting_price": 15000.00, "icon_class": "bi-airplane-fill", "description": "Stunning 4K high-altitude shots and sweeping aerial videography of your venues."},
            {"name": "Videography", "category": "Photography", "starting_price": 30000.00, "icon_class": "bi-camera-reels-fill", "description": "Cinematic high-definition movie highlights, teaser trailers, and digital video reels."},
            {"name": "Pre-Wedding Shoot", "category": "Photography", "starting_price": 25000.00, "icon_class": "bi-calendar-heart", "description": "Scenic romance photo sessions at custom indoor or gorgeous outdoor spots."},
            {"name": "Baby Shoot", "category": "Photography", "starting_price": 12000.00, "icon_class": "bi-balloon-fill", "description": "Infant props, themed styling, and high-patience shoot layouts in heated rooms."},
            {"name": "Maternity Shoot", "category": "Photography", "starting_price": 15000.00, "icon_class": "bi-gender-ambiguous", "description": "Graceful and elegant mother-to-be portraits celebrating milestones."},
            {"name": "Birthday Photography", "category": "Photography", "starting_price": 10000.00, "icon_class": "bi-gift-fill", "description": "Fun highlights, cake smash frames, guest group pictures, and birthday highlights."},
            {"name": "Engagement Photography", "category": "Photography", "starting_price": 20000.00, "icon_class": "bi-award-fill", "description": "Ring exchange, stage couple portraits, and coverage of immediate family gatherings."},
            {"name": "Corporate Photography", "category": "Photography", "starting_price": 25000.00, "icon_class": "bi-briefcase-fill", "description": "Professional headshots, seminar event coverage, office space shoots, and PR catalog photos."},
            {"name": "Tattoo Photography & Designing", "category": "Tattoo", "starting_price": 3000.00, "icon_class": "bi-brush", "description": "Permanent custom body inking designed and documented under sterilized medical environments."},
            {"name": "Event Photography", "category": "Photography", "starting_price": 15000.00, "icon_class": "bi-calendar-event", "description": "Anniversaries, corporate galas, baby showers, or open public gatherings cover."}
        ]
        for s in services_seed:
            Service.objects.create(
                name=s["name"],
                category=s["category"],
                starting_price=s["starting_price"],
                icon_class=s["icon_class"],
                description=s["description"]
            )
        print("13 standard Services seeded.")
        
    # 4. Create Employees
    if Employee.objects.count() == 0:
        Employee.objects.create(name="Amit Sharma", role="Photographer", salary=35000.00, contact_number="9988776655", status="Active")
        Employee.objects.create(name="Vikram Singh", role="Photographer", salary=40000.00, contact_number="9988776656", status="Active")
        Employee.objects.create(name="Sanjay Verma", role="Editor", salary=25000.00, contact_number="9988776657", status="Active")
        Employee.objects.create(name="Deepika Rao", role="Manager", salary=30000.00, contact_number="9988776658", status="Active")
        Employee.objects.create(name="Rahul Dey", role="Designer", salary=28000.00, contact_number="9988776659", status="Active")
        print("5 Roster Employees seeded.")
        
    # 5. Create Customers
    if Customer.objects.count() == 0:
        c1 = Customer.objects.create(name="Karan Malhotra", mobile="9812345670", email="karan@example.com", address="Bandra West, Mumbai", event_date=datetime.date.today() + datetime.timedelta(days=15), event_type="Wedding Shoot", payment_status="Partial")
        c2 = Customer.objects.create(name="Megha Gupta", mobile="9812345671", email="megha@example.com", address="South Ext, Delhi", event_date=datetime.date.today() + datetime.timedelta(days=30), event_type="Pre-Wedding Shoot", payment_status="Pending")
        c3 = Customer.objects.create(name="Anil Kapoor", mobile="9812345672", email="anil@example.com", address="Jubilee Hills, Hyderabad", event_date=datetime.date.today() - datetime.timedelta(days=5), event_type="Baby Shoot", payment_status="Paid")
        print("3 Customers seeded.")
        
    # 6. Create Expenses
    if Expense.objects.count() == 0:
        Expense.objects.create(category="Camera Purchase", amount=125000.00, date=datetime.date.today() - datetime.timedelta(days=45), description="Sony A7 IV mirrorless camera body")
        Expense.objects.create(category="Lens Purchase", amount=85000.00, date=datetime.date.today() - datetime.timedelta(days=40), description="Sony 24-70mm f/2.8 GM lens")
        Expense.objects.create(category="Studio Rent", amount=25000.00, date=datetime.date.today() - datetime.timedelta(days=28), description="Studio rent for May 2026")
        Expense.objects.create(category="Electricity", amount=6500.00, date=datetime.date.today() - datetime.timedelta(days=10), description="Electricity bill May 2026")
        Expense.objects.create(category="Staff Salary", amount=35000.00, date=datetime.date.today() - datetime.timedelta(days=5), description="Paid salary to Amit Sharma")
        Expense.objects.create(category="Travel Cost", amount=4500.00, date=datetime.date.today() - datetime.timedelta(days=2), description="Travel to outdoor venue in Lonavala")
        print("6 Expense logs seeded.")
        
    # 7. Create Invoices
    if Invoice.objects.count() == 0:
        # Save dynamic invoice (Calculates Subtotal & GST auto on save)
        Invoice.objects.create(
            customer_name="Karan Malhotra",
            customer_mobile="9812345670",
            event_type="Wedding Shoot",
            event_date=datetime.date.today() - datetime.timedelta(days=25),
            invoice_type="Combined",
            photography_charge=45000.00,
            videography_charge=30000.00,
            drone_charge=15000.00,
            travel_charge=3000.00,
            album_charge=4500.00,
            discount=5000.00,
            paid_amount=92500.00 # Partial
        )
        Invoice.objects.create(
            customer_name="Anil Kapoor",
            customer_mobile="9812345672",
            event_type="Baby Shoot",
            event_date=datetime.date.today() - datetime.timedelta(days=5),
            invoice_type="Photography",
            photography_charge=12000.00,
            photo_frame_charge=1500.00,
            discount=500.00,
            paid_amount=15340.00 # Fully Paid
        )
        Invoice.objects.create(
            customer_name="Ritesh Deshmukh",
            customer_mobile="9812345675",
            event_type="Custom Arm Band Tattoo",
            event_date=datetime.date.today() - datetime.timedelta(days=12),
            invoice_type="Photography",
            photography_charge=3000.00,
            paid_amount=0.00 # Pending
        )
        print("3 Invoices seeded.")
        
    # 8. Create Bookings
    if Booking.objects.count() == 0:
        s_photo = Service.objects.filter(category='Photography').first()
        s_tattoo = Service.objects.filter(category='Tattoo').first()
        emp_photo = Employee.objects.filter(role='Photographer').first()
        
        Booking.objects.create(
            customer_name="Amitabh Bachchan",
            customer_mobile="9812345680",
            customer_email="amitabh@example.com",
            service=s_photo,
            date=datetime.date.today() + datetime.timedelta(days=10),
            package="Luxury",
            location="Juhu Scheme, Mumbai",
            advance_payment=10000.00,
            total_amount=s_photo.starting_price,
            photographer=emp_photo,
            status="Confirmed"
        )
        Booking.objects.create(
            customer_name="Salman Khan",
            customer_mobile="9812345681",
            customer_email="salman@example.com",
            service=s_tattoo,
            date=datetime.date.today() + datetime.timedelta(days=5),
            package="Premium",
            location="Bandstand, Mumbai",
            advance_payment=1000.00,
            total_amount=s_tattoo.starting_price,
            status="Pending"
        )
        print("2 Bookings seeded.")
        
    # 9. Create AlbumDesigns
    if AlbumDesign.objects.count() == 0:
        AlbumDesign.objects.create(
            album_name="Malhotra Wedding Album",
            client_name="Karan Malhotra",
            album_type="Luxury Album",
            album_size="12x36",
            pages=40,
            cover_type="Acrylic Glass Cover",
            extra_pages=10,
            base_price=8000.00,
            per_page_cost=120.00,
            sheet_cost=80.00,
            design_status="Designing"
        )
        AlbumDesign.objects.create(
            album_name="Kapoor Family Baby Album",
            client_name="Anil Kapoor",
            album_type="Regular Album",
            album_size="12x18",
            pages=20,
            cover_type="Leather Cover",
            base_price=3000.00,
            per_page_cost=50.00,
            sheet_cost=30.00,
            design_status="Pending"
        )
        print("2 Album project designs seeded.")
        
    print("Database seeding completed successfully!")

if __name__ == '__main__':
    seed_db()
