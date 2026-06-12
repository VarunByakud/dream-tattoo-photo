from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from .models import UserProfile, Employee, Customer, Expense, AlbumDesign, Invoice
from core.models import Booking, Service
import datetime
import calendar

# ----------------- Authentication Views -----------------

def login_view(request):
    if request.user.is_authenticated:
        if request.user.profile.role == 'Admin':
            return redirect('dashboard:home')
        else:
            return redirect('dashboard:bookings')
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(username=u, password=p)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            if user.profile.role == 'Admin':
                return redirect('dashboard:home')
            else:
                return redirect('dashboard:bookings')
        else:
            return render(request, 'dashboard/login.html', {'error': 'Invalid username or password credentials'})
    return render(request, 'dashboard/login.html')

def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('core:home')

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    if request.method == 'POST':
        u = request.POST.get('username')
        e = request.POST.get('email')
        p = request.POST.get('password')
        role = request.POST.get('role', 'Customer')
        mobile = request.POST.get('mobile')
        address = request.POST.get('address')
        
        if User.objects.filter(username=u).exists():
            return render(request, 'dashboard/register.html', {'error': 'Username already exists'})
            
        user = User.objects.create_user(username=u, email=e, password=p)
        profile = user.profile
        profile.role = role
        profile.mobile = mobile
        profile.address = address
        profile.save()
        
        login(request, user)
        messages.success(request, f"Account created successfully! Welcome {u}.")
        return redirect('dashboard:home')
        
    return render(request, 'dashboard/register.html')


# ----------------- Dashboard views -----------------

@login_required
def dashboard_home(request):
    if request.user.profile.role != 'Admin':
        return redirect('dashboard:bookings')
    # Summary metrics
    total_customers = Customer.objects.count()
    total_bookings = Booking.objects.count()
    
    invoice_totals = Invoice.objects.aggregate(
        paid=Sum('paid_amount'),
        grand=Sum('grand_total'),
        due=Sum('balance_due')
    )
    total_revenue = invoice_totals['paid'] or 0.00
    pending_payments = invoice_totals['due'] or 0.00
    
    albums_in_progress = AlbumDesign.objects.filter(design_status__in=['Pending', 'Designing']).count()
    
    # Recent items
    recent_bookings = Booking.objects.all().order_by('-created_at')[:5]
    active_albums = AlbumDesign.objects.exclude(design_status='Delivered').order_by('-created_at')[:5]
    
    # Album statistics counts
    album_stats = {
        'Pending': AlbumDesign.objects.filter(design_status='Pending').count(),
        'Designing': AlbumDesign.objects.filter(design_status='Designing').count(),
        'Completed': AlbumDesign.objects.filter(design_status='Completed').count(),
        'Delivered': AlbumDesign.objects.filter(design_status='Delivered').count(),
    }
    
    # Chart.js mock labels for the last 6 months
    chart_months = []
    chart_revenues = []
    chart_bookings_count = []
    
    today = datetime.date.today()
    for i in range(5, -1, -1):
        # Calc past 6 months
        m_date = today - datetime.timedelta(days=i*30)
        m_name = m_date.strftime('%b')
        chart_months.append(m_name)
        
        # Calculate sum for this month
        month_start = datetime.date(m_date.year, m_date.month, 1)
        month_end = datetime.date(m_date.year, m_date.month, calendar.monthrange(m_date.year, m_date.month)[1])
        
        month_rev = Invoice.objects.filter(created_at__date__range=[month_start, month_end]).aggregate(Sum('paid_amount'))['paid_amount__sum'] or 0.0
        month_book = Booking.objects.filter(created_at__date__range=[month_start, month_end]).count()
        
        chart_revenues.append(float(month_rev))
        chart_bookings_count.append(month_book)
        
    context = {
        'total_customers': total_customers,
        'total_bookings': total_bookings,
        'total_revenue': total_revenue,
        'pending_payments': pending_payments,
        'albums_in_progress': albums_in_progress,
        'recent_bookings': recent_bookings,
        'active_albums': active_albums,
        'album_stats': album_stats,
        'chart_months': chart_months,
        'chart_revenues': chart_revenues,
        'chart_bookings_count': chart_bookings_count,
    }
    return render(request, 'dashboard/dashboard.html', context)


