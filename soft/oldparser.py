from telethon.errors import *
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest, CheckChatInviteRequest, DeleteChatUserRequest
from telethon import TelegramClient
from telethon import events
import telethon

from .config import config
from .models import Account, Stats
from colorama import Fore
from datetime import datetime, timedelta
from . import helpers
import pytz
import asyncio
import keyboard
import random
import logging

from telethon.tl.types import ChatInvite, ChatInviteAlready

max_threads = config.general.threads
max_messages = config.parser.max_chats
delay = config.parser.delay
path = config.parser.path

async def chat_generator(chats: list):
    for chat in chats:
        yield chat

async def account_generator(accounts: list):
    for account in accounts:
        account.messages_sent = 0
        account.busy = False
        account.next_message_date = None

    while True:
        if keyboard.is_pressed('ctrl+q'):  # if key ctrl+q is pressed
            break  # finishing the loop

        if all(a.busy for a in accounts) or all(a.messages_sent >= max_messages for a in accounts):
            await asyncio.sleep(3)
            continue

        if all(a.messages_sent >= max_messages for a in accounts):
            yield None

        for account in accounts:
            if account.messages_sent >= max_messages or account.busy:
                continue
            elif account.next_message_date is not None:
                if account.next_message_date > pytz.utc.normalize(datetime.utcnow()):
                    continue

            account.busy = True
            yield account
            break
        await asyncio.sleep(0.05)


async def parse(thread, account: Account, entity, stats, chat):
    users = account.client.iter_participants(chat, aggressive=True)
    while True:
        try:
            user = await users.__anext__()
            if user.username:
                try:
                    some_data  = await account.client.get_entity(chat)
                    get_id = some_data.id
                    messages = await account.client.get_messages(get_id)

                    for message in messages:
                        splited_message = message.message.split(' ')
                        if 'arithmetic' in splited_message:
                            first_number = [item.replace("(", "", 1) for item in splited_message]
                            second_number = [item.replace(")", "", 1) for item in splited_message]
                            bot_answer = f"{int(first_number[0]) + int(second_number[2])}" 
                            await account.client.send_message(chat, f"{bot_answer}")
                            break
                        elif message.reply_markup:
                            await message.click()
                            break
                        elif 'any' in splited_message:
                            await account.client.send_message(chat, f"Hi!")
                            break
                        elif message.media:
                            await account.client.download_media(message.media, "photos")
                            for directory in ['photos']:
                                photos = os.listdir(os.path.join(directory))
                                for file in photos:
                                    if file.endswith('.jpg'):
                                        result = file
                            break

                    if await helpers.user_filter(user, online_last=timedelta(hours=config.parser.online_last)):
                        if config.parser.photo == 'True':
                            if user.photo is None:
                                pass
                            else:
                                with open(path + f'Пользователи-{stats.creation_time_str}.txt', 'a', encoding='utf-8') as f:
                                    f.write(f'{user.username}\n')
                                    stats.sent += 1
                        elif config.parser.photo == 'False':
                            with open(path + f'Пользователи-{stats.creation_time_str}.txt', 'a', encoding='utf-8') as f:
                                f.write(f'{user.username}\n')
                                stats.sent += 1
                        else:
                            helpers.log(thread, f'{Fore.RED}Проверьте параметр "photo" в конфигурационном файле.{Fore.LIGHTWHITE_EX} Его значение должно быть ' +
                                f'{Fore.GREEN}True{Fore.LIGHTWHITE_EX} или {Fore.GREEN}False{Fore.LIGHTWHITE_EX}')
                except Exception as e:
                    if config.parser.photo == 'True':
                        if user.photo is None:
                            pass
                        else:
                            if await helpers.user_filter(user, online_last=timedelta(hours=config.parser.online_last)):
                                with open(path + f'Пользователи-{stats.creation_time_str}.txt', 'a', encoding='utf-8') as f:
                                    f.write(f'{user.username}\n')
                                    stats.sent += 1
                    elif config.parser.photo == 'False':
                        with open(path + f'Пользователи-{stats.creation_time_str}.txt', 'a', encoding='utf-8') as f:
                            f.write(f'{user.username}\n')
                            stats.sent += 1
                    else:
                        helpers.log(thread, f'{Fore.RED}Проверьте параметр "photo" в конфигурационном файле.{Fore.LIGHTWHITE_EX} Его значение должно быть ' +
                            f'{Fore.GREEN}True{Fore.LIGHTWHITE_EX} или {Fore.GREEN}False{Fore.LIGHTWHITE_EX}')
                        # else:
                        #     f.write(f'{user.id}\n')

        except FloodWaitError as e:
            helpers.log(thread,
                        f'Аккаунт {Fore.LIGHTWHITE_EX}{account.phone_number}{Fore.LIGHTWHITE_EX}{Fore.RED}: Аккаунт получил флуд... Ждём {e.seconds} секунд {Fore.LIGHTWHITE_EX}')

            await asyncio.sleep(e.seconds)

        except StopAsyncIteration:
            break

        except PeerFloodError as e:
            helpers.log(thread,
                        f'Аккаунт {Fore.LIGHTWHITE_EX}{account.phone_number}{Fore.LIGHTWHITE_EX}: {Fore.RED}: Аккаунт получил флуд {Fore.LIGHTWHITE_EX}')

        except (UserDeactivatedBanError, UserDeactivatedError) as e:
            helpers.log(thread,
                        f'Аккаунт {Fore.LIGHTWHITE_EX}{account.phone_number}{Fore.LIGHTWHITE_EX}{Fore.RED}: Аккаунт забанен. {Fore.LIGHTWHITE_EX}')


        except (ValueError, UsernameInvalidError) as e:
            helpers.log(thread,
                        f'Аккаунт {Fore.LIGHTWHITE_EX}{account.phone_number}{Fore.LIGHTWHITE_EX}: {Fore.RED}Не нашёл чат {Fore.LIGHTWHITE_EX}{entity}: {e}')
            account.busy = False

        except MultiError as e:
            exception = e.exceptions[0]
            if isinstance(exception, FloodWaitError):
                helpers.log(thread,
                            f'Аккаунт {Fore.LIGHTWHITE_EX}{account.phone_number}{Fore.LIGHTWHITE_EX}{Fore.RED}: Аккаунт получил флуд... Ждём {exception.seconds} секунд{Fore.LIGHTWHITE_EX}')

                await asyncio.sleep(exception.seconds)

        except Exception as e:
            helpers.log(thread,
                        f'Аккаунт {Fore.LIGHTWHITE_EX}{account.phone_number}{Fore.LIGHTWHITE_EX}: {Fore.RED}Неизвестная ошибка! {Fore.LIGHTWHITE_EX} {e.__class__}: {e}')
        helpers.delete_user_from_file(entity, f'{config.parser.directory}/Чаты.txt')



