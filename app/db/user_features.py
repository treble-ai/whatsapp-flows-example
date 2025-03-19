from uuid import UUID

from psycopg import AsyncConnection
from psycopg.rows import class_row

from app.models.user_feature import UserFeature


async def get_user_features(conn: AsyncConnection, user_id: UUID) -> list[UserFeature]:
    async with conn.cursor(row_factory=class_row(UserFeature)) as cursor:
        await cursor.execute(
            "SELECT * FROM user_features WHERE user_id = %s",
            (user_id,),
        )
        user_features = await cursor.fetchall()
        return user_features


async def add_user_features(conn: AsyncConnection, user_id: UUID, features: set[str]) -> None:
    async with conn.cursor() as cursor:
        values = [(user_id, feature_id) for feature_id in features]
        await cursor.executemany(
            "INSERT INTO user_features (user_id, type) VALUES (%s, %s) ON CONFLICT DO NOTHING", values
        )


async def remove_user_features(conn: AsyncConnection, user_id: UUID, features: set[str]) -> None:
    async with conn.cursor() as cursor:
        await cursor.execute(
            "DELETE FROM user_features WHERE user_id = %s AND type = ANY(%s)",
            (user_id, list(features)),
        )
