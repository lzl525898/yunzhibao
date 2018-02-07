/**
 * Created by mlzx on 2015/5/16.
 */


 function ajax_csrf(){
    //ajax csrf 为了ajax POST准备的，只要加载一次，修改HTTP POST的全局变量
//    console.log("ajax_csrf");
    var csrftoken = $.cookie('csrftoken');
    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    $.ajaxSetup({
        crossDomain: false, // obviates need for sameOrigin test
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type)) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });
 }


$(document).ready(function (){
    ajax_csrf();
    change_company();
    change_insurance_type();
    change_insurance_product();
    change_province();
  //  change_pack_method();
//    原地址插件
//    $("#start_city").citySelect();
//    $("#end_city").citySelect();
});

//物流公司管理查看照片
function look_photo(photo_src){
//    alert(photo_src);
    var a = document.getElementById('id_image');
    a.src = '/static/' + photo_src;
//    alert(photo_src);
    $('#look_photo_modal').modal('show');
}

//保险公司详情页面显示modal（设置保险文档）
function company_document_show(document_type){
    $('#id_document_type').val(document_type);
    var document_name = 'name_' + document_type;
    init_modal_input();
    $("div[name=" + document_name + "]").each(function(){
        var modal_input = $('#modal_' + $(this).attr('document_id'));
        modal_input.prop("checked", "checked");
    });
    $('#save_insurance_company_modal').modal('show');
}
//把所有的input的状态变成未选中
function init_modal_input(){
    $('.insurance_document').prop("checked", '')
}
//############################################################order_create页面  四级联动
//原运行方式
function change_company1(){
    var company_selector = document.getElementById('id_company_id');
    var insurance_type_selector = document.getElementById('id_product_type');
    var insurance_product_selector = document.getElementById('id_insurance_product_id');
    if(company_selector!=null) {


        company_selector.onchange = function () {
            var selectedValue = this[this.selectedIndex].value;
            if (selectedValue != '') {
                insurance_product_selector.innerHTML = '';
//                 insurance_product_selector.options.add(getFirstOption());
//                 return false
            }
            $.ajax({
                url: "/bms/interface/locations/get_insurance_company_list/",
                data: {company_id: selectedValue},
                type: 'GET',
                dataType: 'json',
                timeout: 15000,
                success: function (data) {
                    for (var key1 in data['data']) {
                        insurance_product_selector.options.add(getOption(data['data'][key1], key1));
                    }
                    var company_selector1 = document.getElementById('id_company_id');
                    var insurance_type_selector1 = document.getElementById('id_product_type');
                    var insurance_product_selector1 = document.getElementById('id_insurance_product_id');
                    if (insurance_product_selector1.value) {
                        if (company_selector1 && insurance_type_selector1) {
                        } else if (company_selector1 && !insurance_type_selector1) {
                   //         alert(1);
                            insurance_type_selector.innerHTML = '';
                            insurance_type_selector.options.add(getOption('请选择产品类型', ''));
                        } else if (!company_selector1 && insurance_type_selector1) {
                            company_selector1.innerHTML = '';
                            company_selector1.options.add(getOption('请先选择保险公司', ''));
                        } else if (!company_selector1 && !insurance_type_selector1) {
                            company_selector1.innerHTML = '';
                            company_selector1.options.add(getOption('请选择', ''));
                        }
                    } else {
//                    alert(1);
                        insurance_product_selector1.innerHTML = '';
                        insurance_product_selector1.options.add(getOption('您选择的方案无产品', ''));
                    }
                },
                error: function () {
                    $('#id_message').removeClass('control-show');
                    $('#id_message_id').html(data['message'])
                }
            });
        };
    }
}

