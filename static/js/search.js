       $(function () {

           // searchbar
                   $('#container').on('focus', '#search_input', function () {
                       var $weuiSearchBar = $('#search_bar');
                       $weuiSearchBar.addClass('weui_search_focusing');
                   }).on('blur', '#search_input', function () {
                       var $weuiSearchBar = $('#search_bar');
                       $weuiSearchBar.removeClass('weui_search_focusing');
                       if ($(this).val()) {
                           $('#search_text').hide();
                       } else {
                           $('#search_text').show();
                       }
                   }).on('input', '#search_input', function () {
                       var $searchShow = $("#search_show");
                       if ($(this).val()) {
                           $searchShow.show();
                       } else {
                           $searchShow.hide();
                       }
                   }).on('touchend', '#search_cancel', function () {
                       $("#search_show").hide();
                       $('#search_input').val('');
                   }).on('touchend', '#search_clear', function () {
                       $("#search_show").hide();
                       $('#search_input').val('');
                   });




           // .container 设置了 overflow 属性, 导致 Android 手机下输入框获取焦点时, 输入法挡住输入框的 bug
           // 相关 issue: https://github.com/weui/weui/issues/15
           // 解决方法:
           // 0. .container 去掉 overflow 属性, 但此 demo 下会引发别的问题
           // 1. 参考 http://stackoverflow.com/questions/23757345/android-does-not-correctly-scroll-on-input-focus-if-not-body-element
           //    Android 手机下, input 或 textarea 元素聚焦时, 主动滚一把
           if (/Android/gi.test(navigator.userAgent)) {
               window.addEventListener('resize', function () {
                   if (document.activeElement.tagName == 'INPUT' || document.activeElement.tagName == 'TEXTAREA') {
                       window.setTimeout(function () {
                           document.activeElement.scrollIntoViewIfNeeded();
                       }, 0);
                   }
               })
           }
       });