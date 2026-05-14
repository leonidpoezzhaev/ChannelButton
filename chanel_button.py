import telebot
from telebot import types
import time
import sqlite3

bot = telebot.TeleBot('TOKEN')
chanel = '-1003480826321'

@bot.message_handler(commands=['start'])
def start(message):
    if message.chat.type == 'private':
        conn = sqlite3.connect('chanels.db')
        cur = conn.cursor()
        cur.execute('SELECT user_id FROM users WHERE user_id = ?', (message.chat.id,))
        if cur.fetchone() == None:
            cur.execute("INSERT INTO users (user_id, premium) VALUES ('%s', '%s')" % (message.chat.id, False))
        conn.commit()
        cur.close()
        conn.close()
        bot.send_message(message.chat.id, 'Добро пожаловать в бота!')
        markup = types.InlineKeyboardMarkup()
        markup1 = types.InlineKeyboardButton('📰Подписаться на канал', url='https://t.me/lupikprojects')
        markup2 = types.InlineKeyboardButton('✅Проверить подписку', callback_data='subscription')
        markup.add(markup1).row(markup2)
        bot.send_message(message.chat.id, 'Для использования бота необходимо быть подписанным на канал.',
                         reply_markup=markup)

@bot.message_handler(commands=['give_premium'])
def premium(message):
    if str(message.chat.id) == '847720158':
        conn = sqlite3.connect('chanels.db')
        cur = conn.cursor()
        cur.execute('SELECT user_id FROM users')
        for i in cur.fetchall():
            if bot.get_chat(i).username == message.text.split()[1]:
                cur.execute('UPDATE users SET premium = ? WHERE user_id = ?', ('True', i[0]))
                bot.send_message(message.chat.id, f'Пользователь: <a href="t.me/{bot.get_chat(i).username}">{bot.get_chat(i).username}</a>\n'
                                                  f'Айди: <code>{i[0]}</code>\n\n'
                                                  f'✅Премиум доставлен', parse_mode='HTML', disable_web_page_preview=True)
                break
        conn.commit()
        cur.close()
        conn.close()
    else:
        bot.send_message(message.chat.id, 'ну почти)')

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.message:
        if call.data == 'subscription':
            chat_member = bot.get_chat_member(chanel, call.message.chat.id)
            if chat_member.status in ['member', 'creator']:
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                button1 = types.KeyboardButton('🔔Новый пост')
                button2 = types.KeyboardButton('❓Инструкция')
                button3 = types.KeyboardButton('⚙️Настроить каналы')
                button4 = types.KeyboardButton('⭐️Premium')
                markup.add(button1).row(button2, button3).row(button4)
                bot.delete_message(call.message.chat.id, call.message.message_id)
                bot.send_message(call.message.chat.id, 'Спасибо за подписку!', reply_markup=markup)
            else:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                      text='Вы не подписались')
                time.sleep(1)
                markup = types.InlineKeyboardMarkup()
                markup1 = types.InlineKeyboardButton('📰Подписаться на канал', url='https://t.me/lupikprojects')
                markup2 = types.InlineKeyboardButton('✅Проверить подписку', callback_data='subscription')
                markup.add(markup1).row(markup2)
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                      text='Для использования бота необходимо быть подписанным на канал.',
                                      reply_markup=markup)

        elif call.data == 'close':
            bot.delete_message(call.message.chat.id, call.message.message_id)

        elif call.data == 'add_chanel':
            msg = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text='Перешлите сообщение из вашего канала.')
            bot.register_next_step_handler(msg, take_message)

        elif call.data == 'delete_chanel':
            conn = sqlite3.connect('chanels.db')
            cur = conn.cursor()
            cur.execute('SELECT chanels FROM users WHERE user_id = ?', (call.message.chat.id,))
            channels = cur.fetchone()
            cur.close()
            conn.close()

            f = ''
            num = 1
            for i in str(channels[0]).split(';'):
                f += f'{num}. {str(bot.get_chat(int(i)).title)}\n'
                num += 1

            num -= 1
            markup = types.InlineKeyboardMarkup(row_width=3)
            for i in range(1,num+1):
                markup.add(types.InlineKeyboardButton(f'{i}', callback_data=f'{i}'))
            markup.add(types.InlineKeyboardButton('❎Закрыть меню', callback_data='close'))

            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text=f'Выберите канал, который хотите удалить:\n{f}', reply_markup=markup)

        elif call.data in ['1','2','3','4','5','6','7','8','9','10']:
            conn = sqlite3.connect('chanels.db')
            cur = conn.cursor()
            cur.execute('SELECT chanels FROM users WHERE user_id = ?', (call.message.chat.id,))
            channels = cur.fetchone()
            channels = channels[0].split(';')
            del channels[int(call.data)-1]
            f = channels[0]
            for i in channels[1:]:
                f += ';'+i
            cur.execute('UPDATE users SET chanels = ? WHERE user_id = ?', (f,call.message.chat.id))
            conn.commit()
            cur.close()
            conn.close()

            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                  text=f'Канал успешно удален.')

        elif call.data in ['1_post', '2_post', '3_post', '4_post', '5_post', '9_post']:
            num = int(call.data[0])-1
            msg = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text='Введите ваше сообщение.\n\n')
            bot.register_next_step_handler(msg, take_button, num)

        elif call.data == 'need_premium':
            markup = types.InlineKeyboardMarkup(row_width=1)
            button1 = types.InlineKeyboardButton('⭐️Premium', callback_data='plus_premium')
            button2 = types.InlineKeyboardButton('❎Закрыть меню', callback_data='close')
            markup.add(button1,button2)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text='Вы достигли лимита бесплатных каналов.\n'
                                                                                                 'Замените какой-то канал на новый, либо купите Premium.', reply_markup=markup)
        elif call.data == 'need_premium2':
            markup = types.InlineKeyboardMarkup(row_width=1)
            button1 = types.InlineKeyboardButton('⭐️Premium', callback_data='plus_premium')
            button2 = types.InlineKeyboardButton('❎Закрыть меню', callback_data='close')
            markup.add(button1,button2)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text='Отправлять сообщения во все каналы сразу доступно с подпиской Premium.\n'
                                                                                                 'Отправьте сообщение в каждый канал вручную или купите подписку.', reply_markup=markup)

        elif call.data == 'plus_premium':
            conn = sqlite3.connect('chanels.db')
            cur = conn.cursor()
            cur.execute('SELECT premium FROM users WHERE user_id = ?', (call.message.chat.id,))
            status = cur.fetchone()[0]
            cur.close()
            conn.close()
            markup = types.InlineKeyboardMarkup(row_width=1)
            button1 = types.InlineKeyboardButton('💰Купить Premium', callback_data='buy')
            button2 = types.InlineKeyboardButton('❎Закрыть меню', callback_data='close')
            if status == 'True':
                status = 'есть Premium'
                markup.add(button2)
            else:
                status = 'нет Premium'
                markup.add(button1, button2)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                  text='<b>⭐️Premium</b>\n\n'
                                       'Что вы получаете?\n'
                                       '- Добавление до 5 каналов.\n'
                                       '- Публикация постов сразу во все каналы.\n'
                                       '- Спасибо от создателя.\n\n'
                                       'Цена:\n'
                                       'Цена за подписку - 200 рублей.\n'
                                       'Подписка покупается навсегда.\n\n'
                                       f'Ваш статус: {status}', parse_mode='HTML', reply_markup=markup)

        elif call.data == 'buy':
            markup = types.InlineKeyboardMarkup(row_width=1)
            button1 = types.InlineKeyboardButton('💳Оплата', url='https://www.tbank.ru/payment-url')
            button2 = types.InlineKeyboardButton('❎Закрыть меню', callback_data='close')
            markup.add(button1,button2)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text='Проверка оплата и выдача статуса происходит в ручном формате, так что заранее извиняюсь за задержки.\n'
                                                                                                 'Указывайте, пожалуйста, свой id телеграмма в комментарии, чтобы я смог вас найти.\n'
                                                                                                 'Оплатить можно по кнопке ниже:',reply_markup=markup)

