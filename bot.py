from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import sqlite3
import os
from flask import Flask
import threading
import random

TOKEN = "8910180308:AAGUP5gKehIZ16tD1OMuY-DVYvH6kcbt5M8"

# ========== دیتابیس ==========
def init_db():
    conn = sqlite3.connect('german_words.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS words (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            word TEXT NOT NULL,
            meaning TEXT NOT NULL,
            example TEXT,
            level TEXT
        )
    ''')
    
    cursor.execute('SELECT COUNT(*) FROM words')
    if cursor.fetchone()[0] == 0:
        sample_words = [
            ('Hallo', 'سلام', 'Hallo, wie geht es dir?', 'A1'),
            ('Danke', 'متشکرم', 'Danke für deine Hilfe', 'A1'),
            ('Bitte', 'خواهش می‌کنم', 'Bitte schön', 'A1'),
            ('Guten Morgen', 'صبح بخیر', 'Guten Morgen, wie hast du geschlafen?', 'A1'),
            ('Auf Wiedersehen', 'خداحافظ', 'Auf Wiedersehen, bis morgen!', 'A1')
        ]
        cursor.executemany('INSERT INTO words (word, meaning, example, level) VALUES (?, ?, ?, ?)', sample_words)
    
    conn.commit()
    conn.close()

def get_daily_word():
    conn = sqlite3.connect('german_words.db')
    cursor = conn.cursor()
    cursor.execute('SELECT word, meaning, example FROM words ORDER BY RANDOM() LIMIT 1')
    result = cursor.fetchone()
    conn.close()
    return result

# ========== بخش ربات تلگرام ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["📖 لغت روز", "💬 اصطلاح روز"],
        ["🎯 کوییز روز", "📝 آزمون‌ها"],
        ["📚 کتابخانه", "📰 مجله‌ها"],
        ["👤 پروفایل", "⭐ ذخیره شده‌ها"],
        ["🛡 پشتیبانی"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "به ربات DailyDe خوش اومدی! 🎉\n\n"
        "آموزش روزانه زبان مثل آب خوردن!\n\n"
        "چی میخوای؟:",
        reply_markup=reply_markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == "📖 لغت روز":
        word_data = get_daily_word()
        if word_data:
            word, meaning, example = word_data
            message = f"📚 *لغت روز*\n\n"
            message += f"🔹 کلمه: `{word}`\n"
            message += f"🔸 معنی: {meaning}\n"
            message += f"📝 مثال: _{example}_"
            await update.message.reply_text(message, parse_mode="Markdown")
        else:
            await update.message.reply_text("در حال توسعه 🚧")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("/start - شروع\n/help - راهنما")

# ========== بخش Flask (برای Render) ==========
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "Daily De is activated🤖"

@flask_app.route('/health')
def health():
    return "OK"

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    flask_app.run(host='0.0.0.0', port=port)

def run_bot():
    init_db()
    
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("✅ Bot is On")
    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()
    
    run_bot()