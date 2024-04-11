import re
import ssl
import uuid

import requests
from telethon.tl.alltlobjects import LAYER
from typing import Callable, Tuple
from collections.abc import Iterable
from soft import Inviter, Spammer, Parser
from soft.checker import Checker
from soft.config import config
import os
# try:
#     _create_unverified_https_context = ssl._create_unverified_context
# except AttributeError:
#     # Legacy Python that doesn't verify HTTPS certificates by default
#     pass
# else:
#     # Handle target environment that doesn't support HTTPS verification
#     ssl._create_default_https_context = _create_unverified_https_context

class App:
    def __init__(self):
        self.license = None
        self.layer = LAYER

    def run(self):
        print(logo)

        if not self.check_license():
            print('Лицензионный ключ неверный!')
            return
        print('Добро пожаловать!\n')

        print(f'Текущий лаер: {self.layer}')
        print(f'Количество аккаунтов: {self.account_total}')

        self.modes = self.get_modes()

        while True:
            try:
                self.main()
            except KeyboardInterrupt:
                print('\n\nВозвращаемся в главное меню...')

    def main(self):
        title, func = self.choose_mode(self.modes)
        print(f'Выбран режим: {title}')

        self.account_count = self.get_count()
        print(f'Выбрано аккаунтов: {self.account_count} из {self.account_total}')
        input('\nНажмите Enter для продолжения...\n')
        func()
        input('\nНажмите Enter для возвращение в главное меню...')

    def check_license(self):
        if self.license is None:
            self.license = self.get_license()
        url = 'https://harvestersoft.ru/api/license/check'
        response = requests.get(url, json={
            'license_key': self.license,
            'mac_address': self.get_mac_address()
        }).json()
        
        if response['result']['isActive']:
            with open('license.txt', 'w') as file:
                file.write(self.license)
            return True
        else:
            if os.path.isfile('license.txt'):
                os.remove('license.txt')
            return False

    @staticmethod
    def get_mac_address():
        return ':'.join(re.findall('..', '%012x' % uuid.getnode()))

    @staticmethod
    def get_license():
        if os.path.isfile('license.txt'):
            with open('license.txt', 'r') as file:
                return file.read()
        else:
            license_key = input('Введите лицензионный ключ: ')
            return license_key

    def get_count(self):
        count = input('Введите количество аккаунтов (Enter для выбора всех аккаунтов): ')
        if count.isdigit():
            return int(count)
        elif count == '':
            return self.account_total
        else:
            print('\nВведите число!')
            return self.get_count()

    def choose_mode(self, modes) -> Tuple[str, Callable]:
        print()
        print('Доступные режимы:')
        for i, mode in enumerate(modes):
            print(f'\t{i + 1}. {mode[0]}')
        print()

        mode = input('Выберите режим: ')
        if mode.isdigit():
            mode = int(mode)
            if 0 < mode <= len(modes):
                item = modes[mode - 1][1]
                if callable(item):
                    return modes[mode - 1]
                elif isinstance(item, Iterable):
                    return self.choose_mode(item)
            else:
                print('\nНет такого режима!')
                self.choose_mode(modes)
        else:
            print('\nВведите число!')
            return self.choose_mode(modes)

    def get_modes(self):
        modes = (
            # ('Панель аккаунтов', ()),
            ('Чекер', self.check),
            ('Спам', (('Прямой спам', self.spam), ('Спам без пересечений', self.spam_without_crossings))),
            ('Парсинг', self.parse),
            ('Инвайт', self.invite),
            # ('Репорт', self.report)
        )
        return modes

    @property
    def account_total(self):
        files = os.listdir('Аккаунты')
        count = 0
        for file in files:
            if file.endswith('.session') and file.replace('.session', '.json') in files:
                count += 1
        return count

    def check(self):
        checker = Checker(self.account_count)
        checker.run()

    def spam(self):
        spammer = Spammer(self.account_count)
        spammer.run()

    def spam_without_crossings(self):
        spammer = Spammer(self.account_count, without_crossings=True, max_messages_with_one_text=config.spammer.max_messages_without_crossings)
        spammer.run()

    def repost_spam(self):
        pass

    def repost_spam_without_crossings(self):
        pass

    def parse(self):
        parser = Parser(self.account_count)
        parser.run()

    def invite(self):
        inviter = Inviter(self.account_count)
        inviter.run()

    def report(self):
        pass


logo = """
██╗  ██╗ █████╗ ██████╗ ██╗   ██╗███████╗███████╗████████╗███████╗██████╗ 
██║  ██║██╔══██╗██╔══██╗██║   ██║██╔════╝██╔════╝╚══██╔══╝██╔════╝██╔══██╗
███████║███████║██████╔╝██║   ██║█████╗  ███████╗   ██║   █████╗  ██████╔╝
██╔══██║██╔══██║██╔══██╗╚██╗ ██╔╝██╔══╝  ╚════██║   ██║   ██╔══╝  ██╔══██╗
██║  ██║██║  ██║██║  ██║ ╚████╔╝ ███████╗███████║   ██║   ███████╗██║  ██║
╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚══════╝╚══════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝
                                                                          
"""

if __name__ == '__main__':
    app = App()
    app.run()