function change_company() {
    var company_selector = document.getElementById('id_company_id');
    var insurance_type_selector = document.getElementById('id_product_type');
    var insurance_product_selector = document.getElementById('id_insurance_product_id');
    if(insurance_type_selector != null){
    	company_selector.onchange = function () {
            var selectedValue = this[this.selectedIndex].value;
            /*以后添加产品类型需要添加*/
            if(insurance_type_selector.value == 'car'){
                $('#id_car').removeClass('control-show');
                $('#id_insurance_price_id').removeClass('control-show');
                $('#id_batch').addClass('control-show');
                $('#id_ticket').addClass('control-show');
                $('#id_hidden_good_type').addClass('control-show');
                $('#id_hidden_pack_method').addClass('control-show');
                $('#id_hidden_common_good').addClass('control-show');
               // $('#id_hidden_good_type').removeClass('control-show');
            }else if(insurance_type_selector.value == 'batch'){
                $('#id_car').addClass('control-show');
                $('#id_insurance_price_id').addClass('control-show');
                $('#id_batch').removeClass('control-show');
                $('#id_ticket').addClass('control-show');
                $('#id_hidden_good_type').addClass('control-show');
                $('#id_hidden_pack_method').addClass('control-show');
                $('#id_hidden_common_good').addClass('control-show');
            }else if(insurance_type_selector.value == 'ticket'){
                $('#id_car').addClass('control-show');
                $('#id_batch').addClass('control-show');
                $('#id_ticket').removeClass('control-show');
                $('#id_insurance_price_id').removeClass('control-show');
                $('#id_hidden_good_type').removeClass('control-show');
                $('#id_hidden_pack_method').removeClass('control-show');
                $('#id_hidden_common_good').removeClass('control-show');
            }
            if (selectedValue != '') {
                insurance_product_selector.innerHTML = '';
            }
            $.ajax({
                url: "/bms/interface/locations/get_insurance_type_list/",
                data: {insurance_type_key: insurance_type_selector.value,company_id: company_selector.value},
                type: 'GET',
                dataType: 'json',
                timeout: 15000,
                success: function (data) {
                     for (var key1 in data['data']) {
                             insurance_product_selector.options.add(getOption(data['data'][key1], key1));
                         }
                    var company_selector1 = document.getElementById('id_company_id');
                    var insurance_type_selector1 = document.getElementById('id_product_type');
                    var insurance_product_selector1 = document.getElementById('id_insurance_product_id');
                    if(insurance_product_selector1.value){
                        if(company_selector1 && insurance_type_selector1){
                        }else if(company_selector1 && !insurance_type_selector1){
                        insurance_type_selector.innerHTML ='';
                        insurance_type_selector.options.add(getOption('请选择产品类型',''));
                        }else if(!company_selector1 && insurance_type_selector1){
                            company_selector1.innerHTML ='';
                            company_selector1.options.add(getOption('请先选择保险公司',''));
                        }else if(!company_selector1 && !insurance_type_selector1){
                            company_selector1.innerHTML ='';
                            company_selector1.options.add(getOption('请选择',''));
                        }
                    }else{
                        insurance_product_selector1.innerHTML ='';
                        insurance_product_selector1.options.add(getOption('您选择的方案无产品',''));
                    }
                    if(insurance_type_selector1.value == 'ticket'){
                    	getGoodtype(insurance_product_selector1.value);
                    }
                    add_ZA_detail();
                    /*getGoodtype(insurance_product_selector1.value);*/

                },
                error: function (data) {
                    $('#id_message').removeClass('control-show');
                    $('#id_message_id').html(data['message'])
                }
            });
        }

    }
}