@helpers.exception_handler
async def parse_account_task(thread, accounts, entities, stats):
    try:
        account = await accounts.__anext__()
        entity = await entities.__anext__()
    except StopAsyncIteration:
        stats.done = True
        return

    if account is None:
        stats.done = True
        return

    helpers.log(thread, f'Получили чат для парсинга: {entity}')

    try:
        if not account.client.is_connected():
            if account.messages_sent < max_messages:
                helpers.log(thread,
                            f'Проверяю прокси {account.proxy[1]}:{account.proxy[2]}')
                if await helpers.check_proxy(account.proxy):
                    helpers.log(thread,
                                f'Прокси {account.proxy[1]}:{account.proxy[2]} - рабочий, продолжаю работу...')
                else:
                    helpers.log(thread,
                                f'Прокси {account.proxy[1]}:{account.proxy[2]} - не рабочий, пропускаю...')

                    account.busy = False
                    return
                await account.client.connect()
                helpers.log(thread,
                            f'Аккаунт {Fore.LIGHTWHITE_EX}{account.phone_number}{Fore.LIGHTWHITE_EX}: подключен')
        if entity.split('/')[-1][0] == '+' or 'joinchat' in entity:
            private = True
        else:
            private = False

        if private:
            access_hash = entity.split('/')[-1].split('+')[1]
            chat_invite = await account.client(CheckChatInviteRequest(access_hash))
            if isinstance(chat_invite, ChatInviteAlready):
                helpers.log(thread,
                            f'Аккаунт {Fore.LIGHTWHITE_EX}{account.phone_number}{Fore.LIGHTWHITE_EX}: Пользователь уже является участником чата {entity}')
                chat = chat_invite.chat
            elif isinstance(chat_invite, ChatInvite):
                response = await account.client(ImportChatInviteRequest(access_hash))
                helpers.log(thread,
                            f'Аккаунт {Fore.LIGHTWHITE_EX}{account.phone_number}{Fore.LIGHTWHITE_EX}: Присоединился к чату {entity}')
                chat = response.chats[0]
            else:
                raise ValueError(f'Неизвестный тип инвайта: {chat_invite}')
        else:
            await account.client(JoinChannelRequest(entity))
            helpers.log(thread,
                        f'Аккаунт {Fore.LIGHTWHITE_EX}{account.phone_number}{Fore.LIGHTWHITE_EX}: присоединился к чату {entity}')
            chat = entity

        helpers.log(thread, f'Аккаунт {Fore.LIGHTWHITE_EX}{account.phone_number}{Fore.LIGHTWHITE_EX}: Начал парсинг...')
        await parse(thread, account, entity, stats, chat)
        if config.parser.leave == 'True':
            some_data  = await account.client.get_entity(chat)
            get_id = some_data.id
            await account.client.delete_dialog(get_id)
            delay_time = round(random.uniform(delay[0], delay[1]), 2)
            helpers.log(thread, f'Жду {delay_time} секунд')
            await asyncio.sleep(delay_time)
            account.busy = False
        elif config.parser.leave == 'False':
            delay_time = round(random.uniform(delay[0], delay[1]), 2)
            helpers.log(thread, f'Жду {delay_time} секунд')
            await asyncio.sleep(delay_time)
            account.busy = False   
        else:
            helpers.log(thread, f'{Fore.RED}Проверьте параметр "leave" в конфигурационном файле.{Fore.LIGHTWHITE_EX} Его значение должно быть ' +
                f'{Fore.GREEN}True{Fore.LIGHTWHITE_EX} или {Fore.GREEN}False{Fore.LIGHTWHITE_EX}')

    except (FloodWaitError, PeerFloodError) as e:
        helpers.log(thread,
                    f'Аккаунт {Fore.LIGHTWHITE_EX}{account.phone_number}{Fore.LIGHTWHITE_EX}: {Fore.RED}: Аккаунт получил флуд{Fore.LIGHTWHITE_EX}')


    except (UserDeactivatedBanError, UserDeactivatedError) as e:
        helpers.log(thread, f'Аккаунт {Fore.LIGHTWHITE_EX}{account.phone_number}{Fore.LIGHTWHITE_EX}: {Fore.RED}: Аккаунт забанен.{Fore.LIGHTWHITE_EX}')


    except (ValueError, UsernameInvalidError) as e:
        helpers.log(thread, f'Аккаунт {Fore.LIGHTWHITE_EX}{account.phone_number}{Fore.LIGHTWHITE_EX}: {Fore.RED}Не нашёл чат {Fore.LIGHTWHITE_EX}{entity}: {e}')
        account.busy = False


    except Exception as e:
        helpers.log(thread, f'Аккаунт {Fore.LIGHTWHITE_EX}{account.phone_number}{Fore.LIGHTWHITE_EX}: {Fore.RED}Неизвестная ошибка!{Fore.LIGHTWHITE_EX} {e}')




