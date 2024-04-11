import random

from telethon.tl.functions.channels import InviteToChannelRequest

from . import helpers
from .models import Soft, Account, Stats, Stack
from .config import config
from .exceptions import *
import asyncio



class Inviter(Soft):
    def __init__(self, accounts_count: int = None):
        min_delay, max_delay = config.inviter.delay
        super().__init__(config.inviter.users, accounts_count, entities_per_time=config.inviter.users_per_request, min_delay=min_delay, max_delay=max_delay, entities_file='Файлы/Инвайт/Пользователи.txt')
        self.max_users = config.inviter.max_users
        self.channel = config.inviter.target

    async def on_start(self):
        self.log('Инвайт запущен!')

    async def on_finish(self):
        self.log(f'Инвайтинг завершен! Приглашено {self.stats.success} пользователей.')

    async def do(self, account: Account, users: list):

        account.log('присоединяюсь к чату...')
        chat = await account.join_chat(self.channel)

        account.log(f'Ищу пользователей...')

        users_to_invite = []
        for user in users:
            try:
                users_to_invite.append(await account.client.get_entity(user))
            except (UsernameInvalidError, UsernameNotOccupiedError, ValueError):
                account.log(f'Ошибка при получении пользователя {user}')

        if len(users_to_invite) < len(users):
            while len(users_to_invite) < len(users) and not self.entities.is_empty():
                user = self.entities.pop(one_only=True)
                try:
                    entity = await account.client.get_entity(user)
                    users_to_invite.append(entity)
                except:
                    account.log(f'Ошибка при получении пользователя {user}')

        account.log('приглашаю пользователей..')
        await account.client(InviteToChannelRequest(chat, users_to_invite))
        account.i += len(users_to_invite)
        self.stats.success += len(users_to_invite)
        account.log(f'приглашено уже {account.i} пользователей')
        if account.i >= self.max_users:
            await account.close_connection()
        else:
            self.accounts.push(account)
        return True, None

