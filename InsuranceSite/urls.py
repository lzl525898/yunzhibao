from django.conf.urls import patterns, include, url
# from django.contrib import admin

urlpatterns = patterns(
    '',

    url(r'^$', 'bms.views.index', name='home'),                   # 默认首页
    url(r'^auth/', include('authentic.urls', namespace='authentic')),       # 认证模块
    url(r'^bms/', include('bms.urls', namespace='bms')),                        # 后台管理模块
    url(r'^pss/', include('pss.urls', namespace='pss')),                        # 手机端接口
    url(r'^wss/', include('wss.urls', namespace='wss')),                        # 微信端数据交互
    url(r'^cos/', include('cos.urls', namespace='cos')),                        # 给保险公司人员查看订单
)
