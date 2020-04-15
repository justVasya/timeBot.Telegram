import telebot
from telebot import types
from datetime import datetime
import time
import re


choose_timer_type = types.ReplyKeyboardMarkup()
choose_timer_type.row(types.KeyboardButton("/указатьТаймер"), types.KeyboardButton("/указатьДату") ,)

manual_timer__affirm_or_cancel = types.InlineKeyboardMarkup()
manual_timer__affirm_or_cancel.row(types.InlineKeyboardButton(text="Подтвердить", callback_data="affirm"), types.InlineKeyboardButton(text="Отменить", callback_data="cancel"))


template_timer = types.InlineKeyboardMarkup()
plus_ten__button = types.InlineKeyboardButton(text="+10 мин", callback_data="plus_ten_minuts" )
plus_hour__button = types.InlineKeyboardButton(text="+1час", callback_data="plus_one_hour")
plus_day__button = types.InlineKeyboardButton(text="+1день", callback_data="plus_one_day")
choose_manually__button = types.InlineKeyboardButton(text="Указать самому", callback_data="choose_manually_date")
affirm__button = types.InlineKeyboardButton(text="Подтвердить", callback_data="affirm")
cancel__button = types.InlineKeyboardButton(text="Отменить", callback_data="cancel")
template_timer.row(plus_ten__button, plus_hour__button, plus_day__button)
template_timer.row(choose_manually__button, affirm__button, cancel__button)


total_timer = []

NUMOFTHREADS = 9

bot = telebot.TeleBot("Nope", threaded=True, num_threads=NUMOFTHREADS) #Bot ID
# botuser = bot.get_me() #Just info about bot in case of needs


def get_user_id(id,total_timer): #Get user id and set it in database
    x = 0
    for x in range(len(total_timer)): #Check if we have this id already
        if total_timer[x][0] == id:
            return x
    total_timer.append([id ,0 ,0 ,0, None]) #If not found, then add 0ID 1Minuts 2hours 3Days
    if x == 0: #Know, if we have blank total_timer, it would record to 0+1, but we have it on 0
        return x
    return x + 1

def set_timer(message):
    bot.send_message(message.chat.id, "Принято")
    sleep_for(get_user_id(message.chat.id, total_timer))
    bot.send_message(message.chat.id, "Время вышло!")
    bot.send_message(message.chat.id, "{}".format(message.text), reply_markup=choose_timer_type)


def sleep_for(user_index_in_array):
    global total_timer
    total_sec = int(total_timer[user_index_in_array][1])*60 + int(total_timer[user_index_in_array][2])*60*60 + int(total_timer[user_index_in_array][3])*60*60*24
    time.sleep(total_sec)


@bot.message_handler(commands=["start", "go"])
def start_message(message):
    bot.send_message(message.chat.id, "Я test-бот. Отправь сообщение для теста асинхронности.",reply_markup=choose_timer_type)
    bot.send_message(message.chat.id, "Всего потоков {}. Это значит, что бот может обрабатывать аж до {} таймеров одновременно".format(NUMOFTHREADS,NUMOFTHREADS))


@bot.message_handler(commands=["указатьТаймер"])
def start_message(message):
    global total_timer
    user_id = get_user_id(message.chat.id, total_timer)
    total_timer[user_id][1] = 0
    total_timer[user_id][2] = 0
    total_timer[user_id][3] = 0
    user_id = total_timer[user_id] #Setting this thing to easy use for next command.
    bot.send_message(message.chat.id, "Таймер будет установлен на {} минут | {} часов | {} дней".format(user_id[1],user_id[2],user_id[3]) ,reply_markup = template_timer)


@bot.message_handler(commands=["указатьДату"])
def start_message(message):
    bot.send_message(message.chat.id, "Реализовано (пока-что) не будет.")


# def check_if_time_is_eaqual(arg):
#     global total_timer
#     user_id = get_user_id(message.chat.id, total_timer)
#     regexp_of_numbers = re.findall("[0-9][0-9]:[0-9][0-9]", message.text)