function change_insurance_type() {
    var company_selector = document.getElementById('id_company_id');
    var insurance_type_selector = document.getElementById('id_product_type');
    var insurance_product_selector = document.getElementById('id_insurance_product_id');
    if(insurance_type_selector != null){

        insurance_type_selector.onchange = function () {
            var selectedValue = this[this.selectedIndex].value;
            /*以后添加产品类型需要添加*/
            if(selectedValue == 'car'){
                $('#id_car').removeClass('control-show');
                $('#id_insurance_price_id').removeClass('control-show');
                $('#id_batch').addClass('control-show');
                $('#id_ticket').addClass('control-show');
                $('#id_hidden_good_type').addClass('control-show');
                $('#id_hidden_pack_method').addClass('control-show');
                $('#id_hidden_common_good').addClass('control-show');
               // $('#id_hidden_good_type').removeClass('control-show');
            }else if(selectedValue == 'batch'){
                $('#id_car').addClass('control-show');
                $('#id_insurance_price_id').addClass('control-show');
                $('#id_batch').removeClass('control-show');
                $('#id_ticket').addClass('control-show');
                $('#id_hidden_good_type').addClass('control-show');
                $('#id_hidden_pack_method').addClass('control-show');
                $('#id_hidden_common_good').addClass('control-show');
            }else if(selectedValue == 'ticket'){
                $('#id_car').addClass('control-show');
                $('#id_batch').addClass('control-show');
                $('#id_ticket').removeClass('control-show');
                $('#id_insurance_price_id').removeClass('control-show');
                $('#id_hidden_good_type').removeClass('control-show');
                $('#id_hidden_pack_method').removeClass('control-show');
                $('#id_hidden_common_good').removeClass('control-show');
            }
            if (selectedValue != '') {
                insurance_product_selector.innerHTML = '';
            }
            $.ajax({
                url: "/bms/interface/locations/get_insurance_type_list/",
                data: {insurance_type_key: selectedValue,company_id: company_selector.value},
                type: 'GET',
                dataType: 'json',
                timeout: 15000,
                success: function (data) {
                     for (var key1 in data['data']) {
                             insurance_product_selector.options.add(getOption(data['data'][key1], key1));
                         }
                    var company_selector1 = document.getElementById('id_company_id');
                    var insurance_type_selector1 = document.getElementById('id_product_type');
                    var insurance_product_selector1 = document.getElementById('id_insurance_product_id');
                    if(insurance_product_selector1.value){
                        if(company_selector1 && insurance_type_selector1){

                        }else if(company_selector1 && !insurance_type_selector1){
                        insurance_type_selector.innerHTML ='';
                        insurance_type_selector.options.add(getOption('请选择产品类型',''));
                        }else if(!company_selector1 && insurance_type_selector1){
                            company_selector1.innerHTML ='';
                            company_selector1.options.add(getOption('请先选择保险公司',''));
                        }else if(!company_selector1 && !insurance_type_selector1){
                            company_selector1.innerHTML ='';
                            company_selector1.options.add(getOption('请选择',''));
                        }
                    }else{
                        insurance_product_selector1.innerHTML ='';
                        insurance_product_selector1.options.add(getOption('您选择的方案无产品',''));
                        //test
                        $('#id_hidden_good_type').addClass('control-show');
                        $('#id_hidden_common_good').addClass('control-show');
                    }
                    if(insurance_type_selector1.value == 'ticket'){
                    	getGoodtype(insurance_product_selector1.value);
                    }
                    add_ZA_detail();

                },
                error: function (data) {
                    $('#id_message').removeClass('control-show');
                    $('#id_message_id').html(data['message'])
                }
            });
        }

    }
}

function change_insurance_product(){
    var insurance_product_selector = document.getElementById('id_insurance_product_id');
    var good_type_selector =document.getElementById('id_good_type_id');
    var insurance_type_selector = document.getElementById('id_product_type');
    if(insurance_product_selector!=null) {
    	var insurance_product_selector_value = insurance_product_selector.value
    	if (insurance_product_selector_value != '') {
    	}
    	insurance_product_selector.onchange = function () {
            var selectedValue = this[this.selectedIndex].value;
            if (selectedValue != '') {
            	/*getGoodtype(selectedValue)*/
            	//alert(insurance_type_selector.value )
            	if(insurance_type_selector.value == 'ticket'){
                	getGoodtype(selectedValue);
                }
            }
            add_ZA_detail();
        };
    }

}

//动态显示货物大类（普通货物等）
function getGoodtype(product_id){
	var product_id=product_id;
	var good_type_selector = document.getElementById('id_good_type_id');
	var insurance_product_selector = document.getElementById('id_insurance_product_id');
	$.ajax({
        url: "/bms/interface/locations/get_insurance_product_list",
        data: {insurance_product_key: product_id},
        type: 'GET',
        dataType: 'json',
        timeout: 15000,
        success: function (data) {
        	good_type_selector.innerHTML = '';
            for (var key1 in data['data']) {
            	/*good_type_selector.options.add(getOption(data['data'][key1], key1));*/
            	var text=''+key1+' / '+data['data'][key1];
            	good_type_selector.options.add(getOption(text, key1));
            }
            var insurance_product_selector1 = document.getElementById('id_insurance_product_id');
            var good_type_selector1 = document.getElementById('id_good_type_id');
            if(good_type_selector1.value){
            	if(insurance_product_selector1.value){
            	}
            	else{
            		insurance_product_selector1.innerHTML = '';
            		insurance_product_selector1.options.add(getOption('请先选择产品', ''));
            	}
            }
            else{
            	good_type_selector1.innerHTML = '';
            	good_type_selector1.options.add(getOption('您选择的方案无产品', ''));
            	//test
            	//$('#id_hidden_good_type').addClass('control-show');
            }
            getGoodDetail ()
        },
        error: function () {
            $('#id_message').removeClass('control-show');
            $('#id_message_id').html(data['message'])
         //   $('#id_good_type_id').addClass('control-show');
        }
    });
}



