from sqlalchemy import BigInteger, String, ForeignKey, Boolean, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

engine= create_async_engine(url='sqlite+aiosqlite:///db.sqlite3')

async_session = async_sessionmaker(engine)

class Base (AsyncAttrs, DeclarativeBase):
    pass
echo= True
class User(Base):
    __tablename__ = 'users'

    id:Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id = mapped_column(BigInteger)
    name: Mapped[str] = mapped_column(String, nullable=False, default="Unknown User")
    coins: Mapped[int] = mapped_column(default=0)
    grade: Mapped[int] = mapped_column(default=9)

    mistakes = relationship('Mistake', back_populates='user', cascade='all, delete-orphan')



class Mistake(Base):
    __tablename__ = 'mistakes'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    category: Mapped[str] = mapped_column(String(50))
    wrong_word: Mapped[str] = mapped_column(String(255))
    correct_word: Mapped[str] = mapped_column(String(255))

    user = relationship('User', back_populates='mistakes')




async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

