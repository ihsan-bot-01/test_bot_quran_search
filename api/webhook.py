from http.server import BaseHTTPRequestHandler
import json
import httpx
import os
import asyncio
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
    
    print(f"Поиск запроса: {query}")
    print(f"URL: {API_URL}")
    print(f"Параметры: {params}")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(API_URL, params=params)
            print(f"Статус ответа: {response.status_code}")
            print(f"Содержимое ответа: {response.text[:500]}")
            response.raise_for_status()
            result = response.json()
            print(f"JSON результат: {result}")
            return result
        except Exception as e:
            print(f"Ошибка при запросе: {e}")
            print(f"Тип ошибки: {type(e)}")
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

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("content-type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"Bot is running!")
    
    def do_POST(self):
        try:
            length = int(self.headers.get("content-length", 0))
            raw = self.rfile.read(length) if length else b""
            
            if not raw:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"OK")
                return
            
            # Парсим JSON данные от Telegram
            data = json.loads(raw.decode('utf-8'))
            
            # Проверяем, есть ли сообщение
            if 'message' not in data or 'text' not in data['message']:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"OK")
                return
            
            # Получаем текст сообщения и chat_id
            user_message = data['message']['text']
            chat_id = data['message']['chat']['id']
            
            print(f"Получено сообщение: '{user_message}' от chat_id: {chat_id}")
            
            # Запускаем асинхронную обработку
            asyncio.run(process_message(user_message, chat_id))
            
            self.send_response(200)
            self.send_header("content-type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"OK")
            
        except Exception as e:
            print(f"Ошибка: {e}")
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode("utf-8"))
