from telebot import types

choose_manually = types.InlineKeyboardButton(text="Указать самому",
                                             callback_data="choose_manually_date")
affirm = types.InlineKeyboardButton(text="Подтвердить",
                                    callback_data="affirm")
cancel = types.InlineKeyboardButton(text="Отменить",
                                    callback_data="cancel")

plus_ten = types.InlineKeyboardButton(text="+10 мин",
                                      callback_data="plus_ten_minuts")
plus_hour = types.InlineKeyboardButton(text="+1час",
                                       callback_data="plus_one_hour")
plus_day = types.InlineKeyboardButton(text="+1день",
                                      callback_data="plus_one_day")

choose_timer_type = types.ReplyKeyboardMarkup()
choose_timer_type.row(types.KeyboardButton("/указатьТаймер"),
                      types.KeyboardButton("/указатьДату"))

manual_timer__affirm_or_cancel = types.InlineKeyboardMarkup()
manual_timer__affirm_or_cancel.row(affirm, cancel)

template_timer = types.InlineKeyboardMarkup()
template_timer.row(plus_ten, plus_hour, plus_day)
template_timer.row(choose_manually, affirm, cancel)
