import datetime

from MelodieInfra.jsonobject import StringProperty, BooleanProperty, DateTimeProperty, ListProperty, unicode, JsonObject, \
    DefaultProperty

# https://github.com/dimagi/jsonobject
class User(JsonObject):
    user_name: str = StringProperty(required=True)
    name = StringProperty()
    active = BooleanProperty(default=False)
    date_joined = DateTimeProperty()
    tags = ListProperty(unicode)


user1 = User(
    name='John Doe',
    user_name='jdoe',
    date_joined=datetime.datetime.utcnow(),
    tags=['generic', 'anonymous']
)

print(user1.to_json())
user2 = User({'userName': 'aaaaa'})
print(user2.to_json())