//随货物类型变化选择显示货物详情
function getGoodDetail () {
	var good_type_selector =document.getElementById('id_good_type_id');
	getCargo()
	good_type_selector.onchange = function () {
		getCargo()
		//$('#id_hidden_common_good').removeClass('control-show');
	}
}


//获得货物详情数据
function getCargo(){
	var good_type_selector = document.getElementById('id_good_type_id');
	var insurance_product_selector = document.getElementById('id_insurance_product_id');
	var cargo_selector = document.getElementById('id_common_good_id');
	//alert("insurance_product_selector.value========="+insurance_product_selector.value);
	//alert("good_type_selector.value========="+good_type_selector.value);
	$.ajax({
        url: "/bms/interface/locations/get_product_cargo_list",
        data: {product_id: insurance_product_selector.value,cargo_state:good_type_selector.value},
        type: 'GET',
        dataType: 'json',
        timeout: 15000,
        success: function (data) {
        	cargo_selector.innerHTML = '';
        	for (var key1 in data['data']) {
        		cargo_selector.options.add(getOption(data['data'][key1], key1));
        		//alert("key1==="+key1);
        		//alert("data['data'][key1]==="+data['data'][key1]);
            }
        	var good_type_selector1 = document.getElementById('id_good_type_id');
        	var insurance_product_selector1 = document.getElementById('id_insurance_product_id');
        	var cargo_selector1 = document.getElementById('id_common_good_id');
        	
        	if(cargo_selector1.value){  
        		//alert("cargo_selector===="+cargo_selector1.value)
        		}
        	else{
        	    cargo_selector1.innerHTML = '';
        		cargo_selector1.options.add(getOption('请先选择产品', ''));
        	}
        },
        error: function () {
            $('#id_message').removeClass('control-show');
            $('#id_message_id').html(data['message'])
         //   $('#id_good_type_id').addClass('control-show');
        }
    });
}



//随货物类型变化选择显示
function ge1tGoodDetail () {
	var good_type_selector =document.getElementById('id_good_type_id');
	if (good_type_selector.value == "普通货物"){
		$('#id_hidden_common_good').removeClass('control-show');
	}else{
        $('#id_hidden_common_good').addClass('control-show');
	}
	good_type_selector.onchange = function () {
		var good_type_selector1 =document.getElementById('id_good_type_id');
		if (good_type_selector1.value == "普通货物"){
			$('#id_hidden_common_good').removeClass('control-show');
		}else{
	        $('#id_hidden_common_good').addClass('control-show');
		}
	}
	
}

//包装类型变化
function change_pack_method(){
    var pack_method_selector = document.getElementById('id_pack_method_id');
    if(pack_method_selector !=""){
    	a=pack_method_selector.value
    	getPackDetail(a);
    	pack_method_selector.onchange = function () {
    		var selectedValue = this[this.selectedIndex].value;
    		if(selectedValue !=""){
    			getPackDetail(selectedValue);
    		}
    		else{
    			alert("包装1方式不能为空");
    			var pack_detail_selector = document.getElementById('id_pack_detail_id');
    			pack_detail_selector.innerHTML = '';
    		}
    	}//endfunction
    }//endif
    else{
    	alert("包装类型不能为空");
    }
}


