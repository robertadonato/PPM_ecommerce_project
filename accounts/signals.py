from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from shop.models import Product, Category

@receiver(post_migrate)
def create_groups_and_permissions(sender, **kwargs):
    store_manager_group, created = Group.objects.get_or_create(name='Store Managers')

    content_type = ContentType.objects.get_for_model(Product)
    permissions = Permission.objects.filter(content_type=content_type)
    store_manager_group.permissions.add(*permissions)
    
    content_type = ContentType.objects.get_for_model(Category)
    permissions = Permission.objects.filter(content_type=content_type)
    store_manager_group.permissions.add(*permissions)