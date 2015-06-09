# air_condition  
2015/05/20 :smile: qmlClient 不能正确识别连续点击，待更正  
2015/05/21 :smile: testInterval 正常工作   
2015/05/25 :smile: 增加前台从机  
2015/05/28 :qyyy: 可以正确识别结账功能
2015/06/06 :qyyy: 实现跨网通信
2015/06/06 :sola: V2增加数据库部分
###JSON内容
>     * 退房请求 {'method': 'checkout', 'cid': 'xxx', 'from': "reception"}  
>     * 返回     {'method': 'checkout', 'result': 'ok'}
>     * 查看详单 {'method': 'report', 'cid': 'xxx'}  
>     * 返回     {'method': 'report', 'result': 'ok', 'data': ['第一行内容', '第二行内容', …… ]}  
>     * 登记请求 {'method': 'register', 'id': 'xxx', 'name': 'xxx', 'cid': 'xxx', 'money': 'xxx'}
>     * 返回     {'method': 'register', 'result': 'ok'}
>     * 充值请求 {'method': 'recharge', 'id': 'xxx', 'money': 'xxx'}
>     * 返回     {'method': 'recharge', 'result': 'ok'}

###因为技术原因所做的妥协
>     * 当有超过预设的连接数的从机连接主机时，主机返回None(返回值同无主机时的返回值)。
>     * 当前台发出结账命令时，从机只能在running或者standby状态下才能正确响应，如果是shutdown状态则无法响应。

###版本声明
>     * V1为不增加注册功能的主控机，可以和其他组联调
>     * V2为增加了注册功能的主控机，不可与其他组联调
