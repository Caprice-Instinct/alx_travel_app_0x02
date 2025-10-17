import os
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import Payment
from django.core.mail import send_mail
from django.utils import timezone

CHAPA_SECRET_KEY = os.getenv('CHAPA_SECRET_KEY', 'your_chapa_secret_key_here')
CHAPA_BASE_URL = 'https://api.chapa.co/v1/transaction'

@csrf_exempt
def initiate_payment(request):
    if request.method == 'POST':
        data = request.POST
        booking_reference = data.get('booking_reference')
        amount = data.get('amount')
        email = data.get('email')
        payload = {
            'amount': amount,
            'currency': 'ETB',
            'email': email,
            'tx_ref': booking_reference,
            'callback_url': 'https://yourdomain.com/payment/verify/'
        }
        headers = {'Authorization': f'Bearer {CHAPA_SECRET_KEY}'}
        response = requests.post(f'{CHAPA_BASE_URL}/initialize', json=payload, headers=headers)
        resp_data = response.json()
        if resp_data.get('status') == 'success':
            transaction_id = resp_data['data']['tx_ref']
            payment = Payment.objects.create(
                booking_reference=booking_reference,
                amount=amount,
                transaction_id=transaction_id,
                status='Pending'
            )
            return JsonResponse({'checkout_url': resp_data['data']['checkout_url'], 'payment_id': payment.id})
        return JsonResponse({'error': resp_data.get('message', 'Payment initiation failed')}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def verify_payment(request):
    if request.method == 'POST':
        payment_id = request.POST.get('payment_id')
        try:
            payment = Payment.objects.get(id=payment_id)
        except Payment.DoesNotExist:
            return JsonResponse({'error': 'Payment not found'}, status=404)
        headers = {'Authorization': f'Bearer {CHAPA_SECRET_KEY}'}
        response = requests.get(f'{CHAPA_BASE_URL}/verify/{payment.transaction_id}', headers=headers)
        resp_data = response.json()
        if resp_data.get('status') == 'success' and resp_data['data']['status'] == 'success':
            payment.status = 'Completed'
            payment.updated_at = timezone.now()
            payment.save()
            # Send confirmation email (Celery recommended for production)
            send_mail(
                'Payment Confirmation',
                f'Your payment for booking {payment.booking_reference} was successful.',
                settings.DEFAULT_FROM_EMAIL,
                [request.POST.get('email')],
                fail_silently=True,
            )
            return JsonResponse({'status': 'Completed'})
        else:
            payment.status = 'Failed'
            payment.updated_at = timezone.now()
            payment.save()
            return JsonResponse({'status': 'Failed', 'message': resp_data.get('message', 'Verification failed')}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)
