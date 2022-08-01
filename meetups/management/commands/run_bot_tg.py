import os
import re
from functools import partial

import telegram
from django.core.management.base import BaseCommand
from environs import Env
from jinja2 import Environment, FileSystemLoader
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import LabeledPrice, Update
from telegram.ext import (
    CallbackContext,
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackQueryHandler,
    PreCheckoutQueryHandler
)

from meetups import views, models
from python_meetup.settings import BASE_DIR

TEMPLATES_PATH = os.path.join(BASE_DIR, 'meetups', 'templates', 'bot', '')


def start(update, context, jinja):
    template = jinja.get_template('title.txt')
    query = update.callback_query
    user, user_created = models.Visitor.objects.get_or_create(telegram_id=update.effective_chat.id)

    if query:
        query.answer()

    buttons_md = [
        [
            InlineKeyboardButton(
                text='Показать мероприятия',
                callback_data='show_events'
            ),
            InlineKeyboardButton(
                text='Добавить/изменить свою анкету',
                callback_data='show_account'
            ),
            InlineKeyboardButton(
                text='Донат',
                callback_data='donate_processing'
            ),
        ],
    ]

    if user.is_speaker:
        buttons_md[0].append(
            InlineKeyboardButton(
                text='Показать вопросы',
                callback_data='show_questions'
            )
        )

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=template.render(),
        parse_mode=telegram.ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(buttons_md),
    )


def donate_processing(update: Update, context: CallbackContext) -> None:

    env = Env()
    env.read_env()
    donate_amount = 1

    context.bot.send_invoice(
        chat_id=update.message.chat_id,
        title='Обработка доната',
        description='Спасибо за донат нашему мероприятию!',
        payload="Custom-Payload",
        provider_token=env.str('PAYMENTS_TOKEN'),
        currency="USD",
        prices=[LabeledPrice("На чай", donate_amount * 100)],
        photo_url=env.str('DONATE_IMG_URL'),
        photo_size=512,
        photo_width=512,
        photo_height=512,
    )


def precheckout_callback(update: Update, context: CallbackContext) -> None:

    query = update.pre_checkout_query
    if query.invoice_payload != 'Custom-Payload':
        query.answer(ok=False, error_message="Что-то пошло не так...")
    else:
        query.answer(ok=True)


def successful_payment_callback(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Спасибо за поддержку!!")


def show_events(update, context, jinja):
    events = views.get_active_events()

    template = jinja.get_template('events.txt')
    query = update.callback_query

    event_buttons = []

    for event in events:
        event_buttons.append(
            [
                InlineKeyboardButton(
                    text=event.title,
                    callback_data='show_event_{}'.format(event.pk)
                )
            ]
        )

    buttons_md = [
        *event_buttons,
        [
            InlineKeyboardButton(
                text='Назад',
                callback_data='show_title'
            )
        ]
    ]

    query.message.reply_text(
        text=template.render(
            events=events
        ),
        reply_markup=InlineKeyboardMarkup(buttons_md),
        parse_mode=telegram.ParseMode.MARKDOWN
    )

    query.answer()


def show_event(update, context, jinja):
    template = jinja.get_template('event.txt')

    query = update.callback_query

    if query:
        event_id = query.data.replace('show_event_', '')
        query.answer()
    else:
        event_id = update.message.text.replace('/show_event_', '')

    event = views.get_event_with_sections(event_id)

    block_buttons = []

    for block in event['sections']:
        block_id = block.pk
        block_buttons.append(
            [
                InlineKeyboardButton(
                    text=block.title,
                    callback_data=f'show_block_{block_id}'
                )
            ]
        )

    buttons_md = [
        *block_buttons,
        [
            InlineKeyboardButton(
                text='Назад',
                callback_data='show_events'
            ),
            InlineKeyboardButton(
                text='Главное меню',
                callback_data='show_title'
            )
        ]
    ]

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=template.render(
            name=event['event'].title,
            date=event['event'].start_date,
            description=event['event'].description,
            blocks=event['sections']
        ),
        reply_markup=InlineKeyboardMarkup(buttons_md),
        parse_mode=telegram.ParseMode.MARKDOWN
    )


