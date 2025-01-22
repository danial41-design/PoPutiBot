from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ConversationHandler, CallbackContext
from telegram.ext.filters import TEXT
import sqlite3


CHOOSING_ACTION, CHOOSING, GETTING_CITY_FROM, GETTING_CITY_TO = range(4)


# Подключение к базе данных
conn = sqlite3.connect('requests.db', check_same_thread=False)
cursor = conn.cursor()

# Удаляем старую таблицу, если она существует
cursor.execute("DROP TABLE IF EXISTS deliveries")

# Создаем новую таблицу
cursor.execute("""
CREATE TABLE IF NOT EXISTS deliveries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    action TEXT, -- "передать" или "отвезти"
    item TEXT,
    city_from TEXT,
    city_to TEXT,
    user_id INTEGER,
    username TEXT,
    is_notified INTEGER DEFAULT 0 -- 0 означает, что уведомление не отправлено
)
""")
conn.commit()





async def start(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text(
        "Привет! Вы хотите передать вещь или отвезти её в другой город? "
        "Напишите: 'Передать' или 'Отвезти'."
    )
    return CHOOSING_ACTION


async def choose_action(update: Update, context: CallbackContext) -> int:
    action = update.message.text.lower()
    if action not in ["передать", "отвезти"]:
        await update.message.reply_text("Пожалуйста, выберите только: 'Передать' или 'Отвезти'.")
        return CHOOSING_ACTION

    context.user_data['action'] = action
    if action == "отвезти":
        await update.message.reply_text("Укажите город отправления.")
        return GETTING_CITY_FROM
    elif action == "передать":
        await update.message.reply_text("Что именно вы хотите передать?")
        return CHOOSING





async def get_item(update: Update, context: CallbackContext) -> int:
    context.user_data['item'] = update.message.text
    await update.message.reply_text("Отлично! Укажите город отправления.")
    return GETTING_CITY_FROM




async def get_city_from(update: Update, context: CallbackContext) -> int:
    context.user_data['city_from'] = update.message.text
    await update.message.reply_text("Хорошо! В какой город нужно доставить эту вещь?")
    return GETTING_CITY_TO


async def get_city_to(update: Update, context: CallbackContext) -> int:
    context.user_data['city_to'] = update.message.text

    if context.user_data['action'] == "отвезти":
        # Сохранение данных о пользователе, который хочет отвезти
        cursor.execute("""
        INSERT INTO deliveries (action, item, city_from, city_to, user_id, username) 
        VALUES (?, ?, ?, ?, ?, ?)
        """, (
            "отвезти",
            None,  # Для перевозки item не требуется
            context.user_data['city_from'],
            context.user_data['city_to'],
            update.effective_user.id,
            update.effective_user.username
        ))
        conn.commit()

        # Уведомление пользователей, которые хотят передать
        cursor.execute("""
        SELECT user_id, username FROM deliveries 
        WHERE action = 'передать' AND city_from = ? AND city_to = ? AND is_notified = 0
        """, (context.user_data['city_from'], context.user_data['city_to']))
        results = cursor.fetchall()

        for user_id, username in results:
            try:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=f"Появился человек, который готов отвезти вашу вещь!\n"
                         f"Контакт: @{update.effective_user.username}"
                )
                # Обновляем статус уведомления
                cursor.execute("UPDATE deliveries SET is_notified = 1 WHERE user_id = ?", (user_id,))
            except Exception as e:
                print(f"Ошибка отправки уведомления пользователю @{username}: {e}")

        conn.commit()

        await update.message.reply_text(
            f"Спасибо! Ваш запрос на перевозку сохранён.\n"
            f"Маршрут: {context.user_data['city_from']} → {context.user_data['city_to']}\n"
            f"Мы уведомим тех, кто хочет передать вещи по этому маршруту."
        )

    elif context.user_data['action'] == "передать":
        # Сохранение данных о пользователе, который хочет передать
        cursor.execute("""
        INSERT INTO deliveries (action, item, city_from, city_to, user_id, username) 
        VALUES (?, ?, ?, ?, ?, ?)
        """, (
            "передать",
            context.user_data['item'],
            context.user_data['city_from'],
            context.user_data['city_to'],
            update.effective_user.id,
            update.effective_user.username
        ))
        conn.commit()

        await update.message.reply_text(
            f"Спасибо! Ваш запрос на передачу сохранён.\n"
            f"Маршрут: {context.user_data['city_from']} → {context.user_data['city_to']}\n"
            f"Мы уведомим вас, если кто-то будет готов отвезти вашу вещь."
        )

    return ConversationHandler.END


async def cancel(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("Операция отменена. Если потребуется помощь, пишите!")
    return ConversationHandler.END


async def list_requests(update: Update, context: CallbackContext):
    cursor.execute("SELECT item, city_from, city_to, username FROM deliveries")
    requests = cursor.fetchall()
    if not requests:
        await update.message.reply_text("Запросов пока нет.")
    else:
        response = "Вот текущие запросы на доставку:\n"
        for item, city_from, city_to, username in requests:
            response += f"- {item}: из {city_from} в {city_to} (от @{username})\n"
        await update.message.reply_text(response)


def main():
    # Создайте объект Application
    application = Application.builder().token("8185832801:AAFZBgAiqDLCN3_4pn-w-lFR7G94wz66z78").build()

    # Обработчик команд
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING_ACTION: [MessageHandler(TEXT, choose_action)],
            CHOOSING: [MessageHandler(TEXT, get_item)],  # Новый этап для предмета передачи
            GETTING_CITY_FROM: [MessageHandler(TEXT, get_city_from)],
            GETTING_CITY_TO: [MessageHandler(TEXT, get_city_to)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    # Регистрируем обработчики
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler('list', list_requests))

    # Запуск бота
    application.run_polling()

if __name__ == '__main__':
    main()
import schedule
import time
import sqlite3

# Функция для очистки базы данных
def clear_database():
    conn = sqlite3.connect('requests.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM deliveries")
    conn.commit()
    conn.close()
    print("База данных очищена.")

# Планируем задачу на каждую неделю
schedule.every().week.do(clear_database)

# Основной цикл выполнения
while True:
    schedule.run_pending()
    time.sleep(1)




