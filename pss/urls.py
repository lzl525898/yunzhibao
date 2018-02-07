__author__ = 'mlzx'
from django.conf.urls import patterns, include, url

urlpatterns = patterns(
    '',

    ####    物流得到key
    url(r'^interface/logistics/get/key/$', 'pss.views.logistics_get_key', name='logistics_get_key'),

    ####    物流公司生产订单
    url(r'^interface/logistics/order/create/$', 'pss.views.logistics_company_order', name='logistics_company_order'),

    url(r'^send/verification_code/$', 'authentic.views_interface.send_code', name='send_verification_code'),
    
     url(r'^api1.0/authorize/$', 'pss.views_api.authorize', name='authorize'),
     url(r'^api1.0/token_refresh/$', 'pss.views_api.refresh_token', name='refresh_token'),
     url(r'^api1.0/token_auth/$', 'pss.views_api.check_token', name='check_token'),
#      url(r'^test/$', 'pss.views_zhongan.runDemo', name='runDemo'),
     url(r'^testjava/$', 'pss.views_zhongan.runDemojava', name='runDemojava'),#ceshi
     #获取订单详情
#      url(r'^api1.0/get_order_detail/(?P<order_id>\w{24})/$', 'pss.views_api.get_order_detail', name='get_order_detail'),
#      url(r'^api1.0/get_documents/(?P<phone>\d+)/$', 'pss.views_api.get_documents', name='get_documents'),
     url(r'^api1.0/get_order_detail/$', 'pss.views_api.get_order_detail', name='get_order_detail'),
     url(r'^api1.0/get_documents/$', 'pss.views_api.get_documents', name='get_documents'),
     url(r'^api1.0/create_order/$', 'pss.views_api.create_order', name='create_order'),
     url(r'^api1.0/add_deposit/$', 'pss.views_api.add_deposit', name='add_deposit'),
     url(r'^api1.0/minus_deposit/$', 'pss.views_api.minus_deposit', name='minus_deposit'),
     url(r'^api1.0/get_balance/$', 'pss.views_api.get_balance', name='get_balance'),
     url(r'^api1.0/get_cargo/$', 'pss.views_api.get_cargo', name='get_cargo'),
     url(r'^api1.0/get_pack/$', 'pss.views_api.get_pack', name='get_pack'),
     url(r'^api1.0/get_area_list/$', 'pss.views_api.get_area_list', name='get_area_list'),
     url(r'^api1.0/immediate_insurance/$', 'pss.views_api.immediate_insurance', name='immediate_insurance'),
     url(r'^api1.0/confirm_insurance/$', 'pss.views_api.confirm_insurance', name='confirm_insurance'),
     url(r'^api1.0/get_insure_order_detail/$', 'pss.views_api.get_insure_order_detail', name='get_insure_order_detail'),
     
     #leka
     url(r'^api1.0/leka_immediate_insurance/$', 'pss.views_leka.leka_immediate_insurance', name='leka_immediate_insurance'),
     url(r'^api1.0/leka_get_order_detail/$', 'pss.views_leka.leka_get_order_detail', name='leka_get_order_detail'),
     url(r'^api1.0/leka_get_documents/$', 'pss.views_leka.leka_get_documents', name='leka_get_documents'),
     url(r'^api1.0/leka_get_order_list/$', 'pss.views_leka.leka_get_order_list', name='leka_get_order_list'),
     url(r'^api1.0/confirm_ceshi/$', 'pss.views_api.confirm_ceshi', name='confirm_ceshi'),

     #2017/08/03砖头
     #创建订单
     url(r'^api1.0/zhuantou_immediate_insurance/$', 'pss.views_zhuantou.zhuantou_immediate_insurance', name='zhuantou_immediate_insurance'),
     #查看保单地址
     url(r'^api1.0/zhuantou_search_insurance/$', 'pss.views_zhuantou.zhuantou_search_insurance', name='zhuantou_search_insurance'),
     #2017/10/22砖头对接借口
     url(r'^api1.0/zhuantou_insurance_create/$', 'pss.views_zhuantou.zhuantou_insurance_create', name='zhuantou_insurance_create'),
     #2018/01/23查看保单接口
     url(r'^api1.0/zhuantou_insurance_detail/$', 'pss.views_zhuantou.zhuantou_insurance_detail', name='zhuantou_insurance_detail'),
     #2018/01/24查看保单列表（分页）
     url(r'^api1.0/zhuantou_insurance_list/$', 'pss.views_zhuantou.zhuantou_insurance_list', name='zhuantou_insurance_list'),
)