function getPackDetail (pack_type){
	var pack_type=pack_type;
	//alert('getPackDetail-------'+pack_type);
	var pack_detail_selector = document.getElementById('id_pack_detail_id');
	
	$.ajax({
        url: "/bms/interface/locations/get_pack_detail_list",
        data: {pack_type: pack_type},
        type: 'GET',
        dataType: 'json',
        timeout: 15000,
        success: function (data) {
        	//alert("success");
        	//ert(data.data.pack_detail)
        	pack_detail_list=data.data.pack_detail
        	pack_detail_selector.innerHTML = '';
        	for (var  key in pack_detail_list){
        		//alert(pack_detail_list[key]);
        		pack_detail=pack_detail_list[key];
        		value=pack_detail[0];
        		text=pack_detail[1];
        		pack_detail_selector.options.add(getOption(text,value));
        	}
        	var pack_method_selector1 = document.getElementById('id_pack_method_id');
        	var pack_detail_selector1 = document.getElementById('id_pack_detail_id');
        	if (pack_method_selector1.value &&  pack_detail_selector1.value ){}
        	else if(!pack_detail_selector1.value){
        		pack_detail_selector1.innerHTML = '';
        		pack_detail_selector.options.add(getOption('无具体包装方式',''));
        	}	
        },
        error: function () {
           alert(data);
           //alert("网络异常请稍后再试");
        }
    });
}

function getOption(text,value){
    var o = document.createElement('option');
    o.text = text;
    o.value = value;
    return o;
}
function getFirstOption(){
    return getOption('请选择', '');
}

//2017/12/01/添加众安信息部分
function add_ZA_detail1(){
	//alert(44444)
	var insurance_type_selector = document.getElementById('id_product_type');
    var insurance_product_selector = document.getElementById('id_insurance_product_id');
    
    var index=insurance_product_selector.selectedIndex;//获取当前option  selectedIndex代表的是你所选中项的index
    var product_name=insurance_product_selector.options[index].text;
    //alert(product_name);
    //初始化众安添加信息部分
    document.getElementById("id_tb_client_type").style.display="none";//投保人类型
    document.getElementById("id_taxpayerRegNum").style.display="none";//纳税人识别号
    document.getElementById("id_taxpayerRegNum_ticket").style.display="none";//纳税人识别号(单票)
	  document.getElementById("id_holderCertNo_ticket").style.display="none";//投保人证件（单票）
    document.getElementById("id_holderCertType").style.display="none";//投保人证件类型
    document.getElementById("id_holderCertNo").style.display="none";//投保人证件号
    document.getElementById("id_insureCertType").style.display="none";//被保人证件类型
    document.getElementById("id_bb_insureCertNo").style.display="none";//被保人证件号
    if(insurance_type_selector.value == 'ticket'){
    		if (   product_name.indexOf("众安") >= 0  ){
    			document.getElementById("id_tb_client_type").style.display="block";//投保人类型
    			//alert("shi众安保险");
    		}
    		else{
    			document.getElementById("id_tb_client_type").style.display="none";//投保人类型
    			//alert("bushidanpiao");
    		}
    }
    else if (insurance_type_selector.value == 'batch'){
				if (product_name.indexOf("众安") >= 0 ){
					//alert(55)
					document.getElementById("id_tb_client_type").style.display="block";//投保人类型
				    document.getElementById("id_taxpayerRegNum").style.display="block";//纳税人识别号
				    document.getElementById("id_holderCertType").style.display="block";//投保人证件类型
				    document.getElementById("id_holderCertNo").style.display="block";//投保人证件号
				    document.getElementById("id_insureCertType").style.display="block";//被保人证件类型
				    document.getElementById("id_bb_insureCertNo").style.display="block";//被保人证件号
				}
				else{
					document.getElementById("id_tb_client_type").style.display="none";//投保人类型
				    document.getElementById("id_taxpayerRegNum").style.display="none";//纳税人识别号
				    document.getElementById("id_holderCertType").style.display="none";//投保人证件类型
				    document.getElementById("id_holderCertNo").style.display="none";//投保人证件号
				    document.getElementById("id_insureCertType").style.display="none";//被保人证件类型
				    document.getElementById("id_bb_insureCertNo").style.display="none";//被保人证件号
				}
		}
}