# Пока-что реализовывать это я не буду. Надо иметь базу данных для такой херни
# Так что, подождём.



@bot.message_handler(regexp="[0-9]*[0-9]")
def start_message(message):
    global total_timer #Global use
    user_id = get_user_id(message.chat.id, total_timer)
    regexp_of_numbers = re.findall("[0-9]*[0-9]", message.text)

    if len(regexp_of_numbers) == 3:
        if (int(regexp_of_numbers[2]) > 2 or int(regexp_of_numbers[1]) > 48):
            bot.send_message(message.chat.id, "Не возможно поставить таймер больше чем на 2 дня!".format(regexp_of_numbers[0],regexp_of_numbers[1],regexp_of_numbers[2]), parse_mode='Markdown')

        else:
            total_timer[user_id][1] = regexp_of_numbers[0]
            total_timer[user_id][2] = regexp_of_numbers[1]
            total_timer[user_id][3] = regexp_of_numbers[2]
            bot.send_message(message.chat.id, "Поставить таймер на *{} минут*, *{} часов*, *{} дней* ?".format(regexp_of_numbers[0],regexp_of_numbers[1],regexp_of_numbers[2]), parse_mode='Markdown', reply_markup=manual_timer__affirm_or_cancel)

    else: bot.send_message(message.chat.id, "Введите именно 3 числа!")


# @bot.message_handler(commands=["Подтвердить"])
# def start_message(message):
#     msg = bot.send_message(message.chat.id, "Введите текст таймера:", reply_markup=choose_timer_type)
#     bot.register_next_step_handler(msg, set_timer)
#
#
# @bot.message_handler(commands=["Отменить"])
# def start_message(message):
#     global total_timer
#     user_id = get_user_id(message.chat.id, total_timer)
#     total_timer[user_id][1] = 0
#     total_timer[user_id][2] = 0
#     total_timer[user_id][3] = 0
#     bot.send_message(message.chat.id, "Отменено",reply_markup=choose_timer_type)



@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.message:
        global total_timer

        if call.data == "plus_one_hour" or call.data == "plus_ten_minuts" or call.data == "plus_one_day":
            user_id = get_user_id(call.message.chat.id, total_timer) #Used if because of last line of this IF

            if call.data == "plus_ten_minuts":
                if (total_timer[user_id][1] / 60) == 1 : #If we got 60 min (1 hour)
                    total_timer[user_id][1] = 0 #Zero minuts
                    total_timer[user_id][2] += 1 #Ad hours
                    bot.answer_callback_query(callback_query_id=call.id, text='Hello world')
                else:
                    total_timer[user_id][1] += 10

            if call.data == "plus_one_hour":
                if (total_timer[user_id][2] / 24) == 1 :
                    total_timer[user_id][2] = 0
                    if (total_timer[user_id][3] + 1) == 3:
                        return
                    else: total_timer[user_id][3] += 1
                else:
                    total_timer[user_id][2] += 1

            if call.data == "plus_one_day":
                if total_timer[user_id][3] >= 2 :
                    return
                else:
                    total_timer[user_id][3] += 1
            user_id = total_timer[user_id]
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Таймер будет установлен на {} минут | {} часов | {} дней(не больше двух)".format(user_id[1],user_id[2],user_id[3]),reply_markup = template_timer)

        if call.data == "choose_manually_date":
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_message(call.message.chat.id, "Хорошо, отправьте сообщение следущего вида: x минут, x часов, x дней \nЕсли какое либо значение вам не нужно, то используйте 0")

        if call.data == "affirm":
            msg = bot.send_message(call.message.chat.id, "Введите текст таймера:", reply_markup=choose_timer_type)
            bot.register_next_step_handler(msg, set_timer)

        if call.data == "cancel":
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_message(call.message.chat.id, "Отменено")



bot.polling()
