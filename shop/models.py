from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.text import slugify
from PIL import Image
from cloudinary.models import CloudinaryField 
from django.utils import timezone
from decimal import Decimal
from django.db.models import Prefetch

User = get_user_model()

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True, null=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('shop:category_detail', args=[self.slug])

class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = CloudinaryField('image', folder='dulcis_fabula/products', blank=True, null=True)
    stock = models.PositiveIntegerField(default=10)
    available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    ingredients = models.TextField(blank=True, null=True)
    allergens = models.TextField(blank=True, null=True)
    weight = models.PositiveIntegerField(help_text="Peso in grammi", default=100, blank=True)
    shelf_life = models.PositiveIntegerField(help_text="Durata in giorni", default=30, blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['available']),
        ]
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('shop:product_detail', kwargs={'pk': self.id, 'slug': self.slug})
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
        
    def get_discount_info(self):
        active_offer = self.active_offers.first()
        if active_offer:
            discounted = float(self.price) * (100 - float(active_offer.discount_percentage)) / 100
            return {
                'discounted_price': round(discounted, 2),
                'percentage': active_offer.discount_percentage,
                'offer': active_offer,
                'savings': float(self.price) - discounted
            }
        return None

    def get_discounted_price(self):
        active_offer = self.active_offers.first()
        if active_offer:
            return Decimal(str(self.price * (100 - active_offer.discount_percentage) / 100)).quantize(Decimal('0.00'))
        return self.price
    
    def get_savings(self):
        discounted = self.get_discounted_price()
        return round(self.price - discounted, 2)
    
    def has_active_offer(self):
        return self.offers.filter(
            active=True,
            start_date__lte=timezone.now(),
            end_date__gte=timezone.now()
        ).exists()
        
    @property
    def active_offers(self):
        return self.offers.filter(
            active=True,
            start_date__lte=timezone.now(),
            end_date__gte=timezone.now()
        )
        
    @property
    def is_new(self):
        return (timezone.now() - self.created_at).days <= 30
    
    def get_related_products(self, limit=4):
        return Product.objects.filter(
            category=self.category,
            available=True
        ).exclude(id=self.id).select_related('category').prefetch_related(
            Prefetch('offers', queryset=Offer.objects.filter(
                active=True,
                start_date__lte=timezone.now(),
                end_date__gte=timezone.now()
            ))
        )[:limit]
                
class Offer(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='offers')
    discount_percentage = models.DecimalField(max_digits=4, decimal_places=2)
    active = models.BooleanField(default=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.discount_percentage}% off {self.product.name}"

    def is_active(self):
        now = timezone.now()
        return (self.active and self.start_date <= now <= self.end_date)

class OfferProduct(models.Model):
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name='products')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product.name} x {self.quantity} in {self.offer.name}"              
                
class Review(models.Model):
    RATING_CHOICES = [
        (1, '1 Stella'),
        (2, '2 Stelle'),
        (3, '3 Stelle'),
        (4, '4 Stelle'),
        (5, '5 Stelle'),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('product', 'user')
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.product.name} - {self.rating} stelle'

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Carrello di - {self.user.username}"
    
    def get_total_price(self):
        try:
            return sum(item.get_total_price() for item in self.items.all())
        except (AttributeError, TypeError):
            return Decimal('0.00')

    def get_total_items(self):
        return sum(item.quantity for item in self.items.all())
    
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    
    class Meta:
        unique_together = ('cart', 'product')
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
    
    def get_total_price(self):
        """Prezzo totale considerando eventuali sconti"""
        return self.quantity * self.product.get_discounted_price()

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    paid = models.BooleanField(default=False)
    
    class Meta:
        ordering = ('-created',)
    
    def __str__(self):
        return f'Order {self.id}'
    
    def apply_discounts(self):
        subtotal = sum(item.get_total_price() for item in self.items.all())

        self.total = subtotal
        
        self.save()

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return str(self.id)
    
    is_gift = models.BooleanField(default=False)
    
    def get_total_price(self):
        return Decimal('0.00') if self.is_gift else self.price * self.quantity

class Coupon(models.Model):
    code = models.CharField(max_length=20, unique=True)
    discount_type = models.CharField(max_length=10, choices=[('percent', 'Percentuale'), ('fixed', 'Importo Fisso')])
    discount_value = models.DecimalField(max_digits=5, decimal_places=2)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    active = models.BooleanField(default=True)
    max_usage = models.PositiveIntegerField(default=1)
    current_usage = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.code} ({self.discount_value}{'%' if self.discount_type == 'percent' else '€'})"

    def is_valid(self):
        now = timezone.now()
        return (
            self.active and 
            self.valid_from <= now <= self.valid_to and 
            self.current_usage < self.max_usage
        )

    def apply_discount(self, amount):
        if self.discount_type == 'percent':
            return amount * (100 - self.discount_value) / 100
        return max(0, amount - self.discount_value)
    
class Wishlist(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    products = models.ManyToManyField('shop.Product', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Wishlist di {self.user.username}"