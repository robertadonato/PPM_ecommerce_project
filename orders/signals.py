from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import Order

@receiver(post_save, sender=Order)
def send_order_confirmation(sender, instance, created, **kwargs):
    if created:
        subject = f'Conferma Ordine #{instance.order_number}'
        message = f'''Grazie per il tuo ordine!
        
        Dettagli ordine:
        Numero: {instance.order_number}
        Totale: €{instance.total_amount}
        Status: {instance.get_status_display()}
        '''
        send_mail(
            subject,
            message,
            'noreply@dulcisfabula.it',
            [instance.user.email],
            fail_silently=False,
        )