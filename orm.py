from peewee import *
import datetime
from peewee import ModelSelect

db=SqliteDatabase('history_test.db')
class BaseModel(Model):
    class Meta:
        database = db
class Guest(BaseModel):
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
    time_now=DateTimeField(formats=['%Y-%m-%d'])
class Hotels_find(BaseModel):
    owner=ForeignKeyField(Guest, related_name='hotels')
    name=CharField()
    dist=CharField()
    addres=CharField()
    price=CharField()
    stars=CharField()
    site=CharField()
def create_table_guest():
    with db:
        Guest.create_table()
def create_table_hotels():
    with db:
        Hotels_find.create_table()
'''
def add_row(elem):
    try:
        with db.atomic():
            # Attempt to create the user. If the username is taken, due to the
            # unique constraint, the database will raise an IntegrityError.
            user=User.create(
                username=elem,
                join_date=datetime.datetime.now())
    except IntegrityError:
        flash('That username is already taken')
'''
# User.create_table()
# response_user = User.create(sity='Moscow', join_date=datetime.datetime.now())
# response_user_1 = User.create(sity='Paris', join_date=datetime.datetime.now())

