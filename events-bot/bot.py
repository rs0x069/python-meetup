import re
import json
from functools import partial

from environs import Env
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    Filters,
    ConversationHandler
)
from jinja2 import FileSystemLoader, Environment
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def start(update, context, jinja):
    template = jinja.get_template('title.txt')
    query = update.callback_query

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
                text='Показать вопросы',
                callback_data='show_questions'
            )
        ],
    ]

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=template.render(),
        parse_mode=telegram.ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(buttons_md),
    )


def show_events(update, context, jinja):
    with open('./temp_events.json', encoding='UTF-8') as events_json:
        events = json.load(events_json)

    template = jinja.get_template('events.txt')
    query = update.callback_query

    event_buttons = []

    for event in events:
        event_buttons.append(
            [
                InlineKeyboardButton(
                    text=event['name'],
                    callback_data='show_event_{}'.format(event['id'])
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

    with open('./temp_event.json', encoding='UTF-8') as event_json:
        event = json.load(event_json)

    block_buttons = []

    for block in event['blocks']:
        block_id = block['id']
        block_buttons.append(
            [
                InlineKeyboardButton(
                    text=block['name'],
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
            name=event['name'],
            date=event['date'],
            time_from=event['time_from'],
            time_to=event['time_to'],
            description=event['description'],
            blocks=event['blocks']
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

    with open('temp_block.json', encoding='UTF-8') as block_json:
        block = json.load(block_json)

    event_id = block['event_id']

    speakers_btns = []

    for speaker in block['speakers']:
        speakers_btns.append(
            [
                InlineKeyboardButton(
                    text='Задать вопрос: {}'.format(speaker['name']),
                    callback_data='ask_block_{}_speaker_{}'.format(
                        block_id,
                        speaker['id']
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
            name=block['name'],
            time_from=block['time_from'],
            time_to=block['time_to'],
            description=block['description'],
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
            speaker_name=speaker_id
        ),
        reply_markup=InlineKeyboardMarkup(buttons_md)
    )

    return 'question'


def question_handler(update, context, jinja, state):
    template = jinja.get_template('question_asked.txt')
    question = update.message.text

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

    with open('./temp_questions.json', encoding='UTF-8') as questions_json:
        questions = json.load(questions_json)

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


def show_question(update, context, jinja):
    template = jinja.get_template('question.txt')
    question_id = update.message.text.replace('/answer_', '')

    with open('./temp_question.json', encoding='UTF-8') as question_json:
        question = json.load(question_json)

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
            id=question['id'],
            block=question['block']['name'],
            question=question['question']
        ),
        reply_markup=InlineKeyboardMarkup(buttons_md),
        parse_mode=telegram.ParseMode.MARKDOWN
    )

    return 'answer'


def answer_question(update, context):
    answer = update.message.text

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

    return ConversationHandler.END


if __name__ == '__main__':
    env = Env()
    env.read_env()
    bot_token = env.str('TELEGRAM_BOT_TOKEN')

    jinja = Environment(
        loader=FileSystemLoader('./templates')
    )

    updater = Updater(token=bot_token, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', partial(start, jinja=jinja)))
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

    question_answer_handler = ConversationHandler(
        entry_points=[
            MessageHandler(
                Filters.regex(r'^(/answer_[\d]+)$'),
                partial(show_question, jinja=jinja)
            )
        ],
        states={
            'answer': [
                MessageHandler(
                    Filters.text,
                    answer_question
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
