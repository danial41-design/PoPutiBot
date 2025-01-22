from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler
from bot.database import Database

CHOOSING_ACTION, CHOOSING, GETTING_CITY_FROM, GETTING_CITY_TO = range(4)


class Delivery:
    def __init__(self, user_id, username, city_from, city_to):
        self.user_id = user_id
        self.username = username
        self.city_from = city_from
        self.city_to = city_to

    def save_to_db(self):
        raise NotImplementedError("Subclasses should implement this method!")


class SendDelivery(Delivery):
    def __init__(self, user_id, username, item, city_from, city_to):
        super().__init__(user_id, username, city_from, city_to)
        self.item = item

    def save_to_db(self):
        Database.insert_delivery('передать', self.item, self.city_from, self.city_to, self.user_id, self.username)


class TransportDelivery(Delivery):
    def save_to_db(self):
        Database.insert_delivery('отвезти', None, self.city_from, self.city_to, self.user_id, self.username)


class DeliveryHandler:
    def __init__(self):
        self.user_data = {}

    async def start(self, update: Update, context: CallbackContext) -> int:
        await update.message.reply_text(
            "Привет! Вы хотите передать вещь или отвезти её в другой город? Напишите: 'Передать' или 'Отвезти'."
        )
        return CHOOSING_ACTION

    async def choose_action(self, update: Update, context: CallbackContext) -> int:
        action = update.message.text.lower()
        if action not in ['передать', 'отвезти']:
            await update.message.reply_text("Пожалуйста, выберите только: 'Передать' или 'Отвезти'.")
            return CHOOSING_ACTION

        self.user_data['action'] = action
        if action == 'отвезти':
            await update.message.reply_text("Укажите город отправления.")
            return GETTING_CITY_FROM
        else:
            await update.message.reply_text("Что вы хотите передать?")
            return CHOOSING

    async def get_item(self, update: Update, context: CallbackContext) -> int:
        self.user_data['item'] = update.message.text
        await update.message.reply_text("Отлично! Укажите город отправления.")
        return GETTING_CITY_FROM

    async def get_city_from(self, update: Update, context: CallbackContext) -> int:
        self.user_data['city_from'] = update.message.text
        await update.message.reply_text("Хорошо! В какой город нужно доставить эту вещь?")
        return GETTING_CITY_TO

    async def get_city_to(self, update: Update, context: CallbackContext) -> int:
        self.user_data['city_to'] = update.message.text
        user_id = update.effective_user.id
        username = update.effective_user.username

        if self.user_data['action'] == 'отвезти':
            delivery = TransportDelivery(user_id, username, self.user_data['city_from'], self.user_data['city_to'])
        else:
            delivery = SendDelivery(user_id, username, self.user_data['item'], self.user_data['city_from'],
                                    self.user_data['city_to'])

        delivery.save_to_db()

        await update.message.reply_text("Ваш запрос сохранён. Мы уведомим вас при наличии подходящих перевозчиков.")
        return ConversationHandler.END

    async def cancel(self, update: Update, context: CallbackContext) -> int:
        await update.message.reply_text("Операция отменена. Если потребуется помощь, пишите!")
        return ConversationHandler.END

    async def list_requests(self, update: Update, context: CallbackContext):
        requests = Database.fetch_all_deliveries()
        if not requests:
            await update.message.reply_text("Запросов пока нет.")
        else:
            response = "Вот текущие запросы на доставку:\n"
            for item, city_from, city_to, username in requests:
                response += f"- {item or 'Без предмета'}: из {city_from} в {city_to} (от @{username})\n"
            await update.message.reply_text(response)