function add_ZA_detail(){
	//alert(44444)
	var insurance_type_selector = document.getElementById('id_product_type');
    var insurance_product_selector = document.getElementById('id_insurance_product_id');
    
    var index=insurance_product_selector.selectedIndex;//获取当前option  selectedIndex代表的是你所选中项的index
    var product_name=insurance_product_selector.options[index].text;
    //alert(product_name);
    //初始化众安添加信息部分
    if (product_name.indexOf("众安") >= 0 ){
    	 if(insurance_type_selector.value == 'ticket'){
     			document.getElementById("id_tb_client_type_ticket").style.display="block";//投保人类型
    	 }
    	 else if(insurance_type_selector.value == 'batch'){
    		 document.getElementById("id_tb_client_type").style.display="block";//投保人类型
		     document.getElementById("id_taxpayerRegNum").style.display="block";//纳税人识别号
		     document.getElementById("id_holderCertType").style.display="block";//投保人证件类型
		     document.getElementById("id_holderCertNo").style.display="block";//投保人证件号
		     document.getElementById("id_insureCertType").style.display="block";//被保人证件类型
		     document.getElementById("id_bb_insureCertNo").style.display="block";//被保人证件号
    	 }
    	 else{
    		 	document.getElementById("id_tb_client_type_ticket").style.display="none";//投保人类型(单票)
 	        	document.getElementById("id_taxpayerRegNum_ticket").style.display="none";//纳税人识别号(单票)
 	    		document.getElementById("id_holderCertNo_ticket").style.display="none";//投保人证件（单票）
    		 	document.getElementById("id_tb_client_type").style.display="none";//投保人类型
    	        document.getElementById("id_taxpayerRegNum").style.display="none";//纳税人识别号
    	        document.getElementById("id_holderCertType").style.display="none";//投保人证件类型
    	        document.getElementById("id_holderCertNo").style.display="none";//投保人证件号
    	        document.getElementById("id_insureCertType").style.display="none";//被保人证件类型
    	        document.getElementById("id_bb_insureCertNo").style.display="none";//被保人证件号
    	 }
    	 
    }
    else{
    	//初始化众安添加信息部分
    	document.getElementById("id_tb_client_type").style.display="none";//投保人类型
        document.getElementById("id_taxpayerRegNum").style.display="none";//纳税人识别号
        document.getElementById("id_taxpayerRegNum_ticket").style.display="none";//纳税人识别号(单票)
    	  document.getElementById("id_holderCertNo_ticket").style.display="none";//投保人证件（单票）
        document.getElementById("id_holderCertType").style.display="none";//投保人证件类型
        document.getElementById("id_holderCertNo").style.display="none";//投保人证件号
        document.getElementById("id_insureCertType").style.display="none";//被保人证件类型
        document.getElementById("id_bb_insureCertNo").style.display="none";//被保人证件号
    }
    

}
//*************************************************************************************

//#############################################省市区三级联动#################
function change_province() {
    var target_province_selector = document.getElementById('targetSiteName_prov');
    var city_selector = document.getElementById('targetSiteName_city');
    var area_selector = document.getElementById('targetSiteName_dist');
    var start_province_selector = document.getElementById('startSiteName_prov');
    var bms_order_type = document.getElementById('bms_order_type');
    if(target_province_selector != null){
    	//alert(bms_order_type.value)
    	if (bms_order_type.value == "create"){
    		change_city_list('targetSiteName_');
    	}
    	target_province_selector.onchange = function () {
    		change_city_list('targetSiteName_');
        }
    }//end first if
    if(start_province_selector != null){
    	if (bms_order_type.value == "create"){
    		change_city_list('startSiteName_');
    	}
    	start_province_selector.onchange = function () {
    		//alert(start_province_selector.value)
    		//alert("3333")
    		change_city_list('startSiteName_');
        }
    }//end first if
}

function change_city_list(state) {
	//alert("555")
	var state=state
	//alert("state"+state)
    var province_selector = document.getElementById( state+'prov');
    var city_selector = document.getElementById(state+'city');
    $.ajax({
        url: "/bms/interface/locations/get_city_list/",
        data: {prov_code: province_selector.value},
        type: 'GET',
        dataType: 'json',
        timeout: 15000,
        success: function (data) {
        //	//alert("success")
        	var a=1
        	city_selector.innerHTML = '';
        	 for (var key1 in data['data']) {
        		 city_selector.options.add(getOption(data['data'][key1], key1));
            }
        	 change_dist_list(state);
        },
        error: function (data) {
            $('#id_message').removeClass('control-show');
            $('#id_message_id').html(data['message'])
        }
    });
    
    city_selector.onchange = function () {
    	change_dist_list(state);
    }
    

}

