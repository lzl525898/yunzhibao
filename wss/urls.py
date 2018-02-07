__author__ = 'mlzx'
from django.conf.urls import patterns, include, url

urlpatterns = patterns(
    '',
    url(r'^receiver/$', 'wss.views.we_chat_receiver', name='we_chat_receiver'),
    url(r'^bind/$', 'wss.views.view_bind', name='bind'),
    url(r'^unbind/$', 'wss.views.view_unbind', name='unbind'),
    url(r'^unbind_null/$', 'wss.views.view_unbind_null', name='unbind_null'),
    url(r'^register/$', 'wss.views.view_register', name='register'),
    url(r'^forget/password/send_code/$', 'wss.views.send_code', name='send_code'),
    url(r'^forget/password/update/$', 'wss.views.update_password', name='update_password'), 
    url(r'^password/update/$', 'wss.views.update_my_password', name='update_my_password'),
    #   用户注册协议
    url(r'^register/agreement/$', 'wss.views.user_agreement', name='user_agreement'),
    url(r'^certificate/$', 'wss.views.view_certificate', name='certificate'),
    url(r'^certificate/result/$', 'wss.views.view_certificate', name='certificate_result'),
    url(r'^test/data/update/$', 'wss.views.update_data', name='update_data'),
    
    #二维码登陆
    url(r'^register_code/$', 'wss.views.view_register_code', name='register_code'),
    url(r'^view_register_pic/$', 'wss.views.view_register_pic', name='view_register_pic'),
   # url(r'^send_wx_message/$', 'wss.views_sendmessage.test', name='test'),


    #########################################   律师相关    #########################################


    #########################################   理赔人员相关    #########################################


    #########################################   客户相关    #########################################

    #########################################    保险Lloyds   #########################################

    #########################################   学习learn    #########################################

    #########################################   投保    #########################################
    #投保
    url(r'^insure/product_list/$', 'wss.views_insure.product_list', name='product_list'),
    url(r'^insure/product_detail1/$', 'wss.views_insure.product_detail1', name='product_detail1'),
    url(r'^insure/product_detail2/$', 'wss.views_insure.product_detail2', name='product_detail2'),
    url(r'^insure/product_detail3/$', 'wss.views_insure.product_detail3', name='product_detail3'),
    url(r'^insure/product_detail4/$', 'wss.views_insure.product_detail4', name='product_detail4'),
    url(r'^insure/product_detail5/$', 'wss.views_insure.product_detail5', name='product_detail5'),
    url(r'^insure/product_detail6/$', 'wss.views_insure.product_detail6', name='product_detail6'),
    url(r'^insure/product_detail7/$', 'wss.views_insure.product_detail7', name='product_detail7'),
    url(r'^insure/product_detail8/$', 'wss.views_insure.product_detail8', name='product_detail8'),
    url(r'^insure/product_detail9/$', 'wss.views_insure.product_detail9', name='product_detail9'),

    #意外险
    url(r'^insure/product_ywx_list/$', 'wss.views_insure.product_ywx_list', name='product_ywx_list'),
    url(r'^insure/product_ywx_detail1/$', 'wss.views_insure.product_ywx_detail1', name='product_ywx_detail1'),
    url(r'^insure/product_ywx_detail2/$', 'wss.views_insure.product_ywx_detail2', name='product_ywx_detail2'),

    url(r'^insure/prompt/$', 'wss.views_insure.prompt', name='prompt'),
    url(r'^insure/document/detail/(?P<document_id>\w{24})/$', 'wss.views_insure.document_detail', name='document_detail'),
    #开始创建订单
    url(r'^insure/order_create/$', 'wss.views_insure.order_create', name='order_create'),
    #提交订单
    url(r'^insure/order_submit/$', 'wss.views_insure.order_submit', name='order_submit'),
    #付款
    url(r'^insure/order_pay/(?P<order_id>\w{24})/$', 'wss.views_insure.order_pay', name='order_pay'),
    # url(r'^insure/null/$', 'wss.views_insure.null', name='null'),

    #########################################   我的mine    #########################################
    #我的订单
    url(r'^mine/my_order/$', 'wss.views_mine.order_list', name='order_list'),
    url(r'^mine/order_detail/(?P<order_id>\w{24})/$', 'wss.views_mine.order_detail', name='order_detail'),
    # #车次清单list
    url(r'^mine/batch_list/(?P<order_id>\w{24})/$', 'wss.views_mine.batch_list', name='batch_list'),
    url(r'^mine/batch_list_pic/(?P<order_id>\w{24})/$', 'wss.views_mine.batch_list_pic', name='batch_list_pic'),

    #查看电子保单
    url(r'^mine/insurance_list_pic/(?P<order_id>\w{24})/$', 'wss.views_mine.insurance_list_pic', name='insurance_list_pic'),

    #我的账号
    url(r'^mine/my_account/$', 'wss.views_mine.my_account', name='my_account'),
    url(r'^mine/stored_premium/$', 'wss.views_mine.stored_premium', name='stored_premium'),
     #微信支付
    url(r'^insure/wx_pay/$', 'wss.views_insure.wx_pay', name='wx_pay'),

    #支付余额
    url(r'^mine/pay/user_balance/$', 'wss.views_mine.pay_user_balance', name='pay_user_balance'),

    # #支付成功
    url(r'^mine/pay/result/$', 'wss.views_mine.pay_result', name='pay_result'),

    #支付详情
    url(r'^mine/pay/detail/$', 'wss.views_mine.pay_detail', name='pay_detail'),


    #优惠券
    url(r'^mine/coupon_list/$', 'wss.views_mine.coupon_list', name='coupon_list'),
    url(r'^mine/coupon_detail/(?P<coupon_id>\w{24})/$', 'wss.views_mine.coupon_detail', name='coupon_detail'),
    # #保单查询
    # url(r'^mine/suggestions/$', 'wss.views_mine.suggestions', name='suggestions'),
    #建议和意见
    url(r'^mine/suggestions/$', 'wss.views_mine.suggestions', name='suggestions'),
    #联系客服
    url(r'^mine/contact/$', 'wss.views_mine.contact', name='contact'),
    #登陆
    url(r'^mine/land/$', 'wss.views_mine.land', name='land'),
    #解除绑定
    # url(r'^mine/unbind/$', 'wss.views_mine.land', name='land'),

    #########################################   宣传推广   #########################################

    #物流公司
    url(r'^propaganda/transport_list/$', 'wss.views_propaganda.transport_list', name='transport_list'),
    url(r'^propaganda/transport_detail/(?P<logistics_id>\w{24})/$', 'wss.views_propaganda.transport_detail', name='transport_detail'),

    #物流管理系统
    url(r'^propaganda/manager_list/$', 'wss.views_propaganda.manager_list', name='manager_list'),
    url(r'^propaganda/manager_detail/$', 'wss.views_propaganda.manager_detail', name='manager_detail'),
    #律师
    url(r'^propaganda/lawyer_list/$', 'wss.views_propaganda.lawyer_list', name='lawyer_list'),
    url(r'^propaganda/lawyer_detail/(?P<lawyer_id>\w{24})/$', 'wss.views_propaganda.lawyer_detail', name='lawyer_detail'),
    #货车司机
    url(r'^propaganda/driver_list/$', 'wss.views_propaganda.driver_list', name='driver_list'),
    url(r'^propaganda/driver_detail/(?P<driver_id>\w{24})/$', 'wss.views_propaganda.driver_detail', name='driver_detail'),

    #########################################   公用    #########################################

    url(r'^success/$', 'wss.views.success', name='success'),
    url(r'^warn/$', 'wss.views.warn', name='warn'),
    #我的车车
    url(r'^mine/my_car_list/$', 'wss.views_mine.my_car_list', name='myCar_list'),
    url(r'^mine/my_car_create/$', 'wss.views_mine.my_car_create', name='myCar_create'),
    url(r'^mine/reference_pic/(?P<type_id>\d+)/$', 'wss.views_mine.reference_pic', name='ref_pic'),
    url(r'^mine/car_detail/(?P<car_id>\w{24})/$', 'wss.views_mine.my_car_detail', name='car_detail'),
    url(r'^mine/car_edit/(?P<car_id>\w{24})/$', 'wss.views_mine.my_car_edit', name='car_edit'),
    url(r'^mine/car_delete/(?P<car_id>\w{24})/$', 'wss.views_mine.my_car_delete', name='car_delete'),
    url(r'^mine/car_upload/(?P<car_id>\w{24})/$', 'wss.views_mine.my_car_upload', name='car_upload'),
    
    
    ########################################测试1##########
    #测试订单列表
#     url(r'^insure/product_type_list/(?P<product_type>[^/]+)/$', 'wss.views_insure.product_type_list', name='product_type_list'),
#     url(r'^insure/product_detial/(?P<product_id>[^/]+)/$', 'wss.views_insure.product_detial', name='product_detial'),
    #投保页面
#     url(r'^insure/product_prompt/$', 'wss.views_insure.product_prompt', name='product_prompt'),
#     url(r'^insure/order_create_update/$', 'wss.views_insure.order_create_update', name='order_create_update'),
#     url(r'^insure/order_create_update/(?P<product_id>\w{24})/$', 'wss.views_insure.order_create_update', name='order_create_update'),
    #提交订单
#     url(r'^insure/order_submit_update/$', 'wss.views_insure.order_submit_update', name='order_submit_update'),
    
    
    ########################################测试2##########
    #产品介绍页面
    url(r'^insure/introduce_product/(?P<product_type>[^/]+)/$', 'wss.views_insure.introduce_product', name='introduce_product'),
    #投保页面
    url(r'^insure/insure_product/$', 'wss.views_insure.insure', name='insure_product'),
    #筛选产品创建订单
    url(r'^insure/filter_product/$', 'wss.views_insure.filter_product', name='filter_product'),
    #编辑订单详情
    url(r'^insure/order_detail_update/(?P<order_id>[^/]+)/$',  'wss.views_insure.order_detail_update', name='order_detail_update'),
    #2017/6/20添加等待页面
    #编辑订单详情
    url(r'^insure/order_wait/(?P<order_id>[^/]+)/$',  'wss.views_insure.order_wait', name='order_wait'),
    #选择产品确认投保部分
    url(r'^insure/order_choose_product/(?P<order_id>[^/]+)/$',  'wss.views_insure.order_choose_product', name='order_choose_product'),
    #编辑未支付的订单
    url(r'^insure/order_edit/(?P<order_id>[^/]+)/$',  'wss.views_insure.order_edit', name='order_edit'),
    #复制一单
    url(r'^insure/order_copy/(?P<order_id>[^/]+)/$',  'wss.views_insure.order_copy', name='order_copy'),
    #删除未支付的订单
    url(r'^insure/order_delete/(?P<order_id>[^/]+)/$',  'wss.views_insure.order_delete', name='order_delete'),
    #付款
    url(r'^insure/order_pay_update/(?P<order_id>\w{24})/$', 'wss.views_insure.order_pay_update', name='order_pay_update'),
    #获取包装方式json
    url(r'^insure/get_packs_list/$', 'wss.views_insure.get_packs_list', name='get_packs'),
    url(r'^insure/get_cargos_list/$', 'wss.views_insure.get_cargos_list', name='get_cargos'),
    
    # 删除单个车次图片
    url(r'^insure/delete_batch_pic/(?P<order_id>\w{24})/$', 'wss.views_insure.wx_delete_batch_pic', name='wx_delete_batch_pic'),
   
    
    #车险首页
     url(r'^insure/auto_insurance/$', 'wss.views_insure.auto_insurance', name='auto_insurance_first'),
     #询价
     url(r'^insure/enquiry/$', 'wss.views_insure.insure_enquiry', name='insure_enquiry'),
     
     #车辆信息
     url(r'^insure/enquiry_user/$', 'wss.views_insure.insure_enquiry_user', name='insure_enquiry_user'),
     #投保人与被保人信息
     url(r'^insure/enquiry_insure_type/$', 'wss.views_insure.enquiry_insure_type', name='insure_enquiry_type'),
     #保险起期
     url(r'^insure/insurance_period/$', 'wss.views_insure.insurance_period', name='insurance_period'),
     #开始询价
     url(r'^insure/start_inquiry/$', 'wss.views_insure.start_inquiry', name='start_inquiry'),
     #订单详情
      url(r'^insure/jdclbx_detail/(?P<order_id>\w{24})/$', 'wss.views_insure.jdclbx_detail', name='jdclbx_detail'),
      
      url(r'^insure/check_info/$', 'wss.views_insure.check_info', name='check_info'),
     #我的车险订单列表
     url(r'^mine/my_car_order/(?P<order_state>[^/]+)/$','wss.views_mine.car_order_list', name='car_order_list'),
#      url(r'^mine/my_car_order/$','wss.views_mine.car_order_list', name='car_order_list'),

     #询价详情
      url(r'^insure/jdclbx_intermediary_detail/(?P<intermediary_id>\w{24})/$', 'wss.views_insure.jdclbx_intermediary_detail', name='jdclbx_intermediary_detail'),
      #确认投保
      url(r'^insure/jdclbx_confirm_insurance/(?P<intermediary_id>\w{24})/$', 'wss.views_insure.jdclbx_confirm_insurance', name='jdclbx_confirm_insurance'),
     
      url(r'^insure/jdclbx_confirm_pay/(?P<order_id>\w{24})/$', 'wss.views_insure.jdclbx_confirm_pay', name='jdclbx_confirm_pay'),
      #重新询价
      url(r'^insure/jdclbx_edit_list/(?P<order_id>\w{24})/$', 'wss.views_insure.jdclbx_edit_list', name='jdclbx_edit_list'),
      #修改基本信息
      url(r'^insure/jdclbx_baseinfo_edit/(?P<order_id>\w{24})/$', 'wss.views_insure.jdclbx_baseinfo_edit', name='jdclbx_baseinfo_edit'),
      #修改保险信息
      url(r'^insure/jdclbx_insurance_edit/(?P<order_id>\w{24})/$', 'wss.views_insure.jdclbx_insurance_edit', name='jdclbx_insurance_edit'),
      #行驶证图片
      url(r'^insure/driving_license_pic/(?P<order_id>\w{24})/$', 'wss.views_insure.driving_license_pic', name='driving_license_pic'),
      #删除订单
      url(r'^insure/jdclbx_order_delete/(?P<order_id>\w{24})/$', 'wss.views_insure.jdclbx_order_delete', name='jdclbx_order_delete'),
      #编辑订单
      url(r'^insure/jdclbx_order_edit/(?P<order_id>\w{24})/$', 'wss.views_insure.jdclbx_order_edit', name='jdclbx_order_edit'),
      
      #2017修改方法
     #添加验证订单方法-投保
     url(r'^insure/jdclbx_order_create_new/$', 'wss.views_insure.jdclbx_order_create_new', name='jdclbx_order_create_new'),
     #添加验证订单方法-编辑
     url(r'^insure/jdclbx_order_edit_new/(?P<order_id>\w{24})/$',  'wss.views_insure.jdclbx_order_edit_new', name='jdclbx_order_edit_new'),
     
     #2017生成二维码
     url(r'^mine/wx_build_code_pic/$', 'wss.views_mine.wx_build_code_pic', name='wx_build_code_pic'),
     #2017验证是否认证
     url(r'^certificate_test/(?P<client_id>\w{24})/$', 'wss.views.view_certificate_test', name='certificate_test'),

     #修改流程
     url(r'^insure/test_apply/$', 'wss.views_insure.test_apply', name='test_apply'),
     
     #2017-08-22添加传值部分
     #判断是否给汇聚宝传值
    url(r'^insure/post_order_detail', 'wss.views_mine.post_order_detail', name='post_order_detail'),
    #2017/11/20运单保险订单查询
    url(r'^mine/yundan_order_list/$', 'wss.views_mine.yundan_order_list', name='yundan_order_list'),
    #2017/11/28 维护订单众安产品信息
    url(r'^insure/add_za_order_detail', 'wss.views_insure.add_za_order_detail', name='add_za_order_detail'),
    
    #2017/12/10查看保险管家中的保单地址
    url(r'^mine/search_policy_picture/(?P<policy_id>\w{24})/$', 'wss.views_mine.search_policy_picture', name='search_policy_picture'),
    #2017/12/08添加员工保险
    url(r'^mine/wx_employee_list/(?P<page_index>\d+)/$', 'wss.views_mine.wx_employee_list', name='wx_employee_list'),
    url(r'^mine/wx_employee_detail/(?P<employee_id>\w{24})/$', 'wss.views_mine.wx_employee_detail', name='wx_employee_detail'),
    #2017/12/10添加货运年险
    url(r'^mine/wx_freight_list/(?P<page_index>\d+)/$', 'wss.views_mine.wx_freight_list', name='wx_freight_list'),
    url(r'^mine/wx_freight_detail/(?P<freight_id>\w{24})/$', 'wss.views_mine.wx_freight_detail', name='wx_freight_detail'),
    #2017/12/10添加个人保险
    url(r'^mine/wx_personal_list/(?P<page_index>\d+)/$', 'wss.views_mine.wx_personal_list', name='wx_personal_list'),
    url(r'^mine/wx_personal_detail/(?P<personal_id>\w{24})/$', 'wss.views_mine.wx_personal_detail', name='wx_personal_detail'),
    #2017/12/10添加车险车辆
    url(r'^mine/wx_car_list/(?P<page_index>\d+)/$', 'wss.views_mine.wx_car_list', name='wx_car_list'),
    url(r'^mine/wx_car_detail/(?P<car_id>\w{24})/$', 'wss.views_mine.wx_car_detail', name='wx_car_detail'),
    #2017/12/15修改车险车辆时间
    url(r'^mine/wx_change_car_time/(?P<car_id>\w{24})/$', 'wss.views_mine.wx_change_car_time', name='wx_change_car_time'),
    #2017/12/11添加分页功能（个人，员工，货运）
    url(r'^mine/get_policy_detail', 'wss.views_mine.get_policy_detail', name='get_policy_detail'),
    #2017/12/14添加其他保险
    url(r'^mine/wx_other_insurance_list/(?P<page_index>\d+)/$', 'wss.views_mine.wx_other_insurance_list', name='wx_other_insurance_list'),
    url(r'^mine/wx_other_insurance_detail/(?P<other_insurance_id>\w{24})/$', 'wss.views_mine.wx_other_insurance_detail', name='wx_other_insurance_detail'),
    #二手商品
    url(r'^second/wx_secondhand_list/(?P<page_index>\d+)/$', 'wss.views_secondHand.wx_second_list', name='secondhand_list'),
    url(r'^second/wx_publish_info/$', 'wss.views_secondHand.wx_publish_info', name='publish_info'),
    url(r'^second/wx_secondhand_detail/(?P<secondhand_id>\w{24})/$', 'wss.views_secondHand.wx_secondhand_detail', name='secondhand_detail'),
    url(r'^second/wx_secondhand_edit/(?P<secondhand_id>\w{24})/$', 'wss.views_secondHand.wx_secondhand_edit', name='wx_secondhand_edit'),
    url(r'^second/wx_secondhand_delete/(?P<secondhand_id>\w{24})/$', 'wss.views_secondHand.wx_secondhand_delete', name='secondhand_delete'),
    #管理我的二手商品
    url(r'^second/wx_my_secondhands/(?P<page_index>\d+)/$', 'wss.views_secondHand.wx_my_secondhands', name='wx_my_secondhands'),
    url(r'^second/wx_change_secondhand/(?P<secondhand_id>\w{24})/$', 'wss.views_secondHand.wx_change_secondhand', name='wx_change_secondhand'),
    #2017/12/29添加分页功能
    url(r'^second/get_secondhand_detail', 'wss.views_secondHand.get_secondhand_detail', name='get_secondhand_detail'),
    
    #2018/1/16特推产品部分
    url(r'^recommend/wx_recommend_product/(?P<recommend_product_id>\w{24})/$', 'wss.views_recommendProduct.wx_recommend_product', name='wx_recommend_product'),
    url(r'^recommend/wx_recommend_list/(?P<page_index>\d+)/$', 'wss.views_recommendProduct.wx_recommend_list', name='wx_recommend_list'),
    #2018/01/30选择商品类型
    url(r'^second/wx_goodstype_list', 'wss.views_secondHand.wx_goodstype_list', name='wx_goodstype_list'),
)

