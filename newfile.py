import telebot

# توكن البوت الخاص بك
BOT_TOKEN = "8943659346:AAGy7cO1kn6iqVmmG9m5rGi9oL5Hr_VF5l8"

# تهيئة البوت
bot = telebot.TeleBot(BOT_TOKEN)

# الأمر /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = "أهلاً بك! 👋\nالبوت يعمل الآن بنجاح."
    bot.reply_to(message, welcome_text)

# استقبال جميع الرسائل والرد عليها
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    bot.reply_to(message, f"وصلت رسالتك: {message.text}")

# تشغيل البوت باستمرار
if __name__ == "__main__":
    bot.infinity_polling()
  
