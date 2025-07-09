from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, Offer, OfferProduct, Review, Cart, CartItem

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']
    list_filter = ['created_at']

class ReviewInline(admin.TabularInline):
    model = Review
    extra = 0
    readonly_fields = ['user', 'created_at']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'stock', 'available', 'created_at']
    list_filter = ['available', 'category', 'created_at']
    list_editable = ['price', 'stock', 'available']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ReviewInline]
    
    fieldsets = (
        ('Informazioni Generali', {
            'fields': ('name', 'slug', 'category', 'description', 'image')
        }),
        ('Prezzo e Disponibilità', {
            'fields': ('price', 'stock', 'available')
        }),
        ('Specifiche Dolci', {
            'fields': ('ingredients', 'allergens', 'weight', 'shelf_life')
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser and request.user.is_store_manager:
            return qs
        return qs

class OfferProductInline(admin.TabularInline):
    model = OfferProduct
    extra = 1

@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ['product', 'discount_percentage', 'start_date', 'end_date', 'active']
    list_filter = ['active', 'product']
    search_fields = ['product__name']
    date_hierarchy = 'start_date'

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['product__name', 'user__username']
    readonly_fields = ['created_at']

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'get_total_items', 'get_total_price', 'updated_at']
    inlines = [CartItemInline]
    readonly_fields = ['created_at', 'updated_at']