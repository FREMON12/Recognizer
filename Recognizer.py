from enum import Enum
import telebot
import requests
from face_rec import find_faces, public_bd_add, private_bd_add, private_bd_del, bd_init
from telebot import types


class Status(Enum):
    FREE = 0
    ADD_PHOTO_PR = 1
    ADD_NAME_PR = 2
    ADD_PHOTO_PU = 3
    ADD_NAME_PU = 4
    DEL_PR = 5


TOKEN = '1436680880:AAHLf59LuuVFP1FfRfV_z4dgqewqgaOJh58'

bot = telebot.TeleBot(TOKEN)
user_stat = {}
bd_init()


def check_usr(message):
    if not user_stat.get(message.from_user.id):
        user_stat[message.from_user.id] = [Status.FREE, 0, 0]


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    check_usr(message)
    user_stat[message.from_user.id] = [Status.FREE, 0, 0]
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Распознать фото")
    item2 = types.KeyboardButton("Добавить в локальную базу")
    item3 = types.KeyboardButton("Добавить в глобальную базу")
    item4 = types.KeyboardButton("Удалить из локальной базы")
    markup.add(item1, item2, item3, item4, )
    sti = open('img/1.jpg', 'rb')
    bot.send_sticker(message.chat.id, sti)
    bot.send_message(message.chat.id,
                     "Добро пожаловать, {0.first_name}!\nЯ - <b>{1.first_name}</b>, "
                     "бот, который умеет распознавать людей. "
                     "\nДоступные команды:\n""/start - запуск бота\n"
                     "/analize - распознать фото\n"
                     "/add - добавить в локальную БД\n"
                     "/add_g - добавить в глобальную БД\n"
                     "/del - удалить из локальной БД\n"
                     "/vk - моя страница ВКонтакте\n"
                     "/inst - моя страница в Instagram\n"
                     .format(message.from_user, bot.get_me()), parse_mode='html',
                     reply_markup=markup)


@bot.message_handler(commands=['vk'])
def vk(message):
    markup = types.InlineKeyboardMarkup()
    sti = open('img/1.jpg', 'rb')
    bot.send_sticker(message.chat.id, sti)
    markup.add(types.InlineKeyboardButton("Посетить мою страницу в вк", url="https://vk.com/vinglivskt"))
    bot.send_message(message.chat.id, "Нажмите на кнопку ниже для перехода", parse_mode='html',
                     reply_markup=markup)


