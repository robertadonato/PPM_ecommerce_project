from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.conf import settings
from django.apps import apps
from django.utils.translation import gettext_lazy as _
from django.apps import apps

class User(AbstractUser):
    is_store_manager = models.BooleanField(
        default=False,
        verbose_name='Store Manager status',
        help_text='Designates whether the user can manage orders and products.'
    )
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    is_store_manager = models.BooleanField(default=False)
    
    groups = models.ManyToManyField(
        Group,
        verbose_name=_('groups'),
        blank=True,
        help_text=_('The groups this user belongs to.'),
        related_name="customuser_set",
        related_query_name="user",
    )
    
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name="customuser_set",
        related_query_name="user",
    )
    
    def __str__(self):
        return self.username
    
    def get_product(self):
        Product = apps.get_model('shop', 'Product')
        return Product.objects.first()

    def save(self, *args, **kwargs):
        creating = not self.pk
        super().save(*args, **kwargs)
        
        if creating:
            if self.is_store_manager:
                store_manager_group = Group.objects.get(name='Store Managers')
                self.groups.add(store_manager_group)