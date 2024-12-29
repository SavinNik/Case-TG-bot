import os
import random
from datetime import datetime

import telebot
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv


load_dotenv()

TOKEN = os.getenv("TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
CAPTIONS_FILE = os.getenv("CAPTIONS_FILE")
SAVE_DIR = os.getenv("SAVE_DIR")

bot = telebot.TeleBot(TOKEN)

def load_captions(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.readlines()

captions = load_captions(CAPTIONS_FILE)


if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)


@bot.message_handler(content_types=['photo'])
def handle_photo(message):

    user_id = message.from_user.id
    file_info = bot.get_file(message.photo[-1].file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    timestamp = datetime.now().strftime('%Y-%m-%d_%H:%M')
    file_name = f"{timestamp}_{user_id}.jpg"
    file_path = os.path.join(SAVE_DIR, file_name)

    with open(file_path, 'wb') as new_file:
        new_file.write(downloaded_file)

    caption = random.choice(captions).strip()
    img = Image.open(BytesIO(downloaded_file))
    draw = ImageDraw.Draw(img)

    font_path = 'Lobster-Regular.ttf'
    font = ImageFont.truetype(font_path, 36)

    draw.text((10, 10), caption, font=font, fill="red")

    output = BytesIO()
    output.name = 'output.jpg'
    img.save(output, format='JPEG')
    output.seek(0)

    bot.send_photo(message.chat.id, output, caption="Вот ваша картинка!")
    bot.send_message(message.chat.id, "Хотите поделиться этой картинкой в нашем канале? (Да/Нет)")


@bot.message_handler(func=lambda message: message.text in ['Да', 'Нет'])
def share_response(message):
    if message.text == 'Да':
        timestamp = datetime.now().strftime('%Y-%m-%d_%H:%M')
        file_name = f"{timestamp}_{message.from_user.id}.jpg"
        file_path = os.path.join(SAVE_DIR, file_name)
        with open(file_path, 'rb') as photo:
            bot.send_photo(CHANNEL_ID, photo)
        bot.send_message(message.chat.id, "Картинка успешно отправлена в канал!")
    else:
        bot.send_message(message.chat.id, "Хорошо, картинка не будет отправлена.")




if __name__ == '__main__':
    bot.polling(none_stop=True)
