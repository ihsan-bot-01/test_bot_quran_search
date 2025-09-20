import json
import httpx
import os
from telegram import Bot

# Получаем токен бота из переменных окружения
BOT_TOKEN = os.getenv('BOT_TOKEN')
API_URL = "https://api.testvpsonline.online/search"

async def search_text(query):
    """Отправляет запрос на поиск и возвращает результат"""
    params = {
        'query': query,
        'lang': 'ru',
        'k': 1,
        'ctx': 1
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(API_URL, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Ошибка при запросе: {e}")
            return None

def format_results(data):
    """Форматирует результаты поиска"""
    if not data or 'results' not in data:
        return "Ничего не найдено"
    
    formatted_lines = []
    for result in data['results']:
        surah = result.get('surah', '')
        ayah = result.get('ayah', '')
        text = result.get('text', '')
        formatted_lines.append(f"{surah}.{ayah} {text}")
    
    return '\n'.join(formatted_lines)

def handler(request):
    """Основная функция-обработчик для Vercel"""
    import asyncio
    
    if request.method == 'GET':
        return 'Bot is running!'
    
    if request.method == 'POST':
        try:
            # Получаем данные из webhook
            body = request.get_json()
            
            # Проверяем, есть ли сообщение
            if not body or 'message' not in body or 'text' not in body['message']:
                return 'OK'
            
            # Получаем текст сообщения и chat_id
            user_message = body['message']['text']
            chat_id = body['message']['chat']['id']
            
            # Запускаем асинхронную обработку
            asyncio.run(process_message(user_message, chat_id))
            
            return 'OK'
            
        except Exception as e:
            print(f"Ошибка: {e}")
            return 'Error', 500
    
    return 'Method not allowed', 405

async def process_message(user_message, chat_id):
    """Обрабатывает сообщение асинхронно"""
    # Отправляем запрос на поиск
    search_result = await search_text(user_message)
    
    # Форматируем ответ
    if search_result:
        formatted_response = format_results(search_result)
    else:
        formatted_response = "Произошла ошибка при поиске"
    
    # Отправляем ответ через Telegram API
    bot = Bot(token=BOT_TOKEN)
    await bot.send_message(chat_id=chat_id, text=formatted_response)
