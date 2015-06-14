import QtQuick 2.4
import QtQuick.Controls 1.3
import QtQuick.Window 2.2
import Qt.WebSockets 1.0
import QtQuick.Dialogs 1.2
import QtQuick.Layouts 1.1
import QtQuick.Controls.Styles 1.3

ApplicationWindow {
    id: client
    title: qsTr("Client")
    width: 400
    height: 400
    visible: true

    property var clientID
    property var fanSpeed
    property var tempMax
    property var tempMin
    property var tBefore
    property var tAfter
    property var tmpURL: "ws://localhost:6666/"
    property var tmpCID: "305f";

    WebSocket {
        id: socket
        url: tmpURL

        onTextMessageReceived: {
            console.debug("Receive: " + message);
            var msg = JSON.parse(message);

            switch(msg.method){
            case "handshake":
                if(msg.result === "ok") {
                    if(msg.config["mode"] === "winter")
                        mode.text = qsTr("制热");
                    else if(msg.config["mode"] === "summer")
                        mode.text = qsTr("制冷");
                    tempMin = msg.config["temp-min"];
                    tempMax = msg.config["temp-max"];
                    console.debug(tempMin+" "+tempMax);
                }
                break;
            case "get":
                if(msg.state === "standby") {
                    state.text = "待机";
                } else if(msg.state === "running") {
                    state.text = "运行";
                } else {
                    state.text = "停机";
                    socket.active = false;
                }
                curTemp.text = msg.temp;
                cost.text = msg.cost;
                break;
            case "set": case "changed":
                if(msg.state === "standby") {
                    state.text = "待机";
                } else if(msg.state === "running") {
                    state.text = "运行";
                } else {
                    state.text = "停机";
                    socket.active = false;
                }
                break;
            case "shutdown":
                if(msg.result === "ok")
                    socket.active = false;
                break;
            case "checkout":
                var checkout = {
                    "method" : "checkout",
                    "cid": clientID,
                    "result": "ok"
                }
                socket.sendTextMessage(JSON.stringify(checkout));
                socket.active = false;
                break;
            }
        }
        onStatusChanged:{
            if (socket.status == WebSocket.Open) {
                console.debug("Socket open");
                var handshake = {
                    "method" : "handshake",
                    "cid" : clientID,
                    "temp" : parseInt(curTemp.text),
                    "speed" : fanSpeed,
                    "target" : parseInt(destTemp.text)
                }
                socket.sendTextMessage(JSON.stringify(handshake));
                state.text = "运行";
                console.debug("Send: "+ JSON.stringify(handshake));
            } else if(socket.status == WebSocket.Connecting) {
                console.debug("Connecting... " + socket.url);
            } else {
                if (socket.status == WebSocket.Closed) {
                    console.debug("Socket closed");
                } else if (socket.status == WebSocket.Error) {
                    socket.active = false
                    console.debug("Error: " + socket.errorString);
                }
                state.text = "停机";
                radioOff.checked = true;
                reset();
            }
        }
        active: false
    }

    /*** 菜单 ***/
    menuBar: MenuBar {
        Menu {
            title: "菜单";
            MenuItem {
                text: "设置";
                onTriggered:{
                    scene_main.visible = false;
                    scene_setting.visible = true;
                    textFieldURL.text = socket.url;
                    textFieldCID.text = clientID;
                }
            }
        }
    }

    /*** 主界面 ***/
    Item {
        id: scene_main
        visible: true
        anchors.fill: parent

        GroupBox {
            id: groupSwitch
            x: 270
            width: 80
            height: 80
            anchors.top: groupFan.bottom
            anchors.topMargin: 30
            anchors.right: parent.right
            anchors.rightMargin: 50
            title: qsTr("开关")

            ColumnLayout {
                anchors.fill: parent

                ExclusiveGroup { id: onoff }
                RadioButton {
                    id: radioOn
                    text: qsTr("On")
                    exclusiveGroup: onoff
                    onClicked: {
                        clientID = tmpCID;
                        socket.url = tmpURL;
                        socket.active = true;
                    }
                }

                RadioButton {
                    id: radioOff
                    text: qsTr("Off")
                    exclusiveGroup: onoff
                    checked: true
                    onClicked: {
                        var shutdown = {
                            method: "shutdown",
                            cid: clientID
                        }
                        socket.sendTextMessage(JSON.stringify(shutdown));
                    }
                }
            }
        }

        GroupBox {
            id: groupTemp
            x: 50
            width: 80
            height: 80
            anchors.left: parent.left
            anchors.leftMargin: 150
            anchors.top: groupSwitch.top
            anchors.topMargin: 0
            title: qsTr("温度调节")

            ColumnLayout {
                id: columnLayout
                anchors.fill: parent

                Button {
                    id: tempUp
                    text: qsTr("+")
                    Layout.fillWidth: true
                    checkable: false
                    onClicked: {
                        var tmp = parseInt(destTemp.text);
                        if(tmp < tempMax) {
                            destTemp.text = (tmp + 1).toString();
                        }
                        testInterval.restart();
                    }
                }

                Button {
                    id: tempDown
                    text: qsTr("-")
                    Layout.fillWidth: true
                    onClicked: {
                        var tmp = parseInt(destTemp.text);
                        if(tmp > tempMin) {
                            destTemp.text = (tmp - 1).toString();
                        }
                        testInterval.restart();
                    }
                }
            }
        }

        GroupBox {
            id: groupFan
            x: 270
            title: qsTr("风速调节")
            width: 80
            height: 140
            anchors.top: parent.top
            anchors.topMargin: 60
            anchors.right: parent.right
            anchors.rightMargin: 50

            ColumnLayout {
                anchors.fill: parent

                ExclusiveGroup {
                    id: exFan
                    onCurrentChanged: {
                        console.debug(exFan.current.toString());
                        switch(exFan.current.toString())
                        {
                        case radioHigh.toString():
                            fanSpeed = "high";
                            break;
                        case radioMed.toString():
                            fanSpeed = "medium";
                            break;
                        case radioLow.toString():
                            fanSpeed = "low";
                            break;
                        }
                        testInterval.restart();
                    }
                }
                RadioButton {
                    id: radioHigh
                    text: qsTr("高")
                    exclusiveGroup: exFan
                }
                RadioButton {
                    id: radioMed
                    text: qsTr("中")
                    checked: true
                    exclusiveGroup: exFan
                }

                RadioButton {
                    id: radioLow
                    text: qsTr("低")
                    exclusiveGroup: exFan
                }
            }
        }

        GroupBox {
            id: groupCur
            width: 80
            height: 60
            anchors.top: parent.top
            anchors.topMargin: 60
            anchors.left: parent.left
            anchors.leftMargin: 150
            title: qsTr("当前温度")

            RowLayout {
                anchors.fill: parent

                Label {
                    id: curTemp
                    text: qsTr("25")
                    font.pointSize: 12
                    verticalAlignment: Text.AlignVCenter
                    horizontalAlignment: Text.AlignRight
                    onTextChanged: {
                        if(state.text == "待机") {
                            var changeReq = {
                                "method": "changed",
                                "cid": clientID,
                                "temp": parseInt(curTemp.text)
                            }
                            socket.sendTextMessage(JSON.stringify(changeReq));
                            console.debug("Send: " + JSON.stringify(changeReq));
                        }
                    }
                }

                Label {
                    id: label1
                    text: qsTr("℃")
                    font.pointSize: 12
                    anchors.leftMargin: 47
                    verticalAlignment: Text.AlignVCenter
                    horizontalAlignment: Text.AlignLeft
                }
            }
        }

        GroupBox {
            id: groupDest
            width: 80
            height: 60
            anchors.left: parent.left
            anchors.leftMargin: 50
            anchors.top: parent.top
            anchors.topMargin: 60
            title: qsTr("目标温度")

            RowLayout {
                anchors.fill: parent

                Label {
                    id: destTemp
                    text: qsTr("25")
                    font.pointSize: 12
                    verticalAlignment: Text.AlignVCenter
                    horizontalAlignment: Text.AlignRight
                }

                Label {
                    id: label2
                    text: qsTr("℃")
                    font.pointSize: 12
                    anchors.leftMargin: 53
                    verticalAlignment: Text.AlignVCenter
                    horizontalAlignment: Text.AlignLeft
                }
            }
        }

        GroupBox {
            id: groupFee
            width: 80
            height: 60
            anchors.top: groupCur.bottom
            anchors.topMargin: 20
            anchors.left: parent.left
            anchors.leftMargin: 50
            title: qsTr("费用")

            RowLayout {
                anchors.fill: parent

                Label {
                    id: dollar
                    text: qsTr("￥")
                    font.pointSize: 12
                    verticalAlignment: Text.AlignVCenter
                    horizontalAlignment: Text.AlignRight
                }

                Label {
                    id: cost
                    text: qsTr("0")
                    font.pointSize: 12
                    verticalAlignment: Text.AlignVCenter
                    horizontalAlignment: Text.AlignLeft
                }
            }
        }

        GroupBox {
            id: groupMode
            width: 80
            height: 60
            anchors.left: parent.left
            anchors.leftMargin: 150
            anchors.top: groupDest.bottom
            anchors.topMargin: 20
            title: qsTr("工作模式")

            Label {
                id: mode
                font.pointSize: 12
                verticalAlignment: Text.AlignVCenter
                anchors.fill: parent
                horizontalAlignment: Text.AlignHCenter
            }
        }

        GroupBox {
            id: groupState
            x: 150
            width: 80
            height: 80
            anchors.top: groupSwitch.top
            anchors.topMargin: 0
            anchors.left: parent.left
            anchors.leftMargin: 50
            title: qsTr("状态")
            Label {
                id: state
                text: qsTr("停机")
                anchors.fill: parent
                verticalAlignment: Text.AlignVCenter
                font.pointSize: 12
                horizontalAlignment: Text.AlignHCenter
                onTextChanged: {
                    if(state.text == "运行"){
                        repeatTimer.start();
                        autoChange.stop();
                    } else if(state.text == "待机") {
                        repeatTimer.stop();
                        autoChange.start();
                    } else if(state.text == "停机") {
                        repeatTimer.stop();
                        autoChange.stop();
                    }
                }
            }
        }
    }

    /*** 设置界面 ***/
    Item {
        id: scene_setting
        visible: false
        anchors.fill: parent

        Label {
            id: labelURL
            width: 75
            height: 23
            text: qsTr("主控机URL")
            anchors.top: parent.top
            anchors.topMargin: 100
            anchors.left: parent.left
            anchors.leftMargin: 80
            verticalAlignment: Text.AlignVCenter
            horizontalAlignment: Text.AlignHCenter
        }

        Label {
            id: labelCID
            width: 75
            height: 23
            text: qsTr("从控机编号")
            anchors.top: labelURL.bottom
            anchors.topMargin: 30
            anchors.left: parent.left
            anchors.leftMargin: 80
            verticalAlignment: Text.AlignVCenter
            horizontalAlignment: Text.AlignHCenter
        }

        TextField {
            id: textFieldURL
            x: 172
            width: 160
            height: 23
            anchors.top: parent.top
            anchors.topMargin: 100
            anchors.right: parent.right
            anchors.rightMargin: 80
            onTextChanged: {
                if(textFieldURL.text.trim().length > 0 && textFieldCID.text.trim().length > 0)
                    buttonSet.enabled = true;
                else
                    buttonSet.enabled = false;
            }
        }

        TextField {
            id: textFieldCID
            x: 161
            width: 160
            height: 23
            anchors.top: textFieldURL.bottom
            anchors.topMargin: 30
            anchors.right: parent.right
            anchors.rightMargin: 80
            onTextChanged: {
                if(textFieldURL.text.trim().length > 0 && textFieldCID.text.trim().length > 0)
                    buttonSet.enabled = true;
                else
                    buttonSet.enabled = false;
            }
        }

        Button {
            id: buttonSet
            x: 175
            y: 212
            text: qsTr("设置")
            enabled: false
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 100
            anchors.right: parent.right
            anchors.rightMargin: 80
            onClicked: {
                tmpURL = textFieldURL.text.trim();
                tmpCID = textFieldCID.text.trim();
                messageDialog.show(qsTr("设置成功！重新连接后生效"), StandardIcon.Information)
            }
        }

        Button {
            id: buttonBack
            x: 50
            y: 212
            text: qsTr("返回")
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 100
            anchors.left: parent.left
            anchors.leftMargin: 80
            onClicked: {
                scene_main.visible = true;
                scene_setting.visible = false;
            }
        }
    }

    BusyIndicator {
        anchors.bottomMargin: 60
        z: 1
        anchors.fill: parent
        anchors.margins: 60
        running: socket.status == WebSocket.Connecting || socket.status == WebSocket.Closing
    }

    MessageDialog {
        id: messageDialog
        title: " "
        function show(caption, icon) {
            messageDialog.text = caption;
            messageDialog.icon = icon;
            messageDialog.open();
        }
    }

    /*** Timer ***/
    Timer {
        id: repeatTimer
        interval: 1000 * 60
        repeat: true
        onTriggered: {
            var getReq = {
                "method": "get",
                "cid": clientID
            }
            socket.sendTextMessage(JSON.stringify(getReq));
            console.debug("Send: " + JSON.stringify(getReq));
        }
    }

    Timer {
        id: autoChange
        interval: 1000 * 60 * 2
        repeat: true
        onTriggered: {
            var tmp = parseInt(curTemp.text);
            if(mode.text === "制热"){
                curTemp.text = (tmp - 1).toString();
            }
            else if (mode.text == "制冷"){
                curTemp.text = (tmp + 1).toString();
            }
        }
    }

    Timer {
        id: testInterval
        interval: 1000 * 10
        repeat: false
        onTriggered: {
            var setReq = {
                "method": "set",
                "cid": clientID,
                "target": parseInt(destTemp.text),
                "speed": fanSpeed
            }
            socket.sendTextMessage(JSON.stringify(setReq));
            console.debug("Send: "+ JSON.stringify(setReq));
        }
    }

    Component.onCompleted: {
        socket.url = tmpURL;
        clientID = tmpCID;
        fanSpeed = "medium";
        tBefore = 0;
        reset();
    }

    /*** custom function ***/
    function reset() {
        curTemp.text = 25;
        destTemp.text = 25;
        cost.text = 0.0;
        mode.text = "";
        radioMed.checked = true;
        testInterval.stop();
    }
}
