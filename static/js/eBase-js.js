var EcBase = EcBase || {};

EcBase.createBarAndLine = function (obj, callBack) {
    var yAxis = obj.yAxis;
    var data=obj.data;
    for (var i = 0; i < yAxis.length; i++) {
    	yAxis[i].type = "value";
        yAxis[i].axisLabel = {formatter: '{value}' + yAxis[i].unit};
    }
    if(obj.data[0].data.length == 0){
    	obj.data=[];
    }
    var option = {
        tooltip: {
            trigger: 'axis'
        },
        legend: {
            data: obj.data
        },
        calculable: true,
        xAxis: [
            {
                type: 'category',
                data: obj.xAxis
            }
        ],
        yAxis: obj.yAxis,
        series: obj.data
    };
    if (obj.switch == "true") {
        for (var i = 0; i < data.length; i++) {
            if (data[i].yAxisIndex != undefined) {
                data[i].xAxisIndex = data[i].yAxisIndex;
                delete data[i]["yAxisIndex"];
            }
        }
        var temp = option.yAxis;
        option.yAxis = option.xAxis;
        option.xAxis = temp;
    }
    var chart = echarts.init(document.getElementById(obj.id));
    chart.setOption(option);
    chart.on("click", function (param) {
        eval("(" + callBack(param.data) + ")");
    });
}