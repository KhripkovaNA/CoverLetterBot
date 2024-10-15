from typing import Any, Dict
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select
from sqlalchemy import update as sqlalchemy_update, delete as sqlalchemy_delete
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload
from bot.database import connection


class BaseRepository:
    model = None  # This should be set in the child class

    @classmethod
    @connection
    async def find_one_or_none_by_id(cls, data_id: int, session: AsyncSession):
        # Find a record by its id
        logger.info(f"Поиск {cls.model.__name__} с id: {data_id}")
        try:
            query = select(cls.model).filter_by(id=data_id)
            result = await session.execute(query)
            record = result.scalar_one_or_none()
            if record:
                logger.info(f"Запись с id {data_id} найдена.")
            else:
                logger.info(f"Запись с id {data_id} не найдена.")
            return record
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске записи с id {data_id}: {e}")
            raise

    @classmethod
    @connection
    async def find_one_or_none(cls, session: AsyncSession, **filter_by):
        # Find one record matching the provided filters
        logger.info(f"Поиск одной записи {cls.model.__name__} по фильтрам: {filter_by}")
        related_objects = filter_by.pop('related_objects', [])
        load_strategy = filter_by.pop('load_strategy', 'joined')
        try:
            query = select(cls.model).filter_by(**filter_by)

            # Apply loading strategy for related objects
            if related_objects:
                if load_strategy == 'joined':
                    for rel in related_objects:
                        query = query.options(joinedload(getattr(cls.model, rel)))
                elif load_strategy == 'selectin':
                    for rel in related_objects:
                        query = query.options(selectinload(getattr(cls.model, rel)))

            result = await session.execute(query)
            record = result.scalar_one_or_none()

            if record:
                logger.info(f"Запись найдена по фильтрам: {filter_by}.")
            else:
                logger.info(f"Запись не найдена по фильтрам: {filter_by}.")
            return record
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске записи по фильтрам {filter_by}: {e}")
            raise

    @classmethod
    async def find_all(cls, session: AsyncSession, **filter_by):
        # Find all records matching the provided filters
        logger.info(f"Поиск всех записей {cls.model.__name__}.")
        try:
            query = select(cls.model).filter_by(**filter_by)
            result = await session.execute(query)
            records = result.scalars().all()
            logger.info(f"Найдено {len(records)} записей.")
            return records
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске всех записей по фильтрам {filter_by}: {e}")
            raise

    @classmethod
    @connection
    async def add(cls, session: AsyncSession, **values):
        # Add a new record
        logger.info(f"Добавление записи {cls.model.__name__}")
        new_instance = cls.model(**values)
        session.add(new_instance)
        try:
            await session.commit()
            logger.info(f"Запись {cls.model.__name__} успешно добавлена.")
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"Ошибка при добавлении записи: {e}")
            raise e
        return new_instance

    @classmethod
    @connection
    async def update(cls, session: AsyncSession, filter_by: Dict[str, Any], **values):
        # Update a record or records matching the provided filters
        logger.info(f"Обновление записей {cls.model.__name__} по фильтрам {filter_by}.")
        query = (
            sqlalchemy_update(cls.model)
            .where(*[getattr(cls.model, k) == v for k, v in filter_by.items()])
            .values(**values)
            .execution_options(synchronize_session="fetch")
        )
        try:
            result = await session.execute(query)
            await session.commit()
            logger.info(f"Обновлено {result.rowcount} записей.")
            return result.rowcount
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"Ошибка при обновлении записей: {e}")
            raise e

    @classmethod
    @connection
    async def delete(cls, session: AsyncSession, delete_all: bool = False, **filter_by):
        # Delete records matching the provided filters
        logger.info(f"Удаление записей {cls.model.__name__} по фильтру: {filter_by}")
        if not delete_all and not filter_by:
            logger.error("Нужен хотя бы один фильтр для удаления.")
            raise ValueError("Нужен хотя бы один фильтр для удаления.")

        query = sqlalchemy_delete(cls.model).filter_by(**filter_by)
        try:
            result = await session.execute(query)
            await session.commit()
            logger.info(f"Удалено {result.rowcount} записей.")
            return result.rowcount
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"Ошибка при удалении записей: {e}")
            raise e
