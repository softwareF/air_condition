import QtQuick 2.4
import QtQuick.Controls 1.3
import QtQuick.Window 2.2
import QtQuick.Dialogs 1.2
import Qt.WebSockets 1.0

ApplicationWindow {
    id: window
    title: qsTr("Reception")
    width: 300
    height: 300

    menuBar: MenuBar {
        Menu {
            title: "菜单";
            MenuItem {
                text: "登记";
                onTriggered:{
                    scene_1.visible = false;
                    scene_2.visible = true;
                    scene_3.visible = false;
                }
            }
            MenuItem {
                text: "充值";
                onTriggered:{
                    scene_1.visible = false;
                    scene_2.visible = false;
                    scene_3.visible = true;
                }
            }
        }
    }

    WebSocket {
        id: socket
        url: "ws://localhost:6666/"

        onTextMessageReceived: {
            console.debug("Receive: " + message);
            var msg = JSON.parse(message);
            switch(msg.method){
            case "checkout":
                if(msg.result === "ok"){
                    messageDialog.show(qsTr("结账成功！"), StandardIcon.Information);
                } else {
                    messageDialog.show(qsTr("结账失败！"), StandardIcon.Warning);
                }
                break;
            case "report":
                if(msg.result === "ok") {
                    textArea.text = "";
                    for(var i = 0; i < msg.data.length; ++i){
                        textArea.append(msg.data[i]);
                    }
                    reportWindow.setVisible(true);
                } else {
                    messageDialog.show(qsTr("操作失败，客户未结账！"), StandardIcon.Warning);
                }
                break;
            case "register":
                if(msg.result === "ok") {
                    messageDialog.show(qsTr("登记成功！"), StandardIcon.Information);
                    textField1.text = textField2.text = textField3.text = "";
                } else {
                    messageDialog.show(qsTr("登记失败！"), StandardIcon.Warning);
                }
                break;
            case "recharge":
                if(msg.result === "ok") {
                    messageDialog.show(qsTr("充值成功！"), StandardIcon.Information);
                    textFieldID.text = textFieldMoney.text = "";
                } else {
                    messageDialog.show(qsTr("充值失败！"), StandardIcon.Warning);
                }
            }
        }
        onStatusChanged: {
            console.debug(socket.status);
            if(socket.status != WebSocket.Connecting && socket.status != WebSocket.Open)
                Qt.quit();
        }
        active: true
    }

    Item {
        id: scene_1
        visible: true
        anchors.fill: parent
        Label {
            id: labelCid
            x: 50
            y: 84
            width: 75
            height: 23
            text: qsTr("房间编号")
            verticalAlignment: Text.AlignVCenter
            horizontalAlignment: Text.AlignHCenter
        }

        TextField {
            id: input
            x: 125
            y: 84
            width: 125
            height: 23
            font.pointSize: 10
            horizontalAlignment: Text.AlignLeft
            focus: true
        }

        Button {
            id: buttonCheckout
            x: 50
            y: 182
            text: qsTr("结账退房")
            onClicked: {
                var cid = input.text;
                if(cid.trim().length > 0) {
                    var checkout = {
                        method: "checkout",
                        cid: cid,
                        from: "reception"
                    }
                    socket.sendTextMessage(JSON.stringify(checkout));
                }
            }
        }

        Button {
            id: buttonReport
            x: 174
            y: 182
            text: qsTr("查看详单")
            enabled: true
            onClicked: {
                var cid = input.text;
                if(cid.trim().length > 0) {
                    var report = {
                        method: "report",
                        cid: cid
                    }
                    socket.sendTextMessage(JSON.stringify(report));
                }
            }
        }
    }

    Item {
        id: scene_2
        visible: false
        anchors.fill: parent

        Label {
            id: label1
            width: 75
            height: 23
            text: qsTr("客户编号")
            anchors.top: parent.top
            anchors.topMargin: 55
            anchors.left: parent.left
            anchors.leftMargin: 50
            verticalAlignment: Text.AlignVCenter
            horizontalAlignment: Text.AlignHCenter
        }

        Label {
            id: label2
            width: 75
            height: 23
            text: qsTr("客户名称")
            anchors.top: label1.bottom
            anchors.topMargin: 10
            anchors.left: parent.left
            anchors.leftMargin: 50
            verticalAlignment: Text.AlignVCenter
            horizontalAlignment: Text.AlignHCenter
        }

        Label {
            id: label3
            width: 75
            height: 23
            text: qsTr("房间编号")
            anchors.top: label2.bottom
            anchors.topMargin: 10
            anchors.left: parent.left
            anchors.leftMargin: 50
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }

        Label {
            id: label4
            width: 75
            height: 23
            text: qsTr("预存金额")
            anchors.top: label3.bottom
            anchors.topMargin: 10
            anchors.left: parent.left
            anchors.leftMargin: 50
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }

        TextField {
            id: textField1
            width: 125
            height: 23
            anchors.top: parent.top
            anchors.topMargin: 55
            anchors.right: parent.right
            anchors.rightMargin: 50
            onTextChanged: {
                if(textField1.text.trim().length > 0 && textField2.text.trim().length > 0 && textField3.text.trim().length > 0 && textField4.text.trim().length > 0)
                    buttonRegister.enabled = true;
                else
                    buttonRegister.enabled = false;
            }
        }

        TextField {
            id: textField2
            width: 125
            height: 23
            anchors.top: textField1.bottom
            anchors.topMargin: 10
            anchors.right: parent.right
            anchors.rightMargin: 50
            onTextChanged: {
                if(textField1.text.trim().length > 0 && textField2.text.trim().length > 0 && textField3.text.trim().length > 0 && textField4.text.trim().length > 0)
                    buttonRegister.enabled = true;
                else
                    buttonRegister.enabled = false;
            }
        }

        TextField {
            id: textField3
            width: 125
            height: 23
            anchors.top: textField2.bottom
            anchors.topMargin: 10
            anchors.right: parent.right
            anchors.rightMargin: 50
            onTextChanged: {
                if(textField1.text.trim().length > 0 && textField2.text.trim().length > 0 && textField3.text.trim().length > 0 && textField4.text.trim().length > 0)
                    buttonRegister.enabled = true;
                else
                    buttonRegister.enabled = false;
            }
        }

        TextField {
            id: textField4
            width: 125
            height: 23
            anchors.top: textField3.bottom
            anchors.topMargin: 10
            anchors.right: parent.right
            anchors.rightMargin: 50
            onTextChanged: {
                if(textField1.text.trim().length > 0 && textField2.text.trim().length > 0 && textField3.text.trim().length > 0 && textField4.text.trim().length > 0)
                    buttonRegister.enabled = true;
                else
                    buttonRegister.enabled = false;
            }
        }

        Button {
            id: buttonRegister
            x: 175
            y: 212
            text: qsTr("登记")
            enabled: false
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 60
            anchors.right: parent.right
            anchors.rightMargin: 50
            onClicked: {
                var Id = textField1.text;
                var Name = textField2.text;
                var Cid = textField3.text
                var Money = textField4.text
                var register = {
                    method: "register",
                    id: Id,
                    name: Name,
                    cid: Cid,
                    money: Money
                }
                socket.sendTextMessage(JSON.stringify(register));
            }
        }

        Button {
            id: buttonBack2
            x: 50
            y: 212
            text: qsTr("返回")
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 60
            anchors.left: parent.left
            anchors.leftMargin: 50
            onClicked: {
                scene_1.visible = true;
                scene_2.visible = false;
                scene_3.visible = false;
            }
        }
    }

    Item {
        id: scene_3
        visible: false
        anchors.fill: parent

        Label {
            id: labelID
            width: 75
            height: 23
            text: qsTr("客户编号")
            anchors.top: parent.top
            anchors.topMargin: 88
            anchors.left: parent.left
            anchors.leftMargin: 50
            verticalAlignment: Text.AlignVCenter
            horizontalAlignment: Text.AlignHCenter
        }

        Label {
            id: labelMoney
            width: 75
            height: 23
            text: qsTr("充值金额")
            anchors.top: labelID.bottom
            anchors.topMargin: 10
            anchors.left: parent.left
            anchors.leftMargin: 50
            verticalAlignment: Text.AlignVCenter
            horizontalAlignment: Text.AlignHCenter
        }

        TextField {
            id: textFieldID
            x: 260
            width: 125
            height: 23
            anchors.top: parent.top
            anchors.topMargin: 88
            anchors.right: parent.right
            anchors.rightMargin: 50
            onTextChanged: {
                if(textFieldID.text.trim().length > 0 && textFieldMoney.text.trim().length > 0)
                    buttonRecharge.enabled = true;
                else
                    buttonRecharge.enabled = false;
            }
        }

        TextField {
            id: textFieldMoney
            x: 260
            width: 125
            height: 23
            anchors.top: textFieldID.bottom
            anchors.topMargin: 10
            anchors.right: parent.right
            anchors.rightMargin: 50
            onTextChanged: {
                if(textFieldID.text.trim().length > 0 && textFieldMoney.text.trim().length > 0)
                    buttonRecharge.enabled = true;
                else
                    buttonRecharge.enabled = false;
            }
        }

        Button {
            id: buttonRecharge
            x: 175
            y: 212
            text: qsTr("充值")
            enabled: false
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 60
            anchors.right: parent.right
            anchors.rightMargin: 50
            onClicked: {
                var Id = textFieldID.text;
                var Money = textFieldMoney.text;
                var recharge = {
                    method: "recharge",
                    id: Id,
                    money: Money
                }
                socket.sendTextMessage(JSON.stringify(recharge));
            }
        }

        Button {
            id: buttonBack3
            x: 50
            y: 212
            text: qsTr("返回")
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 60
            anchors.left: parent.left
            anchors.leftMargin: 50
            onClicked: {
                scene_1.visible = true;
                scene_2.visible = false;
                scene_3.visible = false;
            }
        }
    }

    BusyIndicator {
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

    Window {
        id: reportWindow
        title: qsTr("详单")
        width: 640
        height: 480
        visible: false

        TextArea {
            id: textArea
            text: ""
            readOnly: true
            anchors.fill: parent
        }
    }
}
