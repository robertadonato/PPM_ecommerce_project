from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from shop.models import Product, Category
from orders.models import Order, OrderItem

class Command(BaseCommand):
    help = 'Create user groups and permissions'

    def handle(self, *args, **options):
        customers_group, _ = Group.objects.get_or_create(name='Customers')
        managers_group, _ = Group.objects.get_or_create(name='Store Managers')
        
        customer_perms = [
            Permission.objects.get(codename='view_product'),
            Permission.objects.get(codename='view_category'),
        ]
        customers_group.permissions.set(customer_perms)
        
        manager_models = [Product, Category, Order, OrderItem]
        manager_perms = []
        for model in manager_models:
            ct = ContentType.objects.get_for_model(model)
            manager_perms.extend(Permission.objects.filter(content_type=ct))
        
        managers_group.permissions.set(manager_perms)
        
        if not User.objects.filter(username='manager').exists():
            manager = User.objects.create_user(
                username='manager',
                password='manager123',
                is_staff=True,
                is_store_manager=True
            )
            manager.groups.add(managers_group)
            self.stdout.write(self.style.SUCCESS('Creato utente manager: manager / manager123'))
        
        self.stdout.write(self.style.SUCCESS('Setup completato'))