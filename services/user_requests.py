from services.models import async_session
from services.models import User
from sqlalchemy import select, func


class UserRequests:
    async def add(self, user_dto): #принимает DTO object
        async with async_session() as session:
            user = User(**vars(user_dto)) #типа to_model
            session.add(user)
            await session.commit()


    async def check(self,tg_id): #чётко работает
        async with async_session() as session:
            result = await session.scalar(select(func.count()).where(User.tg_id == tg_id)) #scalar это как #execute, но возвращается сразу объектом
            print(result)
            print("Check сработал")
            return result

    async def get(self,tg_id):
        async with async_session() as session:
            result = await session.execute(select(User).where(User.tg_id == tg_id))
            user = result.scalar_one_or_none()
            return user

    async def update(self, user_dto):
        async with async_session() as session:
            session.add(user_dto)
            print("произведён update")
            await session.commit()


        