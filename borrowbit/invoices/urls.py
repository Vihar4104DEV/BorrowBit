"""
URL patterns for the invoice app.
"""
from django.urls import path
from . import views

app_name = 'invoices'

urlpatterns = [
    # Customer invoice views
    path('', views.invoice_list, name='invoice_list'),
    path('list/', views.invoice_list, name='invoice_list_alt'),
    path('<int:invoice_id>/', views.invoice_detail, name='invoice_detail'),
    path('<int:invoice_id>/pdf/', views.invoice_pdf_view, name='invoice_pdf_view'),
    path('<int:invoice_id>/pdf/download/', views.invoice_pdf_download, name='invoice_pdf_download'),
    path('<int:invoice_id>/pdf/regenerate/', views.regenerate_invoice_pdf, name='regenerate_invoice_pdf'),
    
    # Admin invoice views
    path('admin/', views.admin_invoice_list, name='admin_invoice_list'),
    path('admin/<int:invoice_id>/', views.admin_invoice_detail, name='admin_invoice_detail'),
    path('admin/<int:invoice_id>/pdf/', views.admin_invoice_pdf_download, name='admin_invoice_pdf_download'),
    path('admin/<int:invoice_id>/mark-paid/', views.mark_invoice_as_paid, name='mark_invoice_as_paid'),
    path('admin/<int:invoice_id>/send/', views.send_invoice, name='send_invoice'),
    
    # AJAX endpoints
    path('<int:invoice_id>/ajax/generate-pdf/', views.ajax_generate_pdf, name='ajax_generate_pdf'),
    
    # Demo/Test endpoints
    path('demo/pdf/', views.demo_invoice_pdf, name='demo_invoice_pdf'),
    
    # Class-based views (alternative)
    path('cbv/', views.InvoiceListView.as_view(), name='invoice_list_cbv'),
    path('cbv/<int:pk>/', views.InvoiceDetailView.as_view(), name='invoice_detail_cbv'),
]
