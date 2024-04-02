import logging
import re

from aiogram import types, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, FSInputFile

import config
import kb
import main
import states
import text

router = Router()


# Валидатор ФИО
def validate_full_name(full_name):
    if any(char.isdigit() for char in full_name):
        return False

    words = full_name.split()
    if len(words) != 3:
        return False

    if not all(len(word) >= 2 for word in words):
        return False

    return True


@router.message(Command(commands=['start']))
async def start_cmd_handler(message: Message, state: FSMContext):
    user_name = message.from_user.username
    logging.info(message.chat.id)
    welcome_message = f"{user_name}, " + text.WELCOME_TEXT
    await message.reply(welcome_message)
    await message.answer(text.WRITE_FIO)

    # Устанавливаем состояние, ожидающие ввод имени
    await state.set_state(states.UserInfo.name)


@router.message(states.UserInfo.name)
async def process_name_handler(message: Message, state: FSMContext):
    full_name = message.text

    # Проверяем ФИО
    err = validate_full_name(full_name)

    # Если ФИО не подходит
    if not err:
        await message.reply(text.FIO_ERR)
        await message.answer(text.WRITE_FIO)

        # Снова устанавливаем состояние, ожидающие ввод имени
        await state.set_state(states.UserInfo.name)
        return

    # Если ФИО подходит
    await state.update_data(name=full_name)

    await message.reply(f"Спасибо, {full_name}. Ваше ФИО сохранено")

    await message.answer(text.WRITE_PHONE)

    # Устанавливаем состояние, ожидающие ввод номера телефона
    await state.set_state(states.UserInfo.phone_number)


@router.message(states.UserInfo.phone_number)
async def process_phone_number_handler(message: Message, state: FSMContext):
    phone_number = message.text

    # Проверяем формат номера телефона с помощью регулярного выражения
    phone_pattern = re.compile(r'^\d{1} \d{3} \d{3} \d{2} \d{2}$')

    if not phone_pattern.match(phone_number) or phone_number[0] != '7':
        await message.reply(text.PHONE_ERR)

        # Снова устанавливаем состояние, ожидающие ввод номера телефона
        await state.set_state(states.UserInfo.phone_number)
        return

    # Если формат номера телефона верный, сохраняем его
    await state.update_data(phone_number=phone_number)

    await message.reply(f"Спасибо, ваш номер телефона {phone_number} сохранен")

    await message.answer(text.WRITE_COMMENT)

    # Устанавливаем состояние, ожидающие ввод комментария
    await state.set_state(states.UserInfo.comment)


@router.message(states.UserInfo.comment)
async def process_message_handler(message: Message, state: FSMContext):
    comment = message.text

    await state.update_data(comment=comment)

    await message.reply(f'Ваш комментарий сохранен: "{comment}"')

    # Отправляем наш документ с положениями
    await message.answer_document(
        document=FSInputFile(config.PATH_TO_FILE),
        caption=text.LAST_STEP
    )

    # Создаём инлайн-кнопку
    markup = kb.generate_markup([["ДА!", text.YES_BUTTON]])

    await message.answer(text.CLICK_YES, reply_markup=markup)


@router.callback_query(F.data == text.YES_BUTTON)
async def handle_button(callback_query: types.CallbackQuery, state: FSMContext):

    # Отправляем фото и текст
    await main.bot.send_photo(
        chat_id=callback_query.message.chat.id,
        photo=FSInputFile(config.PATH_TO_IMAGE),
        caption=text.THANKS
    )

    username_tag = callback_query.from_user.username
    user_data = await state.get_data()

    # Формируем отчёт
    report = (f'Пришла новая заявка от {username_tag}\n ФИО: {user_data.get("name")}\n '
              f'Номер телефона: {user_data.get("phone_number")}\n Комментарий: {user_data.get("comment")}')

    # Отправляем отчёт
    await main.bot.send_message(
        chat_id=config.CHAT_ID,
        text=report
    )

    # Чистим состояние
    await state.clear()
