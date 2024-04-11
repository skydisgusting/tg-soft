from telethon import TelegramClient
from telethon import events
from telethon.errors import *
from telethon import types
from telethon.tl.types import ChatInvite, ChatInviteAlready
import telethon

from .config import config
from .models import Account, Stats
from colorama import Fore
from . import helpers, mail

import keyboard
import asyncio
import random
import pytz

max_threads = config.general.threads
reports = config.reporter.reports
delay: list = config.reporter.delay
path = config.reporter.path

async def chat_generator(chats: list):
	while True:
		for chat in chats:
			yield chat

async def account_generator(accounts: list):
	for account in accounts:
		account.reports_sent = 0
		yield account

def mail_generator(accounts: list):
	for account in accounts:
		yield account

def target_generator(targets: list):
	for target in targets:
		yield target

async def reporter(thread, account: Account, get_chose, entities, stats):
	stats.sent = 0
	while stats.sent != 1:
		try:
			if get_chose == '1':
				try:
					result = account.client(functions.messages.ReportRequest(
						peer=entities,
						id=[42],
						reason=types.InputReportReasonChildAbuse(),
						message='Child Abuse'))
					is_resulted = await result
					if is_resulted == True:
						stats.sent += 1
						#total_reports += 1
						helpers.log(thread, f'Аккаунт {Fore.LIGHTWHITE_EX}{account.phone_number}{Fore.LIGHTWHITE_EX}: {Fore.GREEN}Репорт прошел{Fore.LIGHTWHITE_EX}')
					else:
						helpers.log(thread, f'Аккаунт {Fore.LIGHTWHITE_EX}{account.phone_number}{Fore.LIGHTWHITE_EX}: {Fore.RED}Репорт не прошел{Fore.LIGHTWHITE_EX}')
				except (UserDeactivatedBanError, UserDeactivatedError) as e:
					helpers.log(thread, f'Аккаунт {Fore.LIGHTWHITE_EX}{account.phone_number}{Fore.LIGHTWHITE_EX}: {Fore.RED}: Аккаунт забанен.{Fore.LIGHTWHITE_EX}')
			if get_chose == '2':
				try:
					result = account.client(functions.messages.ReportRequest(
						peer=entities,
						id=[42],
						reason=types.InputReportReasonFake(),
						message='Fake'))
					is_resulted = await result
					if is_resulted == True:
						stats.sent += 1
						#total_reports += 1
						helpers.log(thread, f'Аккаунт {Fore.LIGHTWHITE_EX}{account.phone_number}{Fore.LIGHTWHITE_EX}: {Fore.GREEN}Репорт прошел{Fore.LIGHTWHITE_EX}')
					else:
						helpers.log(thread, f'Аккаунт {Fore.LIGHTWHITE_EX}{account.phone_number}{Fore.LIGHTWHITE_EX}: {Fore.RED}Репорт не прошел{Fore.LIGHTWHITE_EX}')
				except (UserDeactivatedBanError, UserDeactivatedError) as e:
					helpers.log(thread, f'Аккаунт {Fore.LIGHTWHITE_EX}{account.phone_number}{Fore.LIGHTWHITE_EX}: {Fore.RED}: Аккаунт забанен.{Fore.LIGHTWHITE_EX}')
			if get_chose == '3':
				try:
					result = account.client(functions.messages.ReportRequest(
						peer=entities,
						id=[42],
						reason=types.InputReportReasonOther(),
						message='Other'))
					is_resulted = await result
					if is_resulted == True:
						stats.sent += 1
						#total_reports += 1
						helpers.log(thread, f'Аккаунт {Fore.LIGHTWHITE_EX}{account.phone_number}{Fore.LIGHTWHITE_EX}: {Fore.GREEN}Репорт прошел{Fore.LIGHTWHITE_EX}')
					else:
						helpers.log(thread, f'Аккаунт {Fore.LIGHTWHITE_EX}{account.phone_number}{Fore.LIGHTWHITE_EX}: {Fore.RED}Репорт не прошел{Fore.LIGHTWHITE_EX}')
				except (UserDeactivatedBanError, UserDeactivatedError) as e:
					helpers.log(thread, f'Аккаунт {Fore.LIGHTWHITE_EX}{account.phone_number}{Fore.LIGHTWHITE_EX}: {Fore.RED}: Аккаунт забанен.{Fore.LIGHTWHITE_EX}')
			if get_chose == '4':
				try:
					result = account.client(functions.messages.ReportRequest(
						peer=entities,
						id=[42],
						reason=types.InputReportReasonSpam(),
						message='Spam'))
					is_resulted = await result
					if is_resulted == True:
						stats.sent += 1
						#total_reports += 1
						helpers.log(thread, f'Аккаунт {Fore.LIGHTWHITE_EX}{account.phone_number}{Fore.LIGHTWHITE_EX}: {Fore.GREEN}Репорт прошел{Fore.LIGHTWHITE_EX}')
					else:
						helpers.log(thread, f'Аккаунт {Fore.LIGHTWHITE_EX}{account.phone_number}{Fore.LIGHTWHITE_EX}: {Fore.RED}Репорт не прошел{Fore.LIGHTWHITE_EX}')
				except (UserDeactivatedBanError, UserDeactivatedError) as e:
					helpers.log(thread, f'Аккаунт {Fore.LIGHTWHITE_EX}{account.phone_number}{Fore.LIGHTWHITE_EX}: {Fore.RED}: Аккаунт забанен.{Fore.LIGHTWHITE_EX}')
			if get_chose == '5':
				try:
					result = account.client(functions.messages.ReportRequest(
						peer=entities,
						id=[42],
						reason=types.InputReportReasonCopyright(),
						message='Copyright'))
					is_resulted = await result
					if is_resulted == True:
						stats.sent += 1
						#total_reports += 1
						helpers.log(thread, f'Аккаунт {Fore.LIGHTWHITE_EX}{account.phone_number}{Fore.LIGHTWHITE_EX}: {Fore.GREEN}Репорт прошел{Fore.LIGHTWHITE_EX}')
					else:
						helpers.log(thread, f'Аккаунт {Fore.LIGHTWHITE_EX}{account.phone_number}{Fore.LIGHTWHITE_EX}: {Fore.RED}Репорт не прошел{Fore.LIGHTWHITE_EX}')
				except (UserDeactivatedBanError, UserDeactivatedError) as e:
					helpers.log(thread, f'Аккаунт {Fore.LIGHTWHITE_EX}{account.phone_number}{Fore.LIGHTWHITE_EX}: {Fore.RED}: Аккаунт забанен.{Fore.LIGHTWHITE_EX}')
			if get_chose == '6':
				try:
					result = account.client(functions.messages.ReportRequest(
						peer=entities,
						id=[42],
						reason=types.InputReportReasonPornography(),
						message='Pornography'))
					is_resulted = await result
					if is_resulted == True:
						stats.sent += 1
						#total_reports += 1
						helpers.log(thread, f'Аккаунт {Fore.LIGHTWHITE_EX}{account.phone_number}{Fore.LIGHTWHITE_EX}: {Fore.GREEN}Репорт прошел{Fore.LIGHTWHITE_EX}')
					else:
						helpers.log(thread, f'Аккаунт {Fore.LIGHTWHITE_EX}{account.phone_number}{Fore.LIGHTWHITE_EX}: {Fore.RED}Репорт не прошел{Fore.LIGHTWHITE_EX}')
				except (UserDeactivatedBanError, UserDeactivatedError) as e:
					helpers.log(thread, f'Аккаунт {Fore.LIGHTWHITE_EX}{account.phone_number}{Fore.LIGHTWHITE_EX}: {Fore.RED}: Аккаунт забанен.{Fore.LIGHTWHITE_EX}')
			if get_chose == '7':
				try:
					result = account.client(functions.messages.ReportRequest(
						peer=entities,
						id=[42],
						reason=types.InputReportReasonViolence(),
						message='Violence'))
					is_resulted = await result
					if is_resulted == True:
						stats.sent += 1
						#total_reports += 1
						helpers.log(thread, f'Аккаунт {Fore.LIGHTWHITE_EX}{account.phone_number}{Fore.LIGHTWHITE_EX}: {Fore.GREEN}Репорт прошел{Fore.LIGHTWHITE_EX}')
					else:
						helpers.log(thread, f'Аккаунт {Fore.LIGHTWHITE_EX}{account.phone_number}{Fore.LIGHTWHITE_EX}: {Fore.RED}Репорт не прошел{Fore.LIGHTWHITE_EX}')
				except (UserDeactivatedBanError, UserDeactivatedError) as e:
					helpers.log(thread, f'Аккаунт {Fore.LIGHTWHITE_EX}{account.phone_number}{Fore.LIGHTWHITE_EX}: {Fore.RED}: Аккаунт забанен.{Fore.LIGHTWHITE_EX}')
				break
		except Exception as e:
			await asyncio.sleep(4)
			print(f"[ - ] {e}")

