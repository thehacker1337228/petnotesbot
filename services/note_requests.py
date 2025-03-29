from services.models import async_session
from services.models import Note
from sqlalchemy import select, update


class NoteRequests:

    async def cnt(self, user_id):
        async with async_session() as session:
            result = await session.execute(select(Note).where(Note.user_id == user_id))
            return len(result.scalars().all()) #получаем кол-во заметок у юзера



    async def add(self, note_dto): #принимает DTO object Работает
        async with async_session() as session:
            note = Note(**vars(note_dto)) #типа to_model
            session.add(note)
            await session.commit()

    async def get_all(self, user_id): #работает
        async with async_session() as session:
            result = await session.execute(
                select(Note).where(
                    (Note.is_deleted == None) | (Note.is_deleted == 0),
                    Note.user_id == user_id
                )
            )
            notes = result.scalars().all()  # Получаем список dto objects объектов
            return notes


    async def delete(self, note_id, tg_id): #работает
        async with async_session() as session:
            await session.execute(
                update(Note)
                .where(Note.note_id == note_id, Note.user_id == tg_id)
                .values(is_deleted=1)
            )
            await session.commit()

    async def update(self, note_dto): #работает
        async with async_session() as session:
            session.add(note_dto)
            print("произведён note update")
            await session.commit()

    async def get_note(self, note_id): #работает
        async with async_session() as session:
            result = await session.execute(select(Note).where(Note.note_id == note_id))
            note = result.scalar_one_or_none()
            return note
