"""
Django settings for InsuranceSite project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))



# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '2*4kmq=(**k_lc6@1zgqiey@#k)scy*!c98d2an_#(2bfe3h-m'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []

#celery srtart
import djcelery
from celery.schedules import  crontab
djcelery.setup_loader()


CELERY_TIMEZONE='Asia/Shanghai'
CELERY_ALWAYS_EAGER = False
CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
BROKER_URL = 'redis://localhost:6379'
CELERY_RESULT_BACKEND = 'redis://localhost:6379'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERYBEAT_SCHEDULER = 'celery.beat.PersistentScheduler'
CELERYBEAT_SCHEDULE = {
     'add-every-day-6-morning': {
         'task': 'bms.tasks.TimingTaskWithOut',
         'schedule': crontab(hour=3, minute=1),
     },
}
#celery end

# Application definition

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'mongoengine.django.mongo_auth',    # 支持mongo认证
    'common',                       # 公用模块
    'authentic',                          # 认证模块
    'bms',                                  # 后台管理模块
    'pss',                          # 手机端服务支撑模块
    'wss',                           # 微信端服务支撑模块
    'cos' ,                          # 给保险公司人员查看订单
    'djcelery'  ,     ##celery 定时任务
    'rest_framework'
)
# REST_FRAMEWORK = {
#     'DEFAULT_PERMISSION_CLASSES': (
#         'rest_framework.permissions.IsAuthenticated',
#     )
# }

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
    )
}
MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

)

ROOT_URLCONF = 'InsuranceSite.urls'

WSGI_APPLICATION = 'InsuranceSite.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.dummy',   # 无关系数据库
    }
}


AUTHENTICATION_BACKENDS = {
    'mongoengine.django.auth.MongoEngineBackend'
}

AUTH_USER_MODEL = 'mongo_auth.MongoUser'
MONGO_USER_DOCUMENT = 'mongoengine.django.auth.User'

SESSION_ENGINE = 'mongoengine.django.sessions'
SESSION_SERIALIZER = 'mongoengine.django.sessions.BSONSerializer'

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/
FILE_CHARSET = 'utf-8'
DEFAULT_CHARSET = 'utf-8'
LANGUAGE_CODE = 'zh-cn'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

#USE_TZ = True
USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR,  'templates'),
)


#使static目录可以访问--------------------------------
MEDIA_ROOT = os.path.join(BASE_DIR, STATIC_URL.replace("/", ""))

STATICFILES_DIRS = (
    MEDIA_ROOT,
)

#未登录用户缺省登录地址--------------------------------
LOGIN_URL = '/auth/login/'

# 一些用于templates的常量

APP_NAME = '运之宝'
COPYRIGHT = '© 2016 哈尔滨中科方德股份有限公司'
SERVER_URL = 'http://123.57.35.153'
# SERVER_URL = 'http://yunzhibao56.com'
# SERVER_URL = 'http://123.56.197.215'
# SERVER_URL = 'http://10.0.0.123:8005'
# 网络连接超时，单位毫秒
HTTP_CONNECTION_TIME_OUT = 10000
#众安保险公司编码
ZHONGAN_COMPANY_CODE = "0401"

YUNZHIBAO_PHONE = "13359700418"

#添加车达达对接部分
#测试地址
QUCHEXIAN_URL = "http://www.tianshoufenqi.com"
#正式地址
#QUCHEXIAN_URL = "http://www.quchexian.cn"