@bot.message_handler(content_types=['text'])
def bot_message(message):
    if message.chat.type == 'private':
        if bot.get_chat_member(chanel, message.chat.id).status in ['member', 'creator']:
            if message.text == '⚙️Настроить каналы':
                conn = sqlite3.connect('chanels.db')
                cur = conn.cursor()
                cur.execute('SELECT chanels, premium FROM users WHERE user_id = ?', (message.chat.id,))
                channels = cur.fetchone()
                cur.close()
                conn.close()
                markup = types.InlineKeyboardMarkup(row_width=1)

                if channels[1] == 'False' and len(channels[0].split(';')) == 3:
                    button1 = types.InlineKeyboardButton('⭐️Добавить канал', callback_data='need_premium')
                else:
                    button1 = types.InlineKeyboardButton('🆕Добавить канал', callback_data='add_chanel')
                button2 = types.InlineKeyboardButton('🗑Удалить канал', callback_data='delete_chanel')

                if channels[0] == None or channels[0] == '':
                    markup.add(button1)
                    bot.send_message(message.chat.id, 'Вы не добавили не одного канала.', reply_markup=markup)
                else:
                    f = ''
                    num = 1
                    for i in str(channels[0]).split(';'):
                        f += f'{num}. {str(bot.get_chat(int(i)).title)}\n'
                        num += 1
                    if len(channels[0].split(';')) < 5:
                        markup.add(button1, button2)
                    else:
                        markup.add(button2)
                    bot.send_message(message.chat.id, f'Ваши каналы:\n{f}', reply_markup=markup)

            elif message.text == '🔔Новый пост':
                conn = sqlite3.connect('chanels.db')
                cur = conn.cursor()
                cur.execute('SELECT chanels, premium FROM users WHERE user_id = ?', (message.chat.id,))
                channels = cur.fetchone()
                cur.close()
                conn.close()
                if channels[0] in [None, '']:
                    bot.send_message(message.chat.id, 'Вы не добавили не одного канала.')
                else:
                    f = ''
                    num = 1
                    for i in str(channels[0]).split(';'):
                        f += f'{num}. {str(bot.get_chat(int(i)).title)}\n'
                        num += 1
                    num -= 1
                    markup = types.InlineKeyboardMarkup(row_width=3)
                    for i in range(1, num + 1):
                        markup.add(types.InlineKeyboardButton(f'{i}', callback_data=f'{i}_post'))
                    if channels[1] == 'True':
                        markup.add(types.InlineKeyboardButton('👨‍👩‍👦Выбрать все', callback_data='9_post'))
                    else:
                        markup.add(types.InlineKeyboardButton('⭐️Выбрать все', callback_data='need_premium2'))

                    bot.send_message(message.chat.id, f'Выберите канал:\n{f}', reply_markup=markup)

            elif message.text == '⭐️Premium':
                conn = sqlite3.connect('chanels.db')
                cur = conn.cursor()
                cur.execute('SELECT premium FROM users WHERE user_id = ?', (message.chat.id,))
                status = cur.fetchone()[0]
                cur.close()
                conn.close()
                markup = types.InlineKeyboardMarkup(row_width=1)

                if status == 'True':
                    status = 'есть Premium'
                    button2 = types.InlineKeyboardButton('❎Закрыть меню', callback_data='close')
                    markup.add(button2)
                else:
                    status = 'нет Premium'
                    button1 = types.InlineKeyboardButton('💰Купить Premium', callback_data='buy')
                    button2 = types.InlineKeyboardButton('❎Закрыть меню', callback_data='close')
                    markup.add(button1, button2)

                bot.send_message(message.chat.id, '<b>⭐️Premium</b>\n\n'
                                           'Что вы получаете?\n'
                                            '- Добавление до 5 каналов.\n'
                                            '- Публикация постов сразу во все каналы.\n'
                                            '- Спасибо от создателя.\n\n'
                                            'Цена:\n'
                                           'Цена за подписку - 200 рублей.\n'
                                           'Подписка покупается навсегда.\n\n'
                                           f'Ваш статус: {status}', parse_mode='HTML', reply_markup=markup)

            elif message.text == '❓Инструкция':
                markup = types.InlineKeyboardMarkup(row_width=1)
                button1 = types.InlineKeyboardButton('⭐️Premium', callback_data='plus_premium')
                button2 = types.InlineKeyboardButton('❎Закрыть меню', callback_data='close')
                markup.add(button1, button2)
                bot.send_message(message.chat.id, '❓Инструкция\n\n'
                                                  'Что делает этот бот?\n'
                                                  'Данный бот позволяет отправлять сообщение в канал, прикрепляя к нему кнопку с ссылкой.\n\n'
                                                  'Инструкция по пользованию:\n'
                                                  '1. Добавьте ваш канал через кнопку "⚙️Настроить каналы".\n'
                                                  '2. Нажмите кнопку "🔔Новый пост" и выберите ваш канал.\n'
                                                  '3. Напишите текст для вашего сообщения в канал.\n'
                                                  '4. Напишите текст, который далее будет отображен в кнопке, а также ссылку, куда кнопка будет вести.\n\n'
                                                  'Бесплатная версия позволяет добавлять до 3-ех каналов за раз, но подписка Premium дает дополнительные возможности, подробности кнопкой ниже.', reply_markup=markup)
        else:
            markup = types.InlineKeyboardMarkup()
            markup1 = types.InlineKeyboardButton('📰Подписаться на канал', url='https://t.me/lupikprojects')
            markup2 = types.InlineKeyboardButton('✅Проверить подписку', callback_data='subscription')
            markup.add(markup1).row(markup2)
            bot.send_message(message.chat.id, 'Для использования бота необходимо быть подписанным на канал.',
                             reply_markup=markup)