async def threaded_parse(thread, accounts, get_chose, entities, stats):
	tasks = []
	while True:

		if keyboard.is_pressed('ctrl+q'):  # if key ctrl+q is pressed
			stats.done = True
			return  # finishing the loop
		try:
			if stats.done:
				return
			task = asyncio.create_task(parse_account_task(thread, accounts, get_chose, entities, stats))
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

async def parse_account_task(thread, accounts, get_chose, entities, stats):
	try:
		account = await accounts.__anext__()
		entity = await entities.__anext__()
	except StopAsyncIteration:
		stats.done = True
		return

	if account is None:
		stats.done = True
		return

	helpers.log(thread, f'Получил объект для репорта: {entity}')

	try:
		if not account.client.is_connected():
			if account.reports_sent < reports:
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

			helpers.log(thread, f'Аккаунт {Fore.LIGHTWHITE_EX}{account.phone_number}{Fore.LIGHTWHITE_EX}: Начал репорт')
			await reporter(thread, account, get_chose, entity, stats)
			try:
				delay_time = random.uniform(int(delay[0]), int(delay[1]))
			except:
				delay_time = int(delay[0])
			helpers.log(thread, f'Жду {delay_time} секунд')
			await asyncio.sleep(delay_time)
			account.busy = False   

	except (FloodWaitError, PeerFloodError) as e:
		helpers.log(thread,
					f'Аккаунт {Fore.LIGHTWHITE_EX}{account.phone_number}{Fore.LIGHTWHITE_EX}: {Fore.RED}: Аккаунт получил флуд{Fore.LIGHTWHITE_EX}')


	except (UserDeactivatedBanError, UserDeactivatedError) as e:
		helpers.log(thread, f'Аккаунт {Fore.LIGHTWHITE_EX}{account.phone_number}{Fore.LIGHTWHITE_EX}: {Fore.RED}: Аккаунт забанен.{Fore.LIGHTWHITE_EX}')


	except (ValueError, UsernameInvalidError) as e:
		helpers.log(thread, f'Аккаунт {Fore.LIGHTWHITE_EX}{account.phone_number}{Fore.LIGHTWHITE_EX}: {Fore.RED}Не нашёл чат {Fore.LIGHTWHITE_EX}{entity}: {e}')
		account.busy = False


