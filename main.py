from typing import List

import flet as ft
from langchain.schema import HumanMessage, SystemMessage
from langchain.chat_models.gigachat import GigaChat



class Message():
    def __init__(self, user_name: str, text: str, message_type: str):
        self.user_name = user_name
        self.text = text
        self.message_type = message_type


class ChatMessage(ft.Row):
    def __init__(self, message: Message):
        super().__init__()
        self.vertical_alignment = "start"
        self.controls = [
            ft.CircleAvatar(
                content=ft.Text(self.get_initials(message.user_name)),
                color=ft.colors.WHITE,
                bgcolor=self.get_avatar_color(message.user_name),
            ),
            ft.Column(
                [
                    ft.Text(message.user_name, weight="bold"),
                    ft.Text(message.text, selectable=True),

                ],
                tight=True,
                spacing=5,
                width=400
            ),
        ]

    def get_initials(self, user_name: str):
        if user_name:
            return user_name[:1].capitalize()
        else:
            return "Unknown"  # or any default value you prefer

    def get_avatar_color(self, user_name: str):
        colors_lookup = [
            ft.colors.AMBER,
            ft.colors.BLUE,
            ft.colors.BROWN,
            ft.colors.CYAN,
            ft.colors.GREEN,
            ft.colors.INDIGO,
            ft.colors.LIME,
            ft.colors.ORANGE,
            ft.colors.PINK,
            ft.colors.PURPLE,
            ft.colors.RED,
            ft.colors.TEAL,
            ft.colors.YELLOW,
        ]
        return colors_lookup[hash(user_name) % len(colors_lookup)]


def main(page: ft.Page):
    page.title = 'MindTrack'
    page.horizontal_alignment = "stretch"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    bot = GigaChat(
        credentials='auth_token',  ##token
        verify_ssl_certs=False)

    messages = [
        SystemMessage(
            content="Ты эмпатичный бот-психолог, который помогает пользователю решить его проблемы."
        )
    ]

    def authorization(e):
        if user_login.value == 'admin' and user_pass.value == 'admin':
            page.session.set("user_name", user_login.value)
            page.dialog.open = False
            new_message.prefix = ft.Text(f"{user_login.value}: ")
            page.pubsub.send_all(Message(user_name=user_login.value, text=f"{user_login.value} has joined the chat.",
                                         message_type="login_message"))
            page.update()
        else:
            page.snack_bar = ft.SnackBar(ft.Text('Неверно введены данные'))
            page.snack_bar.open = True
            page.update()

    def send_message_click(e):
        if new_message.value != "":
            page.pubsub.send_all(Message(page.session.get("user_name"), new_message.value, message_type="chat_message"))
            user_input = str(new_message.value)
            new_message.value = ""
            messages.append(HumanMessage(content=user_input))
            res = bot(messages)
            page.pubsub.send_all(Message('MindBot', res.content, message_type="chat_message"))
            new_message.value = ""
            new_message.focus()
            page.update()

    def on_message(message: Message):
        if message.message_type == "chat_message":
            m = ChatMessage(message)
        elif message.message_type == "login_message":
            m = ft.Text(message.text, italic=True, color=ft.colors.RED_100, size=12)
        chat.controls.append(m)
        page.update()

    # Validate date
    def validate(e):
        if all([user_login.value, user_pass.value]):
            btn_auth.disabled = False
        else:
            btn_auth.disabled = True

        page.update()

    page.pubsub.subscribe(on_message)

    user_login = ft.TextField(
        label='Логин',
        width=250,
        on_change=validate)

    user_pass = ft.TextField(
        label='Пароль',
        width=250,
        on_change=validate)

    btn_auth = ft.OutlinedButton(
        text='Авторизоваться',
        width=250,
        on_click=authorization,
        disabled=True)

    page.dialog = ft.AlertDialog(
        open=True,
        modal=True,
        title=ft.Text("Авторизация"),
        content=ft.Column([user_login, user_pass], width=250, height=120, tight=True),
        actions=[btn_auth],
        actions_alignment=ft.MainAxisAlignment.CENTER
    )
    # Chat messages
    chat = ft.ListView(
        expand=True,
        spacing=10,
        auto_scroll=True,
    )

    # A new message entry form
    new_message = ft.TextField(
        hint_text="Write a message...",
        autofocus=True,
        shift_enter=True,
        min_lines=1,
        max_lines=5,
        filled=True,
        expand=True,
        on_submit=send_message_click,
    )

    # Add everything to the page
    page.add(
        ft.Container(
            content=chat,
            border=ft.border.all(1, ft.colors.OUTLINE),
            border_radius=5,
            padding=10,
            expand=True,
        ),
        ft.Row(
            [
                new_message,
                ft.IconButton(
                    icon=ft.icons.SEND_ROUNDED,
                    tooltip="Send message",
                    on_click=send_message_click,
                ),
            ]
        ),
    )


ft.app(main)