def show_block(update, context, jinja):
    query = update.callback_query

    if query:
        block_id = query.data.replace('show_block_', '')
    else:
        block_id = update.message.text.replace('/show_block_', '')

    template = jinja.get_template('block.txt')

    block = views.get_section_with_speakers(block_id)

    event_id = block['section'].event.pk

    speakers_btns = []

    for speaker in block['speakers']:
        speakers_btns.append(
            [
                InlineKeyboardButton(
                    text='Задать вопрос: {} {}'.format(speaker.firstname, speaker.lastname),
                    callback_data='ask_block_{}_speaker_{}'.format(
                        block_id,
                        speaker.pk
                    )
                )
            ]
        )

    buttons_md = [
        *speakers_btns,
        [
            InlineKeyboardButton(
                text='Назад',
                callback_data=f'show_event_{event_id}'
            ),
            InlineKeyboardButton(
                text='Главное меню',
                callback_data='show_title'
            )
        ]
    ]

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=template.render(
            name=block['section'].title,
            time_from=block['section'].start_time,
            time_to=block['section'].end_time,
            description=block['section'].description,
            speakers=block['speakers']
        ),
        reply_markup=InlineKeyboardMarkup(buttons_md),
        parse_mode=telegram.ParseMode.MARKDOWN
    )

    return ConversationHandler.END


def ask_question(update, context, jinja, state):
    template = jinja.get_template('ask.txt')

    query = update.callback_query
    query.answer()

    block_id = re.search(r'^(ask_block_[\d]+)', query.data).group(1).replace(
        'ask_block_', ''
    )
    speaker_id = re.search(r'(speaker_[\d]+)$', query.data).group(1).replace(
        'speaker_', ''
    )

    state['block_id'] = block_id
    state['speaker_id'] = speaker_id
    speaker = models.Visitor.objects.get(pk=speaker_id)

    buttons_md = [
        [
            InlineKeyboardButton(
                text='Назад',
                callback_data=f'show_block_{block_id}'
            ),
            InlineKeyboardButton(
                text='Главное меню',
                callback_data='show_title'
            )
        ]
    ]

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=template.render(
            speaker_name=f'{speaker.firstname} {speaker.lastname}'
        ),
        reply_markup=InlineKeyboardMarkup(buttons_md)
    )

    return 'question'


def question_handler(update, context, jinja, state):
    template = jinja.get_template('question_asked.txt')
    question_template = jinja.get_template('send_question.txt')
    question = update.message.text

    user = update.message.from_user

    buttons_md = [
        [
            InlineKeyboardButton(
                'Назад к блоку',
                callback_data='show_block_{}'.format(state['block_id'])
            ),
            InlineKeyboardButton(
                'Главное меню',
                callback_data='show_title'
            )
        ]
    ]

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=template.render(),
        reply_markup=InlineKeyboardMarkup(buttons_md)
    )

    saved_question, block = views.save_question(state['block_id'], user['id'], state['speaker_id'], question)

    if saved_question:
        context.bot.send_message(
            chat_id=saved_question.speaker.telegram_id,
            text=question_template.render(
                block=saved_question.section.title,
                question=question,
                question_id=saved_question.pk
            ),
            parse_mode=telegram.ParseMode.MARKDOWN
        )

    return ConversationHandler.END


def show_account(update, context, jinja):
    template = jinja.get_template('account/account.txt')

    buttons_md = [
        [
            InlineKeyboardButton(
                text='Отмена',
                callback_data='cancel_account'
            )
        ]
    ]

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=template.render(),
        reply_markup=InlineKeyboardMarkup(buttons_md),
        parse_mode=telegram.ParseMode.MARKDOWN

    )

    return 'first_name'


def cancel_account(update, context):
    buttons_md = [
        [
            InlineKeyboardButton(
                text='В главное меню',
                callback_data='show_title'
            )
        ]
    ]
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Хорошо, ты всегда можешь заполнить анкету позже из главного меню.',
        reply_markup=InlineKeyboardMarkup(buttons_md)
    )

    return ConversationHandler.END


def account_first_name(update, context, jinja, state):
    template = jinja.get_template('account/first_name.txt')

    state['first_name'] = update.message.text

    buttons_md = [
        [
            InlineKeyboardButton(
                text='Отмена',
                callback_data='cancel_account'
            )
        ]
    ]

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=template.render(),
        reply_markup=InlineKeyboardMarkup(buttons_md),
        parse_mode=telegram.ParseMode.MARKDOWN
    )

    return 'last_name'


def account_last_name(update, context, jinja, state):
    template = jinja.get_template('account/last_name.txt')

    state['last_name'] = update.message.text

    buttons_md = [
        [
            InlineKeyboardButton(
                text='Пропустить',
                callback_data='skip_company'
            ),
            InlineKeyboardButton(
                text='Отмена',
                callback_data='cancel_account'
            )
        ]
    ]

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=template.render(),
        reply_markup=InlineKeyboardMarkup(buttons_md),
        parse_mode=telegram.ParseMode.MARKDOWN
    )

    return 'company'


