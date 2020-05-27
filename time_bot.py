import re
from time import sleep
import telebot
from keyboards_markup import choose_timer_type, \
                                manual_timer__affirm_or_cancel, template_timer

USER_DATA = []
NUMOFTHREADS = 9
TOKEN = "Your token goes here"

bot = telebot.TeleBot(TOKEN,
                      threaded=True,
                      num_threads=NUMOFTHREADS)  # Bot ID


def get_user_id(user_id, user_data_):  # Get user id and set it in database
    """This function tries to find user, and if fails, creates new one"""
    for index, user_data in enumerate(user_data_):
        # Check if we have this id already
        if user_id in user_data:
            return index
    # And if we did not find any, create new one.
    USER_DATA.append([user_id, 0, 0, 0])
    # ID - Minuts - Hours - Days
    return get_user_id(user_id, USER_DATA)


def set_timer(message):
    """This is shell for 'sleep_for' function."""
    bot.send_message(message.chat.id, "Принято")
    sleep_for(get_user_id(message.chat.id, USER_DATA))
    bot.send_message(message.chat.id, "Время вышло!")
    bot.send_message(message.chat.id, "{}".format(message.text),
                     reply_markup=choose_timer_type)


def sleep_for(user_index):
    """Name of this function speaks for itself"""
    global USER_DATA
    total_sec = int(USER_DATA[user_index][1])*60 + \
                int(USER_DATA[user_index][2])*60*60 + \
                int(USER_DATA[user_index][3])*60*60*24
    sleep(total_sec)


@bot.message_handler(commands=["start", "go"])
def start_message(message):
    """"""
    bot.send_message(message.chat.id, "Привет. Я просто таймер-бот. "
                     "Ничего более.", reply_markup=choose_timer_type)
    bot.send_message(message.chat.id, "Всего потоков {}. Это значит, что бот "
                                      "может обрабатывать аж до {} "
                                      "таймеров одновременно".format(
                                          NUMOFTHREADS, NUMOFTHREADS))
    # Not sure if this code style is OK .-.


@bot.message_handler(commands=["указатьТаймер"])
def init_timer(message):
    """"""
    global USER_DATA
    user_id = get_user_id(message.chat.id, USER_DATA)

    for index in range(1, 4):
        # Making empty time variable for next use
        USER_DATA[user_id][index] = 0

    user_id = USER_DATA[user_id]
    # Setting this thing to easy use for next command.
    bot.send_message(message.chat.id,
                     "Таймер будет установлен на {} минут | {} часов"
                     "| {} дней".format(user_id[1], user_id[2], user_id[3]),
                     reply_markup=template_timer)


@bot.message_handler(commands=["указатьДату"])
def init_calendar_date(message):
    """"""
    bot.send_message(message.chat.id, "Реализовано (пока-что) не будет.")


@bot.message_handler(regexp="[0-9]*[0-9]")
def init_regexp(message):
    """"""
    global USER_DATA  # Global use
    user_id = get_user_id(message.chat.id, USER_DATA)
    regexp_of_numbers = re.findall("[0-9]*[0-9]", message.text)

    if len(regexp_of_numbers) == 3:
        if (int(regexp_of_numbers[2]) > 2 or int(regexp_of_numbers[1]) > 48):
            bot.send_message(message.chat.id, "Не возможно поставить таймер"
                             "больше чем на 2 дня!", parse_mode='Markdown')
        else:
            USER_DATA[user_id][1] = regexp_of_numbers[0]
            USER_DATA[user_id][2] = regexp_of_numbers[1]
            USER_DATA[user_id][3] = regexp_of_numbers[2]
            bot.send_message(message.chat.id, "Поставить таймер на *{} минут*,"
                             " *{} часов*, *{} дней* ?".format(
                                 regexp_of_numbers[0],
                                 regexp_of_numbers[1],
                                 regexp_of_numbers[2]),
                             parse_mode='Markdown',
                             reply_markup=manual_timer__affirm_or_cancel)
    else:
        bot.send_message(message.chat.id, "Введите именно 3 числа!")


@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    """"""
    if call.message:
        global USER_DATA
        user_id = get_user_id(call.message.chat.id, USER_DATA)

        if call.data == "plus_one_hour" or \
           call.data == "plus_ten_minuts" or \
           call.data == "plus_one_day":

            if call.data == "plus_ten_minuts":
                if (USER_DATA[user_id][1] / 60) == 1:
                    USER_DATA[user_id][1] = 0
                    USER_DATA[user_id][2] += 1
                else:
                    USER_DATA[user_id][1] += 10

            if call.data == "plus_one_hour":
                if (USER_DATA[user_id][2] / 24) == 1:
                    USER_DATA[user_id][2] = 0
                    if (USER_DATA[user_id][3] + 1) == 3:
                        return
                    else:
                        USER_DATA[user_id][3] += 1
                else:
                    USER_DATA[user_id][2] += 1

            if call.data == "plus_one_day":
                if USER_DATA[user_id][3] >= 2:
                    return
                else:
                    USER_DATA[user_id][3] += 1

            user_id = USER_DATA[user_id]
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  text="Таймер будет установлен на {} минут |"
                                  " {} часов | {} дней(не больше двух)".format(
                                      user_id[1],
                                      user_id[2],
                                      user_id[3]),
                                  reply_markup=template_timer)

        if call.data == "choose_manually_date":
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_message(call.message.chat.id,
                             "Хорошо, отправьте сообщение следущего "
                             "вида: x минут, x часов, x дней \n"
                             "Если какое либо значение вам не нужно, то"
                             " используйте 0")

        if call.data == "affirm":
            msg = bot.send_message(call.message.chat.id,
                                   "Введите текст таймера:",
                                   reply_markup=choose_timer_type)
            bot.register_next_step_handler(msg, set_timer)

        if call.data == "cancel":
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_message(call.message.chat.id, "Отменено")


bot.polling()
