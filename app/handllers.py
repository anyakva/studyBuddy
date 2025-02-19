import logging
from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.enums import ParseMode
from aiogram.fsm.state import StatesGroup,State
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import random
from app.dopolnenia.text import words, options_main


import app.keyboards as kb
import app.bd.requests as rq


router= Router()

user_message_ids = {}
class Reg(StatesGroup):
    name = State()
    classes = State()


class TestStates(StatesGroup):
    answering_question = State()  # Состояние для вопроса
    finished = State()  # Состояние для завершения теста


@router.message(CommandStart())
async def cmd_start(message: Message):
    await rq.set_user(message.from_user.id)
    await message. answer(f'Привет, {message.from_user.first_name} ',)
    await message.answer(' Я — Репетишка, твой верный помощник в мире знаний!'
                         ' 🌟 Моя миссия — замотивировать тебя учиться и делать '
                         'подготовку к экзаменам увлекательной. Готов ли ты начать?',
                         reply_markup=kb.main)



@router. callback_query(F. data == 'YES')
async def YES(callback: CallbackQuery):
    await callback.message.answer('Здорово, что ты решил начать учиться!'
                                  ' 🎉 Давай я задам тебе несколько вопросов,'
                                  ' чтобы сделать нашу подготовку максимально удобной'
                                  ' и интересной. Для начала пройди регистрацию\nДля продолжение напиши комманду "/reg"')
@router. callback_query(F. data == 'NO')
async def NO(callback: CallbackQuery):
    await callback.message.answer('Привет! Я понимаю, что учиться порой бывает непросто и скучно. 😅 '
                         'Но подумай, как много возможностей откроется перед тобой после успешной '
                         'сдачи экзаменов! 🎓Я здесь, чтобы сделать процесс подготовки '
                         'интереснее и легче. Если передумаешь кликай на кнопку выше❤️')


@router.message(Command('reg'))
async def reg_one(message: Message, state: FSMContext):
    await state.set_state(Reg.name)
    await message.answer('Введи своё имя')

@router.message(Reg.name)
async def reg_two(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Reg.classes)
    await rq.update_name(message.from_user.id, message.text)
    await message.answer("Введите класс, в котором вы сейчас обучаетесь. Укажите число: 9, 10 или 11. Если твой класс ниже, выберите 9.",reply_markup=kb.get_classes)

@router.message(Reg.classes, F.text.in_(["9", "10", "11"]))
async def register_class(message: Message, state: FSMContext):
    await state.update_data(classes=message.text)
    await rq.update_grade(message.from_user.id, message.text)
    data = await state.get_data()

    await message.answer(f'Спасибо, регистрация завершена.\n Имя: {data["name"]}\nКласс: {data["classes"]} \nДля продолжение напиши комманду "/education"')
    await state.clear()