function change_dist_list(state) {
//	alert("666")
    var province_selector = document.getElementById(state+'prov');
    var city_selector = document.getElementById(state+'city');
    var dist_selector = document.getElementById(state+'dist');
    $.ajax({
        url: "/bms/interface/locations/get_dist_list/",
        data: {city_code: city_selector.value},
        type: 'GET',
        dataType: 'json',
        timeout: 15000,
        success: function (data) {
       // 	alert("success")
        	var a=1
        	dist_selector.innerHTML = '';
        	 for (var key1 in data['data']) {
        		 dist_selector.options.add(getOption(data['data'][key1], key1));
            }
        },
        error: function (data) {
            $('#id_message').removeClass('control-show');
            $('#id_message_id').html(data['message'])
        }
    });
}


//############################################################创建认证管理页面  联动
function chang_user_type(){
    var user_type = $('#id_user_type');
    var id_user_classify = $('#id_user_classify');
    if(user_type.val()=='transport'){
        $("#id_user_classify option").remove();
        $("#id_user_classify").append("<option value='singleLine'>专线</option>");
        $("#id_user_classify").append("<option value='multiLine'>货代</option>");
        $('#id_business_certificate').removeClass('control-show');
        $('#id_driver_certificate').addClass('control-show');
        $('#id_boss_certificate').addClass('control-show');
    }else if(user_type.val()=='driver'){
        $("#id_user_classify option").remove();
        $("#id_user_classify").append("<option value=''>暂无类别</option>");
        $('#id_business_certificate').addClass('control-show');
        $('#id_driver_certificate').removeClass('control-show');
        $('#id_boss_certificate').addClass('control-show');
    }else if(user_type.val()=='boss'){
        $("#id_user_classify option").remove();
        $("#id_user_classify").append("<option value='individuals'>个人</option>");
        $("#id_user_classify").append("<option value='units'>单位</option>");
        $('#id_business_certificate').addClass('control-show');
        $('#id_driver_certificate').addClass('control-show');
        $('#id_boss_certificate').addClass('control-show');
    }
    //车主
    else if(user_type.val()=='owner'){
        $("#id_user_classify option").remove();
        $("#id_user_classify").append("<option value='individuals'>个人</option>");
        $('#id_business_certificate').addClass('control-show');
        $('#id_driver_certificate').addClass('control-show');
        $('#id_boss_certificate').addClass('control-show');
    }else if(user_type.val()=='default_type'){
        $("#id_user_classify option").remove();
        $("#id_user_classify").append("<option value='default_classify'>请选择</option>");
        $("#id_user_classify").append("<option value='singleLine'>专线</option>");
        $("#id_user_classify").append("<option value='multiLine'>货代</option>");
        $("#id_user_classify").append("<option value='individuals'>个人</option>");
        $("#id_user_classify").append("<option value='units'>单位</option>");
        $('#id_business_certificate').addClass('control-show');
        $('#id_driver_certificate').addClass('control-show');
        $('#id_boss_certificate').addClass('control-show');
    }
}
function change_user_classify(){
    var user_type = $('#id_user_type');
    var id_user_classify = $('#id_user_classify');
    if(user_type.val()=='default_type'){
        $("#id_user_classify option").remove();
        $("#id_user_classify").append("<option value=''>请先选择认证目标</option>");
    }
    if(id_user_classify.val()=='units'){
        $('#id_business_certificate').addClass('control-show');
        $('#id_driver_certificate').addClass('control-show');
        $('#id_boss_certificate').removeClass('control-show');
    }
    if(id_user_classify.val()=='individuals'){
        $('#id_business_certificate').addClass('control-show');
        $('#id_driver_certificate').addClass('control-show');
        $('#id_boss_certificate').addClass('control-show');
    }

}

//*************************************************************************************



