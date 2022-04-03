"""
orm peewe. class Guest, class Hotel_find
"""
from peewee import *
db = SqliteDatabase('history_test.db')


class BaseModel(Model):
    class Meta:
        database = db


class Guest(BaseModel):
    time_now=DateTimeField(formats=['%Y-%m-%d %H:%M:%S'])
    cmd=CharField()
    user_id=CharField()
    sity=CharField()
    sity_id=CharField()
    date_in=DateField()
    date_out=DateField()
    low_price=CharField(default=None)
    top_price=CharField(default=None)
    count_hotels=IntegerField()
    foto=BooleanField()
    foto_count=IntegerField()
    max_dist=CharField(default=None)
    currency=CharField()


class Hotels_Find(BaseModel):
    owner=ForeignKeyField(Guest, related_name='hotels')
    name=CharField()
    dist=CharField()
    addres=CharField()
    price_day=CharField()
    price=CharField()
    stars=CharField()
    site=CharField()
    date_in=DateField()
    date_out=DateField()
    foto=CharField()


def create_table_guest():
    with db:
        Guest.create_table()


def create_table_hotels():
    with db:
        Hotels_Find.create_table()
