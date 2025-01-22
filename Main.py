from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ConversationHandler, CallbackContext
from telegram.ext.filters import TEXT
from bot.handlers import DeliveryHandler
from bot.scheduler import start_scheduler


CHOOSING_ACTION, CHOOSING, GETTING_CITY_FROM, GETTING_CITY_TO = range(4)


def main():
    application = Application.builder().token("8185832801:AAFZBgAiqDLCN3_4pn-w-lFR7G94wz66z78").build()

    delivery_handler = DeliveryHandler()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', delivery_handler.start)],
        states={
            CHOOSING_ACTION: [MessageHandler(TEXT, delivery_handler.choose_action)],
            CHOOSING: [MessageHandler(TEXT, delivery_handler.get_item)],
            GETTING_CITY_FROM: [MessageHandler(TEXT, delivery_handler.get_city_from)],
            GETTING_CITY_TO: [MessageHandler(TEXT, delivery_handler.get_city_to)],
        },
        fallbacks=[CommandHandler('cancel', delivery_handler.cancel)],
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler('list', delivery_handler.list_requests))

    start_scheduler()

    application.run_polling()


if __name__ == '__main__':
    main()
