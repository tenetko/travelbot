import os
import telebot
from datetime import datetime
from travelpayouts import TravelpayoutsParser

class TicketBot:
    MONTHS = {
        "января": "1",
        "февраля": "2",
        "марта": "3",
        "апреля": "4",
        "мая": "5",
        "июня": "6",
        "июля": "7",
        "августа": "8",
        "сентября": "9",
        "октября": "10",
        "ноября": "11",
        "декабря": "12",
    }
    def __init__(self):
        self.tp = TravelpayoutsParser()
        self.org_iata = ""
        self.dst_iata = ""
        self.dep_date = ""
        self.ret_date = ""

    def run(self):
        bot = telebot.TeleBot(os.environ.get("TELEGRAM_TOKEN"))

        @bot.message_handler(commands=["start"])
        def start_message(message):
            bot.send_message(message.chat.id, "Вы хотите улететь? Если да, то введите 1. Если нет - то 0")

        @bot.message_handler(content_types=["text"])
        def handle_input(message):
            if message.text == "0":
                bot.send_message(message.chat.id, "(((")

            elif message.text == "1":
                bot.send_message(message.chat.id, "Введите аэропорт вылета")
                bot.register_next_step_handler(message, get_org_iata_code)

            else:
                bot.send_message(message.chat.id, "Не пойму, что вы хотите! Давайте начнём сначала")
                bot.clear_step_handler(message)

        @bot.message_handler(content_types=["text"])
        def get_org_iata_code(message):
            self.org_iata = self.tp.translate_to_iata(message.text)
            if self.org_iata == "":
                bot.send_message(message.chat.id, "Не знаю такого города! Давайте начнём сначала")
                bot.clear_step_handler(message)
            else:
                bot.send_message(message.chat.id, "Введите аэропорт прилёта")
                bot.register_next_step_handler(message, get_dst_iata_code)

        @bot.message_handler(content_types=["text"])
        def get_dst_iata_code(message):
            self.dst_iata = self.tp.translate_to_iata(message.text)
            if self.dst_iata == "":
                bot.send_message(message.chat.id, "Не знаю такого города! Давайте начнём сначала")
                bot.clear_step_handler(message)
            else:
                bot.send_message(message.chat.id, "Введите дату вылета\nФормат: 01.01, 1 января")
                bot.register_next_step_handler(message, get_dep_date)

        @bot.message_handler(content_types=["text"])
        def get_dep_date(message):
            try:
                self.dep_date = self.convert_date(message.text)

                bot.send_message(
                    message.chat.id,
                    'Введите дату возвращения или отправьте "нет", если вам не нужен обратный билет\n' +
                    'Формат: 01.01.2023, 1 января 2023',
                    )
                bot.register_next_step_handler(message, get_ret_date)

            except ValueError as e:
                bot.send_message(message.chat.id, "Не могу понять эту дату! Давайте начнём сначала")
                bot.clear_step_handler(message)

            except KeyError as e:
                bot.send_message(message.chat.id, "Не могу понять эту дату! Давайте начнём сначала")
                bot.clear_step_handler(message)

        @bot.message_handler(content_types=["text"])
        def get_ret_date(message):
            try:
                self.ret_date = self.get_return_date(message.text)
                display_results(message)
                bot.clear_step_handler(message)

            except ValueError as e:
                bot.send_message(message.chat.id, "Не могу понять эту дату! Давайте начнём сначала")
                bot.clear_step_handler(message)

            except KeyError as e:
                bot.send_message(message.chat.id, "Не могу понять эту дату! Давайте начнём сначала")
                bot.clear_step_handler(message)

        @bot.message_handler(content_types=["text"])
        def display_results(message):
            search_result = self.tp.make_price_request(self.org_iata, self.dst_iata, self.dep_date, self.ret_date)

            if search_result['data'] is None:
                bot.send_message(message.chat.id, "Разница между двумя датами не должна быть больше 30 дней")

            elif len(search_result['data']) == 0:
                bot.send_message(message.chat.id, "Я не нашёл билетов! Давайте начнём сначала")

            else:
                price = search_result['data'][0]['price']
                url = 'https://www.aviasales.ru' + search_result['data'][0]['link']
                bot.send_message(message.chat.id, f"Цена: {price}. [Ссылка на билет]({url})", parse_mode='Markdown')

        bot.infinity_polling()

    def convert_date(self, date):
        date_string = ""

        if " " in date:
            date_split = date.split(" ")

            if len(date_split) > 1 and date_split[1].isalpha():
                date_split[1] = self.MONTHS[date_split[1].lower()]
                date_split.append(datetime.strftime(datetime.now(), "%Y"))
                if len(date_split[0]) == 1:
                    date_split[0] = "0" + date_split[0]

                date_string = ".".join(date_split)

        if '.' in date:
            date_string = date + "." + datetime.strftime(datetime.now(), "%Y")

        parsed_date = datetime.strptime(date_string, '%d.%m.%Y')
        date_string = datetime.strftime(parsed_date, '%Y-%m-%d')

        return date_string


    def get_return_date(self, date):
        if date.lower() == "нет":
            return ""

        return self.convert_date(date)

if __name__ == "__main__":
    bot = TicketBot()
    bot.run()