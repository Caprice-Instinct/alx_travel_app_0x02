from django.contrib import admin
from .models import Booking, Payment


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_email', 'property_name', 'check_in_date', 'check_out_date', 'total_price', 'created_at']
    list_filter = ['check_in_date', 'check_out_date', 'created_at']
    search_fields = ['user_email', 'property_name', 'booking_reference']
    readonly_fields = ['booking_reference', 'created_at', 'updated_at']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'booking_reference', 'amount', 'status', 'transaction_id', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['booking_reference', 'transaction_id']
    readonly_fields = ['created_at', 'updated_at']
