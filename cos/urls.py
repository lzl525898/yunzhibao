from django.conf.urls import patterns, include, url

urlpatterns = patterns(
    '',
    ####    订单
    url(r'^order/order_list/(?P<page_index>\d+)/$', 'cos.views_order.order_list', name='order_list'),
    url(r'^order/order_detail/(?P<order_id>\w{24})/$', 'cos.views_order.order_detail', name='order_detail'),
    #订单导出excel表
    url(r'^order/order_export/$', 'cos.views_order.order_export', name='order_export'),
    #批量导入保单号
    url(r'^order/import_insurance/$', 'cos.views_order.import_insurance', name='import_insurance'),
    ####    中介询价订单
    url(r'^order/cos_jdclbx_list/(?P<page_index>\d+)/$', 'cos.views_order.cos_jdclbx_list', name='cos_jdclbx_list'),
    url(r'^order/cos_jdclbx_detail/(?P<jdclbx_id>\w{24})/$', 'cos.views_order.cos_jdclbx_detail', name='cos_jdclbx_detail'),
    #报价
    url(r'^order/cos_intermediary_price/(?P<jdclbx_id>\w{24})/$', 'cos.views_order.cos_intermediary_price', name='cos_intermediary_price'),
    #确认报价
    url(r'^order/confirm_intermediary_price/(?P<jdclbx_id>\w{24})/$', 'cos.views_order.confirm_intermediary_price', name='confirm_intermediary_price'),
    #已投保订单列表
    url(r'^order/confirm_jdclbx_list/(?P<page_index>\d+)/$', 'cos.views_order.confirm_jdclbx_list', name='confirm_jdclbx_list'),
    url(r'^order/confirm_jdclbx_detail/(?P<jdclbx_id>\w{24})/$', 'cos.views_order.confirm_jdclbx_detail', name='confirm_jdclbx_detail'),
     #增加保单号
    url(r'^order/add_jdclbx_pic/(?P<jdclbx_id>\w{24})/$', 'cos.views_order.add_jdclbx_pic', name='add_jdclbx_pic'),
    #拒绝承保
    url(r'^order/jdclbx_refuse_company/(?P<jdclbx_id>\w{24})/$', 'cos.views_order.jdclbx_refuse_company', name='jdclbx_refuse_company'),
    #批量导入保单号2017/11/05
    url(r'^order/import_insurance_new/$', 'cos.views_order.import_insurance_new', name='import_insurance_new'),

)

