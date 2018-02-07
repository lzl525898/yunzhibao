wx.config({
    debug: true, // 开启调试模式,调用的所有api的返回值会在客户端alert出来，若要查看传入的参数，可以在pc端打开，参数信息会通过log打出，仅在pc端时才会打印。
    appId: 'wxa88405ef667fd9da', // 必填，公众号的唯一标识
    timestamp: '{{ timestamp|safe }}', // 必填，生成签名的时间戳
    nonceStr: '{{ nonceStr|safe }}', // 必填，生成签名的随机串
    signature:'{{ signature |safe}}',// 必填，签名，见附录1
    jsApiList: [    
				'checkJsApi' ,
				'onMenuShareTimeline',
				'onMenuShareAppMessage',
				'onMenuShareQQ',
				'onMenuShareWeibo',
]     // 必填，需要使用的JS接口列表，所有JS接口列表见附录2
});


  wx.ready(function () {
	 // alert('44');
	  // 1 判断当前版本是否支持指定 JS 接口，支持批量判断*/
	  document.querySelector('#checkJsApi').onclick = function () {
	    wx.checkJsApi({
	      jsApiList: [
	        'getNetworkType',
	        'previewImage',
	        'onMenuShareWeibo',
	      ],
	      success: function (res) {
	        alert(JSON.stringify(res));
	      }
	    }); 
	  };
	  
	  
	  
	  // 2. 分享接口
	  // 2.1 监听“分享给朋友”，按钮点击、自定义分享内容及分享结果接口
	  document.querySelector('#onMenuShareAppMessage').onclick = function () {
	    wx.onMenuShareAppMessage({
	      title: '保险列表详情',
	      desc: '运之宝~只为让您安心~~。',
	      link: 'http://crteam.top/wss/insure/product_list?referee_id={{ mine_id }}',
	      imgUrl: 'https://mmbiz.qlogo.cn/mmbiz/rrFA3l0J5Ub0pCbLOgmNnlm1sZ8beiaLefnP8xwT9SCciaxyrNQz2KAFDMjRDWCR4XVCtLj29rMLfF9NUUWrUtKg/0?wx_fmt=png',
	      trigger: function (res) {
	        alert('用户点击发送给朋友');
	      },
	      success: function (res) {
	        alert('已分享');
	      },
	      cancel: function (res) {
	        alert('已取消');
	      },
	      fail: function (res) {
	        alert(JSON.stringify(res));
	      }
	    });
	    alert('已注册获取“发送给朋友”状态事件');
	  };
	  
	// 2.2 监听“分享到朋友圈”按钮点击、自定义分享内容及分享结果接口
	  document.querySelector('#onMenuShareTimeline').onclick = function () {
	    wx.onMenuShareTimeline({
	      title: '保险列表部分',
	      link:'http://crteam.top/wss/insure/product_list/ ',
	      imgUrl: 'https://mmbiz.qlogo.cn/mmbiz/rrFA3l0J5Ub0pCbLOgmNnlm1sZ8beiaLeeIibavLCjib3DrnHIkFL0Z3XTztcibZhb2564ics3njB1YuymjWQg7F3Cw/0?wx_fmt=png',
	      trigger: function (res) {
	        alert('用户点击分享到朋友圈');
	      },
	      success: function (res) {
	        alert('已分享');
	      },
	      cancel: function (res) {
	        alert('已取消');
	      },
	      fail: function (res) {
	        alert(JSON.stringify(res));
	      }
	    });
	    alert('已注册获取“分享到朋友圈”状态事件');
	  };
	  	  
	  
});