def account_company(update, context, jinja, state):
    template = jinja.get_template('account/company.txt')

    state['company'] = update.message.text

    buttons_md = [
        [
            InlineKeyboardButton(
                text='Пропустить',
                callback_data='skip_position'
            ),
            InlineKeyboardButton(
                text='Отмена',
                callback_data='cancel_account'
            )
        ]
    ]

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=template.render(),
        reply_markup=InlineKeyboardMarkup(buttons_md),
        parse_mode=telegram.ParseMode.MARKDOWN
    )

    return 'position'


def account_skip_company(update, context, jinja):
    template = jinja.get_template('account/company.txt')

    buttons_md = [
        [
            InlineKeyboardButton(
                text='Пропустить',
                callback_data='skip_position'
            ),
            InlineKeyboardButton(
                text='Отмена',
                callback_data='cancel_account'
            )
        ]
    ]

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=template.render(),
        reply_markup=InlineKeyboardMarkup(buttons_md),
        parse_mode=telegram.ParseMode.MARKDOWN
    )

    return 'position'


def account_position(update, context, jinja, state):
    template = jinja.get_template('account/position.txt')

    state['position'] = update.message.text

    buttons_md = [
        [
            InlineKeyboardButton(
                text='Пропустить',
                callback_data='skip_phonenumber'
            ),
            InlineKeyboardButton(
                text='Отмена',
                callback_data='cancel_account'
            )
        ]
    ]

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=template.render(),
        reply_markup=InlineKeyboardMarkup(buttons_md),
        parse_mode=telegram.ParseMode.MARKDOWN
    )

    return 'phonenumber'


def account_skip_position(update, context, jinja, state):
    template = jinja.get_template('account/position.txt')
    buttons_md = [
        [
            InlineKeyboardButton(
                text='Пропустить',
                callback_data='skip_phonenumber'
            ),
            InlineKeyboardButton(
                text='Отмена',
                callback_data='cancel_account'
            )
        ]
    ]

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=template.render(),
        reply_markup=InlineKeyboardMarkup(buttons_md),
        parse_mode=telegram.ParseMode.MARKDOWN
    )

    return 'phonenumber'


def account_phonenumber(update, context, jinja, state):
    template = jinja.get_template('account/phonenumber.txt')

    state['phonenumber'] = update.message.text

    buttons_md = [
        [
            InlineKeyboardButton(
                text='Пропустить',
                callback_data='skip_email'
            ),
            InlineKeyboardButton(
                text='Отмена',
                callback_data='cancel_account'
            )
        ]
    ]

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=template.render(),
        reply_markup=InlineKeyboardMarkup(buttons_md),
        parse_mode=telegram.ParseMode.MARKDOWN
    )

    return 'email'


def account_skip_phonenumber(update, context, jinja):
    template = jinja.get_template('account/phonenumber.txt')

    buttons_md = [
        [
            InlineKeyboardButton(
                text='Пропустить',
                callback_data='skip_email'
            ),
            InlineKeyboardButton(
                text='Отмена',
                callback_data='cancel_account'
            )
        ]
    ]

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=template.render(),
        reply_markup=InlineKeyboardMarkup(buttons_md),
        parse_mode=telegram.ParseMode.MARKDOWN
    )

    return 'email'


def account_email(update, context, jinja, state):
    template = jinja.get_template('account/email.txt')

    state['email'] = update.message.text

    buttons_md = [
        [
            InlineKeyboardButton(
                text='Пропустить',
                callback_data='skip_about'
            ),
            InlineKeyboardButton(
                text='Отмена',
                callback_data='cancel_account'
            )
        ]
    ]

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=template.render(),
        reply_markup=InlineKeyboardMarkup(buttons_md),
        parse_mode=telegram.ParseMode.MARKDOWN
    )

    return 'about'


def account_skip_email(update, context, jinja):
    template = jinja.get_template('account/email.txt')

    buttons_md = [
        [
            InlineKeyboardButton(
                text='Пропустить',
                callback_data='skip_about'
            ),
            InlineKeyboardButton(
                text='Отмена',
                callback_data='cancel_account'
            )
        ]
    ]

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=template.render(),
        reply_markup=InlineKeyboardMarkup(buttons_md),
        parse_mode=telegram.ParseMode.MARKDOWN
    )

    return 'about'


