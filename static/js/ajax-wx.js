/**
 * Created by mlzx on 2015/5/16.
 */

//
// function ajax_csrf(){
//    //ajax csrf 为了ajax POST准备的，只要加载一次，修改HTTP POST的全局变量
////    console.log("ajax_csrf");
//    var csrftoken = $.cookie('csrftoken');
//    function csrfSafeMethod(method) {
//        // these HTTP methods do not require CSRF protection
//        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
//    }
//    $.ajaxSetup({
//        crossDomain: false, // obviates need for sameOrigin test
//        beforeSend: function(xhr, settings) {
//            if (!csrfSafeMethod(settings.type)) {
//                xhr.setRequestHeader("X-CSRFToken", csrftoken);
//            }
//        }
//    });
// }




$(document).ready(function (){

//    ajax_csrf();
//    $("#start_city").citySelect();
//    $("#end_city").citySelect();
});
function is_weixin(){
	var ua = navigator.userAgent.toLowerCase();
	if(ua.match(/MicroMessenger/i)== "micromessenger" ) {
		return true;
 	} else {
		return false;
	}
}
/* 关闭浏览器*/
function close_window(){
    wx.closeWindow();
}
/* 关闭对话框*/
function close_dialog(){
    $(".weui_dialog_alert").hide();
}

/* 计算建议字数*/
function advice_count(){
    var text = document.getElementById("id_advice").value;
    var count = parseInt(200)-parseInt(text.length);
    if(count>=0){
        $('#id_textarea_suggestions').text(count);
    }else{
        alert("最多可提交200字")
    }
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
    }else if(user_type.val()=='owner'){
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

