import json
import httpx
from telegram import Update
from telegram.ext import Application, MessageHandler, filters
from http.server import BaseHTTPRequestHandler
import os

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

async def handle_message(update: Update, context):
    """Обрабатывает сообщения пользователей"""
    user_message = update.message.text
    
    # Отправляем запрос на поиск
    search_result = await search_text(user_message)
    
    # Форматируем и отправляем ответ
    if search_result:
        formatted_response = format_results(search_result)
        await update.message.reply_text(formatted_response)
    else:
        await update.message.reply_text("Произошла ошибка при поиске")

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            # Создаем приложение
            application = Application.builder().token(BOT_TOKEN).build()
            
            # Добавляем обработчик сообщений
            application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
            
            # Обрабатываем webhook
            update_data = json.loads(post_data.decode('utf-8'))
            update = Update.de_json(update_data, application.bot)
            
            # Обрабатываем обновление
            import asyncio
            asyncio.run(application.process_update(update))
            
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'OK')
            
        except Exception as e:
            print(f"Ошибка: {e}")
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b'Error')
    
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Bot is running!')
