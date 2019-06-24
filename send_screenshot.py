#!/usr/bin/python3.4

import re, sys, os
from selenium import webdriver
import telebot
#from telebot import apihelper
import config, time

patch = '/etc/zabbix/externalscripts/telegramm_confirm_problems/'
try:
    mes = sys.argv[1]
    print('mes: ',mes)
except IndexError:
    exit(0)

try:
    url = re.findall(r'http[^ ]*', mes)[0]
    print('url: ',url)
except IndexError:
    exit(0)
    
#apihelper.proxy = config.proxy

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--window-size=1420,1080')
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
driver = webdriver.Chrome(chrome_options=chrome_options)

driver.get(url)
driver.implicitly_wait(20)
screenshot_name = patch + 'screenshot.png'
os.remove(screenshot_name)
driver.save_screenshot(screenshot_name)

driver.close()

screenshot = open(screenshot_name, 'rb')

bot = telebot.TeleBot(config.token)

#bot.send_message('-192029615', url)
bot.send_photo('-192029615', screenshot)


