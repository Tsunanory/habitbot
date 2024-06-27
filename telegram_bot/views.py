import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .bot import main


@csrf_exempt
def webhook(request):
    if request.method == 'POST':
        update = json.loads(request.body)
        main.update_queue.put(update)
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'error': 'invalid request'}, status=400)

# Add to your main urls.py

urlpatterns = [
    path('telegram/webhook/', webhook, name='telegram-webhook'),
]
