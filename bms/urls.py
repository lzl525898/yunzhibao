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
    #2017添加注册用户详情页面
    url(r'^user/registered_detail/(?P<registered_id>\w{24})/$', 'bms.views_user.registered_detail', name='registered_detail'),

    ########                用户认证                ########
    url(r'^user/certificate/(?P<page_index>\d+)/$', 'bms.views_user.certificate_list', name='certificate_list'),
    url(r'^user/certificate/detail/(?P<certificate_id>\w{24})/$', 'bms.views_user.certificate_detail', name='certificate_detail'),
    url(r'^user/certificate/create/(?P<registered_id>\w{24})/$', 'bms.views_user.certificate_create', name='certificate_create'),
    #认证
    url(r'^user/certificate/result/(?P<certificate_id>\w{24})/$', 'bms.views_user.certificate_result', name='certificate_result'),
    #驳回
    url(r'^user/certificate/reject/(?P<certificate_id>\w{24})/$', 'bms.views_user.certificate_reject', name='certificate_reject'),
    #重新认证
    url(r'^user/certificate/reject_repeat/(?P<certificate_id>\w{24})/$', 'bms.views_user.certificate_reject_repeat', name='certificate_reject_repeat'),

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
    
    #车主
    url(r'^user/owner/(?P<page_index>\d+)/$', 'bms.views_user.owner_list', name='owner_list'),
    url(r'^user/owner_detail/(?P<owner_id>\w{24})/$', 'bms.views_user.owner_detail', name='owner_detail'),
    url(r'^user/owner_edit/(?P<owner_id>\w{24})/$', 'bms.views_user.owner_edit', name='owner_edit'),
    #
    #理赔人员
    url(r'^user/claim/(?P<page_index>\d+)/$', 'bms.views_user.claim_list', name='claim_list'),
    url(r'^user/claim_detail/(?P<claim_id>\w{24})/$', 'bms.views_user.claim_detail', name='claim_detail'),
    url(r'^user/claim_edit/(?P<claim_id>\w{24})/$', 'bms.views_user.claim_edit', name='claim_edit'),
    url(r'^user/claim_create/$', 'bms.views_user.claim_create', name='claim_create'),
    # url(r'^user/claim_delete/(?P<claim_id>\w{24})/$', 'bms.views_user.claim_delete', name='claim_delete'),
    #
    #保险中介人员
    url(r'^user/intermediary_people_list/(?P<page_index>\d+)/$', 'bms.views_user.intermediary_people_list', name='intermediary_people_list'),
    url(r'^user/intermediary_people_create/$', 'bms.views_user.intermediary_people_create', name='intermediary_people_create'),
    url(r'^user/intermediary_people_detail/(?P<intermediary_people_id>\w{24})/$', 'bms.views_user.intermediary_people_detail', name='intermediary_people_detail'),
    url(r'^user/intermediary_people_edit/(?P<intermediary_people_id>\w{24})/$', 'bms.views_user.intermediary_people_edit', name='intermediary_people_edit'),
    
    
    #律师
    url(r'^user/lawyer/(?P<page_index>\d+)/$', 'bms.views_user.lawyer_list', name='lawyer_list'),
    url(r'^user/lawyer_detail/(?P<lawyer_id>\w{24})/$', 'bms.views_user.lawyer_detail', name='lawyer_detail'),
    url(r'^user/lawyer_edit/(?P<lawyer_id>\w{24})/$', 'bms.views_user.lawyer_edit', name='lawyer_edit'),
    url(r'^user/lawyer_create/$', 'bms.views_user.lawyer_create', name='lawyer_create'),
    # url(r'^user/lawyer_delete/(?P<lawyer_id>\w{24})/$', 'bms.views_user.lawyer_delete', name='lawyer_delete'),

    #
    #预存保费
    url(r'^user/balance/(?P<page_index>\d+)/$', 'bms.views_user.balance_list', name='balance_list'),
    url(r'^user/deposit/$', 'bms.views_user.deposit', name='deposit'),
    url(r'^user/deposit_statistical/(?P<page_index>\d+)/$', 'bms.views_user.deposit_statistical', name='deposit_statistical'),
    url(r'^user/wx_deposit_statistical/(?P<page_index>\d+)/$', 'bms.views_user.wx_deposit_statistical', name='wx_deposit_statistical'),

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

    ###    产品
    url(r'^product/insurance_product/(?P<page_index>\d+)/$', 'bms.views_product.insurance_product_list', name='insurance_product_list'),
    url(r'^product/insurance_product_detail/(?P<insurance_product_id>\w{24})/$', 'bms.views_product.insurance_product_detail', name='insurance_product_detail'),
    url(r'^product/insurance_product_edit/(?P<insurance_product_id>\w{24})/$', 'bms.views_product.insurance_product_edit', name='insurance_product_edit'),
    url(r'^product/insurance_product_create/$', 'bms.views_product.insurance_product_create', name='insurance_product_create'),
    #       为产品新增文档
    url(r'^product/insurance_product_create_document/(?P<insurance_product_id>\w{24})/(?P<company_id>\w{24})/$', 'bms.views_product.insurance_product_create_document', name='insurance_product_create_document'),
    url(r'^product/insurance_product_delete_document/(?P<insurance_product_id>\w{24})/(?P<document_id>\w{24})/$', 'bms.views_product.insurance_product_delete_document', name='insurance_product_delete_document'),

    ###    优惠券
    url(r'^product/coupon/(?P<page_index>\d+)/$', 'bms.views_product.coupon_list', name='coupon_list'),
    url(r'^product/coupon/coupon_detail/(?P<coupon_id>\w{24})/$', 'bms.views_product.coupon_detail', name='coupon_detail'),
    url(r'^product/coupon/coupon_edit/(?P<coupon_id>\w{24})/$', 'bms.views_product.coupon_edit', name='coupon_edit'),
    url(r'^product/coupon/coupon_create/$', 'bms.views_product.coupon_create', name='coupon_create'),
    #   发送优惠券
    url(r'^product/coupon/coupon_send_list/(?P<coupon_id>\w{24})/(?P<page_index>\d+)/$', 'bms.views_product.coupon_send_list', name='coupon_send_list'),
    url(r'^product/coupon/coupon_send/(?P<coupon_id>\w{24})/$', 'bms.views_product.coupon_send', name='coupon_send'),
    #   优惠券发放记录
    url(r'^product/coupon/coupon_send/record/(?P<page_index>\d+)/$', 'bms.views_product.coupon_send_record', name='coupon_send_record'),
    #中介渠道
    url(r'^product/intermediary/(?P<page_index>\d+)/$', 'bms.views_product.intermediary_list', name='intermediary_list'),
    url(r'^product/intermediary_create/$', 'bms.views_product.intermediary_create', name='intermediary_create'),
    url(r'^product/intermediary_detail/(?P<intermediary_id>\w{24})/$', 'bms.views_product.intermediary_detail', name='intermediary_detail'),
    url(r'^product/intermediary_edit/(?P<intermediary_id>\w{24})/$', 'bms.views_product.intermediary_edit', name='intermediary_edit'),
    #添加中介渠道对应公司产品费率
    url(r'^product/intermediary_company_rate/(?P<intermediary_id>\w{24})/$', 'bms.views_product.intermediary_company_rate', name='intermediary_company_rate'),
    
    #车险订单
    url(r'^order/jdclbx_list/(?P<page_index>\d+)/$', 'bms.views_jdcbx.jdclbx_list', name='jdclbx_list'),
    url(r'^order/jdclbx_create/$', 'bms.views_jdcbx.jdclbx_create', name='jdclbx_create'),
    url(r'^order/jdclbx_detail/(?P<jdclbx_id>\w{24})/$', 'bms.views_jdcbx.jdclbx_detail', name='jdclbx_detail'),
    url(r'^order/jdclbx_edit/(?P<jdclbx_id>\w{24})/$', 'bms.views_jdcbx.jdclbx_edit', name='jdclbx_edit'),
    url(r'^order/jdclbx_verify/(?P<jdclbx_id>\w{24})/$', 'bms.views_jdcbx.jdclbx_verify', name='jdclbx_verify'),
    url(r'^order/jdclbx_delete/(?P<jdclbx_id>\w{24})/$', 'bms.views_jdcbx.jdclbx_delete', name='jdclbx_delete'),
    #驳回2017/2/9
    url(r'^order/jdclbx_fail/(?P<jdclbx_id>\w{24})/$', 'bms.views_jdcbx.jdclbx_fail', name='jdclbx_fail'),
    #车险确认投保
    url(r'^order/jdclbx_choose_company/(?P<intermediary_price_id>\w{24})/$', 'bms.views_jdcbx.jdclbx_choose_company', name='jdclbx_choose_company'),
    #车险付款
    url(r'^order/jdclbx_pay/(?P<jdclbx_id>\w{24})/$', 'bms.views_jdcbx.jdclbx_pay', name='jdclbx_pay'),
    #车险添加手续费比例
    url(r'^order/add_jdclbx_process/(?P<jdclbx_id>\w{24})/$', 'bms.views_jdcbx.add_jdclbx_process', name='add_jdclbx_process'),
    #车险验证手续费信息填写完成
    url(r'^order/verify_process_state/(?P<jdclbx_id>\w{24})/$', 'bms.views_jdcbx.verify_process_state', name='verify_process_state'),

    ####    订单
    url(r'^order/order_list/(?P<page_index>\d+)/$', 'bms.views_order.order_list', name='order_list'),
    url(r'^order/order_detail/(?P<order_id>\w{24})/$', 'bms.views_order.order_detail', name='order_detail'),
    url(r'^order/order_edit/(?P<order_id>\w{24})/$', 'bms.views_order.order_edit', name='order_edit'),
    url(r'^order/order_create/$', 'bms.views_order.order_create', name='order_create'),
    # ####    屏蔽订单
    url(r'^order/hidden/(?P<order_id>\w{24})/$', 'bms.views_order.order_hidden', name='order_hidden'),
    #付款
    url(r'^order/order_pay/(?P<order_id>\w{24})/$', 'bms.views_order.order_pay', name='order_pay'),
    #修改投保人
    url(r'^order/edit_insured/(?P<order_id>\w{24})/$', 'bms.views_order.edit_insured', name='edit_insured'),
    #批量导入保单号
    url(r'^order/import_insurance/$', 'bms.views_order.import_insurance', name='import_insurance'),
    #增加保单号
    url(r'^order/add_insurance_pic/(?P<order_id>\w{24})/$', 'bms.views_order.add_insurance_pic', name='add_insurance_pic'),
    # 修改单个保单图片
    url(r'^order/edit_insurance_pic/(?P<order_id>\w{24})/$', 'bms.views_order.edit_insurance_pic', name='edit_insurance_pic'),
    # 删除单个保单图片信息
    url(r'^order/delete_insurance_pic/(?P<order_id>\w{24})/$', 'bms.views_order.delete_insurance_pic', name='delete_insurance_pic'),

    # 修改单个车次图片
    url(r'^order/edit_batch_pic/(?P<order_id>\w{24})/$', 'bms.views_order.edit_batch_pic', name='edit_batch_pic'),
    # 删除单个车次图片
    url(r'^order/delete_batch_pic/(?P<order_id>\w{24})/$', 'bms.views_order.delete_batch_pic', name='delete_batch_pic'),

    #订单导出excel表
    url(r'^order/order_export/$', 'bms.views_order.order_export', name='order_export'),

    #为订单中的车次添加清单
    url(r'^insurance/order/batch/add/(?P<order_id>\w{24})/$', 'bms.views_order.add_batch_list', name='add_batch_list'),
    url(r'^insurance/order/batch/edit/(?P<order_id>\w{24})/$', 'bms.views_order.edit_batch_list', name='edit_batch_list'),
    url(r'^insurance/order/batch/delete/(?P<order_id>\w{24})/$', 'bms.views_order.delete_batch_list', name='delete_batch_list'),

    ####        赔案
    url(r'^insurance/compensate/(?P<page_index>\d+)/$', 'bms.views_compensate.compensate_list', name='compensate_list'),
    url(r'^insurance/compensate_detail/(?P<compensate_id>\w{24})/$', 'bms.views_compensate.compensate_detail', name='compensate_detail'),
    #
    # ########               互动信息 interactive                #############################################################################################
    #
    # ####    意见和建议
    # url(r'^interactive/suggestions/(?P<page_index>\d+)/$', 'bms.views_interactive.suggestions_list', name='suggestions_list'),
    # url(r'^interactive/suggestions/(?P<suggestions_id>\w{24})/$', 'bms.views_interactive.suggestions_detail', name='suggestions_detail'),

    ########               微信公众号管理 宣传推广               #####################################################

    ####    物流公司
    url(r'^campaign/logistics_list/(?P<page_index>\d+)/$', 'bms.views_campaign.logistics_list', name='logistics_list'),
    url(r'^campaign/logistics_detail/(?P<logistics_id>\w{24})/$', 'bms.views_campaign.logistics_detail', name='logistics_detail'),
    url(r'^campaign/logistics_edit/(?P<logistics_id>\w{24})/$', 'bms.views_campaign.logistics_edit', name='logistics_edit'),
    url(r'^campaign/logistics_create/$', 'bms.views_campaign.logistics_create', name='logistics_create'),
    url(r'^campaign/logistics_delete/(?P<logistics_id>\w{24})/$', 'bms.views_campaign.logistics_delete', name='logistics_delete'),
    #增加物流公司图片
    url(r'^campaign/add_logistics_pic/(?P<logistics_id>\w{24})/$', 'bms.views_campaign.add_logistics_pic', name='add_logistics_pic'),
    # 修改单个物流公司图片
    url(r'^campaign/edit_logistics_pic/(?P<logistics_id>\w{24})/$', 'bms.views_campaign.edit_logistics_pic', name='edit_logistics_pic'),
    # 删除单个物流公司图片信息
    url(r'^campaign/delete_logistics_pic/(?P<logistics_id>\w{24})/$', 'bms.views_campaign.delete_logistics_pic', name='delete_logistics_pic'),

    url(r'^campaign/campaign_lawyer_list/(?P<page_index>\d+)/$', 'bms.views_campaign.campaign_lawyer_list', name='campaign_lawyer_list'),
    url(r'^campaign/campaign_lawyer_detail/(?P<campaign_lawyer_id>\w{24})/$', 'bms.views_campaign.campaign_lawyer_detail', name='campaign_lawyer_detail'),
    url(r'^campaign/campaign_lawyer_edit/(?P<campaign_lawyer_id>\w{24})/$', 'bms.views_campaign.campaign_lawyer_edit', name='campaign_lawyer_edit'),
    url(r'^campaign/campaign_lawyer_create/$', 'bms.views_campaign.campaign_lawyer_create', name='campaign_lawyer_create'),
    url(r'^campaign/campaign_lawyer_delete/(?P<campaign_lawyer_id>\w{24})/$', 'bms.views_campaign.campaign_lawyer_delete', name='campaign_lawyer_delete'),
    # 宣传推广-司机
    url(r'^campaign/driver_list/(?P<page_index>\d+)/$', 'bms.views_campaign.driver_list', name='campaign_driver_list'),
    url(r'^campaign/driver_create/$', 'bms.views_campaign.driver_create', name='campaign_driver_create'),
    url(r'^campaign/driver_delete/(?P<driver_id>\w{24})/$', 'bms.views_campaign.driver_delete', name='campaign_driver_delete'),
    url(r'^campaign/driver_detail/(?P<driver_id>\w{24})/$', 'bms.views_campaign.driver_detail', name='campaign_driver_detail'),
    url(r'^campaign/driver_edit/(?P<driver_id>\w{24})/$', 'bms.views_campaign.driver_edit', name='driver_edit_test'),
