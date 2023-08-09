import logging

from django.core.management import BaseCommand
from django.conf import settings
import json

from bot.tg.client import TgClient
from bot.tg.schemas import GetUpdatesResponse, SendMessageResponse


class Command(BaseCommand):
    def handle(self, *args, **options):
        get_path = settings.BASE_DIR.joinpath('tg_get_response.json')
        send_path = settings.BASE_DIR.joinpath('tg_send_response.json')

        with open(get_path) as file:
            get_data = json.load(file)
            get_response = GetUpdatesResponse(**get_data)
            print(get_response)

        with open(send_path) as file:
            send_data = json.load(file)
            send_response = SendMessageResponse(**send_data)
            print(send_response)

        client = TgClient()
        client.send_message(220824307, text='bot works')
        # print(client.get_updates())
