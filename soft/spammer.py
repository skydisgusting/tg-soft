import os
import random

from typing import List, Union, Optional

from telethon.errors import UsernameInvalidError, UsernameNotOccupiedError

from .models import Soft, Account, Stack, MultiStack
from .config import config


class MessageController:
    def __init__(self, without_crossings: bool = False, max_messages_with_one_text: Optional[int] = None, randomly: bool = False):
        self.DIR = 'Файлы/Спам'
        self.full_text = self.get_full_text()
        self.texts = self.get_texts()
        self.texts_counter = {text: 0 for text in self.texts}
        self.attachments = self.get_attachments()
        self.attachments_counter = {attachment: 0 for attachment in self.attachments}
        self.without_crossings = without_crossings
        self.max_messages_with_one_text = max_messages_with_one_text
        self.randomly = randomly

    def undo(self, text: str = None, attachment: str = None):
        if text:
            self.texts_counter[text] -= 1
        if attachment:
            self.attachments_counter[attachment] -= 1

    def get_message(self) -> str:
        message = self.get_text()
        if message:
            return self.randomize(message).strip()

    def get_text(self) -> str:
        if self.without_crossings:
            return self.get_text_without_crossings()
        elif self.randomly:
            return self.get_random_text()
        else:
            return self.full_text

    def get_full_text(self):
        with open(f'{self.DIR}/Тексты.txt', 'r', encoding='utf-8') as file:
            return file.read()

    def get_texts(self) -> list:
        return self.full_text.split('-----')

    def get_random_text(self) -> str:
        return random.choice(self.texts)

    def get_text_without_crossings(self) -> str:
        for text, counter in self.texts_counter.items():
            if counter < self.max_messages_with_one_text:
                self.texts_counter[text] += 1
                return text

    def get_attachment(self) -> Union[str, list, None]:
        if self.without_crossings:
            return self.get_attachment_without_crossings()
        elif self.randomly:
            return self.get_random_attachment()
        else:
            return self.attachments

    def get_attachments(self) -> List[str]:
        return [f'{self.DIR}/Вложения/{file}' for file in os.listdir(f'{self.DIR}/Вложения')]

    def get_random_attachment(self) -> str:
        if self.attachments:
            return random.choice(self.attachments)

    def get_attachment_without_crossings(self) -> str:
        for file, counter in self.attachments_counter.items():
            if counter < self.max_messages_with_one_text:
                self.attachments_counter[file] += 1
                return file

    @staticmethod
    def randomize(message: str):
        for _string in message.split('{'):
            _string = _string.split('}')
            for __string in _string:
                if '|' in __string:
                    word = random.choice(__string.split('|'))
                    message = message.replace('{' + __string + '}', word)
        return message


class Spammer(Soft):
    def __init__(self, accounts_count: int = None, without_crossings=False, randomly=False, max_messages_with_one_text=None):
        min_delay, max_delay = config.spammer.delay
        super().__init__(config.spammer.users, accounts_count, min_delay=min_delay, max_delay=max_delay, entities_file='Файлы/Спам/Пользователи.txt')
        self.max_messages = config.spammer.max_messages
        self.without_crossings = without_crossings
        self.message_controller = MessageController(without_crossings=self.without_crossings, max_messages_with_one_text=max_messages_with_one_text, randomly=randomly)

    async def on_start(self):
        self.log(f'Спам запущен! В очереди {self.entities.size()} пользователей.')

    async def on_finish(self):
        self.log(f'Спам завершен! Отправлено {self.stats.success} сообщений.')

    # async def on_error(self, account, error=None):
    #     if self.without_crossings:
    #         self.message_controller.undo(account.last_message, account.last_attachment)

    async def do(self, account: Account, username: str):
        account.last_message, account.last_attachment = None, None

        while True:
            try:
                user = await account.client.get_entity(username)
                break
            except (UsernameInvalidError, UsernameNotOccupiedError, ValueError):
                if self.entities.is_empty():
                    return True, None
                account.log(f'Пользователь {username} не найден! Беру следующего.')
                username = self.entities.pop()

        message = self.message_controller.get_message()
        attachment = self.message_controller.get_attachment()

        account.last_message, account.last_attachment = message, attachment

        if self.message_controller.without_crossings:
            if message is None or attachment is None:
                account.log('Закончились текста/вложения для отправки!')
                await account.close_connection()

        if message is None:
            message = ''

        if not attachment:
            attachment = None

        await account.client.send_message(user, message=message, file=attachment)
        account.i += 1
        self.stats.success += 1
        account.log(f'отправлено уже {account.i} сообщений')
        if account.i >= self.max_messages:
            await account.close_connection()
        else:
            self.accounts.push(account)
        return True, None
