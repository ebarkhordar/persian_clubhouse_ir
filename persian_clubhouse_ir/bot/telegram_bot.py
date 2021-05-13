#!/usr/bin/env python
# pylint: disable=C0116
# This program is dedicated to the public domain under the CC0 license.

import logging
from typing import Dict

import phonenumbers
from telegram import ReplyKeyboardMarkup, Update, ReplyKeyboardRemove
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)

from persian_clubhouse_ir.bot.clubhouse import Clubhouse
from persian_clubhouse_ir.bot.const import Keyboard, MessageText
from persian_clubhouse_ir.bot.models import Profile
from persian_clubhouse_ir.settings import env, MY_CLUBHOUSE_USER_ID

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

CHOOSING, PHONE_NUMBER, INSTAGRAM_USERNAME, CLUBHOUSE_VERIFICATION_CODE, TYPING_REPLY, TYPING_CHOICE = range(6)

reply_keyboard = [
    [Keyboard.update_instagram_account],
    [Keyboard.about_us],
]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

clubhouse = Clubhouse()


def facts_to_str(user_data: Dict[str, str]) -> str:
    facts = list()

    for key, value in user_data.items():
        facts.append(f'{key} - {value}')

    return "\n".join(facts).join(['\n', '\n'])


def start(update: Update, _: CallbackContext) -> int:
    update.message.reply_text(MessageText.start, reply_markup=markup)
    return CHOOSING


def instagram_account(update: Update, _: CallbackContext) -> int:
    update.message.reply_text(MessageText.enter_your_phone_number)
    update.message.reply_text(MessageText.price_message)
    return PHONE_NUMBER


def get_phone_number(update: Update, context: CallbackContext) -> int:
    phone_number = update.message.text
    if not phone_number.replace('+', '').isdigit():
        update.message.reply_text(MessageText.not_valid_phone_number)
        update.message.reply_text(MessageText.enter_your_phone_number)
        return PHONE_NUMBER
    phone_number = phonenumbers.parse(phone_number, "IR")
    if phonenumbers.is_possible_number(phone_number) is False:
        update.message.reply_text(MessageText.not_valid_phone_number)
        update.message.reply_text(MessageText.enter_your_phone_number)
        return PHONE_NUMBER
    phone_number = phonenumbers.format_number(phone_number, phonenumbers.PhoneNumberFormat.E164)
    context.user_data['phone_number'] = phone_number
    clubhouse.start_phone_number_auth(phone_number)
    update.message.reply_text(MessageText.enter_your_instagram_username)
    return INSTAGRAM_USERNAME


def get_instagram_username(update: Update, context: CallbackContext) -> int:
    instagram_username = update.message.text
    context.user_data['instagram_username'] = instagram_username
    update.message.reply_text(MessageText.enter_your_clubhouse_verification_code)
    return CLUBHOUSE_VERIFICATION_CODE


def get_clubhouse_verification_code(update: Update, context: CallbackContext) -> int:
    verification_code = update.message.text
    telegram_user = update.message.from_user
    telegram_username = telegram_user.username
    telegram_user_id = telegram_user.id
    telegram_name = telegram_user.name
    phone_number = context.user_data['phone_number']
    instagram_username = context.user_data['instagram_username']
    result = clubhouse.complete_phone_number_auth(phone_number, verification_code)
    if result.get('success') is False:
        update.message.reply_text(MessageText.failure_instagram_username_update)
        return ConversationHandler.END
    user_profile = result.get("user_profile")
    clubhouse_user_id = user_profile.get('user_id')
    clubhouse_username = user_profile.get('username')
    profile, created = Profile.objects.update_or_create(
        telegram_user_id=telegram_user_id,
        defaults={
            'telegram_username': telegram_username,
            'telegram_name': telegram_name,
            'clubhouse_user_id': clubhouse_user_id,
            'clubhouse_username': clubhouse_username,
            'clubhouse_phone_number': phone_number,
            'clubhouse_auth_token': result['auth_token'],
            'instagram_username': instagram_username,
        }
    )

    new_clubhouse = Clubhouse(user_id=str(profile.clubhouse_user_id), user_token=profile.clubhouse_auth_token)
    new_clubhouse.update_instagram_username(instagram_username)
    if result.get('success') is True:
        new_clubhouse.follow(user_id=MY_CLUBHOUSE_USER_ID)
        update.message.reply_text(MessageText.success_instagram_username_update)
    else:
        update.message.reply_text(MessageText.failure_instagram_username_update)
    return ConversationHandler.END


def about_us(update: Update, _: CallbackContext) -> int:
    update.message.reply_text(
        MessageText.about_us
    )
    return ConversationHandler.END


def done(update: Update, context: CallbackContext) -> int:
    user_data = context.user_data
    update.message.reply_text(MessageText.fallbacks,
                              reply_markup=ReplyKeyboardRemove(),
                              )
    user_data.clear()
    return ConversationHandler.END


def cancel(update: Update, context: CallbackContext) -> int:
    user_data = context.user_data
    update.message.reply_text(MessageText.cancel,
                              reply_markup=ReplyKeyboardRemove(),
                              )
    user_data.clear()
    return ConversationHandler.END


def run_bot() -> None:
    # Create the Updater and pass it your bot's token.
    updater = Updater(env.str("TELEGRAM_BOT_TOKEN"))

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Add conversation handler with the states CHOOSING, TYPING_CHOICE and TYPING_REPLY
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING: [
                MessageHandler(
                    Filters.regex('^' + Keyboard.update_instagram_account + '$'), instagram_account
                ),
                MessageHandler(
                    Filters.regex('^' + Keyboard.about_us + '$'), about_us
                ),
            ],
            PHONE_NUMBER: [
                CommandHandler('cancel', cancel),
                MessageHandler(Filters.text, get_phone_number, ),
            ],
            INSTAGRAM_USERNAME: [
                CommandHandler('cancel', cancel),
                MessageHandler(Filters.text, get_instagram_username, ),
            ],
            CLUBHOUSE_VERIFICATION_CODE: [
                CommandHandler('cancel', cancel),
                MessageHandler(Filters.text, get_clubhouse_verification_code, ),
            ],

        },
        fallbacks=[MessageHandler(Filters.regex('^Done$'), done)],

    )

    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(
        MessageHandler(Filters.regex('^' + Keyboard.update_instagram_account + '$'), instagram_account),
    )
    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()
