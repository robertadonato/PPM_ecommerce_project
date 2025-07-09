from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Q, Avg
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from .models import Product, Category, Offer, Cart, CartItem, Review, Order, OrderItem
from .forms import ReviewForm, CartAddProductForm
from django.contrib.sessions.backends.db import SessionStore
from django.utils import timezone
from decimal import Decimal

def home_view(request):
    now = timezone.now()
    
    try:
        confetti_crumbl = {
            'product': get_object_or_404(Product, id=5),
            'offer': Offer.objects.filter(
                product__slug='confetti-crumbl', 
                active=True,
                start_date__lte=now,
                end_date__gte=now
            ).first()
        }
    except Product.DoesNotExist:
        confetti_crumbl = None
    try:
        blue_coriandoli = {
            'product': get_object_or_404(Product, id=24),
            'offer': Offer.objects.filter(
                product__slug='blue-coriandoli-donut', 
                active=True,
                start_date__lte=now,
                end_date__gte=now
            ).first()
        }
    except Product.DoesNotExist:
        blue_coriandoli = None

    return render(request, 'shop/home.html', {
        'confetti_crumbl': confetti_crumbl,
        'blue_coriandoli': blue_coriandoli,
        'confetti_img': 'https://res.cloudinary.com/djusrww0l/image/upload/v1750783774/confetti_crumbl_zkyx7v.jpg',
        'blue_img': 'https://res.cloudinary.com/djusrww0l/image/upload/v1750783769/blue_coriandoli_donut_klekcn.jpg'
    })

def servizi_view(request):
    return render(request, 'shop/servizi.html')

def chi_siamo_view(request):
    return render(request, 'shop/chi_siamo.html')

def contatti_view(request):
    return render(request, 'shop/contatti.html')

class ProductListView(ListView):
    model = Product
    template_name = 'shop/product_list.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Product.objects.filter(available=True)

        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) | 
                Q(description__icontains=query) |
                Q(ingredients__icontains=query)
            )

        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        sort_by = self.request.GET.get('sort', '-created_at')
        if sort_by in ['name', '-name', 'price', '-price', 'created_at', '-created_at']:
            queryset = queryset.order_by(sort_by)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['current_category'] = self.request.GET.get('category')
        context['query'] = self.request.GET.get('q', '')
        return context

class ProductDetailView(DetailView):
    model = Product
    template_name = 'shop/product_detail.html'
    context_object_name = 'product'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        
        reviews = product.reviews.order_by('-created_at')
        context['reviews'] = reviews
        context['average_rating'] = reviews.aggregate(Avg('rating'))['rating__avg']
        
        if self.request.user.is_authenticated:
            context['review_form'] = ReviewForm()
            
            user_has_purchased = Order.objects.filter(
                user=self.request.user,
                items__product=product
            ).exists()
            context['user_has_purchased'] = user_has_purchased
            
            context['cart_form'] = CartAddProductForm()
        
        context['related_products'] = Product.objects.filter(
            category=product.category,
            available=True
        ).exclude(id=product.id)[:4]
        
        return context

def product_search(request):
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    
    products = Product.objects.filter(available=True)
    
    if query:
        products = products.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        )
    
    if category:
        products = products.filter(category__slug=category)
        
    if min_price:
        products = products.filter(price__gte=min_price)
        
    if max_price:
        products = products.filter(price__lte=max_price)
    
    return render(request, 'shop/search_results.html', {'products': products})
    
def get_offer_details(request, offer_code):
    try:
        offer = Offer.objects.get(code=offer_code)
        data = {
            'code': offer.code,
            'discount': offer.discount,
            'products': [
                {
                    'id': op.product.id,
                    'name': op.product.name,
                    'quantity': op.quantity
                }
                for op in offer.offer_products.select_related('product')
            ]
        }
        return JsonResponse(data)
    except Offer.DoesNotExist:
        return JsonResponse({'error': 'Offerta non trovata'}, status=404)   
    
class StoreManagerDashboard(UserPassesTestMixin, ListView):
    model = Product
    template_name = 'shop/store_manager_dashboard.html'
    
    def test_func(self):
        return self.request.user.is_store_manager or self.request.user.is_superuser

class StoreManagerRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and (
            self.request.user.is_store_manager or self.request.user.is_superuser
        )

