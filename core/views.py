from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Service, GalleryItem, Booking
from django.contrib import messages

# Auto-seed services if table is empty
def check_and_seed_services():
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

def home(request):
    check_and_seed_services()
    # Fetch 3 services to show featured
    services = Service.objects.filter(category='Photography')[:3]
    return render(request, 'core/home.html', {'services': services})

def about(request):
    return render(request, 'core/about.html')

def services(request):
    check_and_seed_services()
    all_services = Service.objects.all().order_by('category', 'name')
    return render(request, 'core/services.html', {'services': all_services})

def gallery(request):
    items = GalleryItem.objects.all().order_by('-uploaded_at')
    return render(request, 'core/gallery.html', {'items': items})

def book_request(request):
    check_and_seed_services()
    services_list = Service.objects.all()
    selected_service_id = request.GET.get('service', '')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        mobile = request.POST.get('mobile')
        email = request.POST.get('email')
        service_id = request.POST.get('service')
        date = request.POST.get('date')
        package = request.POST.get('package')
        location = request.POST.get('location')
        advance_payment = request.POST.get('advance_payment', 0)
        
        # Try to find service object or handle string fallback
        try:
            service_obj = Service.objects.get(id=int(service_id))
        except (ValueError, Service.DoesNotExist):
            # Fallback if hardcoded items were used
            service_obj = Service.objects.first()
            
        booking = Booking.objects.create(
            user=request.user if request.user.is_authenticated else None,
            customer_name=name,
            customer_mobile=mobile,
            customer_email=email,
            service=service_obj,
            date=date,
            package=package,
            location=location,
            advance_payment=advance_payment,
            total_amount=service_obj.starting_price, # Set default price to service base price
            status='Pending'
        )
        
        success_msg = f"Thank you {name}. Your booking request for {service_obj.name} on {date} has been submitted. Our manager will contact you on {mobile} soon!"
        return render(request, 'core/book_request.html', {
            'success_message': success_msg,
            'services': services_list
        })
        
    return render(request, 'core/book_request.html', {
        'services': services_list,
        'selected_service_id': selected_service_id
    })