def report_mail(get_chose):
	accounts = mail_generator(config.reporter.accounts)
	how_many_reports = config.reporter.reports
	target = config.reporter.targets

	for n in str(how_many_reports):
		for i in accounts:
			splited = i.split(':')
			if mail.prepare_mail(account=i, get_chose=get_chose, target=target) == 1:
				helpers.log(1, f'Аккаунт {Fore.LIGHTWHITE_EX}{splited[0]}{Fore.LIGHTWHITE_EX}: {Fore.GREEN}Сообщение было отправлено{Fore.LIGHTWHITE_EX}')
			else:
				helpers.log(1, f"Аккаунт {Fore.LIGHTWHITE_EX}{splited[0]}{Fore.LIGHTWHITE_EX}: {Fore.RED}Сообщение не было отправлено{Fore.LIGHTWHITE_EX}")

async def start_reporter(accounts_list: list, get_chose, threads=max_threads):
	await asyncio.sleep(3)
	accounts = account_generator(accounts_list)
	entities = chat_generator(config.reporter.targets)

	tasks = []
	stats = Stats()

	if len(accounts_list) < threads:
		threads = len(accounts_list)

	for i in range(threads):
		task = asyncio.create_task(threaded_parse(i+1, accounts, get_chose, entities, stats))
		tasks.append(task)
		if not stats.done:
			await helpers.sleep_randomly(i+1)

	await asyncio.gather(*tasks)

	for account in accounts_list:
		if account.client.is_connected():
			await account.client.disconnect()

	print()

	print(f"Репорт завершен.")