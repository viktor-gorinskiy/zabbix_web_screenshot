import telebot
#from telebot import apihelper
import main
import config
import cherrypy

WEBHOOK_HOST = '78.78.79.79' # Локальный ip адрес
WEBHOOK_PORT = 8443  # 443, 80, 88 или 8443 (порт должен быть открыт!)
WEBHOOK_LISTEN = '0.0.0.0'  # На некоторых серверах придется указывать такой же IP, что и выше
WEBHOOK_SSL_CERT = '/etc/zabbix/externalscripts/telegramm_confirm_problems/webhook_cert.pem'  # Путь к сертификату
WEBHOOK_SSL_PRIV = '/etc/zabbix/externalscripts/telegramm_confirm_problems/webhook_pkey.pem'  # Путь к приватному ключу
WEBHOOK_URL_BASE = "https://%s:%s" % (WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/%s/" % (config.token)


class WebhookServer(object):
    @cherrypy.expose
    def index(self):
        if 'content-length' in cherrypy.request.headers and \
                        'content-type' in cherrypy.request.headers and \
                        cherrypy.request.headers['content-type'] == 'application/json':
            length = int(cherrypy.request.headers['content-length'])
            json_string = cherrypy.request.body.read(length).decode("utf-8")
            update = telebot.types.Update.de_json(json_string)
            # Эта функция обеспечивает проверку входящего сообщения
            bot.process_new_updates([update])
            return ''
        else:
            raise cherrypy.HTTPError(403)


if config.proxy:
    apihelper.proxy = config.proxy

def valid_message(message):
    for slovo in config.valid_messages:
        if slovo in message.lower():
            return True


def get_language(lang_code):
    # Иногда language_code может быть None
    if not lang_code:
        return "ru"
    if "-" in lang_code:
        lang_code = lang_code.split("-")[0]
    if lang_code == "ru":
        return "ru"
    else:
        return "ru"

strings = {
    "ru": {
        "ro_msg": "Вам запрещено давать мне команды",
        "ro_what": "Нет никакого смысла писать мне сообщеня, я тупой бот.\n Ответьте на моё предыдущее сообщение c спроблемой, чтоб я понял, что необходимо сделать.",
        "ro_message": "Пожалуйста введите сообщение, в котором будет отражена суть Ваших действий.\n Другими словами, что мне надо сделать?"
    },
    "en": {
        "ro_msg": "You're not allowed to give me commands.",
        "ro_what": "There's no point in texting me, I'm a stupid bot.\nReply to my previous message, that I understood what needed to be done."
    }
}




bot = telebot.TeleBot(config.token)
@bot.message_handler(func=lambda message: message.reply_to_message is not None and message.reply_to_message.from_user.id == config.id_bot) # and message.chat.id == GROUP_ID)
def repeat_all_messages(message): # Название функции не играет никакой роли, в принципе
    print(message.reply_to_message.from_user.id)
    # bot.send_message(message.chat.id, message.text)
    message_string = str(message.text)
    str_data = message.json
    from_id = str_data['from']['id']
    # Поменяем юсернейм на юсершв, если первый пустой
    if str_data['from']['username']:
        from_username = str_data['from']['id']
    from_username = str_data['from']['username']
    print(from_id, ' ', from_username)
    # Проверяем юзера на валидность:
    if str(from_id) in config.valid_users:
        reply_to_message_text = str_data['reply_to_message']['text']
        # Проверяем на наличие проблемы в сообщении:
        if 'PROBLEM' in reply_to_message_text.split('\n')[0] and not 'RESOLVED' in reply_to_message_text.split('\n')[6]:
            event_id = reply_to_message_text.split('\n')[6].split(' ')[1]
            print('event_id ===>\t', event_id)
            print(message_string)
            if valid_message(message_string):
                message_string = message_string + '\nПользователь подтвердивший проблему: ' + str(from_username)
                result_confirmed = main.off_trigge(event_id, message_string)
                # Сообщение от API по умолчанию
                ok = 'unknown response API'
                # проверка, вдруг подтверждать нечего и API вернул error, тоесть заменяем сообщение по умолчанию на ответ из ошибки
                if result_confirmed.setdefault('error'):
                    ok = result_confirmed['error']['data']
                # Проверка, заменяем сообщение по умолчанию на результат ответа от  API
                if result_confirmed.setdefault('result'):
                    ok = 'confirmed event id:\t' + str(result_confirmed['result']['eventids'][0])
                # bot.send_message(message.chat.id, ok)
                bot.send_message(message.chat.id, ok, reply_to_message_id=message.message_id)
            else:
                bot.send_message(message.chat.id, strings.get(get_language(message.from_user.language_code)).get("ro_message"),
                         reply_to_message_id=message.message_id)


        else:
            bot.send_message(message.chat.id, strings.get(get_language(message.from_user.language_code)).get("ro_what"),
                         reply_to_message_id=message.message_id)
    else:
        bot.send_message(message.chat.id, strings.get(get_language(message.from_user.language_code)).get("ro_msg"),
                         reply_to_message_id=message.message_id)


# Снимаем вебхук перед повторной установкой (избавляет от некоторых проблем)
bot.remove_webhook()

 # Ставим заново вебхук
bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH,
                certificate=open(WEBHOOK_SSL_CERT, 'r'))

# Указываем настройки сервера CherryPy
cherrypy.config.update({
    'server.socket_host': WEBHOOK_LISTEN,
    'server.socket_port': WEBHOOK_PORT,
    'server.ssl_module': 'builtin',
    'server.ssl_certificate': WEBHOOK_SSL_CERT,
    'server.ssl_private_key': WEBHOOK_SSL_PRIV
})

 # Собственно, запуск!
cherrypy.quickstart(WebhookServer(), WEBHOOK_URL_PATH, {'/': {}})

