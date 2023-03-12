import telebot
from config import keys, TOKEN
from extensions import APIException, CryptoConverter, DeclensionByCases

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def start(message):
    text = f'Приветствую, {message.from_user.first_name}! \n\nМеня зовут Конвертик, и я могу:' \
           f'\n- перевести Вашу валюту через команду <имя валюты> <в какую валюту перевести> ' \
           f'<количество переводимой валюты> (через пробелы).' \
           f'\nНапример: рубль евро 1\n' \
           f'\n- показать валюты, которые Вы можете конвертировать через команду \n/values;' \
           f'\n- напомнить, что я могу через команду \n/help.'
    bot.send_message(message.chat.id, text)


# Обрабатываеи команду help:
@bot.message_handler(commands=['help'])
def help(message: telebot.types.Message):
    text = 'Чтобы перевести валюту, напишите мне команду следующим образом:' \
           '\n<имя валюты> <в какую валюту перевести> <количество переводимой валюты> через пробелы.' \
           '\nНапример: рубль евро 1\n' \
           '\nЧтобы увидеть валюты, которые я смогу конвертировать, введите команду\n/values'
    bot.reply_to(message, text)


@bot.message_handler(commands=['values'])
def values(message: telebot.types.Message):
    text = 'Я умею переводить:'
    for key in keys.keys():
        text = '\n'.join((text, key,))
    bot.reply_to(message, text)


@bot.message_handler(content_types=['text', ])
def get_price(message: telebot.types.Message):
    try:
        values = message.text.lower().split(' ')

        if len(values) != 3:
            raise APIException('\nКоличество параметров не совпадает!\n'
                                      '\nПишите, пожалуйста, только так:\n<имя валюты> ' \
                                      '<в какую валюту перевести> <количество переводимой валюты> через пробелы'
                                      '\nИначе я Вас не понимаю :(')

        quote, base, amount = values
        total_base = CryptoConverter.get_price(quote, base, amount)
    except APIException as e:
        bot.reply_to(message, f'Вы что-то не так написали:\n{e}')
    except Exception as e:
        bot.reply_to(message, f'Что-то пошло не так :(\n\n{e}\n'
                              f'\nНо это не Ваша вина, так сошлись звёзды в глобальном пространстве.')
    else:
        inclined_quote = DeclensionByCases(quote, float(amount))
        inclined_base = DeclensionByCases(base, float(total_base))
        quote = inclined_quote.incline()
        base = inclined_base.incline()
        text = f'{amount} {quote} = {round(total_base, 5)} {base}'
        bot.send_message(message.chat.id, text)


bot.polling()
