import asyncio
import logging
from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Iterable

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, Update, error
from telegram.ext import ApplicationHandlerStop, BaseHandler, CallbackQueryHandler, CommandHandler, MessageHandler, TypeHandler, filters

from src.core.bot import Bot, UserID
from src.support.upspike_threshold import UpspikeThreshold



logger = logging.getLogger(__name__)



class _Panel(ABC):
    @classmethod
    @abstractmethod
    def create_handlers(cls) -> list[BaseHandler]:
        ...



class _UpspikeThresholdPanel(_Panel):
    BUTTON_NAME = UpspikeThreshold.get_name(title_case=True)
    TEXT = f'Adjust the {UpspikeThreshold.get_name()} using buttons below:'

    class _Value:
        STEP = 0.1
        MIN = 0.1
        MAX = 3

    class _Button(str, Enum):
        def _generate_next_value_(name, start, count, last_values):
            """
            Generates callback data unique across the whole bot
            """
            return f'{UpspikeThreshold.get_name(separator="_")}_{count}'

        DECREASE = auto()
        VALUE = auto()
        INCREASE = auto()

    lock = asyncio.Lock()


    @classmethod
    def create_handlers(cls) -> list[BaseHandler]:
        return [
            MessageHandler(filters.Regex(f'^{cls.BUTTON_NAME}$'), cls._send),  # send original message
            CallbackQueryHandler(cls._adjust_value, pattern='|'.join(cls._Button)),  # adjust value and message
        ]

    @classmethod
    def _create_markup(cls):
        return InlineKeyboardMarkup([[
            InlineKeyboardButton('➖', callback_data=cls._Button.DECREASE),
            InlineKeyboardButton(f'{UpspikeThreshold.get():.0%}', callback_data=cls._Button.VALUE),
            InlineKeyboardButton('➕', callback_data=cls._Button.INCREASE)
        ]])

    @classmethod
    async def _send(cls, update: Update, _):
        await update.message.reply_text(text=cls.TEXT, reply_markup=cls._create_markup())

    @classmethod
    async def _adjust_value(cls, update: Update, _):
        query = update.callback_query
        await query.answer()

        async with cls.lock:  # exclude race condition
            match query.data:
                case cls._Button.DECREASE:
                    if (value := UpspikeThreshold.get() - cls._Value.STEP) >= cls._Value.MIN:
                        await UpspikeThreshold.set(value)

                case cls._Button.INCREASE:
                    if (value := UpspikeThreshold.get() + cls._Value.STEP) <= cls._Value.MAX:
                        await UpspikeThreshold.set(value)

        try:
            await query.edit_message_text(text=cls.TEXT, reply_markup=cls._create_markup())
        except error.BadRequest as e:  # ignore exception about same content after editing
            if 'specified new message content and reply markup are exactly the same' not in str(e): raise



class _StartPanel(_Panel):
    COMMAND_NAME = 'start'
    COMMAND_DESCRIPTION = 'Start the bot and get menu'
    TEXT = 'Menu has been pinned to your input area'

    @classmethod
    def create_handlers(cls) -> list[BaseHandler]:
        return [
            CommandHandler(cls.COMMAND_NAME, cls._send),  # send start message on corresponding command
        ]

    @classmethod
    async def _send(cls, update: Update, _):
        markup = ReplyKeyboardMarkup([[KeyboardButton(_UpspikeThresholdPanel.BUTTON_NAME)]], resize_keyboard=True)
        await update.message.reply_text(text=cls.TEXT, reply_markup=markup)



class CustomBot(Bot):
    def __init__(self, whitelist: Iterable[UserID], **kwargs):
        super().__init__(**kwargs)
        self.whitelist = whitelist
        self.commands = [
            (_StartPanel.COMMAND_NAME, _StartPanel.COMMAND_DESCRIPTION),
        ]
        self.add_handlers(
            TypeHandler(Update, self._authorize_access),  # filter updates based on whitelist
            group=0,
        )
        self.add_handlers(
            *_StartPanel.create_handlers(),
            *_UpspikeThresholdPanel.create_handlers(),
            group=1,
        )

    async def init(self):
        await self.set_my_commands(self.commands)

    async def _authorize_access(self, update: Update, _):
        user = update.effective_user

        if user.id not in self.whitelist:
            if update.message:
                update_repr = f'Message: {update.message.text}'
            elif update.my_chat_member:
                update_repr = f'New member status: {update.my_chat_member.new_chat_member.status}'
            else:
                update_repr = f'Update: {update}'

            logger.warning(f'Unauthorized access from: {user.full_name} @{user.username if user.username else ""} #{user.id}. {update_repr}')
            raise ApplicationHandlerStop
