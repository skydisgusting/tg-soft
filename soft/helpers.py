# -*- coding: utf-8 -*-

import logging
import re
from configparser import ConfigParser
from datetime import datetime, timezone
import asyncio
import random
import os
import aiohttp
import pytz
from aiohttp_proxy import ProxyConnector, ProxyType
import python_socks
from colorama import Fore
import time
from .config import config

from telethon.tl.types import User, UserStatusOffline, UserStatusRecently, UserStatusLastWeek, UserStatusLastMonth, \
    UserStatusOnline

handler = logging.FileHandler(f"log/log-{time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime())}.txt", "w",
                              encoding="UTF-8")
logging.basicConfig(level=logging.INFO, format='%(message)s', handlers=[handler])
logging.getLogger('telethon').setLevel(logging.CRITICAL)
ansi_escape_8bit = re.compile(
    r'(?:\x1B[@-Z\\-_]|[\x80-\x9A\x9C-\x9F]|(?:\x1B\[|\x9B)[0-?]*[ -/]*[@-~])'
)


def get_sessions(directories: list):
    result = []
    for directory in ['Аккаунты']:
        sessions = os.listdir(os.path.join(directory))
        for file in sessions:
            if file.endswith('.session'):
                session = "".join(file.split('.')[:-1])
                result.append(f"{directory}/{session}")
    return result

def clear_console():
    command = 'clear'
    if os.name in ('nt', 'dos'):  # If Machine is running on Windows, use cls
        command = 'cls'
    os.system(command)

def days_since(timestamp_date):
    return (datetime.now() - datetime.fromtimestamp(timestamp_date)).days


async def sleep_randomly(thread):
    start_delay = config.general.start_delay
    t = random.uniform(float(start_delay[0]), float(start_delay[1]))
    if t:
        log(thread, f'Засыпаю на {round(t, 2)} секунд')
        await asyncio.sleep(t)
    log(thread, f'Поток запущен!')


def randomize(message: str):
    for _string in message.split('{'):
        _string = _string.split('}')
        for __string in _string:
            if '|' in __string:
                word = random.choice(__string.split('|'))
                message = message.replace('{' + __string + '}', word)
    return message


def get_message():
    with open('Тексты.txt', 'r', encoding='utf-8') as file:
        return file.read()


def log(thread, message):
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print(f"[{current_time}]: Поток #{thread}: {message}")
    try:
        logging.info(f"[{current_time}] Поток #{thread}: {ansi_escape_8bit.sub('', message)}")
    except:
        pass


async def check_connection(client, account):
    if not account.auto_reconnect:
        if not client.is_connected():
            for i in range(5):
                log(f'{account.phone_number}: Переподключение...')
                await client.connect()
                await asyncio.sleep(account.reconnect_timeout)
            if not client.is_connected():
                log(f'{account.phone_number}: Ошибка подключения!')
                return False
    return True


def exception_handler(func):
    async def wrapper(thread, *args, **kwargs):
        try:
            await func(thread, *args, **kwargs)
        except Exception as e:
            log(thread, f'Ошибка! {e}')

    return wrapper


def account_exception_handler(func):
    async def wrapper(thread, account, *args, **kwargs):
        try:
            await func(thread, account, *args, **kwargs)
        except ConnectionError as e:
            log(thread,
                f'Аккаунт {Fore.LIGHTGREEN_EX}{account.phone_number}{Fore.LIGHTWHITE_EX}: Ошибка подключения! {e}')
        except Exception as e:
            log(thread, f'Аккаунт {Fore.LIGHTGREEN_EX}{account.phone_number}{Fore.LIGHTWHITE_EX}: Ошибка! {e}')

    return wrapper


def get_accounts(directories=None):
    from .models import Account
    if directories is None:
        directories = ['Аккаунты']
    accounts = []
    sessions = get_sessions(directories)
    for session in sessions:
        account = Account(session)
        if account.data is None:
            continue
        accounts.append(account)
    return accounts


def get_users(directories=None):
    with open('users.txt', 'r', encoding='utf-8') as file:
        users = file.read().split('\n')
        return users


def delete_user_from_file(user, file: str):
    with open(file, 'r', encoding='utf-8') as f:
        users = f.read()
    with open(file, 'w', encoding='utf-8') as f:
        f.write(users.replace(user + '\n', '').replace(user, ''))


async def check_proxy(proxy):
    api = 'https://api64.ipify.org/'

    if proxy[0] == python_socks.ProxyType.SOCKS5:
        type = ProxyType.SOCKS5
    else:
        type = ProxyType.HTTP

    host = proxy[1]
    port = proxy[2]
    try:
        username = proxy[4]
        password = proxy[5]
    except IndexError:
        username = None
        password = None

    try:
        connector = ProxyConnector(proxy_type=type, host=host, port=port, username=username, password=password,
                                   rdns=True)
        async with aiohttp.ClientSession(connector=connector) as session:
            resp = await session.get(api)
            if resp.status == 200:
                return True
            else:
                return False
    except Exception as e:
        return False


async def user_filter(user: User, online_min=None, online_max=None, including_admins=False, including_bots=False):
    statuses = config.parser.statuses

    date = datetime(1, 1, 1, 0, 0)
    check_date = date.strftime('%H:%M:%S')
    if online_min or online_max != check_date[1:8]:
        if isinstance(user.status, UserStatusOffline):
            if datetime.utcnow().replace(tzinfo=timezone.utc) - user.status.was_online < online_max:
                if datetime.utcnow().replace(tzinfo=timezone.utc) - user.status.was_online > online_min:
                    return user
                else:
                    return None

    for status in statuses:
        if status is None:
            if user.status is None:
                break
        elif isinstance(user.status, status):
            break
    else:
        return None

    if user.bot and including_bots:
        return user

    elif user.bot:
        return None



    return user


def random_name(self):
    gender = random.choice(['Male', 'Female'])

    if gender == 'Male':
        with open(f'props/names/male_first_names.txt', mode='r', encoding='utf-8') as file:
            first_names = file.read().split('\n')
        with open(f'props/names/male_last_names.txt', mode='r', encoding='utf-8') as file:
            last_names = file.read().split('\n')

    elif gender == 'Female':
        with open(f'props/names/female_first_names.txt', mode='r', encoding='utf-8') as file:
            first_names = file.read().split('\n')
        with open(f'props/names/female_last_names.txt', mode='r', encoding='utf-8') as file:
            last_names = file.read().split('\n')

    first_name, last_name = random.choice(first_names), random.choice(last_names)
    return first_name, last_name, gender










