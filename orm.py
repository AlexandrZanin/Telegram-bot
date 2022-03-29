"""
orm peewe. class Guest, class Hotel_find
"""
from peewee import *
db=SqliteDatabase('history_test.db')
class BaseModel(Model):
    class Meta:
        database = db
class Guest(BaseModel):
    time_now=DateTimeField(formats=['%Y-%m-%d %H:%M:%S'])
    cmd=CharField()
    user_id=CharField()#(default='None')
    sity=CharField()#(default='None')
    sity_id=CharField()#(default='None')
    date_in=DateField()#(default=datetime.date)
    date_out=DateField()#(default=datetime.date)
    low_price=CharField(default=None)
    top_price=CharField(default=None)
    count_hotels=IntegerField()#(default=1)
    foto=BooleanField()#(default=True)
    foto_count=IntegerField()#(default=0)
    max_dist=CharField(default=None)
    currency=CharField()
class Hotels_find(BaseModel):
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
        Hotels_find.create_table()
