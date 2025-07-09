from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView, DetailView
from django.contrib import messages
from django.utils.crypto import get_random_string
from shop.models import Cart, CartItem
from .models import Order, OrderItem
from .forms import OrderForm
from django.conf import settings
import stripe

class OrderListView(LoginRequiredMixin, ListView):
    template_name = 'orders/order_list.html'
    context_object_name = 'orders'
    paginate_by = 10
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'orders/order_detail.html'
    context_object_name = 'order'
    slug_field = 'order_number'
    slug_url_kwarg = 'order_number'
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

@login_required
def create_order(request):
    cart = get_object_or_404(Cart, user=request.user)
    
    if not cart.items.exists():
        messages.error(request, 'Il carrello è vuoto!')
        return redirect('shop:cart')
    
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.order_number = get_random_string(10).upper()
            order.total_amount = cart.get_total_price()
            order.save()
            
            for cart_item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price
                )
                
                product = cart_item.product
                product.stock -= cart_item.quantity
                product.save()
            
            cart.items.all().delete()
            
            messages.success(request, f'Ordine {order.order_number} creato con successo!')
            return redirect('orders:order_detail', order_number=order.order_number)
    else:
        initial_data = {
            'shipping_name': request.user.get_full_name(),
            'shipping_address': request.user.address,
            'shipping_phone': request.user.phone_number,
        }
        form = OrderForm(initial=initial_data)
    
    context = {
        'form': form,
        'cart': cart,
    }
    return render(request, 'orders/create_order.html', context)

@login_required
def checkout(request):
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.items.all()
        
        if not cart_items:
            messages.warning(request, 'Il carrello è vuoto!')
            return redirect('shop:cart')
            
    except Cart.DoesNotExist:
        messages.warning(request, 'Il carrello è vuoto!')
        return redirect('shop:cart')
    
    if request.method == 'POST':
        order = Order.objects.create(
            user=request.user,
            shipping_address=request.POST.get('address'),
            total_amount=cart.get_total_price()
        )
        
        for cart_item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.price
            )
            
            product = cart_item.product
            product.stock -= cart_item.quantity
            product.save()
        
        cart_items.delete()
        
        messages.success(request, f'Ordine #{order.id} creato con successo!')
        return redirect('orders:order_detail', order_id=order.id)
    
    context = {
        'cart_items': cart_items,
        'cart': cart,
    }
    return render(request, 'orders/checkout.html', context)

stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def create_payment_intent(request):
    cart = get_object_or_404(Cart, user=request.user)
    total = cart.get_total_price() * 100
    
    intent = stripe.PaymentIntent.create(
        amount=int(total),
        currency='eur',
        metadata={'user_id': request.user.id}
    )
    
    return JsonResponse({'clientSecret': intent.client_secret})

class UserOrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'orders/order_list.html'
    context_object_name = 'orders'
    paginate_by = 10
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})

@permission_required('orders.view_order', raise_exception=True)
@login_required
def manage_orders(request):
    if not (request.user.is_superuser or 
        getattr(request.user, 'is_store_manager', False) or 
        request.user.has_perm('orders.view_order')):
        messages.error(request, "Non hai i permessi per accedere a questa pagina")
        return redirect('shop:product_list')
    
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'orders/manage_orders.html', {'orders': orders})

@permission_required('orders.view_order', raise_exception=True)
@login_required
def manage_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'orders/manage_order_detail.html', {'order': order})

@permission_required('orders.change_order', raise_exception=True)
@login_required
def update_order_status(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)
        new_status = request.POST.get('status')
        order.status = new_status
        order.save()
        messages.success(request, f'Stato ordine #{order.id} aggiornato!')
    return redirect('orders:manage_orders')

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/order_history.html', {'orders': orders})