@helpers.exception_handler
async def threaded_parse(thread, accounts, entities, stats):
    tasks = []
    while True:
        if keyboard.is_pressed('ctrl+q'):  # if key ctrl+q is pressed
            stats.done = True
            return  # finishing the loop
        try:
            if stats.done:
                return
            task = asyncio.create_task(parse_account_task(thread, accounts, entities, stats))
            tasks.append(task)
            await task

            # await asyncio.ensure_future(task)

        except StopIteration:
            break
        except StopAsyncIteration:
            break
        except Exception as e:
            print(e)
            break

    await asyncio.gather(*tasks)

@helpers.exception_handler
async def mass_parse(accounts_list: list, threads=max_threads):
    await asyncio.sleep(3)
    accounts = account_generator(accounts_list)
    entities = chat_generator(config.parser.chats)

    tasks = []
    stats = Stats()

    if len(accounts_list) < threads:
        threads = len(accounts_list)


    for i in range(threads):
        task = asyncio.create_task(threaded_parse(i+1, accounts, entities, stats))
        tasks.append(task)
        if not stats.done:
            await helpers.sleep_randomly(i+1)

    await asyncio.gather(*tasks)

    for account in accounts_list:
        if account.client.is_connected():
            await account.client.disconnect()

    print()

    print(f'Парсинг завершён! Всего найдено: {Fore.CYAN}{stats.sent}{Fore.LIGHTWHITE_EX} пользователей')
    logging.info(f'Парсинг завершён! Всего найдено: {stats.sent} пользователей')
