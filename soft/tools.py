import asyncio
import os
import random
import string

from colorama import Fore
from telethon.tl.functions.account import UpdateUsernameRequest, UpdateProfileRequest, GetAuthorizationsRequest
from telethon.tl.functions.auth import ResetAuthorizationsRequest
from telethon.tl.functions.photos import UploadProfilePhotoRequest
from telethon.errors import *

from . import helpers
from .config import config
from .models import Stats


def avatar_gen():
    avatars = os.listdir('Дополнительно/avatars')
    count = config.tools.avatars
    counter = {avatar: 0 for avatar in avatars}
    while True:
        for avatar in avatars:
            if counter[avatar] < count:
                counter[avatar] += 1
                yield avatar
            elif all(value >= count for value in counter.values()):
                return


async def delete_accounts(accounts_list: list):
    for account in accounts_list:
        try:
            await account.disconnect()
            account.client.session.save()
            account.client.session.close()
            account.client.session._cursor().close()
            account.client.session._cursor().connection.close()
            os.remove(f'sessions/{account.phone_number}.session')
            os.remove(f'sessions/{account.phone_number}.json')
        except Exception as e:

            accounts_list.remove(account)
            print(f'{account.phone_number}: Ошибка удаления сессии! {e}')
    print(f'Удалено аккаунтов: {len(accounts_list)}')


async def archive_accounts(accounts_list: list):
    for account in accounts_list:
        try:
            await account.disconnect()
            account.client.session.save()
            account.client.session.close()
            account.client.session._cursor().close()
            account.client.session._cursor().connection.close()
            os.rename(f'sessions/{account.phone_number}.session', f'archive/{account.phone_number}.session')
            os.rename(f'sessions/{account.phone_number}.json', f'archive/{account.phone_number}.json')
        except Exception as e:

            accounts_list.remove(account)
            print(f'{account.phone_number}: Ошибка архивации сессии! {e}')
    print(f'Архивировано аккаунтов: {len(accounts_list)}')


async def move_accounts(accounts_list: list, directory: str):
    for account in accounts_list:
        try:
            await account.disconnect()
            account.client.session.save()
            account.client.session.close()
            account.client.session._cursor().close()
            account.client.session._cursor().connection.close()
            os.rename(f'sessions/{account.phone_number}.session', f'{directory}/{account.phone_number}.session')
            os.rename(f'sessions/{account.phone_number}.json', f'{directory}/{account.phone_number}.json')
        except Exception as e:
            accounts_list.remove(account)
            print(f'{account.phone_number}: Ошибка перемещения сессии! {e}')



async def post_usernames(accounts_list: list):
    def random_username(size=20, chars=string.ascii_lowercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))

    async def one_task_username_post(thread, account):
        helpers.log(thread,
                    f'Аккаунт {Fore.LIGHTWHITE_EX}{account.phone_number}{Fore.LIGHTWHITE_EX}: подключаюсь через {account.proxy[1]}:{account.proxy[2]}')
        await account.client.connect()
        for _ in range(5):
            try:
                username = random_username()
                await account.client(UpdateUsernameRequest(username=username))
                break
            except (UsernameOccupiedError, UsernameInvalidError):
                pass
        else:
            helpers.log(thread,
                        f'Аккаунт {Fore.LIGHTWHITE_EX}{account.phone_number}{Fore.LIGHTWHITE_EX}: юзернейм НЕ загружен!')
            return

        helpers.log(thread,
                    f'Аккаунт {Fore.LIGHTWHITE_EX}{account.phone_number}{Fore.LIGHTWHITE_EX}: юзернейм загружен!')

        account.update_data(username=username)

    async def one_thread_username_post(thread, accounts):
        while True:
            try:
                account = next(accounts)
                await one_task_username_post(thread, account)
            except StopIteration:
                return
            except Exception as e:
                print(f'Ошибка при постинге аватара! {e}')
                return



    accounts = iter(accounts_list)

    threads = config.general.threads

    if len(accounts_list) < threads:
        threads = len(accounts_list)

    tasks = []
    for i in range(threads):
        task = asyncio.create_task(one_thread_username_post(i + 1, accounts))
        tasks.append(task)

    await asyncio.gather(*tasks)

    for account in accounts_list:
        if account.client.is_connected():
            await account.client.disconnect()


