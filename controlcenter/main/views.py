import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import Bot, Lead

@csrf_exempt # Отключаем CSRF-защиту, т.к. запросы приходят от внешнего бота
def receive_lead(request):
    """
    Принимает POST-запрос от Telegram-бота с данными новой заявки.
    """
    # 1. Проверяем, что это POST-запрос
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

    # 2. Проверяем наличие нашего секретного токена в заголовках
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return JsonResponse({'status': 'error', 'message': 'Authorization header missing'}, status=401)

    try:
        # Ожидаем заголовок в формате "Token YOUR_SUPER_SECRET_API_TOKEN"
        auth_type, provided_token = auth_header.split()
        if auth_type.lower() != 'token':
            raise ValueError
    except (ValueError, IndexError):
        return JsonResponse({'status': 'error', 'message': 'Invalid token format'}, status=401)
        
    # Сверяем системный токен (общий для всех)
    if provided_token != settings.API_AUTH_TOKEN:
        return JsonResponse({'status': 'error', 'message': 'Invalid system token'}, status=403)

    # 3. Получаем и парсим данные из тела запроса
    try:
        data = json.loads(request.body)
        bot_api_token = data.get('bot_api_token')
        customer_name = data.get('customer_name')
        customer_data = data.get('customer_data')

        if not all([bot_api_token, customer_name, customer_data]):
            return JsonResponse({'status': 'error', 'message': 'Missing data in request body'}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)

    # 4. Находим бота в нашей базе данных по его уникальному токену
    try:
        bot = Bot.objects.get(api_auth_token=bot_api_token)
    except Bot.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Bot with this token not found'}, status=404)

    # 5. Создаем новую заявку (лид) в базе данных
    Lead.objects.create(
        bot=bot,
        customer_name=customer_name,
        customer_data=customer_data
    )

    # 6. Отправляем успешный ответ
    return JsonResponse({'status': 'success', 'message': 'Lead created successfully'}, status=201)