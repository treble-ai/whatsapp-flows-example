from uuid import UUID

from psycopg import AsyncConnection
from psycopg.rows import class_row

from app.models.user import User


async def get_user_by_phone(conn: AsyncConnection, country_code: str, cellphone: str) -> User | None:
    async with conn.cursor(row_factory=class_row(User)) as cursor:
        await cursor.execute(
            "SELECT * FROM users WHERE country_code = %s AND cellphone = %s",
            (country_code, cellphone),
        )
        user = await cursor.fetchone()
        return user


async def update_user(conn: AsyncConnection, user_id: UUID, name: str, email: str) -> None:
    async with conn.cursor() as cursor:
        await cursor.execute(
            "UPDATE users SET name = %s, email = %s WHERE id = %s",
            (name, email, user_id),
        )


async def create_user(conn: AsyncConnection, country_code: str, cellphone: str, name: str, email: str) -> User:
    async with conn.cursor(row_factory=class_row(User)) as cursor:
        await cursor.execute(
            "INSERT INTO users (country_code, cellphone, name, email) VALUES (%s, %s, %s, %s) RETURNING *",
            (country_code, cellphone, name, email),
        )
        user = await cursor.fetchone()
        if user is None:
            raise ValueError("User not created")
        return user
