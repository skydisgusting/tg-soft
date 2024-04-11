import asyncio
from datetime import datetime
import os
import re
import time
from abc import ABC, abstractmethod
from asyncio import CancelledError, Task
import aiohttp
from telethon import TelegramClient, events
from dataclasses import dataclass
from configparser import ConfigParser
from colorama import Fore
import python_socks
import random

from telethon.tl.functions.messages import CheckChatInviteRequest, ImportChatInviteRequest
from telethon.tl.types import ChatInviteAlready, ChatInvite
from typing import List, Union

from . import async_google_trans_new
import json

from telethon.errors import UserDeactivatedBanError, ChatTitleEmptyError, UserRestrictedError, PeerFloodError, \
    FloodWaitError, YouBlockedUserError, UserDeactivatedError, AuthKeyUnregisteredError, SessionRevokedError, \
    AuthKeyDuplicatedError, InvalidBufferError
from telethon.tl.functions.channels import CreateChannelRequest, JoinChannelRequest

from . import helpers
from .config import config
from .exceptions import SoftError, handler
from .helpers import log, sleep_randomly, check_connection, exception_handler

translator = async_google_trans_new.AsyncTranslator()


class Stack:
    def __init__(self, items: list = None, file_name: str = None):
        if items is None:
            self.items = []
        elif isinstance(items, list):
            self.items = items
        else:
            raise TypeError(f'Items of a {self.__class__.__name__} must be a list')
        self.file_name = file_name

    def __getitem__(self, item):
        return self.items[item]

    def __setitem__(self, key, value):
        self.items[key] = value

    def is_empty(self):
        return self.items == []

    def push(self, item):
        if item not in self.items:
            self.items.append(item)
        self.append(item)

    def pop(self):
        if self.items:
            item = self.items.pop()
            self.rewrite()
            return item

    def peek(self):
        item = self.items[len(self.items) - 1]
        return item

    def size(self):
        return len(self.items)

    def rewrite(self):
        if self.file_name:
            with open(self.file_name, 'w') as file:
                file.write("\n".join(self.items))

    def append(self, item):
        if self.file_name:
            with open(self.file_name, 'a') as file:
                file.write(item + "\n")


class MultiStack(Stack):
    def __init__(self, count: int, items: list = None, file_name: str = None):
        super().__init__(items, file_name)
        self.count = count

    def push(self, items: list):
        for item in items:
            if item not in self.items:
                self.items.append(item)
        self.rewrite()

    def pop(self, one_only=False):
        if one_only:
            return super().pop()
        result = []
        for i in range(self.count):
            if not self.is_empty():
                result.append(self.items.pop())
        self.rewrite()
        return result


class Stats:
    def __init__(self):
        self.success = 0
        self.failed = 0
        self.total = 0
        self.done = False

    def __str__(self):
        return f'Stats(success={self.success}, failed={self.failed}, total={self.total})'


@dataclass
class FinalReportCounter:
    total: int = 0
    total_checked: int = 0
    total_spamblock: int = 0

    def __str__(self):
        return f"Всего аккаунтов: {Fore.LIGHTMAGENTA_EX}{self.total}{Fore.LIGHTWHITE_EX}, Всего проверено: {Fore.LIGHTMAGENTA_EX}{self.total_checked}{Fore.LIGHTWHITE_EX}, Спамблок: {Fore.LIGHTMAGENTA_EX}{self.total_spamblock}{Fore.LIGHTWHITE_EX}."


@dataclass
class Status:
    status: str
    time: str = None


