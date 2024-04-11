from configparser import ConfigParser
from telethon.tl.types import UserStatusRecently, UserStatusLastWeek, UserStatusLastMonth, UserStatusOnline
from telethon.tl.types import ChannelParticipantsAdmins, ChannelParticipantsBots


class GeneralConfig:
    def __init__(self):
        self.configfile = ConfigParser()
        self.configfile.read('config.ini', encoding='utf-8')
        self.config = self.configfile['GENERAL']

    @property
    def start_delay(self):
        first_num, second_num = self.config['start_delay'].split('-')
        return int(first_num), int(second_num)

    @property
    def auto_reconnect(self):
        if self.config['auto_reconnect'] in ['false', 'False', '0', '']:
            return False
        else:
            return True

    @property
    def reconnect_timeout(self):
        return int(self.config['reconnect_timeout'])

    @property
    def threads(self):
        return int(self.config['threads'])

    @property
    def proxy_type(self):
        return self.config['proxy_type']

    @property
    def max_flood_sleep(self):
        return int(self.config['максимум_ожидание_при_флуде'])


class ToolsConfig:
    def __init__(self):
        self.configfile = ConfigParser()
        self.configfile.read('config.ini', encoding='utf-8')
        self.config = self.configfile['TOOLS']

    @property
    def avatars(self):
        if int(self.config['avatars']) != 0:
            return int(self.config['avatars'])
        else:
            return None

class SpammerConfig:
    def __init__(self):
        self.configfile = ConfigParser()
        self.configfile.read('config.ini', encoding='utf-8')
        self.config = self.configfile['Спам']
        self.directory = 'Файлы/Спам'

    @property
    def users(self):
        with open(f'{self.directory}/Пользователи.txt', 'r') as file:
            return file.read().splitlines()

    @property
    def delay(self):
        try:
            first_num, second_num = self.config['задержка_между_сообщениями'].split('-')
            return int(first_num), int(second_num)
        except ValueError:
            first_num = self.config['delay']
            return int(first_num)
        except Exception as e:
            print(f"[ERROR] {e}")

    @property
    def max_messages(self):
        return int(self.config['максимум_сообщений'])

    @property
    def max_messages_without_crossings(self):
        return int(self.config['отправлять_каждый_текст'])

    @property
    def randomly(self):
        if self.config['случайный_текст'] == 'да':
            return True
        else:
            return False


class CheckerConfig:
    def __init__(self):
        self.configfile = ConfigParser()
        self.configfile.read('config.ini', encoding='utf-8')
        self.config = self.configfile['CHECKER']

    @property
    def check_type(self):
        return self.config['check_type']

    @property
    def is_fast_check(self):
        if self.config['check_type'] == 'fast':
            return True
        else:
            return False

    @property
    def max_chats(self):
        return int(self.config['max_chats'])

class ReporterConfig:
    def __init__(self):
        self.configfile = ConfigParser()
        self.configfile.read('config.ini', encoding='utf-8')
        self.config = self.configfile['REPORTER']
        self.directory = 'Репортер'
        self.path = f'{self.directory}/Результат/'

    @property
    def targets(self):
        with open(f'{self.directory}/Таргет.txt', 'r', encoding='utf-8') as file:
            return file.read().splitlines()

    @property 
    def messages(self):
        with open(f'{self.directory}/Сообщения.txt', 'r', encoding='utf-8') as file:
            return file.read().splitlines()

    @property
    def accounts(self):
        with open(f'{self.directory}/Аккаунты.txt', 'r', encoding='utf-8') as file:
            return file.read().splitlines()

    @property
    def delay(self):
        try:
            first_num, second_num = self.config['delay'].split('-')
            return first_num, second_num
        except ValueError:
            first_num = self.config['delay']
            return first_num
        except Exception as e:
            print(f"[ERROR] {e}")

    @property
    def reports(self):
        get_reports = self.config['reports']
        return int(get_reports)
    

