from aiogram.types import Message, PreCheckoutQuery, LabeledPrice, ShippingQuery
from aiogram.types.message import ContentType

from messages import MESSAGES
from config import PAYMENTS_TOKEN, donate_img_url
from main import dp, bot


DONATE_LABELS = [
    LabeledPrice(label='Спасибо', amount=1000),
]

@dp.message_handler(commands=['start'])
async def start_cmd(message:Message):
    await message.answer(MESSAGES['start'])

@dp.message_handler(commands=['help'])
async def help_cmd(message:Message):
    await message.answer(MESSAGES['help'])

@dp.message_handler(commands=['terms'])
async def terms_cmd(message:Message):
    await message.answer(MESSAGES['terms'])



@dp.message_handler(commands=['donate'])
async def buy_process(message:Message):
    await bot.send_invoice(
        message.chat.id,
        title=MESSAGES['donate_title'],
        description=MESSAGES['donate_description'],
        provider_token=PAYMENTS_TOKEN,
        currency='rub',
        photo_url=donate_img_url,
        photo_height=512,
        photo_width=512,
        photo_size=512,
        need_email=True,
        need_phone_number=True,
        need_shipping_address=False,
        is_flexible=False,
        prices=DONATE_LABELS,
        start_parameter='example',
        payload='send_invoice',
    )

@dp.pre_checkout_query_handler(lambda q: True)
async def checkout_process(pre_checkout_query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@dp.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment(message:Message):
    await bot.send_message(
        message.chat.id,
        MESSAGES['successful_payment'].format(total_amount=message.successful_payment.total_amount/100,
                                              currency=message.successful_payment.currency)
    )