from .config import config

from .models import Soft, Account
from .tools import move_accounts
import asyncio
import time
from .async_google_trans_new import AsyncTranslator

max_threads = config.general.threads


async def threaded_check(thread, accounts, fast=False):
    while True:
        try:
            account = await accounts.__anext__()
            await account.check(thread, fast=fast)

        except StopIteration:
            break
        except StopAsyncIteration:
            break
        except Exception as e:
            print(e)
            break


async def check_account_generator(accounts_list: list):
    for account in accounts_list:
        yield account


async def check(accounts, threads=max_threads):
    tasks = []

    if len(accounts) < threads:
        threads = len(accounts)

    ths = [_ for _ in range(threads)]

    account_gen = check_account_generator(accounts)

    start_time = time.perf_counter()
    athread = 1
    for _ in ths:
        task = asyncio.create_task(threaded_check(athread, account_gen, config.checker.is_fast_check))
        tasks.append(task)
        athread += 1

    await asyncio.gather(*tasks)

    end_time = time.perf_counter()
    print(f'Проверка завершена! Время выполнения: {round(end_time - start_time)} секунд')

    ok_accounts = []
    spamblock_accounts = []
    banned_accounts = []
    not_checked = []

    for account in accounts:
        await account.disconnect()
        if account.status:
            if account.status.status == 'SPAMBLOCK':
                spamblock_accounts.append(account)
            elif account.status.status == 'BANNED':
                banned_accounts.append(account)
            elif account.status.status == 'NO_LIMITS':
                ok_accounts.append(account)
            else:
                not_checked.append(account)
        else:
            not_checked.append(account)
    print(f'\nАккаунтов без ограничений: {len(ok_accounts)}'
          f'\nАккаунтов со спамблоком: {len(spamblock_accounts)}'
          f'\nАккаунтов в бане: {len(banned_accounts)}'
          f'\nАккаунтов не проверено: {len(not_checked)}')
    if ok_accounts:
        await move_accounts(ok_accounts, 'Чекер/Живые')

    if spamblock_accounts:
        await move_accounts(spamblock_accounts, 'Чекер/Спамблок')

    if banned_accounts:
        await move_accounts(banned_accounts, 'Чекер/Бан')

    if not_checked:
        await move_accounts(not_checked, 'Чекер/Не проверено')


class Checker(Soft):
    def __init__(self, accounts_count: int = None):
        super().__init__(accounts_count=accounts_count, advanced_log=False)
        self.translator = AsyncTranslator()

    async def on_start(self):
        self.log('Чек запущен!')

    async def on_finish(self):
        self.log(f'Чек завершен! Проверено {self.stats.success} аккаунтов.')

    async def do(self, account: Account, _):

        await account.client.send_message('https://t.me/SpamBot', '/start')
        last_message = await account.client.get_messages('https://t.me/SpamBot', limit=1)
        original_answer = last_message[0].text
        answer = await self.translator.translate(original_answer, lang_tgt='en')

        if 'free' in answer:
            account.log('Аккаунт без ограничений')
        elif 'limited' in answer:
            account.log('Аккаунт ограничен')

        return True, None

    async def on_error(self, account: Account, error=None, result=None):

        pass

