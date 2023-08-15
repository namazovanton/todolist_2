from typing import Callable, Any

from todolist_2.models import BaseModel


class FSM(BaseModel):
    next_handler: Callable
    data: dict[str, Any] = {}


users: dict[int, FSM] = {}

CATEGORIES = ('ONE', 'TWO', 'THREE')


def main(chat_id, msg):
    if msg == '/create':
        handler_create_goal_command(chat_id, msg)
    elif msg == '/cancel':
        users.pop(chat_id, None)
    elif chat_id in users:
        users[chat_id].next_handler(chat_id, msg)


def handler_create_goal_command(chat_id, msg):
    print(f'Categories: {CATEGORIES}')
    users[chat_id] = FSM(next_handler=send_handler)


def send_handler(chat_id, msg):
    cat = CATEGORIES[int(msg)-1]
    users[chat_id].data.update({'category': cat})

    print(f'Select category {cat}')

    print(f'Set title')
    users[chat_id].next_handler = third_handler


def third_handler(chat_id, msg):
    cat = users[chat_id].data['category']
    # goal.create
    print(f'Goal created with cat:"{cat}", title={msg}')
    users.pop(chat_id, None)


if __name__ == '__main__':
    main(10, '/create')
    main(10, '1')
    main(10, 'New goal')

