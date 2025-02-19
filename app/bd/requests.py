from app.bd.models import async_session
from app.bd.models import User, Mistake
from sqlalchemy import select, update, delete, func
import ast
from sqlalchemy import create_engine
from app.bd.models import engine


async def set_user(tg_id: int):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if not user:
            session.add(User(tg_id=tg_id))
            await session.commit()

async def get_user_by_tg_id(tg_id: int):
    async with async_session() as session:
        return await session.scalar(select(User).where(User.tg_id == tg_id))

async def get_all_users() -> list:
    async with async_session() as session:
        return (await session.scalars(select(User.tg_id))).all()

async def get_user_count() -> int:
    async with async_session() as session:
        return await session.scalar(select(func.count(User.id)))

async def update_name(tg_id, name):
    update_query = update(User).where(User.tg_id == tg_id).values(name= name)
    async with async_session() as session:
        await session.execute(update_query)
        await session.commit()

async def delete_user_by_tg_id(tg_id: int) -> None:
    async with async_session() as session:
        await session.execute(delete(User).where(User.tg_id == tg_id))
        await session.commit()
async def update_grade(tg_id, grade):
    update_query = update(User).where(User.tg_id == tg_id).values(grade= grade)
    async with async_session() as session:
        await session.execute(update_query)
        await session.commit()

async def get_user_mistake_count(tg_id: int, category: str) -> int:
    user = await get_user_by_tg_id(tg_id)
    if not user:
        return 0

    model = Mistake
    filters = [model.user_id == user.id]

    if category:
        filters.append(model.category == category)

    async with async_session() as session:
        return await session.scalar(select(func.count(model.id)).where(*filters))

async def get_user_mistakes(tg_id: int, category: str) -> list:
    user = await get_user_by_tg_id(tg_id)
    if not user:
        return []

    async with async_session() as session:
        model = Mistake
        query = select(model).where(model.user_id == user.id)
        if category:
            query = query.where(model.category == category)

        results = await session.execute(query)
        mistakes = results.scalars().all()

        return [
            {
                'words': m.correct_word,
                'words_dop': m.wrong_word
            }
            for m in mistakes
        ]


async def save_user_mistake(tg_id: int, category: str, wrong_word: str = None, correct_word: str = None) -> None:
    user = await get_user_by_tg_id(tg_id)
    if not user:
        return

    async with async_session() as session:
        model = Mistake
        filter_conditions = (
                (model.user_id == user.id) &
                (model.category == category) &
                (model.wrong_word == wrong_word) &
                (model.correct_word == correct_word)
        )

        existing_mistake = await session.scalar(select(model).where(filter_conditions))
        if not existing_mistake:
            new_mistake = model(
                user_id=user.id,
                category=category,
                wrong_word=wrong_word,
                correct_word=correct_word
            )
            session.add(new_mistake)
            await session.commit()

async def remove_user_mistake(tg_id: int, category: str, word_right: str = None) -> None:
    user = await get_user_by_tg_id(tg_id)
    if not user:
        return

    async with async_session() as session:
        model = Mistake
        conditions = (
            (model.user_id == user.id) & (model.category == category) & (model.correct_word == word_right)
        )

        await session.execute(delete(model).where(conditions))
        await session.commit()
