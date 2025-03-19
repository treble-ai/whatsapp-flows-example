from app.models.db import DBBase


class User(DBBase):
    country_code: str
    cellphone: str
    name: str
    email: str
