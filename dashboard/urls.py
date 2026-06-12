from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='home'),
    path('customers/', views.customers_list, name='customers'),
    path('customers/add/', views.customer_add, name='customer_add'),
    path('customers/edit/<int:pk>/', views.customer_edit, name='customer_edit'),
    path('customers/delete/<int:pk>/', views.customer_delete, name='customer_delete'),
    
    path('bookings/', views.bookings_list, name='bookings'),
    path('bookings/update/<int:pk>/<str:status>/', views.booking_update_status, name='booking_update_status'),
    path('bookings/assign/<int:pk>/', views.booking_assign, name='booking_assign'),
    
    path('billing/', views.billing_list, name='billing'),
    path('billing/create/', views.billing_create, name='billing_create'),
    path('billing/invoice/<int:pk>/', views.invoice_detail, name='invoice_detail'),
    path('billing/invoice/<int:pk>/pdf/', views.invoice_pdf, name='invoice_pdf'),
    
    path('albums/', views.albums_list, name='albums'),
    path('albums/add/', views.album_add, name='album_add'),
    path('albums/edit/<int:pk>/', views.album_edit, name='album_edit'),
    
    path('expenses/', views.expenses_list, name='expenses'),
    path('expenses/add/', views.expense_add, name='expense_add'),
    
    path('employees/', views.employees_list, name='employees'),
    path('employees/add/', views.employee_add, name='employee_add'),
    
    path('reports/', views.reports_view, name='reports'),
    path('reports/export/excel/', views.export_reports_excel, name='export_reports_excel'),
    path('reports/export/pdf/', views.export_reports_pdf, name='export_reports_pdf'),
    
    # Auth views
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
]
