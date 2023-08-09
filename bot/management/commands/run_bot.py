import logging
from typing import Callable, Any

from django.core.management import BaseCommand
from django.conf import settings
import json

from bot.models import TgUser
from bot.tg.client import TgClient
from bot.tg.schemas import GetUpdatesResponse, SendMessageResponse, Message
from todolist_2.models import BaseModel


import logging

from django.core.management import BaseCommand
from django.conf import settings
import json

from bot.tg.client import TgClient
from bot.tg.schemas import GetUpdatesResponse, SendMessageResponse


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tg_client = TgClient()

    def handle(self, *args, **options):
        offset = 0
        self.stdout.write(self.style.SUCCESS('Bot started...'))
        while True:
            res = self.tg_client.get_updates(offset=offset, allowed_updates='message')
            for item in res.result:
                offset = item.update_id + 1
                self.handle_message(item.message)

    def handle_message(self, msg: Message):
        tg_user, _ = TgUser.objects.get_or_create(chat_id=msg.chat.id, defaults={'username': msg.chat.username})
        if not tg_user.is_verified:
            tg_user.update_verification_code()
            self.tg_client.send_message(msg.chat.id, f'Verification code: {tg_user.verification_code}')

        else:
            self.tg_client.send_message(msg.chat.id, f'You already verified')


        # self.tg_client.send_message(chat_id=msg.chat.id, text=msg.text)
        # print(msg)


#         tg_user, _ = TgUser.objects.get_or_create(chat_id=msg.chat.id, defaults={'username': msg.chat.username})
#         if not tg_user.is_verified:
#             tg_user.update_verification_code()
#             self.tg_client.send_message(msg.chat.id, f'Verification code: {tg_user.verification_code}')
#         else:
#             self.tg_client.send_message(msg.chat.id, 'You already verified')
















# class FSM(BaseModel):
#     next_handler: Callable
#     data: dict[str, Any] = {}


# class Command(BaseCommand):
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.tg_client = TgClient()
#         self.clients: dict[int, FSM] = {}
#
#     def handle(self, *args, **options):
#         offset = 0
#         self.stdout.write(self.style.SUCCESS('Bot started...'))
#         while True:
#             res = self.tg_client.get_updates(offset=offset, allowed_updates='message')
#             for item in res.result:
#                 offset = item.update_id + 1
#                 self.handle_message(item.message)
#
#     def handle_message(self, msg: Message):
#         tg_user, _ = TgUser.objects.get_or_create(chat_id=msg.chat.id, defaults={'username': msg.chat.username})
#         if not tg_user.is_verified:
#             tg_user.update_verification_code()
#             self.tg_client.send_message(msg.chat.id, f'Verification code: {tg_user.verification_code}')
#         else:
#             self.tg_client.send_message(msg.chat.id, 'You already verified')














            # self.handle_auth_user(tg_user, msg)









    # def handle_auth_user(self, tg_user: TgUser, msg: Message):
    #     if msg.text.startswith('/'):
    #         match msg.text:
    #             case '/goals':
    #                 ...
    #             case '/create':
    #                 ...
    #             case '/cancel':
    #                 ...
    #     else:
    #         ...
        # self.tg_client.send_message(msg.chat.id, 'You already verified')