def dobavil(message, id_channel):
    if message.text == '🆒Добавил':
        try:
            sms = bot.send_message(id_channel, message.text, disable_notification=True)
            bot.delete_message(sms.chat.id, sms.message_id)
            conn = sqlite3.connect('chanels.db')
            cur = conn.cursor()
            cur.execute('SELECT chanels FROM users WHERE user_id = ?', (message.chat.id,))
            old_chanels = cur.fetchone()[0]
            if old_chanels != None and old_chanels != '':
                cur.execute('UPDATE users SET chanels = ? WHERE user_id = ?',((str(old_chanels)+';'+str(id_channel)),message.chat.id))
            else:
                cur.execute('UPDATE users SET chanels = ? WHERE user_id = ?',(str(id_channel), message.chat.id))
            conn.commit()
            cur.close()
            conn.close()

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            button1 = types.KeyboardButton('🔔Новый пост')
            button2 = types.KeyboardButton('❓Инструкция')
            button3 = types.KeyboardButton('⚙️Настроить каналы')
            button4 = types.KeyboardButton('⭐️Premium')
            markup.add(button1).row(button2, button3).row(button4)
            bot.send_message(message.chat.id,'Успешно.', reply_markup=markup)

        except telebot.apihelper.ApiTelegramException:
            msg = bot.send_message(message.chat.id,'Ошибка. Добавьте меня в канал и разрешите сообщения')
            bot.register_next_step_handler(msg, dobavil, id_channel)

    elif message.text == '↩️Отмена':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button1 = types.KeyboardButton('🔔Новый пост')
        button2 = types.KeyboardButton('❓Инструкция')
        button3 = types.KeyboardButton('⚙️Настроить каналы')
        button4 = types.KeyboardButton('⭐️Premium')
        markup.add(button1).row(button2, button3).row(button4)
        bot.send_message(message.chat.id, 'Отмена.', reply_markup=markup)