class ParserConfig:
    def __init__(self):
        self.configfile = ConfigParser()
        self.configfile.read('config.ini', encoding="utf-8")
        self.config = self.configfile['PARSER']
        self.directory = "Файлы/Парсер"
        self.path = f"{self.directory}/Результат/"
        self._statuses = {
            'online': UserStatusOnline,
            'recently': UserStatusRecently,
            'last_week': UserStatusLastWeek,
            'last_month': UserStatusLastMonth,
        }
        self._targets = {
            'admins': ChannelParticipantsAdmins,
            'bots': ChannelParticipantsBots,
        }

    @property
    def chats(self):
        with open(f'{self.directory}/Чаты.txt', 'r', encoding='utf-8') as file:
            return file.read().splitlines()

    @property
    def delay(self):
        try:
            first_num, second_num = self.config['задержка_между_чатами'].split('-')
            return int(first_num), int(second_num)
        except ValueError:
            first_num = self.config['задержка_между_чатами']
            return int(first_num)
        except Exception as e:
            print(f"[ERROR] {e}")

    @property
    def max_chats(self):
        return int(self.config['максимум_чатов_с_аккаунта'])

    @property
    def photo(self):
        if self.config['парсить_с_фото'].lower() == 'да':
            return True
        if self.config['парсить_с_фото'].lower() == 'нет':
            return False

    @property
    def leave(self):
        if self.config['выходить_после_парсинга'].lower() == 'да':
            return True
        if self.config['выходить_после_парсинга'].lower() == 'нет':
            return False

    @property
    def online_min(self) -> int:
        days_online = self.config['онлайн_последние_дней']
        hours_online = self.config['онлайн_последние_часов']
        days = int(days_online) * 24
        hours = int(hours_online)
        return hours + days

    @property
    def online_max(self) -> int:
        days_online = self.config['максимальный_онлайн_последние_дней']
        hours_online = self.config['максимальный_онлайн_последние_часов']
        days = int(days_online) * 24
        hours = int(hours_online)
        return hours + days
    
    @property
    def targets(self):
        default_users = self.config['пользователи']
        admins = self.config['админы']
        bots = self.config['боты']
        _participants = [ChannelParticipantsAdmins, ChannelParticipantsBots]
        participants = []
        if default_users.lower() == "да":
            participants.append("users")
        if admins.lower() == "да":
            participants.append(ChannelParticipantsAdmins)
        if bots.lower() == "да":
            participants.append(ChannelParticipantsBots)
        return participants

    @property
    def statuses(self):
        online = self.config['сейчас_онлайн']
        recently = self.config['был_недавно']
        last_week = self.config['был_неделю_назад']
        last_month = self.config['был_месяц_назад']
        _statuses = [online, recently, last_week, last_month]
        statuses = []
        if online.lower() == "да":
            statuses.append(UserStatusOnline)
        if recently.lower() == "да":
            statuses.append(UserStatusRecently)
        if last_week.lower() == "да":
            statuses.append(UserStatusLastWeek)
        if last_month.lower() == "да":
            statuses.append(UserStatusLastMonth)
        return statuses


class InviterConfig:
    def __init__(self):
        self.directory = 'Файлы/Инвайт'
        self.configfile = ConfigParser()
        self.configfile.read('config.ini', encoding='utf-8')
        self.config = self.configfile['INVITER']

    @property
    def target(self):
        with open(f'{self.directory}/Таргет.txt', 'r') as file:
            return file.read()

    @property
    def users(self):
        with open(f'{self.directory}/Пользователи.txt', 'r') as file:
            return file.read().splitlines()

    @property
    def delay(self):
        first_num, second_num = self.config['задержка_между_приглашениями'].split('-')
        return int(first_num), int(second_num)

    @property
    def max_users(self):
        return int(self.config['максимум_пользователей'])

    @property
    def users_per_request(self):
        return int(self.config['пользователей_за_приглашение'])


class Config:
    def __init__(self):
        self.general = GeneralConfig()
        self.tools = ToolsConfig()
        self.spammer = SpammerConfig()
        self.checker = CheckerConfig()
        self.parser = ParserConfig()
        self.inviter = InviterConfig()
        self.reporter = ReporterConfig()


config = Config()