# ----------------- Customer Management -----------------

@login_required
def customers_list(request):
    search_query = request.GET.get('search', '')
    if search_query:
        customers = Customer.objects.filter(name__icontains=search_query).order_by('-created_at')
    else:
        customers = Customer.objects.all().order_by('-created_at')
        
    return render(request, 'dashboard/customers.html', {
        'customers': customers,
        'search_query': search_query
    })

@login_required
def customer_add(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        mobile = request.POST.get('mobile')
        email = request.POST.get('email')
        address = request.POST.get('address')
        event_date_str = request.POST.get('event_date')
        event_type = request.POST.get('event_type')
        payment_status = request.POST.get('payment_status', 'Pending')
        
        event_date = None
        if event_date_str:
            event_date = datetime.datetime.strptime(event_date_str, '%Y-%m-%d').date()
            
        Customer.objects.create(
            name=name,
            mobile=mobile,
            email=email,
            address=address,
            event_date=event_date,
            event_type=event_type,
            payment_status=payment_status
        )
        messages.success(request, f"Customer {name} added successfully!")
    return redirect('dashboard:customers')

@login_required
def customer_edit(request, pk):
    customer = get_object_or_404(Customer, id=pk)
    if request.method == 'POST':
        customer.name = request.POST.get('name')
        customer.mobile = request.POST.get('mobile')
        customer.email = request.POST.get('email')
        customer.address = request.POST.get('address')
        event_date_str = request.POST.get('event_date')
        customer.event_type = request.POST.get('event_type')
        customer.payment_status = request.POST.get('payment_status')
        
        if event_date_str:
            customer.event_date = datetime.datetime.strptime(event_date_str, '%Y-%m-%d').date()
        else:
            customer.event_date = None
            
        customer.save()
        messages.success(request, f"Customer {customer.name} details updated!")
        return redirect('dashboard:customers')
        
    customers = Customer.objects.all().order_by('-created_at')
    return render(request, 'dashboard/customers.html', {
        'customers': customers,
        'edit_customer': customer
    })

@login_required
def customer_delete(request, pk):
    if request.user.profile.role != 'Admin':
        messages.error(request, "Permission denied. Only Admins can delete customers.")
        return redirect('dashboard:customers')
        
    customer = get_object_or_404(Customer, id=pk)
    name = customer.name
    customer.delete()
    messages.info(request, f"Customer {name} deleted.")
    return redirect('dashboard:customers')


# ----------------- Booking Management -----------------

@login_required
def bookings_list(request):
    bookings = Booking.objects.all().order_by('-date')
    employees = Employee.objects.filter(status='Active')
    return render(request, 'dashboard/bookings.html', {
        'bookings': bookings,
        'employees': employees
    })

@login_required
def booking_update_status(request, pk, status):
    booking = get_object_or_404(Booking, id=pk)
    if status in ['Pending', 'Confirmed', 'Completed', 'Cancelled']:
        booking.status = status
        booking.save()
        
        # If confirmed, auto create/update customer record to keep in database
        if status == 'Confirmed':
            Customer.objects.get_or_create(
                mobile=booking.customer_mobile,
                defaults={
                    'name': booking.customer_name,
                    'email': booking.customer_email,
                    'address': booking.location,
                    'event_date': booking.date,
                    'event_type': booking.service.name,
                    'payment_status': 'Partial' if booking.advance_payment > 0 else 'Pending'
                }
            )
            
        messages.success(request, f"Booking status for {booking.customer_name} updated to {status}!")
    return redirect('dashboard:bookings')

@login_required
def booking_assign(request, pk):
    booking = get_object_or_404(Booking, id=pk)
    if request.method == 'POST':
        emp_id = request.POST.get('photographer')
        if emp_id:
            emp = get_object_or_404(Employee, id=int(emp_id))
            booking.photographer = emp
            messages.success(request, f"Photographer {emp.name} assigned to session.")
        else:
            booking.photographer = None
            messages.info(request, "Photographer unassigned.")
        booking.save()
    return redirect('dashboard:bookings')


# ----------------- Billing / POS system -----------------

@login_required
def billing_list(request):
    invoices = Invoice.objects.all().order_by('-created_at')
    return render(request, 'dashboard/billing.html', {'invoices': invoices})

@login_required
def billing_create(request):
    if request.method == 'POST':
        c_name = request.POST.get('customer_name')
        c_mobile = request.POST.get('customer_mobile')
        e_type = request.POST.get('event_type')
        e_date_str = request.POST.get('event_date')
        i_type = request.POST.get('invoice_type', 'Photography')
        
        e_date = None
        if e_date_str:
            e_date = datetime.datetime.strptime(e_date_str, '%Y-%m-%d').date()
            
        # Pricing lines
        photo = float(request.POST.get('photography_charge') or 0.0)
        video = float(request.POST.get('videography_charge') or 0.0)
        drone = float(request.POST.get('drone_charge') or 0.0)
        led = float(request.POST.get('led_wall_charge') or 0.0)
        crane = float(request.POST.get('crane_charge') or 0.0)
        live = float(request.POST.get('live_streaming_charge') or 0.0)
        frame = float(request.POST.get('photo_frame_charge') or 0.0)
        travel = float(request.POST.get('travel_charge') or 0.0)
        album = float(request.POST.get('album_charge') or 0.0)
        
        discount = float(request.POST.get('discount') or 0.0)
        paid = float(request.POST.get('paid_amount') or 0.0)
        
        # Save invoice (model overrides save to calculate GST & totals)
        invoice = Invoice.objects.create(
            customer_name=c_name,
            customer_mobile=c_mobile,
            event_type=e_type,
            event_date=e_date,
            invoice_type=i_type,
            photography_charge=photo,
            videography_charge=video,
            drone_charge=drone,
            led_wall_charge=led,
            crane_charge=crane,
            live_streaming_charge=live,
            photo_frame_charge=frame,
            travel_charge=travel,
            album_charge=album,
            discount=discount,
            paid_amount=paid
        )
        
        # Ensure Customer Profile exists in DB
        Customer.objects.get_or_create(
            mobile=c_mobile,
            defaults={
                'name': c_name,
                'event_date': e_date,
                'event_type': e_type,
                'payment_status': invoice.payment_status
            }
        )
        
        messages.success(request, f"Invoice {invoice.invoice_number} generated successfully!")
        return redirect('dashboard:invoice_detail', pk=invoice.id)
        
    return redirect('dashboard:billing')

@login_required
def invoice_detail(request, pk):
    invoice = get_object_or_404(Invoice, id=pk)
    return render(request, 'dashboard/invoice_detail.html', {'invoice': invoice})


# ----------------- PDF Invoice PDF Exporter using ReportLab -----------------

@login_required
def invoice_pdf(request, pk):
    invoice = get_object_or_404(Invoice, id=pk)
    
    # Prepare ReportLab PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Invoice_{invoice.invoice_number}.pdf"'
    
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    
    # Set up document
    doc = SimpleDocTemplate(response, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    story = []
    
    # Styles
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'InvoiceTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        textColor=colors.HexColor('#D4AF37'),
        spaceAfter=6
    )
    subtitle_style = ParagraphStyle(
        'InvoiceSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.HexColor('#555555'),
        spaceAfter=15
    )
    h3_style = ParagraphStyle(
        'H3Style',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=12,
        textColor=colors.HexColor('#D4AF37'),
        spaceAfter=8,
        spaceBefore=15
    )
    normal_style = ParagraphStyle(
        'NormalStyle',
        parent=styles['Normal'],
        fontSize=9,
        leading=13
    )
    bold_style = ParagraphStyle(
        'BoldStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9
    )
    
    # Header Title
    story.append(Paragraph("DREAM TATTOO & PHOTOGRAPHY", title_style))
    story.append(Paragraph("Premium Cinematography, Candid Captures & Hygienic Tattoos", subtitle_style))
    
    # Details Grid
    data_details = [
        [
            Paragraph(f"<b>Invoice Number:</b> {invoice.invoice_number}<br/><b>Date:</b> {invoice.created_at.strftime('%d %M %Y')}", normal_style),
            Paragraph(f"<b>Billed To:</b> {invoice.customer_name}<br/><b>Phone:</b> {invoice.customer_mobile}<br/><b>Event:</b> {invoice.event_type or '-'}", normal_style)
        ]
    ]
    t_details = Table(data_details, colWidths=[260, 260])
    t_details.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F9F9F9')),
        ('PADDING', (0,0), (-1,-1), 10),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#E0E0E0')),
    ]))
    story.append(t_details)
    story.append(Spacer(1, 15))
    
    # Service Breakdown Header
    story.append(Paragraph("SERVICE CHARGES BREAKDOWN", h3_style))
    
    # Items Table
    items_data = [["Service Item / Description", "Amount (INR)"]]
    
    charges = [
        ("Photography Coverage", invoice.photography_charge),
        ("Videography & Cinematic Coverage", invoice.videography_charge),
        ("Aerial Drone Cover", invoice.drone_charge),
        ("LED Wall Event Display", invoice.led_wall_charge),
        ("Crane Support", invoice.crane_charge),
        ("Live Broadcasting", invoice.live_streaming_charge),
        ("Photo Frame prints", invoice.photo_frame_charge),
        ("Travel & Venue Overheads", invoice.travel_charge),
        ("Album Print & Binding", invoice.album_charge),
    ]
    
    for label, amount in charges:
        if amount > 0:
            items_data.append([label, f"Rs {amount:,.2f}"])
            
    # Table layout
    col_widths = [400, 120]
    t_items = Table(items_data, colWidths=col_widths)
    t_items.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#D4AF37')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#000000')),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 9),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('TOPPADDING', (0,0), (-1,0), 6),
        ('ALIGN', (1,0), (1,-1), 'RIGHT'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E0E0E0')),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_items)
    story.append(Spacer(1, 15))
    
    # Financial calculations
    totals_data = [
        ["Subtotal Charges:", f"Rs {invoice.subtotal + invoice.discount:,.2f}"],
        ["Discount Applied:", f"- Rs {invoice.discount:,.2f}"],
        [f"GST Collected ({invoice.gst_rate}%):", f"Rs {invoice.gst_amount:,.2f}"],
        ["Grand Total:", f"Rs {invoice.grand_total:,.2f}"],
        ["Total Amount Paid:", f"Rs {invoice.paid_amount:,.2f}"],
        ["Balance Due Outstanding:", f"Rs {invoice.balance_due:,.2f}"]
    ]
    
    t_totals = Table(totals_data, colWidths=[380, 140])
    t_totals.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'RIGHT'),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('FONTNAME', (0,3), (-1,3), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0,-1), (-1,-1), colors.HexColor('#FF0000')),
        ('TEXTCOLOR', (0,3), (-1,3), colors.HexColor('#D4AF37')),
        ('PADDING', (0,0), (-1,-1), 4),
        ('LINEABOVE', (0,3), (1,3), 1, colors.HexColor('#D4AF37')),
    ]))
    story.append(t_totals)
    story.append(Spacer(1, 20))
    
    # UPI Footer
    story.append(Paragraph("<b>Payment UPI Details:</b> dreamstudio@ybl | Scan to pay using GPay / PhonePe", normal_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph("Thank you for choosing Dream Studio! Feel free to reach out for suggestions.", normal_style))
    
    doc.build(story)
    return response


# ----------------- Album Production / Design -----------------

@login_required
def albums_list(request):
    albums = AlbumDesign.objects.all().order_by('-created_at')
    return render(request, 'dashboard/albums.html', {'albums': albums})

@login_required
def album_add(request):
    if request.method == 'POST':
        album_name = request.POST.get('album_name')
        client_name = request.POST.get('client_name')
        album_type = request.POST.get('album_type')
        album_size = request.POST.get('album_size', '12x36')
        cover_type = request.POST.get('cover_type', 'Leather Cover')
        
        pages = int(request.POST.get('pages') or 30)
        extra_pages = int(request.POST.get('extra_pages') or 0)
        
        base_price = float(request.POST.get('base_price') or 3000)
        per_page_cost = float(request.POST.get('per_page_cost') or 0.0)
        sheet_cost = float(request.POST.get('sheet_cost') or 0.0)
        
        # Save model (calculates sheets & total cost automatically)
        AlbumDesign.objects.create(
            album_name=album_name,
            client_name=client_name,
            album_type=album_type,
            album_size=album_size,
            cover_type=cover_type,
            pages=pages,
            extra_pages=extra_pages,
            base_price=base_price,
            per_page_cost=per_page_cost,
            sheet_cost=sheet_cost
        )
        messages.success(request, f"Album project {album_name} saved in queue successfully!")
    return redirect('dashboard:albums')

@login_required
def album_edit(request, pk):
    album = get_object_or_404(AlbumDesign, id=pk)
    if request.method == 'POST':
        status = request.POST.get('design_status')
        if status in ['Pending', 'Designing', 'Completed', 'Delivered']:
            album.design_status = status
            album.save()
            messages.success(request, f"Album production status updated to {status}!")
    return redirect('dashboard:albums')


# ----------------- Expense Management -----------------

@login_required
def expenses_list(request):
    if request.user.profile.role != 'Admin':
        messages.error(request, "Access denied. Only Admins can view or manage expenses.")
        return redirect('dashboard:home')
    expenses = Expense.objects.all().order_by('-date')
    total_expenses_sum = Expense.objects.aggregate(Sum('amount'))['amount__sum'] or 0.0
    return render(request, 'dashboard/expenses.html', {
        'expenses': expenses,
        'total_expenses_sum': total_expenses_sum
    })

@login_required
def expense_add(request):
    if request.user.profile.role != 'Admin':
        messages.error(request, "Access denied. Only Admins can view or manage expenses.")
        return redirect('dashboard:home')
    if request.method == 'POST':
        category = request.POST.get('category')
        amount = float(request.POST.get('amount') or 0.0)
        date_str = request.POST.get('date')
        description = request.POST.get('description')
        
        date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        
        Expense.objects.create(
            category=category,
            amount=amount,
            date=date,
            description=description
        )
        messages.success(request, "Expense record logged successfully!")
    return redirect('dashboard:expenses')


# ----------------- Employee Roster Management -----------------

@login_required
def employees_list(request):
    if request.user.profile.role != 'Admin':
        messages.error(request, "Access denied. Only Admins can view or manage employees.")
        return redirect('dashboard:home')
    employees = Employee.objects.all().order_by('name')
    return render(request, 'dashboard/employees.html', {'employees': employees})

@login_required
def employee_add(request):
    if request.user.profile.role != 'Admin':
        messages.error(request, "Access denied. Only Admins can view or manage employees.")
        return redirect('dashboard:home')
    if request.method == 'POST':
        name = request.POST.get('name')
        role = request.POST.get('role')
        salary = float(request.POST.get('salary') or 0.0)
        contact = request.POST.get('contact_number')
        status = request.POST.get('status', 'Active')
        
        Employee.objects.create(
            name=name,
            role=role,
            salary=salary,
            contact_number=contact,
            status=status
        )
        messages.success(request, f"Staff member {name} added to roster!")
    return redirect('dashboard:employees')


# ----------------- Reports Views & Exporters -----------------

@login_required
def reports_view(request):
    if request.user.profile.role != 'Admin':
        messages.error(request, "Access denied. Only Admins can view or export financial reports.")
        return redirect('dashboard:home')
    # Overall summary metrics
    revenue_total = Invoice.objects.aggregate(Sum('paid_amount'))['paid_amount__sum'] or 0.0
    expense_total = Expense.objects.aggregate(Sum('amount'))['amount__sum'] or 0.0
    gst_total = Invoice.objects.aggregate(Sum('gst_amount'))['gst_amount__sum'] or 0.0
    net_profit = revenue_total - expense_total
    
    # Mixed transaction histories sorted chronologically
    invoices = Invoice.objects.all().order_by('-created_at')
    expenses = Expense.objects.all().order_by('-date')
    
    transactions = []
    for inv in invoices:
        transactions.append({
            'date': inv.created_at.date(),
            'type': 'INCOMING',
            'title': f"Invoice {inv.invoice_number}",
            'subtitle': f"Client: {inv.customer_name}",
            'amount': float(inv.paid_amount)
        })
    for exp in expenses:
        transactions.append({
            'date': exp.date,
            'type': 'OUTGOING',
            'title': exp.category,
            'subtitle': exp.description,
            'amount': float(exp.amount)
        })
        
    # Sort mixed items descending
    transactions = sorted(transactions, key=lambda x: x['date'], reverse=True)[:25]
    
    context = {
        'revenue_total': revenue_total,
        'expense_total': expense_total,
        'gst_total': gst_total,
        'net_profit': net_profit,
        'transactions': transactions
    }
    return render(request, 'dashboard/reports.html', context)


# Excel Reports Exporter
@login_required
def export_reports_excel(request):
    if request.user.profile.role != 'Admin':
        messages.error(request, "Access denied. Only Admins can view or export financial reports.")
        return redirect('dashboard:home')
    # Setup openpyxl worksheet
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    
    wb = openpyxl.Workbook()
    
    # Styling variables
    gold_fill = PatternFill(start_color="D4AF37", end_color="D4AF37", fill_type="solid")
    grey_fill = PatternFill(start_color="F2F2F2", end_color="F2F2F2", fill_type="solid")
    font_bold = Font(name="Calibri", size=11, bold=True)
    font_title = Font(name="Calibri", size=14, bold=True, color="D4AF37")
    align_left = Alignment(horizontal="left", vertical="center")
    align_right = Alignment(horizontal="right", vertical="center")
    
    thin_border = Border(
        left=Side(style='thin', color='DDDDDD'),
        right=Side(style='thin', color='DDDDDD'),
        top=Side(style='thin', color='DDDDDD'),
        bottom=Side(style='thin', color='DDDDDD')
    )

    # 1st Sheet: Invoice ledger
    ws1 = wb.active
    ws1.title = "Invoices Ledger"
    ws1.append(["Dream Tattoo & Photography - Sales Ledger"])
    ws1.cell(1, 1).font = font_title
    ws1.append([])
    
    headers1 = ["Invoice #", "Date", "Customer Name", "Contact", "Event Type", "Subtotal", "GST Amt", "Grand Total", "Paid Amt", "Status"]
    ws1.append(headers1)
    for col_num in range(1, 11):
        cell = ws1.cell(3, col_num)
        cell.fill = gold_fill
        cell.font = font_bold
        cell.alignment = align_left
        
    for inv in Invoice.objects.all().order_by('-created_at'):
        row = [
            inv.invoice_number,
            inv.created_at.strftime('%Y-%m-%d'),
            inv.customer_name,
            inv.customer_mobile,
            inv.event_type or '',
            float(inv.subtotal),
            float(inv.gst_amount),
            float(inv.grand_total),
            float(inv.paid_amount),
            inv.payment_status
        ]
        ws1.append(row)
        
    # 2nd Sheet: Expenses ledger
    ws2 = wb.create_sheet(title="Expenses Overhead")
    ws2.append(["Dream Tattoo & Photography - Expense Log"])
    ws2.cell(1, 1).font = font_title
    ws2.append([])
    
    headers2 = ["ID", "Date", "Category", "Description", "Amount (INR)"]
    ws2.append(headers2)
    for col_num in range(1, 6):
        cell = ws2.cell(3, col_num)
        cell.fill = gold_fill
        cell.font = font_bold
        cell.alignment = align_left
        
    for exp in Expense.objects.all().order_by('-date'):
        row = [
            exp.id,
            exp.date.strftime('%Y-%m-%d'),
            exp.category,
            exp.description or '',
            float(exp.amount)
        ]
        ws2.append(row)
        
    # Autofit Column widths
    for ws in [ws1, ws2]:
        for col in ws.columns:
            max_len = 0
            for cell in col:
                if cell.row < 3: continue
                if cell.value:
                    max_len = max(max_len, len(str(cell.value)))
            col_letter = openpyxl.utils.get_column_letter(col[0].column)
            ws.column_dimensions[col_letter].width = max(max_len + 3, 12)

    # Return workbook
    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = 'attachment; filename="DreamStudio_Report.xlsx"'
    wb.save(response)
    return response


# Consolidated Financial Summary PDF Exporter using ReportLab
@login_required
def export_reports_pdf(request):
    if request.user.profile.role != 'Admin':
        messages.error(request, "Access denied. Only Admins can view or export financial reports.")
        return redirect('dashboard:home')
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Consolidated_Financial_Report.pdf"'
    
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    
    doc = SimpleDocTemplate(response, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    story = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle', parent=styles['Heading1'],
        fontName='Helvetica-Bold', fontSize=20,
        textColor=colors.HexColor('#D4AF37'), spaceAfter=5
    )
    h3_style = ParagraphStyle(
        'H3Header', parent=styles['Heading3'],
        fontName='Helvetica-Bold', fontSize=12,
        textColor=colors.HexColor('#D4AF37'), spaceAfter=8, spaceBefore=15
    )
    normal_style = ParagraphStyle('NormText', parent=styles['Normal'], fontSize=9)
    
    story.append(Paragraph("DREAM TATTOO & PHOTOGRAPHY", title_style))
    story.append(Paragraph("Consolidated Studio Financial Summary Report", ParagraphStyle('Sub', parent=styles['Normal'], fontSize=10, textColor=colors.gray, spaceAfter=20)))
    
    # Financial Totals block
    revenue_total = Invoice.objects.aggregate(Sum('paid_amount'))['paid_amount__sum'] or 0.0
    expense_total = Expense.objects.aggregate(Sum('amount'))['amount__sum'] or 0.0
    gst_total = Invoice.objects.aggregate(Sum('gst_amount'))['gst_amount__sum'] or 0.0
    net_profit = revenue_total - expense_total
    
    summary_data = [
        ["Metric Category", "Consolidated Amount (INR)"],
        ["Total Billed Sales Revenue (Received)", f"Rs {revenue_total:,.2f}"],
        ["Total Operating Expenses / Overheads", f"Rs {expense_total:,.2f}"],
        ["Total GST Liability collected (Tax due)", f"Rs {gst_total:,.2f}"],
        ["Consolidated Net Profit margin", f"Rs {net_profit:,.2f}"]
    ]
    t_summary = Table(summary_data, colWidths=[320, 200])
    t_summary.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#D4AF37')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.black),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E0E0E0')),
        ('PADDING', (0,0), (-1,-1), 8),
        ('FONTNAME', (0,1), (0,-1), 'Helvetica'),
        ('FONTNAME', (0,4), (-1,4), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0,4), (-1,4), colors.HexColor('#28A745') if net_profit >= 0 else colors.red),
    ]))
    story.append(t_summary)
    
    # Expense Breakdown categories list
    story.append(Spacer(1, 15))
    story.append(Paragraph("EXPENSES OVERHEADS BY CATEGORY", h3_style))
    
    exp_cats = Expense.objects.values('category').annotate(total=Sum('amount')).order_by('-total')
    exp_data = [["Expense Category Description", "Total Spent (INR)"]]
    for item in exp_cats:
        exp_data.append([item['category'], f"Rs {item['total']:,.2f}"])
        
    t_exp = Table(exp_data, colWidths=[320, 200])
    t_exp.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#555555')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E0E0E0')),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_exp)
    
    doc.build(story)
    return response