#     url(r'^campaign/related_user/$', 'bms.views_campaign.related_user', name='related_user'),
#     url(r'^campaign/cancel_related_user/$', 'bms.views_campaign.cancel_related_user', name='cancel_related_user'),




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
    #用户协议
    url(r'^settings/user/protocol/$', 'bms.views_settings.user_protocol', name='settings_user_protocol'),
    url(r'^settings/user/protocol/preview/$', 'bms.views_settings.user_protocol_preview', name='settings_user_protocol_preview'),
    #物流平台设置
    url(r'^settings/platform/$', 'bms.views_settings.settings_platform', name='settings_platform'),
    url(r'^settings/edit_platform/$', 'bms.views_settings.edit_platform', name='edit_platform'),
    
    #保险平台设置
     url(r'^settings/insurance_platform/$', 'bms.views_settings.insurance_platform', name='insurance_platform'),
     url(r'^settings/edit_insurance/(?P<platform_id>\w{24})/$', 'bms.views_settings.edit_insurance', name='edit_insurance'),
     url(r'^settings/insurance_delete/(?P<platform_id>\w{24})/$', 'bms.views_settings.insurance_delete', name='insurance_delete'),
    
    #平台产品维护
    url(r'^settings/platform_product/$', 'bms.views_settings.platform_product', name='platform_product_list'),
    url(r'^settings/platform_product_create/$', 'bms.views_settings.platform_product_create', name='platform_product_save'),
    url(r'^settings/platform_product_delete/(?P<product_id>\w{24})/$', 'bms.views_settings.platform_product_delete', name='platform_product_delete'),
    url(r'^settings/platform_product_detail/(?P<product_id>\w{24})/$', 'bms.views_settings.platform_product_detail', name='platform_product_detail'),
    url(r'^settings/platform_product_edit/(?P<product_id>\w{24})/$', 'bms.views_settings.platform_product_edit', name='platform_product_edit'),
    url(r'^settings/uploadImg/$', 'bms.views_settings.uploadImg', name='uploadImg'),
    
    # 位置 locations
    url(r'^interface/locations/get_insurance_company_list/$', 'bms.views_interface.get_insurance_company_list', name='get_insurance_company_list'),
    url(r'^interface/locations/get_insurance_type_list/$', 'bms.views_interface.get_insurance_type_list', name='get_insurance_type_list'),
    #添加货物类型
    url(r'^interface/locations/get_insurance_product_list$', 'bms.views_interface.get_insurance_product_list', name='get_insurance_product_list'),
    #添加包装方式
    url(r'^interface/locations/get_pack_detail_list', 'bms.views_interface.get_pack_detail_list', name='get_pack_detail_list'),
    #test获取货物详情
    url(r'^interface/locations/get_product_cargo_list', 'bms.views_interface.get_product_cargo_list', name='get_product_cargo_list'),
    #获取城市列表
    url(r'^interface/locations/get_city_list', 'bms.views_interface.get_city_list', name='get_city_list'),
    #获取县/区列表
    url(r'^interface/locations/get_dist_list', 'bms.views_interface.get_dist_list', name='get_dist_list'),
    #获取货物大类对应小类货物详情
    url(r'^interface/locations/get_cargo_detail_list', 'bms.views_interface.get_cargo_detail_list', name='get_cargo_detail_list'),
    #产品详情页面，产品货物小类回显
    url(r'^interface/locations/get_cargo_type_list', 'bms.views_interface.get_cargo_type_list', name='get_cargo_type_list'),

    ########                通用工具 tools                ########
    # 转到详细页
    url(r'^tools/(?P<item_id>\w{24})/$', 'bms.views_tools.item_detail', name='item_detail'),

    ##### 测试专用
    url(r'^test/$', 'bms.views_test.test', name='test'),
    
    ########                数据统计部分               ########
    # 转到详细页
    url(r'^statistics/insurance_amount/$', 'bms.views_statistics.insurance_amount', name='insurance_amount'),
    
    ########                车辆统计               ########
    # 转到详细页
    url(r'^car/car_list/(?P<page_index>\d+)/$', 'bms.views_car.car_list', name='car_list'),
    url(r'^car/car_create/$', 'bms.views_car.car_create', name='car_create'),
    url(r'^car/car_detail/(?P<car_id>\w{24})/$', 'bms.views_car.car_detail', name='car_detail'),
    url(r'^car/car_certificate/(?P<car_id>\w{24})/$', 'bms.views_car.car_certificate', name='car_certificate'),
    url(r'^car/car_delete/(?P<car_id>\w{24})/$', 'bms.views_car.car_delete', name='car_delete'),
    url(r'^car/car_edit/(?P<car_id>\w{24})/$', 'bms.views_car.car_edit', name='car_edit'),
    # 修改单个车辆图片
    url(r'^car/edit_car_pic/(?P<car_id>\w{24})/$', 'bms.views_car.edit_car_pic', name='edit_car_pic'),
    #返还油卡
    url(r'^car/car_oil_card/(?P<car_id>\w{24})/$', 'bms.views_car.car_oil_card', name='car_oil_card'),
        #货物类型入口
    url(r'^product/cargo_intry/(?P<page_index>\d+)$', 'bms.views_product.cargo_intry', name='cargo_intry'),
    url(r'^product/cargo_delete/(?P<cargo_id>\w{24})/$', 'bms.views_product.cargo_delete', name='cargo_delete'),
    url(r'^product/cargo_edit/$', 'bms.views_product.cargo_edit', name='cargo_edit'),
    url(r'^product/cargo_add_product/$', 'bms.views_product.cargo_add_product', name='cargo_add_product'),
    #货物大类维护
    url(r'^product/cargo_type_intry/(?P<page_index>\d+)$', 'bms.views_product.cargo_type_intry', name='cargo_type_intry'),
    url(r'^product/cargo_type_edit/(?P<page_index>\d+)$', 'bms.views_product.cargo_type_edit', name='cargo_type_edit'),
     #众安同步地址
     url(r'^product/cargoArea_sync/$', 'bms.views_product.cargoArea_sync', name='cargoArea_sync'),
     url(r'^product/cargoArea_json/$', 'bms.views_product.cargoArea_json', name='cargoArea_json'),
     url(r'^product/read_city_detail/(?P<page_index>\d+)$', 'bms.views_product.read_city_detail', name='read_city_detail'),
     #不保运输省份
     url(r'^product/add_no_insurable_route/$', 'bms.views_product.add_no_insurable_route', name='add_no_insurable_route'),

    #生成二维码
    url(r'^user/build_code_pic/(?P<client_id>\w{24})/$', 'bms.views_user.build_code_pic', name='build_code_pic'),
    
    #补充用户信息
    url(r'^user/add_user_information/(?P<registered_id>\w{24})/$', 'bms.views_user.add_user_information', name='add_user_information'),
    #补充用户局部信息
    url(r'^user/improve_part_information/(?P<registered_id>\w{24})/$', 'bms.views_user.improve_part_information', name='improve_part_information'),
    #修改用户密码
    url(r'^user/change_user_password/$', 'bms.views_user.change_user_password', name='change_user_password'),
    #修改用户状态
    url(r'^user/change_user_type/(?P<registered_id>\w{24})/$', 'bms.views_user.change_user_type', name='change_user_type'),
    #支付统计
    url(r'^user/payment_statistical/(?P<page_index>\d+)/$', 'bms.views_user.payment_statistical', name='payment_statistical'),
    #订单导出excel表
    url(r'^user/payment_export/$', 'bms.views_user.payment_export', name='payment_export'),
    #修改用户基本信息
    url(r'^user/change_user_imformation/$', 'bms.views_user.change_user_imformation', name='change_user_imformation'),
    #获取用户基本信息
    url(r'^interface/locations/get_user_detail', 'bms.views_interface.get_user_detail', name='get_user_detail'),
    
    ########               汇聚宝对接               ########
    # 修改订单状态
    url(r'^order/change_order_state/$', 'bms.views_order.change_order_state', name='change_order_state'),
    #汇聚宝传单
    url(r'^order/order_pass/(?P<order_id>\w{24})/$', 'bms.views_order.order_pass', name='order_pass'),
    
    ###导出机动车辆保单信息
    #订单导出excel表
    url(r'^order/jdclbx_export/$', 'bms.views_jdcbx.jdclbx_export', name='jdclbx_export'),
    
    ##增加添加保单的方法
    #增加保单号
    url(r'^order/add_insurance_pic_new/(?P<order_id>\w{24})/$', 'bms.views_order.add_insurance_pic_new', name='add_insurance_pic_new'),
    #批量上传订单
    url(r'^order/input_order_list/$', 'bms.views_order.input_order_list', name='input_order_list'),
    
    
    #2017/12/04添加员工保险
    url(r'^car/employee_list/(?P<page_index>\d+)/$', 'bms.views_car.employee_list', name='employee_list'),
    url(r'^car/employee_create/$', 'bms.views_car.employee_create', name='employee_create'),
    url(r'^car/employee_detail/(?P<employee_id>\w{24})/$', 'bms.views_car.employee_detail', name='employee_detail'),
    url(r'^car/employee_edit/(?P<employee_id>\w{24})/$', 'bms.views_car.employee_edit', name='employee_edit'),
    url(r'^car/employee_delete/(?P<employee_id>\w{24})/$', 'bms.views_car.employee_delete', name='employee_delete'),
    
    #2017/12/04添加货运年险
    url(r'^car/freight_list/(?P<page_index>\d+)/$', 'bms.views_car.freight_list', name='freight_list'),
    url(r'^car/freight_create/$', 'bms.views_car.freight_create', name='freight_create'),
    url(r'^car/freight_detail/(?P<freight_id>\w{24})/$', 'bms.views_car.freight_detail', name='freight_detail'),
    url(r'^car/freight_edit/(?P<freight_id>\w{24})/$', 'bms.views_car.freight_edit', name='freight_edit'),
    url(r'^car/freight_delete/(?P<freight_id>\w{24})/$', 'bms.views_car.freight_delete', name='freight_delete'),
    
    #2017/12/06添加个人保险
    url(r'^car/personal_list/(?P<page_index>\d+)/$', 'bms.views_car.personal_list', name='personal_list'),
    url(r'^car/personal_create/$', 'bms.views_car.personal_create', name='personal_create'),
    url(r'^car/personal_detail/(?P<personal_id>\w{24})/$', 'bms.views_car.personal_detail', name='personal_detail'),
    url(r'^car/personal_edit/(?P<personal_id>\w{24})/$', 'bms.views_car.personal_edit', name='personal_edit'),
    url(r'^car/personal_delete/(?P<personal_id>\w{24})/$', 'bms.views_car.personal_delete', name='personal_delete'),
    
    #2017/12/06添加车险（保险管家）车辆统计部分
    url(r'^car/car_create_new/$', 'bms.views_car.car_create_new', name='car_create_new'),
    url(r'^car/car_detail_new/(?P<car_id>\w{24})/$', 'bms.views_car.car_detail_new', name='car_detail_new'),
    url(r'^car/car_edit_new/(?P<car_id>\w{24})/$', 'bms.views_car.car_edit_new', name='car_edit_new'),
    
    #2017/12/13添加其他保险
    url(r'^car/other_insurance_list/(?P<page_index>\d+)/$', 'bms.views_car.other_insurance_list', name='other_insurance_list'),
    url(r'^car/other_insurance_create/$', 'bms.views_car.other_insurance_create', name='other_insurance_create'),
    url(r'^car/other_insurance_detail/(?P<other_insurance_id>\w{24})/$', 'bms.views_car.other_insurance_detail', name='other_insurance_detail'),
    url(r'^car/other_insurance_edit/(?P<other_insurance_id>\w{24})/$', 'bms.views_car.other_insurance_edit', name='other_insurance_edit'),
    url(r'^car/other_insurance_delete/(?P<other_insurance_id>\w{24})/$', 'bms.views_car.other_insurance_delete', name='other_insurance_delete'),
    
    #2017/12/20添加二手商品
    #商品类型部分
    url(r'^mall/goods_type_list/(?P<page_index>\d+)/$', 'bms.views_mall.goods_type_list', name='goods_type_list'),
    url(r'^mall/goods_type_create/$', 'bms.views_mall.goods_type_create', name='goods_type_create'),
    url(r'^mall/goods_type_detail/(?P<goods_type_id>\w{24})/$', 'bms.views_mall.goods_type_detail', name='goods_type_detail'),
    url(r'^mall/goods_type_edit/(?P<goods_type_id>\w{24})/$', 'bms.views_mall.goods_type_edit', name='goods_type_edit'),
    url(r'^mall/goods_type_delete/(?P<goods_type_id>\w{24})/$', 'bms.views_mall.goods_type_delete', name='goods_type_delete'),
    
    #二手商品
    url(r'^mall/mall_goods_list/(?P<page_index>\d+)/$', 'bms.views_mall.mall_goods_list', name='mall_goods_list'),
    url(r'^mall/mall_goods_create/$', 'bms.views_mall.mall_goods_create', name='mall_goods_create'),
    url(r'^mall/mall_goods_detail/(?P<mall_goods_id>\w{24})/$', 'bms.views_mall.mall_goods_detail', name='mall_goods_detail'),
    url(r'^mall/mall_goods_edit/(?P<mall_goods_id>\w{24})/$', 'bms.views_mall.mall_goods_edit', name='mall_goods_edit'),
    url(r'^mall/mall_goods_delete/(?P<mall_goods_id>\w{24})/$', 'bms.views_mall.mall_goods_delete', name='mall_goods_delete'),

    #2018/1/2后台保险管家隐藏保险产品
    url(r'^car/car_change_state/(?P<car_id>\w{24})/$', 'bms.views_car.car_change_state', name='car_change_state'),
    url(r'^car/policy_change_state/(?P<policy_id>\w{24})/$', 'bms.views_car.policy_change_state', name='policy_change_state'),
    
    #特推产品
    url(r'^product/recommend_product_list/(?P<page_index>\d+)/$', 'bms.views_recommend.recommend_product_list', name='recommend_product_list'),
    url(r'^product/recommend_product_create/$', 'bms.views_recommend.recommend_product_create', name='recommend_product_create'),
    url(r'^product/recommend_product_detail/(?P<recommend_product_id>\w{24})/$', 'bms.views_recommend.recommend_product_detail', name='recommend_product_detail'),
    url(r'^product/recommend_product_edit/(?P<recommend_product_id>\w{24})/$', 'bms.views_recommend.recommend_product_edit', name='recommend_product_edit'),
    url(r'^product/recommend_product_delete/(?P<recommend_product_id>\w{24})/$', 'bms.views_recommend.recommend_product_delete', name='recommend_product_delete'),
    
    #广告位
    url(r'^settings/advertising_position_list/(?P<page_index>\d+)/$', 'bms.views_advertising.advertising_position_list', name='advertising_position_list'),
    url(r'^settings/advertising_position_create/$', 'bms.views_advertising.advertising_position_create', name='advertising_position_create'),
    url(r'^settings/advertising_position_detail/(?P<advertising_position_id>\w{24})/$', 'bms.views_advertising.advertising_position_detail', name='advertising_position_detail'),
    url(r'^settings/advertising_position_edit/(?P<advertising_position_id>\w{24})/$', 'bms.views_advertising.advertising_position_edit', name='advertising_position_edit'),
    url(r'^settings/advertising_position_delete/(?P<advertising_position_id>\w{24})/$', 'bms.views_advertising.advertising_position_delete', name='advertising_position_delete'),
    #广告
    url(r'^settings/advertising_list/(?P<page_index>\d+)/$', 'bms.views_advertising.advertising_list', name='advertising_list'),
    url(r'^settings/advertising_create/$', 'bms.views_advertising.advertising_create', name='advertising_create'),
    url(r'^settings/advertising_detail/(?P<advertising_id>\w{24})/$', 'bms.views_advertising.advertising_detail', name='advertising_detail'),
    url(r'^settings/advertising_edit/(?P<advertising_id>\w{24})/$', 'bms.views_advertising.advertising_edit', name='advertising_edit'),
    url(r'^settings/advertising_delete/(?P<advertising_id>\w{24})/$', 'bms.views_advertising.advertising_delete', name='advertising_delete'),

)