class CartView(ListView):
    template_name = 'shop/cart.html'
    context_object_name = 'cart_items'
    
    def get_queryset(self):
        if self.request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=self.request.user)
            return cart.items.all()
        else:
            session_cart = self.request.session.get('cart', {})
            cart_items = []
            for product_id, quantity in session_cart.items():
                try:
                    product = Product.objects.get(id=product_id)
                    cart_items.append({
                        'id': product_id,
                        'product': product,
                        'quantity': quantity,
                        'get_total_price': product.get_discounted_price() * Decimal(quantity)
                    })
                except Product.DoesNotExist:
                    continue
            return cart_items
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_items = context.get('cart_items', [])
        
        subtotal = Decimal('0.00')
        discount = Decimal('0.00')
        shipping_cost = Decimal('5.00')
        
        for item in cart_items:
            try:
                if hasattr(item, 'product'):
                    product = item.product
                    quantity = Decimal(str(item.quantity))
                    original_price = Decimal(str(product.price))
                    discounted_price = Decimal(str(product.get_discounted_price()))
                else:
                    product = item.get('product')
                    if not product:
                        continue
                    quantity = Decimal(str(item.get('quantity', 1)))
                    original_price = Decimal(str(product.price))
                    discounted_price = Decimal(str(product.get_discounted_price()))

                subtotal += discounted_price * quantity
                item_discount = (original_price - discounted_price) * quantity
                discount += Decimal(str(item_discount))
                
            except (AttributeError, KeyError, TypeError) as e:
                print(f"Errore nel processare l'item del carrello: {e}")
                continue

        if self.request.user.is_authenticated:
            shipping_cost = Decimal('0.00')
        
        total = subtotal + shipping_cost
        
        context.update({
            'subtotal': subtotal.quantize(Decimal('0.00')),
            'discount': discount.quantize(Decimal('0.00')),
            'shipping_cost': shipping_cost.quantize(Decimal('0.00')),
            'total': total.quantize(Decimal('0.00'))
        })
        
        return context

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        form = CartAddProductForm(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data['quantity']
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={'quantity': quantity}
            )
            if not created:
                cart_item.quantity += quantity
                cart_item.save()
            messages.success(request, f'{product.name} aggiunto al carrello!')
    else:
        cart = request.session.get('cart', {})
        quantity = int(request.POST.get('quantity', 1))
        
        if str(product_id) in cart:
            cart[str(product_id)] += quantity
        else:
            cart[str(product_id)] = quantity
        
        request.session['cart'] = cart
        messages.success(request, f'{product.name} aggiunto al carrello!')
    
    return redirect('shop:product_detail', pk=product.id, slug=product.slug)

def remove_from_cart(request, item_id):
    if request.user.is_authenticated:
        try:
            cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)
            product_name = cart_item.product.name
            cart_item.delete()
            messages.success(request, f'{product_name} rimosso dal carrello!')
        except CartItem.DoesNotExist:
            messages.error(request, 'Prodotto non trovato nel carrello!')
    else:
        cart = request.session.get('cart', {})
        product = get_object_or_404(Product, id=item_id)
        
        if str(item_id) in cart:
            del cart[str(item_id)]
            request.session['cart'] = cart
            messages.success(request, f'{product.name} rimosso dal carrello!')
        else:
            messages.error(request, 'Prodotto non trovato nel carrello!')
    
    return redirect('shop:cart')

def update_cart_item(request, item_id):
    if request.method == 'POST':
        try:
            quantity = int(request.POST.get('quantity', 1))
            
            if request.user.is_authenticated:
                cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
                product = cart_item.product
                
                if quantity > product.stock:
                    return JsonResponse({
                        'success': False,
                        'message': f'Quantità non disponibile. Massimo: {product.stock}'
                    })
                
                if quantity > 0:
                    cart_item.quantity = quantity
                    cart_item.save()
                else:
                    cart_item.delete()
            else:
                cart = request.session.get('cart', {})
                product = get_object_or_404(Product, id=item_id)
                
                if quantity > product.stock:
                    return JsonResponse({
                        'success': False,
                        'message': f'Quantità non disponibile. Massimo: {product.stock}'
                    })
                
                if quantity > 0:
                    cart[str(item_id)] = quantity
                else:
                    cart.pop(str(item_id), None)
                
                request.session['cart'] = cart
            
            return JsonResponse({'success': True})
        
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=400)
    
    return JsonResponse({
        'success': False,
        'message': 'Metodo non consentito'
    }, status=405)

