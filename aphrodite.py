import telebot
import requests
import randfacts
from telebot import types
from flask import Flask, request
import os

bot = telebot.TeleBot("7376383735:AAEbTuj_M-I0rfjNZbVYF37BYJNQiE4mQq8", parse_mode=None)
WEATHER_API_KEY = "6003fe5eec80fd899a6154daa71d8a8b"
WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"

app = Flask(__name__)

@app.route('/')
def home():
    return "Бот работает!", 200

@app.route(f"/{bot.token}", methods=['POST'])
def webhook():
    json_string = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return 'OK', 200

USER_STATE = {}

def main_menu():
    markup = types.ReplyKeyboardMarkup(row_width=3)
    item1 = types.KeyboardButton('Факты')
    item2 = types.KeyboardButton('Погода')
    item3 = types.KeyboardButton('ИМТ калькулятор')
    markup.add(item1, item2, item3)
    return markup

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    markup = main_menu()
    bot.reply_to(message, "Привет! Выбери опцию:", reply_markup=markup)
    bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAELTyJndT-mzyLyPnPwvQxqh3dczRtEoAACU1gAApWrqUneKpjTBcbatDYE')

@bot.message_handler(func=lambda message: message.text == "Факты")
def get_facts(message):
    try:
        fact = randfacts.get_fact(True)
        bot.reply_to(message, f"🧠 Вот интересный факт:\n{fact}", reply_markup=main_menu())
    except Exception as e:
        print(f"Ошибка: {e}")
        bot.reply_to(message, "❌ Не удалось получить факт. Попробуйте позже.", reply_markup=main_menu())

@bot.message_handler(func=lambda message: message.text == "Погода")
def ask_for_city(message):
    USER_STATE[message.chat.id] = 'weather'
    markup = types.ForceReply(selective=True)
    bot.reply_to(message, "Напишите название города:", reply_markup=markup)

@bot.message_handler(content_types=['sticker'])
def sticker_id(message):
    print(f"Получен стикер с ID: {message.sticker.file_id}")
    bot.reply_to(message, f"Вот ID вашего стикера: {message.sticker.file_id}")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    state = USER_STATE.get(message.chat.id)
    if state == 'weather':
        city = message.text.strip()
        weather_data = weather(city)
        bot.reply_to(message, weather_data, reply_markup=main_menu())
        del USER_STATE[message.chat.id]

def weather(city):
    try:
        params = {
            'q': city,
            'appid': WEATHER_API_KEY,
            'units': 'metric',
            'lang': 'ru'}
        response = requests.get(WEATHER_URL, params=params)
        data = response.json()
        if response.status_code == 200:
            temperature = data["main"]["temp"]
            status = data["weather"][0]["description"]
            return f"🌡 Температура в {city}: {temperature}°C, {status}"
        else:
            return "❌ Город не найден. Проверьте ввод."
    except Exception as e:
        print(e)
        return "❌ Ошибка при обработке запроса."

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    bot.remove_webhook()
    bot.set_webhook(url=f"https://host-tg.onrender.com//{bot.token}")
    app.run(host="0.0.0.0", port=port)
