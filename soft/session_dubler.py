import asyncio
import json
import os
import random
import string

from colorama import Fore
from telethon import TelegramClient, events
from telethon.tl.functions.account import UpdateUsernameRequest, UpdateProfileRequest
from telethon.tl.functions.photos import UploadProfilePhotoRequest
from telethon.errors import *

from . import helpers
from .config import config
from .models import Account


async def duble_sessions(accounts_list: list):
    async def get_code(thread, account: Account):
        last_message = (await account.client.get_messages(777000, limit=1))[0]
        message = last_message.text
        code = re.findall(r'[0-9]+', message)[0]
        await account.client.delete_messages(777000, message_ids=[last_message.id])
        helpers.log(thread,
                    f'Аккаунт {Fore.LIGHTWHITE_EX}{account.phone_number}{Fore.LIGHTWHITE_EX}: получил код {code}')
        return code

    async def one_task(thread, account: Account):
        helpers.log(thread,
                    f'Аккаунт {Fore.LIGHTWHITE_EX}{account.phone_number}{Fore.LIGHTWHITE_EX}: подключаюсь через {account.proxy[1]}:{account.proxy[2]}')

        new_client = TelegramClient(
            session=f'Дублирование сессий/{account.phone_number}.session',
            api_id=account.data['app_id'],
            api_hash=account.data['app_hash'],
            proxy=account.proxy,
            system_version=account.data['sdk'],
            app_version=account.data['app_version'],
            device_model=account.data['device'],
            lang_code=account.data['lang_pack'],
            system_lang_code=account.data['system_lang_pack'],
        )
        await new_client.connect()

        if await new_client.is_user_authorized():
            helpers.log(thread,
                        f'Аккаунт {Fore.LIGHTWHITE_EX}{account.phone_number}{Fore.LIGHTWHITE_EX}: аккаунт уже авторизован')
            await new_client.disconnect()
            await account.client.disconnect()
            return

        await account.client.connect()

        helpers.log(thread, f'Аккаунт {Fore.LIGHTWHITE_EX}{account.phone_number}{Fore.LIGHTWHITE_EX}: отсылаю код')
        await new_client.send_code_request(account.phone_number)

        code = await get_code(thread, account)

        try:
            await new_client.sign_in(account.phone_number, code=code)
        except SessionPasswordNeededError:
            await new_client.sign_in(account.phone_number, password=account.password)

        if await new_client.is_user_authorized():
            helpers.log(thread,
                        f'Аккаунт {Fore.LIGHTWHITE_EX}{account.phone_number}{Fore.LIGHTWHITE_EX}: успешно авторизировался!')
        else:
            helpers.log(thread,
                        f'Аккаунт {Fore.LIGHTWHITE_EX}{account.phone_number}{Fore.LIGHTWHITE_EX}: не удалось авторизироваться!')
            await new_client.disconnect()
            await account.client.disconnect()
            return

        with open(f'Дублирование сессий/{account.phone_number}.json', 'w', encoding='utf-8') as file:
            json.dump(account.data, file, indent=4, ensure_ascii=False)

        last_message = (await account.client.get_messages(777000, limit=1))[0]
        await account.client.delete_messages(777000, message_ids=[last_message.id])

        await new_client.disconnect()
        await account.client.disconnect()
        helpers.log(thread,
                    f'Аккаунт {Fore.LIGHTWHITE_EX}{account.phone_number}{Fore.LIGHTWHITE_EX}: успешно скопировал сессию!')

    async def one_thread(thread, accounts):
        while True:
            try:
                account = next(accounts)
                await one_task(thread, account)
            except StopIteration:
                return
            except ConnectionError:
                helpers.log(thread,
                            f'Аккаунт {Fore.LIGHTWHITE_EX}{account.phone_number}{Fore.LIGHTWHITE_EX}: проблемы с подключением!')
            except (PhoneNumberBannedError, UserDeactivatedBanError, UserDeactivatedError, AuthKeyUnregisteredError, SessionRevokedError, AuthKeyDuplicatedError):
                helpers.log(thread,
                            f'Аккаунт {Fore.LIGHTWHITE_EX}{account.phone_number}{Fore.LIGHTWHITE_EX}: бан!')
            except AttributeError:
                helpers.log(thread,
                            f'Аккаунт {Fore.LIGHTWHITE_EX}{account.phone_number}{Fore.LIGHTWHITE_EX}: ошибка сессии!')
            except Exception as e:
                helpers.log(thread,
                            f'Аккаунт {Fore.LIGHTWHITE_EX}{account.phone_number}{Fore.LIGHTWHITE_EX}: Ошибка при дублировании сессии! {e.__class__}: {e}')

    accounts = iter(accounts_list)
    threads = config.general.threads

    if len(accounts_list) < threads:
        threads = len(accounts_list)

    tasks = []
    for i in range(threads):
        task = asyncio.create_task(one_thread(i + 1, accounts))
        tasks.append(task)

    await asyncio.gather(*tasks)

    for account in accounts_list:
        if account.client.is_connected():
            await account.client.disconnect()

    print(f'Дублирование сессий завершено!')

    filelist = os.listdir('Дублирование сессий')

    for i in filelist:
        if i.endswith('.session') and i.replace('.session', '.json') not in filelist:
            try:
                os.remove(f'Дублирование сессий/{i}')
            except:
                pass