async def send_or_edit_message(bot, user_id, user_message_id, text, reply_markup):
    if user_message_id:
        await bot.edit_message_text(
            chat_id=user_id,
            message_id=user_message_id,
            text=text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
    else:
        sent_message = await bot.send_message(
            user_id,
            text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
        user_message_ids[user_id] = sent_message.message_id


@router.message(Command("education"))
async def cmd_education(message: Message):
    user_id = message.from_user.id
    formatted_message = """<b>📚 Образование с ботом</b>

Удачи в подготовке!"""

    sent_message = await message.bot.send_message(
        chat_id=user_id,
        text=formatted_message,
        reply_markup=await kb.main_menu(),
        parse_mode=ParseMode.HTML
    )

    user_message_ids[user_id] = sent_message.message_id

    await message.delete()

from typing import List, Tuple

# Утилитная функция для отправки сообщений и обработки ошибок
async def send_error_message(message: Message, state: FSMContext, text: str):
    await message.edit_text(text)
    await state.clear()

# Утилитная функция для отправки сообщения с результатом
async def send_result_message(callback: CallbackQuery, state: FSMContext, result_message: str, category: str):
    await send_or_edit_message(callback.message.bot, callback.from_user.id,
                               user_message_ids.get(callback.from_user.id),
                               result_message, await kb.button_categories(category))

# Обработчик для категорий
@router.callback_query(F.data.startswith('category_'))
async def category(callback: CallbackQuery):
    await callback.answer()
    category_name = callback.data.split('_')[1]
    text = f"{options_main.get(category_name)}\n\nКоличество ошибок: {await rq.get_user_mistake_count(callback.from_user.id, category_name)}"

    await send_or_edit_message(callback.message.bot, callback.from_user.id, user_message_ids.get(callback.from_user.id), text, await kb.button_categories(category_name))

# Обработчик для главного меню
@router.callback_query(F.data == 'go_main')
async def go_main(callback: CallbackQuery):
    await send_or_edit_message(callback.message.bot, callback.from_user.id, user_message_ids.get(callback.from_user.id), "✍️ <b>Егэ русский язык</b>", await kb.main_menu())
    await callback.answer()

# Обработчик для старта теста
@router.callback_query(F.data.startswith('start_'))
async def start_test(callback: CallbackQuery, state: FSMContext):
    category = callback.data.split('_')[1]
    words1, words_dop = words.get(category, ([], []))
    await state.update_data(
        category=category,
        used_words=[],
        current_pair=[],
        words=words1,
        words_dop=words_dop
    )

    await state.set_state(TestStates.answering_question)

    await send_next_question(callback.message, state)

@router.callback_query(F.data.startswith('error_'))
async def start_error_correction(callback: CallbackQuery, state: FSMContext):
    category = callback.data.split('_')[1]
    errors = await rq.get_user_mistakes(callback.from_user.id, category)

    if not errors:
        await callback.message.edit_text(
            "👍 У вас нет ошибок для проработки.",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[[
                    InlineKeyboardButton(text="🔙 Назад", callback_data=f"close_{category}")
                ]]
            )
        )
        return

    words_error = [error.get('words', []) for error in errors]
    words_dop_error = [error.get('words_dop', []) for error in errors]
    await state.update_data(
        category=category,
        used_words=[],
        current_pair=[],
        words=words_error,
        words_dop=words_dop_error,
        is_error_correction=True
    )

    await state.set_state(TestStates.answering_question)
    await send_next_question(callback.message, state)

async def send_next_question(message: Message, state: FSMContext, result_message: str = ''):
    data = await state.get_data()
    if not data:
        await send_or_edit_message(message.bot, message.from_user.id, user_message_ids.get(message.from_user.id),
                                    "⏳ Ваша сессия истекла или была сброшена. Пожалуйста, начните заново.",
                                    await kb.main_menu())
        await state.clear()
        return

    category_name = data.get('category')

    if not data.get('words') or not data.get('words_dop'):
        finish_message = "💫 Проработка ошибок завершена!" if data.get('is_error_correction') else "✅ Тест завершен, все слова пройдены!"
        text = f"{options_main.get(category_name, '')}\n\n{finish_message}"
        await message.edit_text(text, reply_markup=await kb.button_categories(category_name))
        await state.clear()
        return

    words, words_dop = random.choice(list(zip(data['words'], data['words_dop'])))

    data['current_pair'] = (words, words_dop)

    answer_buttons = [
        InlineKeyboardButton(text=word, callback_data="correct" if word == words else "wrong")
        for word in random.sample([words, words_dop], 2)
    ]
    answer_buttons.append(InlineKeyboardButton(text="🔙 Завершить", callback_data=f"close_{data['category']}"))

    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button] for button in answer_buttons])
    result_message = f"Выберите верный ответ: {result_message}" if not result_message else result_message

    await state.update_data(data)
    await message.edit_text(result_message, reply_markup=keyboard)

@router.callback_query(F.data.in_(['correct', 'wrong']))
async def handle_answer(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if not data:
        await send_or_edit_message(callback.message.bot, callback.from_user.id,
                                   user_message_ids.get(callback.from_user.id),
                                   "Ваша сессия истекла. Начните заново.",
                                   await kb.main_menu())
        await state.clear()
        return

    correct_word, wrong_word = data.get('current_pair', (None, None))

    if callback.data == "correct":
        if data.get('is_error_correction'):
            data['words'].remove(correct_word)
            data['words_dop'].remove(wrong_word)
            await rq.remove_user_mistake(callback.from_user.id, data['category'], correct_word)
        result_message = "✅ Верно!"
    else:
        result_message = f"❌ Неверно, правильный ответ: {correct_word}"
        if not data.get('is_error_correction'):
            await rq.save_user_mistake(callback.from_user.id, data['category'], wrong_word=wrong_word, correct_word=correct_word)

    await send_next_question(callback.message, state, result_message)

# Закрытие теста
@router.callback_query(F.data.startswith('close_'))
async def close_test(callback: CallbackQuery, state: FSMContext):
    category_name = callback.data.split('_')[1]
    text = options_main.get(category_name, "")
    user_id = callback.from_user.id
    mistake_count = await rq.get_user_mistake_count(user_id, category_name)
    text = f"{text}\n\n📚 Тест завершен!\n\nКоличество ошибок: {mistake_count}"

    await state.clear()
    await callback.message.edit_text(text=text, reply_markup=await kb.button_categories(category_name))
