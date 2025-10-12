from peewee import (
    PostgresqlDatabase, Model, BooleanField,
    IntegerField, CharField, ForeignKeyField, AutoField, BigIntegerField, DateField, DateTimeField
)

from config import settings

db = PostgresqlDatabase(
    database=settings.database.NAME,
    user=settings.database.USER,
    password=settings.database.PASSWORD,
    host=settings.database.HOST,
    port=settings.database.PORT,
)


class BaseModel(Model):
    class Meta:
        database = db


class Users(BaseModel):
    id = AutoField(primary_key=True)
    user_id = BigIntegerField(unique=True)
    username = CharField(null=True)
    language = CharField(null=True)
    contact = CharField(null=True)

    # Search settings
    ad_type = CharField(null=True)  # Аренда/Покупка
    type_object = CharField(null=True)  # Жилая недвижимость/Коммерческая недвижимость/Земельный участок (При покупке)
    type_property = CharField(null=True)  # Новостройки/вторичное (При покупке)
    city = CharField(null=True)
    price = IntegerField(null=True)
    total_area = IntegerField(null=True)


class Apartment_Parameters(BaseModel):
    id = AutoField(primary_key=True)
    user = ForeignKeyField(Users, backref="parameters", on_delete="CASCADE")
    title_parameter = CharField()
    parameter = BooleanField()


class City_Districts(BaseModel):
    id = AutoField(primary_key=True)
    city_name = CharField()
    district = CharField()

    class Meta:
        indexes = (
            (('city_name', 'district'), True),  # Уникальный составной индекс
        )


class Realty(BaseModel):
    id = AutoField(primary_key=True)
    number_rooms = CharField(null=True)
    floors_in_house = CharField(null=True)
    floor = CharField(null=True)
    square = CharField(null=True)
    city = CharField(null=True)
    ad_type = CharField(null=True)  # Аренда/Покупка
    type_property = CharField(null=True)  # Новостройки/вторичное (При покупке)
    object_type = CharField(null=True)  # Квартира/Дуплекс/Вилла
    street = CharField(null=True)
    district = CharField(null=True)
    price = CharField(null=True)
    description = CharField(null=True)

    furniture = CharField(null=True)
    animals = CharField(null=True)
    children = CharField(null=True)

    user = ForeignKeyField(Users, backref="ads", on_delete="CASCADE")

    name = CharField(null=True)
    contact = CharField(null=True)
    agency = CharField(null=True)
    agency_name = CharField(null=True)

    consent_admin = BooleanField(null=True)

    created_at = DateTimeField(null=True)
    published_at = DateTimeField(null=True)


class Favorites(BaseModel):
    id = AutoField(primary_key=True)
    user = ForeignKeyField(Users, backref="favorites", on_delete="CASCADE")
    realty = ForeignKeyField(Realty, backref="users_added_favorites", on_delete="CASCADE")


class PhotosRealty(BaseModel):
    id = AutoField(primary_key=True)
    realty = ForeignKeyField(Realty, backref="photos", on_delete="CASCADE")
    photo_path = CharField(unique=True)


if __name__ == '__main__':
    db.connect()
    db.create_tables([Users, Apartment_Parameters, City_Districts, Realty, Favorites, PhotosRealty])