from .models import Soft, Account, Stack
from .config import config
from .helpers import user_filter

import asyncio
import time

from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.types import ChannelParticipantsAdmins, ChannelParticipantsBots, ChannelParticipantsSearch
from telethon.errors.common import MultiError
from telethon.errors.rpcerrorlist import FloodWaitError

from datetime import datetime, timedelta

def check_bot(target):
	temp_username = []
	count = -4
	for i in range(3):
		count += 1
		temp_username.append(target.username[count])
	username = ''.join(str(x) for x in temp_username)
	return username

class Parser(Soft):
	def __init__(self, accounts_count: int = None):
		min_delay, max_delay = config.parser.delay
		super().__init__(config.parser.chats, accounts_count, min_delay=min_delay, max_delay=max_delay, entities_file='Файлы/Парсер/Чаты.txt')

		self.max_chats = config.parser.max_chats
		self.targets = config.parser.targets
		self.parser_path = config.parser.path
		self.online_min = config.parser.online_min
		self.online_max = config.parser.online_max
		self.photo = config.parser.photo
		self.creation_time = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime())
		self.spam_path = config.spammer.users
		self.inviter_path = config.inviter.users
		self.users_to_uniqe = []
		self.not_uniqe_counter = 0

	async def on_start(self):
		self.log(f'Парсинг запущен! В очереди {self.entities.size()} чатов.')

	async def on_finish(self):
		self.log("Поиск повторяющихся пользователей..")

		passed = []

		for i in self.users_to_uniqe:
			if i not in passed:
				passed.append(i)
			else:
				self.not_uniqe_counter += 1

		if self.not_uniqe_counter == 0:
			self.log("Повторяющихся пользователей не найдено!")
		else:
			self.log(f"Всего повторяющихся пользователей {self.not_uniqe_counter}")

		with open(self.parser_path + f'Пользователи-{self.creation_time}.txt', 'a', encoding='utf-8') as f:
			for i in passed:
				f.write(f'@{i}\n')

		self.log(f'Парсинг завершен! Спаршено {self.stats.success - self.not_uniqe_counter} пользователей.')

		while True:

			print(
				'\n1. Скопировать результат в спамер'
				'\n2. Скопировать результат в инвайтер'
				'\n3. Скопировать результат в спамер и инвайтер'
				'\n4. Пропустить'
				)

			try:
				choice = int(input("\nОтвет: "))
			except ValueError:
				self.log("Введите число!")
				continue

			if choice == 1:
				with open(self.spam_path + f'Пользователи.txt', 'a', encoding='utf-8') as f:
					for i in passed:
						f.write(f'{i}, {chat}\n')
				break
			if choice == 2:
				with open(self.inviter_path + f'Пользователи.txt', 'a', encoding='utf-8') as f:
					for i in passed:
						f.write(f'{i}\n')
				break
			if choice == 3:
				with open(self.spam_path + f'Пользователи.txt', 'a', encoding='utf-8') as f:
					for i in passed:
						f.write(f'{i}\n')
				with open(self.inviter_path + f'Пользователи.txt', 'a', encoding='utf-8') as f:
					for i in passed:
						f.write(f'{i}\n')
				break
			if choice == 4:
				break

	async def do(self, account: Account, chat: str):
		await account.join_chat(chat)
		get_chat_info = await account.client.get_entity(chat)
		counter = 0
		get_all_participants = await account.client(GetFullChannelRequest(get_chat_info))
		get_participants = get_all_participants.full_chat.participants_count
		messages = await account.client.get_messages(get_chat_info.id)
		aggressive = False

		if get_participants >= 10000:
			aggressive = True

		for message in messages:
			if counter < 5:
				try:
					counter =+ 1
					splited_message = message.message.split(' ')
					if 'arithmetic' in splited_message:
						first_number = [item.replace("(", "", 1) for item in splited_message]
						second_number = [item.replace(")", "", 1) for item in splited_message]
						bot_answer = f"{int(first_number[0]) + int(second_number[2])}" 
						await account.client.send_message(chat, f"{bot_answer}")
						break
					if message.reply_markup:
						if message.buttons[0][0].url:
							break
						else:
							await message.click()
							break
						break
					if 'any' in splited_message:
						await account.client.send_message(chat, f"Hi!")
						break
				except AttributeError:
					pass
			else:
				break

		self.log("Начинаю парсинг")
		self.log(f"{chat} - обнаружено {get_participants} пользователей.")

		if "users" in self.targets:
			if aggressive:
				users = account.client.iter_participants(chat, aggressive=aggressive)
			else:
				users = account.client.iter_participants(chat, aggressive=aggressive, limit=9999)
			while True:
				try:
					user = await users.__anext__()
					if user.username:
						username = check_bot(user)
						if username.lower() != "bot":
							if await user_filter(user, online_min=timedelta(hours=self.online_min), online_max=timedelta(hours=self.online_max)):
								if self.photo == True:
									if user.photo:
										self.users_to_uniqe.append(user.username)
										self.stats.success += 1
								if self.photo == False:
										self.users_to_uniqe.append(user.username)
										self.stats.success += 1
				except StopAsyncIteration:
					break
				except MultiError as e:
					for error in e.exceptions:
						if isinstance(error, FloodWaitError):
							account.log(f'Получил флуд. Жду {error.seconds} секунд')
							await asyncio.sleep(error.seconds)
							break
						else:
							account.log(f'Произошла ошибка: {type(error).__name__}, {error}')
							continue
					continue


		if ChannelParticipantsBots in self.targets:
			users = account.client.iter_participants(chat, filter=ChannelParticipantsBots)
			while True:
				try:
					user = await users.__anext__()
					if user.username:
						if self.photo == True:
							if user.photo:
								self.users_to_uniqe.append(user.username)
								self.stats.success += 1
						if self.photo == False:
							self.users_to_uniqe.append(user.username)
							self.stats.success += 1
				except StopAsyncIteration:
					break

		if ChannelParticipantsAdmins in self.targets:
			users = account.client.iter_participants(chat, filter=ChannelParticipantsAdmins, aggressive=aggressive, limit=5000)
			while True:
				try:
					user = await users.__anext__()
					if user.username:
						username = check_bot(user)
						if username.lower() != "bot":
							if self.photo == True:
								if user.photo:
									self.users_to_uniqe.append(user.username)
									self.stats.success += 1
							if self.photo == False:
								self.users_to_uniqe.append(user.username)
								self.stats.success += 1
				except StopAsyncIteration:
					break
					
		return None, None