async def post_avatars(accounts_list: list):
    async def one_task_avatar_post(thread, account, avatar):
        helpers.log(thread,
                    f'Аккаунт {Fore.LIGHTWHITE_EX}{account.phone_number}{Fore.LIGHTWHITE_EX}: подключаюсь через {account.proxy[1]}:{account.proxy[2]}')
        await account.client.connect()
        await account.client(UploadProfilePhotoRequest(await account.client.upload_file(f'Дополнительно/avatars/{avatar}')))
        helpers.log(thread, f'Аккаунт {Fore.LIGHTWHITE_EX}{account.phone_number}{Fore.LIGHTWHITE_EX}: аватар загружен!')

    async def one_thread_avatar_post(thread, accounts, avatars):
        while True:
            try:
                account = next(accounts)
                avatar = next(avatars)
                await one_task_avatar_post(thread, account, avatar)
            except StopIteration:
                return
            except ConnectionError:
                helpers.log(thread,
                            f'Аккаунт {Fore.LIGHTWHITE_EX}{account.phone_number}{Fore.LIGHTWHITE_EX}: ошибка подключения!')

            except Exception as e:
                helpers.log(thread,
                            f'Аккаунт {Fore.LIGHTWHITE_EX}{account.phone_number}{Fore.LIGHTWHITE_EX}: ошибка! {e.__class__}: {e}')
                return



    accounts = iter(accounts_list)
    avatars = avatar_gen()

    threads = config.general.threads

    if len(accounts_list) < threads:
        threads = len(accounts_list)

    tasks = []
    for i in range(threads):
        task = asyncio.create_task(one_thread_avatar_post(i + 1, accounts, avatars))
        tasks.append(task)

    await asyncio.gather(*tasks)

    for account in accounts_list:
        if account.client.is_connected():
            await account.client.disconnect()


async def post_names(accounts_list: list):
    def random_name():
        gender = random.choice(['Male', 'Female'])

        if gender == 'Male':
            with open(f'Дополнительно/names/male_first_names.txt', mode='r', encoding='utf-8') as file:
                first_names = file.read().split('\n')
            with open(f'Дополнительно/names/male_last_names.txt', mode='r', encoding='utf-8') as file:
                last_names = file.read().split('\n')

        elif gender == 'Female':
            with open(f'Дополнительно/names/female_first_names.txt', mode='r', encoding='utf-8') as file:
                first_names = file.read().split('\n')
            with open(f'Дополнительно/names/female_last_names.txt', mode='r', encoding='utf-8') as file:
                last_names = file.read().split('\n')

        first_name, last_name = random.choice(first_names), random.choice(last_names)
        return first_name, last_name, gender

    async def one_task_name_post(thread, account, name):
        helpers.log(thread,
                    f'Аккаунт {Fore.LIGHTWHITE_EX}{account.phone_number}{Fore.LIGHTWHITE_EX}: подключаюсь через {account.proxy[1]}:{account.proxy[2]}')
        await account.client.connect()
        await account.client(UpdateProfileRequest(first_name=name[0], last_name=name[1]))

        helpers.log(thread,
                    f'Аккаунт {Fore.LIGHTWHITE_EX}{account.phone_number}{Fore.LIGHTWHITE_EX}: имя загружено!')
        account.update_data(first_name = name[0], last_name = name[1])

    async def one_thread_name_post(thread, accounts):
        while True:
            try:
                account = next(accounts)
                name = random_name()
                await one_task_name_post(thread, account, name)
            except StopIteration:
                return
            except Exception as e:
                helpers.log(thread,
                            f'Аккаунт {Fore.LIGHTWHITE_EX}{account.phone_number}{Fore.LIGHTWHITE_EX}: ошибка! {e.__class__}: {e}')
                return



    accounts = iter(accounts_list)

    threads = config.general.threads

    if len(accounts_list) < threads:
        threads = len(accounts_list)

    tasks = []
    for i in range(threads):
        task = asyncio.create_task(one_thread_name_post(i + 1, accounts))
        tasks.append(task)

    await asyncio.gather(*tasks)

    for account in accounts_list:
        if account.client.is_connected():
            await account.client.disconnect()


async def close_other_sessions(accounts_list: list):
    async def one_task(thread, account):
        helpers.log(thread,
                    f'Аккаунт {Fore.LIGHTWHITE_EX}{account.phone_number}{Fore.LIGHTWHITE_EX}: подключаюсь через {account.proxy[1]}:{account.proxy[2]}')
        await account.client.connect()
        helpers.log(thread,
                    f'Аккаунт {Fore.LIGHTWHITE_EX}{account.phone_number}{Fore.LIGHTWHITE_EX}: завершаю сессии...')
        await account.client(ResetAuthorizationsRequest())
        helpers.log(thread,
                    f'Аккаунт {Fore.LIGHTWHITE_EX}{account.phone_number}{Fore.LIGHTWHITE_EX}: сессии завершены!')

    async def one_thread(thread, accounts):
        while True:
            try:
                account = next(accounts)
                await one_task(thread, account)
            except StopIteration:
                return
            except Exception as e:
                helpers.log(thread,
                            f'Аккаунт {Fore.LIGHTWHITE_EX}{account.phone_number}{Fore.LIGHTWHITE_EX}: ошибка! {e.__class__}: {e}')
                return



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