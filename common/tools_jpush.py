__author__ = 'mlzx'

import thridPart.jpush as jpush
from thridPart.jpush.common import JPushFailure
import json
try:
    from common.models import SiteSettings
except ImportError:
    from common.models import BaseSettings as SiteSettings
from common.models import Notification
from django.conf import settings


# 极光推送工具类
class JPushTools(object):
    _jpush = None
    app_key = None
    master_secret = None

    def __init__(self, key, secret):
        self.app_key = key
        self.master_secret = secret
        self._jpush = jpush.JPush(self.app_key, self.master_secret)

    @staticmethod
    def default_tool():
        return JPushTools("", "")

    def send_notification(self, alert, title=None,  extras=None, tag=None, alias=None):
        try:
            push = self._jpush.create_push()
            if tag and alias:
                push.audience = jpush.audience(jpush.tag(tag), jpush.alias(alias))
            elif tag:
                push.audience = jpush.audience(jpush.tag(tag))
            elif alias:
                push.audience = jpush.audience(jpush.alias(alias))
            else:
                push.audience = jpush.all_
            if extras or title:
                android_msg = jpush.android(alert=alert, title=title, extras=extras)
                ios_msg = jpush.ios(alert=alert, extras=extras)
                push.notification = jpush.notification(alert=alert, android=android_msg, ios=ios_msg)
            else:
                push.notification = jpush.notification(alert=alert)
            push.options = {"time_to_live": 86400, "apns_production": not settings.DEBUG}
            push.platform = jpush.all_
            push.send()
            notification = Notification()
            notification.alert = alert
            notification.title = title if title else ""
            if extras:
                if isinstance(extras, str):
                    notification.extras = extras
                else:
                    if isinstance(extras, dict):
                        notification.extras = json.dumps(extras)
                    elif isinstance(extras, list):
                        notification.extras = ','.join(extras)
                    else:
                        notification.extras = str(extras)
            if tag:
                notification.tag = tag if isinstance(tag, str) else ','.join(tag)
            if alias:
                notification.alias = alias if isinstance(alias, str) else ','.join(alias)
            notification.save()
            return True
        except JPushFailure as e:
            return False