class Account:
    def __init__(self, session, status=None):
        self.i = 0
        self.session = session
        self.phone_number = self.session.split('/')[1]
        self.status = status
        self.load_data()
        self._client = None
        self.thread = None
        self.advanced_log = True

    @property
    def client(self):
        if self._client is None:
            self._client = self._get_client()
        return self._client

    def load_data(self):
        self.data = self._get_data()
        if self.data is None:
            return
        if self.data.get('twoFA'):
            self.password = self.data['twoFA']
        elif self.data.get('password'):
            self.password = self.data['password']
        elif self.data.get('password_str'):
            self.password = self.data['password_str']
        else:
            self.password = None

    def _get_data(self):
        try:
            with open(f'{self.session}.json', 'r', encoding='utf-8') as file:
                return json.load(file)
        except FileNotFoundError:
            print(
                f'Аккаунт {Fore.LIGHTWHITE_EX}{self.phone_number}{Fore.LIGHTWHITE_EX}: {Fore.RED}Аккаунт не найден!{Fore.LIGHTWHITE_EX}')
            return None

    def _get_client(self):
        self.proxy = self.get_proxy()
        self.auto_reconnect = config.general.auto_reconnect
        self.reconnect_timeout = config.general.reconnect_timeout

        client = TelegramClient(session=self.session,
                                api_id=self.data['app_id'],
                                api_hash=self.data['app_hash'],
                                system_version=self.data['sdk'],
                                app_version=self.data['app_version'],
                                device_model=self.data['device'],
                                lang_code=self.data['lang_pack'],
                                proxy=self.proxy,
                                connection_retries=5,
                                request_retries=5,
                                retry_delay=1,
                                system_lang_code=self.data['system_lang_pack'],
                                auto_reconnect=self.auto_reconnect,
                                timeout=self.reconnect_timeout,
                                receive_updates=False
                                )

        return client

    @staticmethod
    def get_proxy():
        with open(f'proxies.txt') as file:
            proxy_list = file.read().split('\n')
            chosen_proxy = random.choice(proxy_list)
            proxy_type = config.general.proxy_type
            if proxy_type.lower() == 'socks5':
                proxy = chosen_proxy.split(':')
                if len(proxy) == 2:
                    ip = proxy[0]
                    port = int(proxy[1])
                    return python_socks.ProxyType.SOCKS5, ip, port
                ip = proxy[0]
                port = int(proxy[1])
                username = proxy[2]
                password = proxy[3]
                return python_socks.ProxyType.SOCKS5, ip, port, True, username, password

            else:
                proxy = chosen_proxy.split(':')
                if len(proxy) == 2:
                    ip = proxy[0]
                    port = int(proxy[1])
                    return python_socks.ProxyType.HTTP, ip, port
                ip = proxy[0]
                port = int(proxy[1])
                username = proxy[2]
                password = proxy[3]
                return python_socks.ProxyType.HTTP, ip, port, True, username, password

    def update_data(self, **kwargs):
        for key, value in kwargs.items():
            self.data[key] = value

        with open(f'{self.session}.json', 'w', encoding='utf-8') as file:
            json.dump(self.data, file, indent=4, ensure_ascii=False)

    def log(self, text):
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        print(f'[{current_time}] Поток #{self.thread}: Аккаунт {self.phone_number}: {text}')

    async def create_connection(self, thread=None):
        if self.thread is None:
            self.thread = thread
        if not self.client.is_connected():
            self.log(f'подключаюсь через {self.proxy[1]}:{self.proxy[2]}')
            await self.client.connect()

    async def close_connection(self):
        if self.advanced_log:
            self.log('отключаюсь.')
        await self.client.disconnect()
        self._client = None
        self.thread = None

    async def join_chat(self, entity):
        if entity.split('/')[-1][0] == '+' or 'joinchat' in entity:
            private = True
        else:
            private = False

        if private:
            access_hash = entity.split('/')[-1].split('+')[1]
            chat_invite = await self.client(CheckChatInviteRequest(access_hash))
            if isinstance(chat_invite, ChatInviteAlready):
                self.log(f'Пользователь уже является участником чата {entity}')
                chat = chat_invite.chat
            elif isinstance(chat_invite, ChatInvite):
                response = await self.client(ImportChatInviteRequest(access_hash))
                self.log(f'Присоединился к чату {entity}')
                chat = response.chats[0]
            else:
                raise ValueError(f'Неизвестный тип инвайта: {chat_invite}')
        else:
            await self.client(JoinChannelRequest(entity))
            self.log(f'присоединился к чату {entity}')
            chat = entity
        return chat