def take_message(message):
    if message.text == '↩️Отмена':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button1 = types.KeyboardButton('🔔Новый пост')
        button2 = types.KeyboardButton('❓Инструкция')
        button3 = types.KeyboardButton('⚙️Настроить каналы')
        button4 = types.KeyboardButton('⭐️Premium')
        markup.add(button1).row(button2, button3).row(button4)
        bot.send_message(message.chat.id, 'Отмена.', reply_markup=markup)
    else:
        try:
            id_channel = message.forward_origin.chat.id
            chat = bot.get_chat(id_channel)

            conn = sqlite3.connect('chanels.db')
            cur = conn.cursor()
            cur.execute('SELECT chanels FROM users WHERE user_id = ?', (message.chat.id,))
            channels = cur.fetchone()
            cur.close()
            conn.close()

            if (channels[0] != None) and (str(id_channel) in str(channels[0])):
                bot.send_message(message.chat.id, 'Такой канал уже добавлен.')
            else:
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                button1 = types.KeyboardButton('🆒Добавил')
                button2 = types.KeyboardButton('↩️Отмена')
                markup.add(button1,button2)

                msg = bot.send_message(message.chat.id, f'Имя вашего канала: {chat.title}\n'
                                                  f'Теперь добавьте меня в канал и разрешите отправку сообщений.', parse_mode='HTML', reply_markup=markup)

                bot.register_next_step_handler(msg, dobavil, id_channel)
        except AttributeError:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(types.KeyboardButton('↩️Отмена'))
            msg = bot.send_message(message.chat.id, 'Перешлите сообщение из канала.', reply_markup=markup)
            bot.register_next_step_handler(msg, take_message)

def take_button(message, num):
    text = message.text
    msg = bot.send_message(message.chat.id,'Введите название кнопки и ссылку через "<code>~</code>":\n\n'
                                           'Пример: крутая кнопка<code>~</code>t.mе', parse_mode='HTML')
    bot.register_next_step_handler(msg,take_post, num, text)

def take_post(message, num, text):
        try:
            conn = sqlite3.connect('chanels.db')
            cur = conn.cursor()
            cur.execute('SELECT chanels FROM users WHERE user_id = ?', (message.chat.id,))
            channels = cur.fetchone()
            cur.close()
            conn.close()
            button = message.text.split('~')
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton(f'{button[0]}', url=f'{button[1]}'))
            channels = channels[0].split(';')
            if num in [0,1,2,3,4,5]:
                bot.send_message(channels[num], text, reply_markup=markup, parse_mode='HTML')
            else:
                for i in channels:
                    bot.send_message(i, text,reply_markup=markup)
            bot.send_message(message.chat.id, 'Сообщение отправлено!')
        except telebot.apihelper.ApiTelegramException, IndexError:
            msg = bot.send_message(message.chat.id, 'Введите корректную ссылку.')
            bot.register_next_step_handler(msg, take_post, num, text)

bot.polling(none_stop=True)