def checkout(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_items = cart.items.all()
    else:
        cart = request.session.get('cart', {})
        cart_items = []
        for product_id, quantity in cart.items():
            try:
                product = Product.objects.get(id=product_id)
                cart_items.append({
                    'product': product,
                    'quantity': quantity,
                    'get_total_price': product.get_discounted_price() * Decimal(quantity)
                })
            except Product.DoesNotExist:
                continue

    if request.method == 'POST':
        if not cart_items:
            messages.error(request, "Il tuo carrello è vuoto")
            return redirect('shop:cart')

        subtotal = sum(
            item.get_total_price() if hasattr(item, 'get_total_price') 
            else item['get_total_price'] 
            for item in cart_items
        )
        
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            total=subtotal,
            shipping_cost=Decimal('0.00') if request.user.is_authenticated else Decimal('5.00')
        )
        
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product if hasattr(item, 'product') else item['product'],
                price=item.product.price if hasattr(item, 'product') else item['product'].price,
                quantity=item.quantity if hasattr(item, 'quantity') else item['quantity']
            )

        if request.user.is_authenticated:
            cart.items.all().delete()
        else:
            request.session['cart'] = {}

        return render(request, 'shop/checkout/success.html', {'order': order})

    subtotal = Decimal('0.00')
    discount = Decimal('0.00')
    
    for item in cart_items:
        if hasattr(item, 'product'):
            product = item.product
            quantity = Decimal(str(item.quantity))
            original_price = Decimal(str(product.price))
            discounted_price = Decimal(str(product.get_discounted_price()))
        else:
            product = item.get('product')
            if not product:
                continue
            quantity = Decimal(str(item.get('quantity', 1)))
            original_price = Decimal(str(product.price))
            discounted_price = Decimal(str(product.get_discounted_price()))
        
        subtotal += discounted_price * quantity
        item_discount = (original_price - discounted_price) * quantity
        discount += item_discount

    shipping_cost = Decimal('0.00') if request.user.is_authenticated else Decimal('5.00')
    total = subtotal + shipping_cost

    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'discount': discount,
        'shipping_cost': shipping_cost,
        'total': total,
    }
    
    return render(request, 'shop/checkout.html', context)

@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if product.reviews.filter(user=request.user).exists():
        messages.error(request, 'Hai già inviato una recensione per questo prodotto.')
        return redirect('shop:product_detail', slug=product.slug)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            messages.success(request, 'Recensione aggiunta con successo!')
        else:
            messages.error(request, 'Errore nell\'aggiungere la recensione.')
    
    return redirect('shop:product_detail', slug=product.slug)

@login_required
def edit_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)

    if review.user != request.user:
        raise PermissionDenied("Non puoi modificare una recensione che non ti appartiene.")

    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, 'Recensione modificata con successo!')
            return redirect('shop:product_detail', slug=review.product.slug)
    else:
        form = ReviewForm(instance=review)

    return render(request, 'shop/review_edit.html', {'form': form, 'product': review.product})

@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)

    if review.user != request.user:
        raise PermissionDenied("Non puoi eliminare una recensione che non ti appartiene.")

    product_slug = review.product.slug
    review.delete()
    messages.success(request, "Recensione eliminata.")
    return redirect('shop:product_detail', slug=product_slug)

@login_required
@user_passes_test(lambda u: u.is_store_manager or u.is_superuser)
def manage_categories(request):
    categories = Category.objects.all().order_by('name')
    
    if request.method == 'POST':
        pass
    
    context = {
        'categories': categories,
    }
    return render(request, 'shop/manage_categories.html', context)

@login_required
@user_passes_test(lambda u: u.is_store_manager or u.is_superuser)
def manage_products(request):
    products = Product.objects.all().order_by('-created_at')
    
    category = request.GET.get('category')
    if category:
        products = products.filter(category__slug=category)
    
    query = request.GET.get('q')
    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))
    
    context = {
        'products': products,
        'categories': Category.objects.all(),
    }
    return render(request, 'shop/manage_products.html', context)

@login_required
@user_passes_test(lambda u: u.is_superuser)
def product_stats(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'shop/product_stats.html', {'product': product})

class ProductCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Product
    fields = ['name', 'category', 'price', 'stock', 'description', 'image', 'available', 'ingredients', 'allergens', 'weight', 'shelf_life']
    template_name = 'shop/product_form.html'
    success_url = reverse_lazy('shop:manage_products')

    def test_func(self):
        return self.request.user.is_store_manager or self.request.user.is_superuser

    def form_valid(self, form):
        messages.success(self.request, "Prodotto creato con successo!")
        return super().form_valid(form)

class ProductUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Product
    fields = ['name', 'category', 'price', 'stock', 'description', 'image', 'available']
    template_name = 'shop/product_form.html'
    success_url = '/manage/products/'

    def test_func(self):
        return self.request.user.is_store_manager or self.request.user.is_superuser

class ProductDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Product
    template_name = 'shop/product_confirm_delete.html'
    success_url = '/manage/products/'

    def test_func(self):
        return self.request.user.is_store_manager or self.request.user.is_superuser

class CategoryCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Category
    fields = ['name', 'description']
    template_name = 'shop/category_form.html'
    success_url = reverse_lazy('shop:manage_categories')

    def test_func(self):
        return self.request.user.is_store_manager or self.request.user.is_superuser

class CategoryUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Category
    fields = ['name', 'description']
    template_name = 'shop/category_form.html'
    success_url = reverse_lazy('shop:manage_categories')

    def test_func(self):
        return self.request.user.is_store_manager or self.request.user.is_superuser

class CategoryDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Category
    template_name = 'shop/category_confirm_delete.html'
    success_url = reverse_lazy('shop:manage_categories')

    def test_func(self):
        return self.request.user.is_store_manager or self.request.user.is_superuser