def account_about(update, context, jinja, state):
    template = jinja.get_template('account/thank_you.txt')

    state['about'] = update.message.text

    buttons_md = [
        [
            InlineKeyboardButton(
                text='В главное меню',
                callback_data='show_title'
            )
        ]
    ]

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=template.render(),
        reply_markup=InlineKeyboardMarkup(buttons_md),
        parse_mode=telegram.ParseMode.MARKDOWN
    )

    return ConversationHandler.END


def account_skip_about(update, context, jinja, state):
    template = jinja.get_template('account/thank_you.txt')

    buttons_md = [
        [
            InlineKeyboardButton(
                text='В главное меню',
                callback_data='show_title'
            )
        ]
    ]


    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=template.render(),
        reply_markup=InlineKeyboardMarkup(buttons_md),
        parse_mode=telegram.ParseMode.MARKDOWN
    )

    return ConversationHandler.END


def show_questions(update, context, jinja):
    template = jinja.get_template('questions.txt')
    user_id = update.effective_chat.id

    speaker = models.Visitor.objects.get(telegram_id=user_id)

    if not speaker.is_speaker:
        context.bot.send_message(
            chat_id=user_id,
            text='Нет доступа к команде',
        )

        return

    questions = views.get_questions(user_id)

    buttons_md = [
        [
            InlineKeyboardButton(
                'В главное меню',
                callback_data='show_title'
            )
        ]
    ]

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=template.render(
            questions=questions
        ),
        reply_markup=InlineKeyboardMarkup(buttons_md),
        parse_mode=telegram.ParseMode.MARKDOWN
    )


def show_question(update, context, jinja, state):
    template = jinja.get_template('question.txt')
    question_id = update.message.text.replace('/answer_', '')

    question = views.get_question(
        question_id,
        update.effective_chat.id
    )

    if not question:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Нет доступа к команде'
        )

    state['question_id'] = question_id
    state['speaker_id'] = question.speaker.telegram_id

    buttons_md = [
        [
            InlineKeyboardButton(
                'Назад',
                callback_data='show_questions'
            ),
            InlineKeyboardButton(
                'В главное меню',
                callback_data='show_title'
            )
        ]
    ]

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=template.render(
            id=question.pk,
            block=question.section.title,
            question=question.question
        ),
        reply_markup=InlineKeyboardMarkup(buttons_md),
        parse_mode=telegram.ParseMode.MARKDOWN
    )

    return 'answer'


def answer_question(update, context, jinja, state):
    template = jinja.get_template('question_answered.txt')
    answer = update.message.text
    question_id = state['question_id']
    speaker_id = state['speaker_id']

    speaker, visitor, question = views.answer_question(
        question_id,
        speaker_id,
        answer
    )

    buttons_md = [
        [
            InlineKeyboardButton(
                'Назад',
                callback_data='show_questions'
            ),
            InlineKeyboardButton(
                'В главное меню',
                callback_data='show_title'
            )
        ]
    ]

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Спасибо! Ваш ответ отправлен пользователю.',
        reply_markup=InlineKeyboardMarkup(buttons_md)
    )

    context.bot.send_message(
        chat_id=visitor.telegram_id,
        text=template.render(
            question=question.question,
            speaker=f'{speaker.firstname} {speaker.lastname}',
            answer=question.answer,
            block=question.section.title
        )
    )

    return ConversationHandler.END


