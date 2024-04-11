# -*- coding: utf-8 -*-
from telethon.errors.rpcerrorlist import *

exceptions = []
DEBUG = True

class SoftError:
    def __init__(self, rcp_errors, name, code: int = None, message: str = None, continue_work: bool = False):
        self.rcp_errors = rcp_errors
        self.name = name
        self.code = code
        self.message = message
        self.continue_work = continue_work


exceptions.append(SoftError(
    rcp_errors=(UserDeactivatedBanError, UserDeactivatedError, AuthKeyUnregisteredError, SessionRevokedError,
                AuthKeyDuplicatedError),
    name='banned',
    code=len(exceptions) + 1,
    message='Пользователь забанен.'), )

exceptions.append(SoftError(
    rcp_errors=(FloodError,),
    name='flood',
    code=len(exceptions) + 1,
    message='Пользователь получил флуд.',
    continue_work=True), )

exceptions.append(SoftError(
    rcp_errors=(ConnectionError,),
    name='connection_error',
    code=len(exceptions) + 1,
    message='Ошибка соединения.',
    continue_work=True), )

exceptions.append(SoftError(
    rcp_errors=(UsernameInvalidError, UsernameNotOccupiedError),
    name='user_not_found',
    code=len(exceptions) + 1,
    message='Пользователь не найден.',
    continue_work=True), )

exceptions.append(SoftError(
    rcp_errors=(ChatWriteForbiddenError,),
    name='chat_forbidden',
    code=len(exceptions) + 1,
    message='Вы не можете отправлять сообщения в этот чат.',
    continue_work=True), )

exceptions.append(SoftError(
    rcp_errors=(ChannelPrivateError,),
    name='channel_private_error',
    code=len(exceptions) + 1,
    message='Аккаунт в этом чате был заблокирован или не имеет доступа.',
    continue_work=True), )

exceptions.append(SoftError(
    rcp_errors=(ChannelsTooMuchError,),
    name='too_much_channels',
    code=len(exceptions) + 1,
    message='Слишком много каналов.',
    continue_work=True), )

exceptions.append(SoftError(
    rcp_errors=(Exception,),
    name='unknown',
    code=len(exceptions) + 1,
    message='Неизвестная ошибка.',
    continue_work=True), )

def handler(func):
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            for exception in exceptions:
                for exception_type in exception.rcp_errors:
                    if isinstance(e, exception_type):
                        return exception, e

            return None, e
    return wrapper


def sync_handler(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except RPCError as e:
            for exception in exceptions:
                for exception_type in exception.rcp_errors:
                    if isinstance(e, exception_type):
                        return exception
            print('Неизвестная ошибка:', type(e), e)
        except Exception as e:
            print('Неизвестная ошибка:', type(e), e)

    return wrapper
