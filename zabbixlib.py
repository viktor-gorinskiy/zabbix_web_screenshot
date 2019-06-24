#!/usr/bin/python3.4
import requests
import json
import config

# Авторизация: получаем ключ пользователя (auth)
url = config.zabbix_url + '/api_jsonrpc.php'
headers = {'content-type': 'application/json-rpc'}
user_login_payload = json.dumps({
    "jsonrpc": "2.0",
    "method": "user.login",
    "params": {
        "user": config.zabbix_user,
        "password": config.zabbix_user_pasword
    },
    "id": 1
})
user_login_data = json.loads(requests.post(url, user_login_payload, headers=headers).text)
test = True
i= 0
# Проверка на ошибку авторизации и повторная авторизация
while "error" in user_login_data and test:
    print ("Была обнаружена ошибка авторизации")
    if i > 3:
        user_login_data = json.loads(requests.post(url, user_login_payload, headers=headers).text)
    else:
        test = False

auth = user_login_data['result']


def zabbix(**kwargs):
    payload = json.dumps({
        "jsonrpc": "2.0",
        "method": kwargs['method'],
        "params": kwargs['params'],
        "auth": auth,
        "id": 1
    })
    return json.loads(requests.post(url, payload, headers=headers).text)


