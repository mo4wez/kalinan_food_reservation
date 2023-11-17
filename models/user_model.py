import bcrypt
from peewee import Model, SqliteDatabase, CharField

db = SqliteDatabase('bot_users.db')

class User(Model):
    chat_id = CharField(unique=True)
    first_name = CharField()
    username = CharField(null=True)
    kalinan_username = CharField(unique=True)
    kalinan_password = CharField()

    class Meta:
        database = db

    @classmethod
    def create_user(cls, chat_id, first_name, username, kalinan_username, kalinan_password):
        # Create a new user
        return cls.create(
            chat_id=chat_id,
            first_name=first_name,
            username=username,
            kalinan_username=kalinan_username,
            kalinan_password=kalinan_password  # Convert bytes to string for storage
        )

db.connect()
db.create_tables([User], safe=True)