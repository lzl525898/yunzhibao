__author__ = 'mlzx'
from mongoengine import Document, StringField, IntField


class Event(Document):
    MESSAGE_TYPE = (
        ('text', '文本消息'),
        ('event', '事件消息'),
        ('image', '图片消息'),
        ('voice', '语音消息'),
        ('video', '视频消息'),
        ('shortvideo', '小视频消息'),
        ('location', '地理位置消息'),
        ('link', '链接消息'),
    )
    from_user_name = StringField(max_length=40, required=True)                #消息来源
    to_user_name = StringField(max_length=40, required=True)                #消息目的
    create_time = IntField(required=True)
    msg_type = StringField(max_length=20, required=True, choices=MESSAGE_TYPE, default='event')
    content = StringField(max_length=500, required=True)

    meta = {
        'ordering': ['-create_time']
    }