@bot.message_handler(commands=['inst'])
def Instagram(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Перейти в Инстаграм", url="https://www.instagram.com/vinglivskt/?r=nametag"))
    sti = open('img/1.jpg', 'rb')
    bot.send_sticker(message.chat.id, sti)
    bot.send_message(message.chat.id, "Нажмите на кнопку ниже для перехода в мой Instagram", parse_mode='html',
                     reply_markup=markup)


@bot.message_handler(commands=['analize'])
def handle_analize(message):
    check_usr(message)
    user_stat[message.from_user.id] = [Status.FREE, 0, 0]
    bot.reply_to(message, "Пришлите фото для распознания.")


@bot.message_handler(commands=['add_g'])
def handle_add_public(message):
    check_usr(message)
    bot.send_message(message.chat.id,
                     "Отправьте фотографию человека, которого вы хотите добавить в глобальную БД.")
    user_stat[message.from_user.id][0] = Status.ADD_PHOTO_PU


@bot.message_handler(commands=['add'])
def handle_add(message):
    check_usr(message)
    bot.send_message(message.chat.id, "Отправьте фотографию человека, которого вы хотите добавить в локальную БД.")
    user_stat[message.from_user.id][0] = Status.ADD_PHOTO_PR


@bot.message_handler(commands=['del'])
def handle_del(message):
    check_usr(message)
    bot.send_message(message.chat.id, "Введите имя человека, которого вы хотите удалить из своей библиотеки.")
    user_stat[message.from_user.id][0] = Status.DEL_PR


@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    check_usr(message)
    if user_stat[message.from_user.id][0] == Status.ADD_PHOTO_PR:
        photo_path = bot.get_file(message.photo[len(message.photo) - 1].file_id).file_path
        request = requests.get('https://api.telegram.org/file/bot{}/{}'.format(TOKEN, photo_path))
        user_stat[message.from_user.id][1] = request.content
        bot.reply_to(message, "Введите имя этого человека")
        user_stat[message.from_user.id][0] = Status.ADD_NAME_PR
    elif user_stat[message.from_user.id][0] == Status.ADD_PHOTO_PU:
        photo_path = bot.get_file(message.photo[len(message.photo) - 1].file_id).file_path
        request = requests.get('https://api.telegram.org/file/bot{}/{}'.format(TOKEN, photo_path))
        user_stat[message.from_user.id][1] = request.content
        bot.reply_to(message, "Введите имя этого человека")
        user_stat[message.from_user.id][0] = Status.ADD_NAME_PU
    elif user_stat[message.from_user.id][0] == Status.FREE:

        photo_path = bot.get_file(message.photo[len(message.photo) - 1].file_id).file_path
        request = requests.get('https://api.telegram.org/file/bot{}/{}'.format(TOKEN, photo_path))
        adding_photo = open("tmp.jpg", "wb")
        adding_photo.write(request.content)

        bot.send_message(message.chat.id, "Обработка")
        name_list = find_faces("tmp.jpg", message.from_user.id)
        out_str = ""
        for name in name_list:
            out_str = out_str + name + '\n'
        if out_str == "":
            out_str = "Не удалось найти лица"
        else:
            out_str = "Распозанные лица:\n" + out_str
            img = open('out.png', 'rb')
            bot.send_photo(message.chat.id, img)
        bot.reply_to(message, out_str)

    else:
        bot.reply_to(message, "Произошла ошибка, возможно вы делаете что-то не так(")


@bot.message_handler(content_types=['text'])
def handle_text(message):
    check_usr(message)

    if user_stat[message.from_user.id][0] == Status.ADD_NAME_PU:
        user_stat[message.from_user.id][2] = message.text
        print(user_stat[message.from_user.id][2])

        adding_photo = open("tmp.jpg", "wb")
        adding_photo.write(user_stat[message.from_user.id][1])

        if public_bd_add("tmp.jpg", user_stat[message.from_user.id][2]):
            bot.reply_to(message, "Человек успешно добавлен")
        else:
            bot.reply_to(message, "Что-то пошло не так. Лица не найдены")
        user_stat[message.from_user.id][0] = Status.FREE
    elif user_stat[message.from_user.id][0] == Status.ADD_NAME_PR:
        user_stat[message.from_user.id][2] = message.text
        print(user_stat[message.from_user.id][2])
        adding_photo = open("tmp.jpg", "wb")
        adding_photo.write(user_stat[message.from_user.id][1])
        if private_bd_add(message.from_user.id, "tmp.jpg", user_stat[message.from_user.id][2]):
            bot.reply_to(message, "Человек успешно добавлен")
        else:
            bot.reply_to(message, "Что-то пошло не так. Лица не найдены")
        user_stat[message.from_user.id][0] = Status.FREE
    elif user_stat[message.from_user.id][0] == Status.DEL_PR:
        if private_bd_del(message.from_user.id, message.text):
            bot.reply_to(message, "Человек успешно удален из вашей библиотеки.")
        else:
            bot.reply_to(message, "Что-то пошло не так. Человек не найден")
        user_stat[message.from_user.id][0] = Status.FREE

    elif message.text == "Распознать фото":
        handle_analize(message)
    elif message.text == "Добавить в глобальную базу":
        handle_add_public(message)
    elif message.text == "Добавить в локальную базу":
        handle_add(message)
    elif message.text == "Удалить из локальной базы":
        handle_del(message)
    else:
        bot.reply_to(message, "Произошла ошибка, возможно вы делаете что-то не так(")


bot.polling(none_stop=True)