class Command(BaseCommand):
    help = 'Start Telegram bot'

    def handle(self, *args, **options):
        env = Env()
        env.read_env()

        telegram_token = env("TELEGRAM_TOKEN")

        jinja = Environment(
            loader=FileSystemLoader(TEMPLATES_PATH)
        )

        updater = Updater(token=telegram_token, use_context=True)
        dp = updater.dispatcher

        dp.add_handler(CommandHandler('start', partial(start, jinja=jinja)))
        dp.add_handler(CommandHandler('donate_processing', donate_processing))
        dp.add_handler(PreCheckoutQueryHandler(precheckout_callback))
        dp.add_handler(CallbackQueryHandler(
            partial(start, jinja=jinja),
            pattern='show_title')
        )
        dp.add_handler(CallbackQueryHandler(
            partial(show_events, jinja=jinja),
            pattern='show_events')
        )
        dp.add_handler(MessageHandler(
            Filters.regex(r'^(/show_event_[\d]+)$'),
            partial(show_event, jinja=jinja))
        )
        dp.add_handler(MessageHandler(
            Filters.regex(r'^(/show_block_[\d]+)$'),
            partial(show_block, jinja=jinja))
        )
        dp.add_handler(CallbackQueryHandler(
            partial(show_event, jinja=jinja),
            pattern=r'^(show_event_[\d]+)$')
        )
        dp.add_handler(CallbackQueryHandler(
            partial(show_block, jinja=jinja),
            pattern=r'^(show_block_[\d]+)$')
        )
        dp.add_handler(CallbackQueryHandler(
            partial(show_questions, jinja=jinja),
            pattern='show_questions')
        )

        ask_state = {
            'block_id': None,
            'speaker_id': None,
        }

        ask_conv_handler = ConversationHandler(
            entry_points=[CallbackQueryHandler(
                partial(ask_question, jinja=jinja, state=ask_state),
                pattern=r'^(ask_block_[\d]+_speaker_[\d]+)$'
            )],
            allow_reentry=True,
            states={
                'question': [
                    MessageHandler(
                        Filters.text,
                        partial(question_handler, jinja=jinja, state=ask_state)
                    )
                ]
            },
            fallbacks=[
                CallbackQueryHandler(
                    partial(show_block, jinja=jinja),
                    pattern=r'^(show_block_[\d]+)$',
                )
            ],
        )

        dp.add_handler(ask_conv_handler)

        account_state = {
            'first_name': '',
            'last_name': '',
            'company': '',
            'position': '',
            'phonenumber': '',
            'email': '',
            'about': ''
        }

        account_info_handler = ConversationHandler(
            entry_points=[CallbackQueryHandler(
                partial(show_account, jinja=jinja),
                pattern='show_account'
            )],
            states={
                'first_name': [
                    MessageHandler(
                        Filters.text,
                        partial(
                            account_first_name,
                            jinja=jinja,
                            state=account_state
                        )
                    )
                ],
                'last_name': [
                    MessageHandler(
                        Filters.text,
                        partial(
                            account_last_name,
                            jinja=jinja,
                            state=account_state
                        )
                    ),
                ],
                'company': [
                    MessageHandler(
                        Filters.text,
                        partial(
                            account_company,
                            jinja=jinja,
                            state=account_state
                        )
                    ),
                    CallbackQueryHandler(
                        partial(
                            account_skip_company,
                            jinja=jinja
                        ),
                        pattern='skip_company'
                    )
                ],
                'position': [
                    MessageHandler(
                        Filters.text,
                        partial(
                            account_position,
                            jinja=jinja,
                            state=account_state
                        )
                    ),
                    CallbackQueryHandler(
                        partial(
                            account_skip_position,
                            jinja=jinja,
                            state=account_state
                        ),
                        pattern='skip_position'
                    )
                ],
                'phonenumber': [
                    MessageHandler(
                        Filters.text,
                        partial(
                            account_phonenumber,
                            jinja=jinja,
                            state=account_state
                        )
                    ),
                    CallbackQueryHandler(
                        partial(
                            account_skip_phonenumber,
                            jinja=jinja
                        ),
                        pattern='skip_phonenumber'
                    )
                ],
                'email': [
                    MessageHandler(
                        Filters.text,
                        partial(
                            account_email,
                            jinja=jinja,
                            state=account_state
                        )
                    ),
                    CallbackQueryHandler(
                        partial(
                            account_skip_email,
                            jinja=jinja
                        ),
                        pattern='skip_email'
                    )
                ],
                'about': [
                    MessageHandler(
                        Filters.text,
                        partial(
                            account_about,
                            jinja=jinja,
                            state=account_state
                        )
                    ),
                    CallbackQueryHandler(
                        partial(
                            account_skip_about,
                            jinja=jinja,
                            state=account_state
                        ),
                        pattern='skip_about'
                    )
                ]
            },
            fallbacks=[
                CallbackQueryHandler(
                    cancel_account,
                    pattern='cancel_account',
                )
            ],
            allow_reentry=True
        )

        dp.add_handler(account_info_handler)

        answer_state = {
            'question_id': None,
            'speaker_id': None
        }

        question_answer_handler = ConversationHandler(
            entry_points=[
                MessageHandler(
                    Filters.regex(r'^(/answer_[\d]+)$'),
                    partial(show_question, jinja=jinja, state=answer_state)
                )
            ],
            states={
                'answer': [
                    MessageHandler(
                        Filters.text,
                        partial(answer_question, jinja=jinja, state=answer_state)
                    )
                ]
            },
            fallbacks=[
                CallbackQueryHandler(
                    partial(show_questions, jinja=jinja),
                    pattern=r'show_questions',
                ),
                CallbackQueryHandler(
                    partial(start, jinja=jinja),
                    pattern=r'show_title',
                )
            ],
            allow_reentry=True
        )

        dp.add_handler(question_answer_handler)

        updater.start_polling()

        updater.idle()

