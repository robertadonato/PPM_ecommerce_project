from django.contrib import admin
from django.utils.html import format_html
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'quantity', 'price']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'status', 'total_amount', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['order_number', 'user__username', 'shipping_name']
    list_editable = ['status']
    inlines = [OrderItemInline]
    readonly_fields = ['order_number', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Informazioni Ordine', {
            'fields': ('order_number', 'user', 'status', 'total_amount')
        }),
        ('Dati Spedizione', {
            'fields': ('shipping_name', 'shipping_address', 'shipping_city', 
                      'shipping_postal_code', 'shipping_phone')
        }),
        ('Timestamp', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser and request.user.is_store_manager:
            return qs
        return qs