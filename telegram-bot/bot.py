from time import sleep
import telebot
from telebot import types
import requests
import datetime

# ОПИСАНИЕ
# бот предлагает обновить информацию или подписаться на получение данных о
# свободных местах на ленина или вокзале.
# При подписке ситема опрашивает количество свободных мест и если оно
# увеличится то оповестит пользователя и прекратит опрос


bot = telebot.TeleBot('1720400501:AAGmrogatHb7XdYj0DCySphxHAVfU1exi6c')
leninan_URL = 'https://29adc6ed95a7.ngrok.io/lenina'
vokzal_URL = 'https://48544930e7d4.ngrok.io/vokzal'
user_check_list = list()  # сохраняем id пользователя, текущее количество свободных мест, url камеры, имя камеры
timeout_sec = 10


@bot.message_handler(content_types=['text'])
def start(message):
    if message.text == "/start":
        bot.send_message(message.from_user.id, "Я бот рассказывающий о свободных парковках в Петрозаводске! "
                                               "Ты можешь посмотреть общее количество свободных мест на парковках "
                                               "или подписать на одну из них и я сообщу о появлении новых мест")
    elif message.text == "/info":
        bot.send_message(message.from_user.id, "Я бот рассказывающий о свободных парковках в Петрозаводске!")
    elif message.text == "/help":
        bot.send_message(message.from_user.id, "Не переживай, просто выбери информация "
                                               "о какой парковке тебя интересует")
    chose_menu(message)


def chose_menu(message):
    bot.send_message(message.from_user.id, "Сейчас на парковках ситуация следующая, свободно мест:")
    bot.send_message(message.from_user.id, "Вокзал - " + str(requests.get(vokzal_URL).json()[0]))
    bot.send_message(message.from_user.id, "Ленина 19 - " + str(requests.get(leninan_URL).json()[0]))

    keyboard = types.InlineKeyboardMarkup()  # наша клавиатура
    key_refresh = types.InlineKeyboardButton(text='Обновить информацию', callback_data='key_refresh')  # кнопка «Да»
    keyboard.add(key_refresh)  # добавляем кнопку в клавиатуру
    key_vokzal = types.InlineKeyboardButton(text='Вокзал', callback_data='vokzal')
    keyboard.add(key_vokzal)
    key_lenina = types.InlineKeyboardButton(text='Ленина 19', callback_data='lenina')
    keyboard.add(key_lenina)
    question = 'Отслеживать освободившиеся места?'
    bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    global user_check_list
    if call.data == "key_refresh":
        chose_menu(call)

    elif call.data == "vokzal":
        bot.send_message(call.message.chat.id, 'Повентелирую вопросик :)')
        # первое - свободно, второе занято
        res_space = requests.get(leninan_URL).json()
        if not any(x == call.message.chat.id for x, *_ in user_check_list):
            user_check_list.append([call.message.chat.id, res_space[0], vokzal_URL, 'Вокзал'])

        check_free_space(call)

    elif call.data == "lenina":
        bot.send_message(call.message.chat.id, 'Услышал тебя :)')
        # первое - свободно, второе занято
        res_space = requests.get(leninan_URL).json()
        if not any(x == call.message.chat.id for x, *_ in user_check_list):
            user_check_list.append([call.message.chat.id, res_space[0], leninan_URL, 'Ленина 19'])

        check_free_space(call)


def check_free_space(message):
    global user_check_list
    while True:
        sleep(timeout_sec)
        res_index = [n for n, x in enumerate(user_check_list) if x[:1] == [message.from_user.id]]
        if len(res_index) != 0:
            user_row = user_check_list[res_index[0]]
            user_street_name = user_row[3]
            user_url = user_row[2]
            user_empty_space = user_row[1]
            res_space = requests.get(user_url).json()
            empty_space = res_space[0]
            if empty_space > user_empty_space:
                bot.send_message(message.from_user.id, "Бегом на " + str(user_street_name) + "! "
                                                                                             "Там освободилось место! Доступно " + str(
                    empty_space))
                user_row[3] = datetime.datetime.now()
                user_row[1] = empty_space
                break
        else:
            break


bot.polling(none_stop=True, interval=1)
