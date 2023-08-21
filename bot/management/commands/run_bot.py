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
    """Класс функционала телеграм-бота.
    Команды: вывод целей, создание цели."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tg_client = TgClient()
        self.clients: dict[int, FSM] = {}

    def handle(self, *args, **options):
        """Функция по обработке старых сообщений"""
        offset = 0
        self.stdout.write(self.style.SUCCESS('Bot started...'))
        old_messages = self.tg_client.get_updates(offset=offset).result
        while True:
            new_message = self.tg_client.get_updates(offset=offset)
            for item in new_message.result:
                offset = item.update_id + 1
                if item not in old_messages:
                    self.handle_message(item.message)

    def handle_message(self, msg: Message):
        """Функция по верификации пользователя"""
        tg_user, _ = TgUser.objects.get_or_create(chat_id=msg.chat.id, defaults={'username': msg.chat.username})
        if not tg_user.is_verified:
            tg_user.update_verification_code()
            self.tg_client.send_message(msg.chat.id, f'Verification code: {tg_user.verification_code}')

        else:
            self.tg_user_auth(tg_user, msg)

    def tg_user_auth(self, tg_user: TgUser, msg: Message):
        """Функция по обработке команд от пользователя"""
        if msg.text.startswith('/'):
            match msg.text:
                case '/goals':
                    self.get_goals_list(tg_user.chat_id, msg)
                case '/create':
                    self.create_goal(tg_user.chat_id, msg)
                case '/cancel':
                    self.clients.pop(tg_user.chat_id, None)
        elif tg_user.chat_id in self.clients:
            if msg.text.startswith('cat-'):
                self.choose_category_for_goal(tg_user.chat_id, msg)
            elif self.clients[tg_user.chat_id].data['category'] is not None:
                self.save_new_goal(tg_user.chat_id, msg)
            else:
                self.tg_client.send_message(msg.chat.id, 'Unknown command')
        else:
            self.tg_client.send_message(msg.chat.id, 'Unknown command')

    def get_goals_list(self, chat_id, msg: Message) -> None:
        """Функция по получению списка целей"""
        tg_user = TgUser.objects.get(chat_id=chat_id)
        user = User.objects.get(tguser=tg_user)
        goals_list = [goal.title for goal in Goal.objects.filter(
            user=user,
            category__is_deleted=False,
        ).exclude(status=Goal.Status.archived)]
        self.tg_client.send_message(msg.chat.id, f'Your goals: {", ".join(goals_list)}')

    def create_goal(self, chat_id, msg: Message) -> None:
        """Функция по созданию цели"""
        tg_user = TgUser.objects.get(chat_id=chat_id)
        user = User.objects.get(tguser=tg_user)

        categories_list = (category.title for category in GoalCategory.objects.filter(user=user, is_deleted=False))
        self.tg_client.send_message(msg.chat.id, f'Categories: {", ".join(categories_list)}.'
                                                 f'\nChoose number of category.'
                                                 f'\nValid format is: (cat-1, cat-2, cat-3 ...).')
        self.clients[chat_id] = FSM()
        self.clients[chat_id].next_handler = self.choose_category_for_goal

    def choose_category_for_goal(self, chat_id, msg: Message) -> None:
        """Функция по выбору категории для создания в ней цели"""
        if not msg.text.startswith('cat-'):
            self.tg_client.send_message(msg.chat.id, f'Valid format is integer (1, 2, 3...). '
                                                     f'\nPlease, try again.')
        else:
            tg_user = TgUser.objects.get(chat_id=chat_id)
            user = User.objects.get(tguser=tg_user)
            categories_list = list((GoalCategory.objects.filter(user=user, is_deleted=False)))
            category_number = int(msg.text.split("-")[1])
            chosen_category = categories_list[category_number - 1]
            self.clients[chat_id].data.update({'category': chosen_category})
            self.tg_client.send_message(msg.chat.id, f'Selected category: "{chosen_category.title}". Please,set title.')
            self.clients[chat_id] = FSM()
            self.clients[chat_id].next_handler = self.save_new_goal

    def save_new_goal(self, chat_id, msg: Message) -> None:
        """Функция по сохранению созданной цели"""
        chosen_category = self.clients[chat_id].data['category']
        tg_user = TgUser.objects.get(chat_id=chat_id)
        user = User.objects.get(tguser=tg_user)
        new_goal = Goal.objects.create(title=msg.text, user=user, category=chosen_category)
        new_goal.save()
        self.tg_client.send_message(msg.chat.id, f'Goal created in category: "{chosen_category.title}". '
                                                 f'\nTitle: "{msg.text}".')
        self.clients.pop(chat_id, None)
