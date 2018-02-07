from django.conf.urls import patterns, include, url

urlpatterns = patterns(
    '',
    # 首页
    url(r'^index/$', 'bms.views.index', name='index'),

    ########                用户管理user                ########
    # 用户管理
    # 管理员 admin
    url(r'^user/admin/(?P<page_index>\d+)/$', 'bms.views_user.admin_list', name='admin_list'),
    url(r'^user/admin_edit/(?P<admin_id>\w{24})/$', 'bms.views_user.admin_edit', name='admin_edit'),
    url(r'^user/admin_save/(?P<admin_id>\w{24})/$', 'bms.views_user.admin_save', name='admin_save'),
    url(r'^user/admin_create/$', 'bms.views_user.admin_create', name='admin_create'),
    # url(r'^user/admin_delete/(?P<admin_id>\w{24})/$', 'bms.views_user.admin_delete', name='admin_delete'),
    #
    # #客户
    # url(r'^user/client/(?P<page_index>\d+)/$', 'bms.views_user.client_list', name='client_list'),
    # url(r'^user/client_edit/(?P<client_id>\w{24})/$', 'bms.views_user.client_edit', name='client_edit'),
    # url(r'^user/client_create/$', 'bms.views_user.client_create', name='client_create'),
    # url(r'^user/client_delete/(?P<client_id>\w{24})/$', 'bms.views_user.client_delete', name='client_delete'),
    #
    #注册用户
    url(r'^user/registered/(?P<page_index>\d+)/$', 'bms.views_user.registered_list', name='registered_list'),
    url(r'^user/registered_edit/(?P<registered_id>\w{24})/$', 'bms.views_user.registered_edit', name='registered_edit'),
    url(r'^user/registered_create/$', 'bms.views_user.registered_create', name='registered_create'),

    ########                用户认证                ########
    url(r'^certificate/(?P<page_index>\d+)/$', 'bms.views_user.certificate_list', name='certificate_list'),
    url(r'^certificate/detail/(?P<certificate_id>\w{24})/$', 'bms.views_user.certificate_detail', name='certificate_detail'),
    url(r'^certificate/create/(?P<registered_id>\w{24})/$', 'bms.views_user.certificate_create', name='certificate_create'),
    #认证
    url(r'^certificate/result/(?P<certificate_id>\w{24})/$', 'bms.views_user.certificate_result', name='certificate_result'),
    #驳回
    url(r'^certificate/reject/(?P<certificate_id>\w{24})/$', 'bms.views_user.certificate_reject', name='certificate_reject'),
    #重新认证
    url(r'^certificate/reject_repeat/(?P<certificate_id>\w{24})/$', 'bms.views_user.certificate_reject_repeat', name='certificate_reject_repeat'),

    #物流公司
    url(r'^user/transport/(?P<page_index>\d+)/$', 'bms.views_user.transport_list', name='transport_list'),
    url(r'^user/transport_detail/(?P<transport_id>\w{24})/$', 'bms.views_user.transport_detail', name='transport_detail'),
    url(r'^user/transport_edit/(?P<transport_id>\w{24})/$', 'bms.views_user.transport_edit', name='transport_edit'),

    #司机
    url(r'^user/driver/(?P<page_index>\d+)/$', 'bms.views_user.driver_list', name='driver_list'),
    url(r'^user/driver_detail/(?P<driver_id>\w{24})/$', 'bms.views_user.driver_detail', name='driver_detail'),
    url(r'^user/driver_edit/(?P<driver_id>\w{24})/$', 'bms.views_user.driver_edit', name='driver_edit'),

    #货主
    url(r'^user/boss/(?P<page_index>\d+)/$', 'bms.views_user.boss_list', name='boss_list'),
    url(r'^user/boss_detail/(?P<boss_id>\w{24})/$', 'bms.views_user.boss_detail', name='boss_detail'),
    url(r'^user/boss_edit/(?P<boss_id>\w{24})/$', 'bms.views_user.boss_edit', name='boss_edit'),
    #
    #理赔人员
    url(r'^user/claim/(?P<page_index>\d+)/$', 'bms.views_user.claim_list', name='claim_list'),
    url(r'^user/claim_detail/(?P<claim_id>\w{24})/$', 'bms.views_user.claim_detail', name='claim_detail'),
    url(r'^user/claim_edit/(?P<claim_id>\w{24})/$', 'bms.views_user.claim_edit', name='claim_edit'),
    url(r'^user/claim_create/$', 'bms.views_user.claim_create', name='claim_create'),
    # url(r'^user/claim_delete/(?P<claim_id>\w{24})/$', 'bms.views_user.claim_delete', name='claim_delete'),
    #
    #律师
    url(r'^user/lawyer/(?P<page_index>\d+)/$', 'bms.views_user.lawyer_list', name='lawyer_list'),
    url(r'^user/lawyer_detail/(?P<lawyer_id>\w{24})/$', 'bms.views_user.lawyer_detail', name='lawyer_detail'),
    url(r'^user/lawyer_edit/(?P<lawyer_id>\w{24})/$', 'bms.views_user.lawyer_edit', name='lawyer_edit'),
    url(r'^user/lawyer_create/$', 'bms.views_user.lawyer_create', name='lawyer_create'),
    # url(r'^user/lawyer_delete/(?P<lawyer_id>\w{24})/$', 'bms.views_user.lawyer_delete', name='lawyer_delete'),

    ########                产品管理               ########
    ####    保险总公司
    url(r'^product/head_company/(?P<page_index>\d+)/$', 'bms.views_product.head_company_list', name='head_company_list'),
    url(r'^product/head_company_detail/(?P<head_company_id>\w{24})/$', 'bms.views_product.head_company_detail', name='head_company_detail'),
    url(r'^product/head_company_edit/(?P<head_company_id>\w{24})/$', 'bms.views_product.head_company_edit', name='head_company_edit'),
    url(r'^product/head_company_create/$', 'bms.views_product.head_company_create', name='head_company_create'),

    ####    保险分公司
    url(r'^product/tail_company/(?P<page_index>\d+)/$', 'bms.views_product.tail_company_list', name='tail_company_list'),
    url(r'^product/tail_company_detail/(?P<tail_company_id>\w{24})/$', 'bms.views_product.tail_company_detail', name='tail_company_detail'),
    url(r'^product/tail_company_edit/(?P<tail_company_id>\w{24})/$', 'bms.views_product.tail_company_edit', name='tail_company_edit'),
    url(r'^product/tail_company_create/$', 'bms.views_product.tail_company_create', name='tail_company_create'),
    ###    产品
    url(r'^product/insurance_product/(?P<page_index>\d+)/$', 'bms.views_product.insurance_product_list', name='insurance_product_list'),
    url(r'^product/insurance_product_detail/(?P<insurance_product_id>\w{24})/$', 'bms.views_product.insurance_product_detail', name='insurance_product_detail'),
    url(r'^product/insurance_product_edit/(?P<insurance_product_id>\w{24})/$', 'bms.views_product.insurance_product_edit', name='insurance_product_edit'),
    url(r'^product/insurance_product_create/$', 'bms.views_product.insurance_product_create', name='insurance_product_create'),
    #       为产品新增文档
    url(r'^product/insurance_product_create_document/(?P<insurance_product_id>\w{24})/(?P<company_id>\w{24})/$', 'bms.views_product.insurance_product_create_document', name='insurance_product_create_document'),
    url(r'^product/insurance_product_delete_document/(?P<insurance_product_id>\w{24})/(?P<document_id>\w{24})/$', 'bms.views_product.insurance_product_delete_document', name='insurance_product_delete_document'),

    ###    产品
    url(r'^insurance/coupon/(?P<page_index>\d+)/$', 'bms.views_product.coupon_list', name='coupon_list'),
    # url(r'^coupon/insurance_coupon_detail/(?P<insurance_coupon_id>\w{24})/$', 'bms.views_product.insurance_coupon_detail', name='insurance_coupon_detail'),
    # url(r'^coupon/insurance_coupon_edit/(?P<insurance_coupon_id>\w{24})/$', 'bms.views_product.insurance_coupon_edit', name='insurance_coupon_edit'),
    # url(r'^coupon/insurance_coupon_create/$', 'bms.views_product.insurance_coupon_create', name='insurance_coupon_create'),

    ####    订单
    url(r'^insurance/order/(?P<page_index>\d+)/$', 'bms.views_order.order_list', name='order_list'),
    url(r'^insurance/order_detail/(?P<order_id>\w{24})/$', 'bms.views_order.order_detail', name='order_detail'),
    url(r'^insurance/order_edit/(?P<order_id>\w{24})/$', 'bms.views_order.order_edit', name='order_edit'),
    url(r'^insurance/order_create/$', 'bms.views_order.order_create', name='order_create'),
    #付款
    url(r'^insurance/order_pay/(?P<order_id>\w{24})/$', 'bms.views_order.order_pay', name='order_pay'),
    # ####    屏蔽保单
    # url(r'^insurance/policy/hidden/(?P<policy_id>\w{24})/$', 'bms.views_product.policy_hidden', name='policy_hidden'),


    # url(r'^insurance/company_delete/(?P<company_id>\w{24})/$', 'bms.views_insurance.company_delete', name='company_delete'),
    ####    投保文档的修改和新增
    # url(r'^insurance/company/document/save/(?P<company_id>\w{24})/$', 'bms.views_insurance.company_document_save', name='company_document_save'),

    ####    保险文档
    url(r'^insurance/document/(?P<page_index>\d+)/$', 'bms.views_product.insurance_document_list', name='insurance_document_list'),
    url(r'^insurance/document_detail/(?P<document_id>\w{24})/$', 'bms.views_product.insurance_document_detail', name='insurance_document_detail'),
    url(r'^insurance/document_edit/(?P<document_id>\w{24})/$', 'bms.views_product.insurance_document_edit', name='insurance_document_edit'),
    url(r'^insurance/document_create/$', 'bms.views_product.insurance_document_create', name='insurance_document_create'),
    # # url(r'^insurance/document_delete/(?P<document_id>\w{24})/$', 'bms.views_insurance.document_delete', name='document_delete'),
    ####    预览文档内容
    url(r'^insurance/document/preview/(?P<document_id>\w{24})/$', 'bms.views_product.insurance_document_preview', name='insurance_document_preview'),
    ####        赔案
    url(r'^insurance/compensate/(?P<page_index>\d+)/$', 'bms.views_compensate.compensate_list', name='compensate_list'),
    url(r'^insurance/compensate_detail/(?P<compensate_id>\w{24})/$', 'bms.views_compensate.compensate_detail', name='compensate_detail'),
    #
    # ########               互动信息 interactive                #############################################################################################
    #
    # ####    意见和建议
    # url(r'^interactive/suggestions/(?P<page_index>\d+)/$', 'bms.views_interactive.suggestions_list', name='suggestions_list'),
    # url(r'^interactive/suggestions/(?P<suggestions_id>\w{24})/$', 'bms.views_interactive.suggestions_detail', name='suggestions_detail'),

    ########                异常管理 exception                ########
    # 异常 exception
    url(r'^exception/(?P<page_index>\d+)/$', 'bms.views_exception.exception_list', name='exception_list'),
    url(r'^exception/(?P<exception_id>\w{24})/$', 'bms.views_exception.exception_detail', name='exception_detail'),
    url(r'^exception/new/$', 'bms.views_exception.new_exception_detail', name='new_exception_detail'),
    url(r'^exception/delete/(?P<exception_id>\w{24})/$', 'bms.views_exception.exception_delete', name='exception_delete'),
    url(r'^exception/delete/all/$', 'bms.views_exception.exception_delete_all', name='exception_delete_all'),
    url(r'^exception/delete/similar/(?P<exception_id>\w{24})/$', 'bms.views_exception.exception_delete_similar', name='exception_delete_similar'),


    ########                系统日志 logs                ########
    # 系统日志日志 logs
    url(r'^logs/(?P<page_index>\d+)/$', 'bms.views_log.log_list', name='log_list'),
    url(r'^logs/(?P<log_id>\w{24})/$', 'bms.views_log.log_detail', name='log_detail'),
    url(r'^logs/delete/(?P<log_id>\w{24})/$', 'bms.views_log.log_delete', name='log_delete'),
    url(r'^logs/delete/all/$', 'bms.views_log.log_delete_all', name='log_delete_all'),

    # 微信事件日志 wechat event wechat_events
    url(r'^wechat/event/(?P<page_index>\d+)/$', 'bms.views_log.wechat_event_list', name='wechat_event_list'),
    url(r'^wechat/event/(?P<wechat_event_id>\w{24})/$', 'bms.views_log.wechat_event_detail', name='wechat_event_detail'),
    url(r'^wechat/event/delete/(?P<wechat_event_id>\w{24})/$', 'bms.views_log.wechat_event_delete', name='wechat_event_delete'),
    url(r'^wechat/event/delete/all/$', 'bms.views_log.wechat_event_delete_all', name='wechat_event_delete_all'),

    ########                服务器设置管理 settings                ########
    # 设置 settings
    url(r'^settings/$', 'bms.views_settings.settings_index', name='settings'),
    url(r'^settings/base/$', 'bms.views_settings.settings_base', name='settings_base'),
    url(r'^settings/database/$', 'bms.views_settings.settings_database', name='settings_database'),
    url(r'^settings/database/save/$', 'bms.views_settings.settings_database_save', name='settings_database_save'),
    url(r'^settings/debug/$', 'bms.views_settings.debug_model', name='setting_debug_model'),


    # 位置 locations
    url(r'^interface/locations/get_insurance_company_list/$', 'bms.views_interface.get_insurance_company_list', name='get_insurance_company_list'),
    url(r'^interface/locations/get_insurance_type_list/$', 'bms.views_interface.get_insurance_type_list', name='get_insurance_type_list'),
    #添加货物类型
    url(r'^interface/locations/get_insurance_product_list$', 'bms.views_interface.get_insurance_product_list', name='get_insurance_product_list'),

    ##### 测试专用
    url(r'^test/$', 'bms.views_test.test', name='test'),


)

