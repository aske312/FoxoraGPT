from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from transformers import pipeline
from dotenv import load_dotenv
import logging
import os

# Загружаем переменные из .env
load_dotenv()

# Получаем значения
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Загружаем модель GPT (например, GPT-2)
generator = pipeline("text-generation", model="gpt2")

# Словарь для хранения контекста диалога (user_id: context)
user_context = {}


# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_context[user_id] = []  # Инициализируем контекст для пользователя
    await update.message.reply_text(
        "Привет! Я FoxoraGPT. Напиши мне что-нибудь, и я постараюсь помочь. "
        "Используй /reset, чтобы сбросить контекст диалога."
    )


# Обработчик команды /reset
async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_context[user_id] = []  # Сбрасываем контекст
    await update.message.reply_text("Контекст диалога сброшен. Начнем с чистого листа!")


# Обработчик текстовых сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_message = update.message.text

    # Добавляем сообщение пользователя в контекст
    if user_id not in user_context:
        user_context[user_id] = []
    user_context[user_id].append(f"Пользователь: {user_message}")

    # Формируем промт для GPT с учетом контекста
    prompt = "\n".join(user_context[user_id][-5:])  # Используем последние 5 сообщений как контекст
    generated_text = generator(prompt, max_length=100, num_return_sequences=1)[0]["generated_text"]

    # Извлекаем ответ бота (все, что после последнего "Пользователь:")
    response = generated_text.split("Пользователь:")[-1].strip()

    # Добавляем ответ бота в контекст
    user_context[user_id].append(f"Бот: {response}")

    # Отправляем ответ пользователю
    await update.message.reply_text(response)


# Основная функция
def main():
    # Замените "YOUR_TELEGRAM_BOT_TOKEN" на токен вашего бота
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("reset", reset_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Запускаем бота
    application.run_polling()


if __name__ == "__main__":
    main()
