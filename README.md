# air_condition  
2015/05/20 :smile: qmlClient 不能正确识别连续点击，待更正  
2015/05/21 :smile: testInterval 正常工作   
2015/05/25 :smile: 增加前台从机  
2015/05/28 :qyyy: 可以正确识别结账功能
2015/06/06 :qyyy: 实现跨网通信
2015/06/06 :sola: V2增加数据库部分
2015/06/12 :qyyy: 合并V1、V2版本，新增计时器功能的特殊客户端client.py。新增链接库
###JSON内容
>     * 退房请求 {'method': 'checkout', 'cid': 'xxx', 'from': "reception"}  
>     * 返回     {'method': 'checkout', 'result': 'ok'}
>     * 查看详单 {'method': 'report', 'cid': 'xxx'}  
>     * 返回     {'method': 'report', 'result': 'ok', 'data': ['第一行内容', '第二行内容', …… ]}  
>     * 登记请求 {'method': 'register', 'id': 'xxx', 'name': 'xxx', 'cid': 'xxx', 'money': 'xxx'}
>     * 返回     {'method': 'register', 'result': 'ok'}
>     * 充值请求 {'method': 'recharge', 'id': 'xxx', 'money': 'xxx'}
>     * 返回     {'method': 'recharge', 'result': 'ok'}
>     * 计时     {'method': 'timer'}
>     * 返回     无

###因为技术原因所做的妥协
>     * 没有进行优先级调度


###版本声明
>     * server.py为主控机部分
>     * client.py为特殊从机，充当定时器
>     * qmlReputation文件夹内的工程为前台
>     * qmlClient文件夹内为从控机
