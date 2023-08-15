from typing import Callable, Any
from bot.models import TgUser
from bot.tg.schemas import Message
from core.models import User
from goals.models import Goal, GoalCategory
from todolist_2.models import BaseModel
from django.core.management import BaseCommand
from bot.tg.client import TgClient


class FSM(BaseModel):
    next_handler: Callable
    data: dict[str, Any] = {}


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tg_client = TgClient()
        self.clients: dict[int, FSM] = {}

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
            self.tg_user_auth(tg_user, msg)

    def tg_user_auth(self, tg_user: TgUser, msg: Message):
        if msg.text.startswith('/'):
            match msg.text:
                case '/goals':
                    goals_list = list(Goal.objects.filter(
                        category__board__participants__user=tg_user,
                        category__is_deleted=False
                    ).exclude(status=Goal.Status.archived))
                    self.tg_client.send_message(msg.chat.id, f'Your goals: {goals_list}')
                case '/create':
                    self.create_goal(tg_user.chat_id, msg)
                case '/cancel':
                    self.clients.pop(tg_user.chat_id, None)

        else:
            self.tg_client.send_message(msg.chat.id, 'Unknown command')

    def create_goal(self, chat_id, msg):
        """Функция по созданию цели"""
        categories_list = list(GoalCategory.objects.filter(user=self.clients[chat_id], is_deleted=False))
        self.tg_client.send_message(msg.chat.id, f'Categories: {categories_list}')
        self.clients[chat_id] = FSM(next_handler=self.choose_category_for_goal)

    def choose_category_for_goal(self, chat_id, msg):
        """Функция по выбору категории для создания в ней цели"""
        categories_list = list(GoalCategory.objects.filter(user=self.clients[chat_id], is_deleted=False))

        chosen_category = categories_list[int(msg)-1]
        self.clients[chat_id].data.update({'category': chosen_category})
        self.tg_client.send_message(msg.chat.id, f'Selected category: "{chosen_category}". Please,set title.')
        self.clients[chat_id].next_handler = self.save_new_goal

    def save_new_goal(self, chat_id, msg):
        chosen_category = self.clients[chat_id].data['category']
        self.tg_client.send_message(msg.chat.id, f'Goal created in category: "{chosen_category}". Title: "{msg}".')

        new_goal = Goal.objects.create(title=msg, user=self.clients[chat_id], category=chosen_category)
        new_goal.save()
        self.clients.pop(chat_id, None)