class Soft(ABC):
    def __init__(self, entities=None, accounts_count: int = None, entities_per_time: int = 1, min_delay: int = 0,
                 max_delay: int = 0, entities_file=None, advanced_log: bool = True):
        super().__init__()
        self.advanced_log = advanced_log
        self.loop = asyncio.new_event_loop()
        self.accounts = Stack(items=self._get_accounts()[:accounts_count])
        self._entities = entities
        self.entities = self.create_stack(items=entities, count=entities_per_time, file=entities_file)
        self.stats = Stats()
        self.threads = config.general.threads
        self.delay = min_delay, max_delay

    def __del__(self):
        self.loop.close()

    def run(self):
        self.loop.run_until_complete(self.main())

    @staticmethod
    def _get_sessions() -> list:
        result = []
        for directory in ['Аккаунты']:
            sessions = os.listdir(os.path.join(directory))
            for file in sessions:
                if file.endswith('.session'):
                    session = "".join(file.split('.')[:-1])
                    result.append(f"{directory}/{session}")
        return result

    def _get_accounts(self) -> list:
        accounts = []
        sessions = self._get_sessions()
        for session in sessions:
            account = Account(session)
            if not self.advanced_log:
                account.advanced_log = False
            if account.data is None:
                continue
            accounts.append(account)
        return accounts

    async def main(self):
        await self.on_start()

        threads = await self.create_threads()
        await asyncio.gather(*threads)

        await self.on_finish()

    async def create_threads(self) -> List[Task]:
        tasks = []
        for i in range(self.threads):
            tasks.append(asyncio.create_task(self.run_thread(i + 1)))
            await asyncio.sleep(random.uniform(*config.general.start_delay))
        return tasks

    async def run_thread(self, thread):
        while True:
            if self.accounts.is_empty():
                break
            if self.entities.is_empty() and self._entities is not None:
                break

            account = self.accounts.pop()
            entity = self.entities.pop()

            account.thread = thread

            result, error = await self._do(account, entity)
            if error and isinstance(result, SoftError):
                account.log(result.message)
                if not result.continue_work or result is None:
                    await account.close_connection()

                if result.name == 'flood':
                    if isinstance(error, FloodWaitError):
                        if error.seconds > config.general.max_flood_sleep:
                            await account.close_connection()
                        if self.advanced_log:
                            account.log(f'жду {error.seconds} секунд')
                        await asyncio.sleep(error.seconds)
                        self.accounts.push(account)
                        self.entities.push(entity)
                    else:
                        random_delay = random.uniform(*self.delay)
                        if self.advanced_log:
                            account.log(f'жду {int(random_delay)} секунд')
                        await asyncio.sleep(random_delay)
                        self.accounts.push(account)
                        self.entities.push(entity)
                elif isinstance(error, Exception):
                    self.accounts.push(account)
                    self.entities.push(entity)
                    account.log(f'Ошибка: {type(error).__name__}: {error}')
                await self.on_error(account, error, result)
                continue

            await self.on_success(account)
            random_delay = random.uniform(*self.delay)
            if self.advanced_log and random_delay > 0:
                account.log(f'жду {int(random_delay)} секунд')
            await asyncio.sleep(random_delay)

    async def on_start(self):
        pass

    @handler
    async def _do(self, account, entity):
        await account.create_connection()
        return await self.do(account, entity)

    @abstractmethod
    async def do(self, account, entity):
        pass

    async def on_success(self, account):
        pass

    async def on_error(self, account, error: Exception = None, result: SoftError = None):
        pass

    async def on_finish(self):
        pass

    @staticmethod
    def create_stack(items: list, count: int = 1, file: str = None) -> Union[Stack, MultiStack]:
        if count == 1:
            return Stack(items=items, file_name=file)
        else:
            return MultiStack(items=items, count=count, file_name=file)

    @staticmethod
    def log(text):
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        print(f'[{current_time}] {text}')
