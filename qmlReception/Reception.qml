import QtQuick 2.4
import QtQuick.Controls 1.3
import QtQuick.Window 2.2
import QtQuick.Dialogs 1.2
import Qt.WebSockets 1.0

Window {
    id: window1
    title: qsTr("Reception")
    width: 300
    height: 300

    WebSocket {
        id: socket
        url: "ws://localhost:6666/"

        onTextMessageReceived: {
            console.debug("Receive: " + message);
            var msg = JSON.parse(message);
            switch(msg.method){
            case "checkout":
                if(msg.result === "ok"){
                    messageDialog.show(qsTr("操作成功！"), StandardIcon.Information);
                } else {
                    messageDialog.show(qsTr("操作失败！"), StandardIcon.Warning);
                }
                break;
            case "report":
                textArea.text = "";
                for(var i = 0; i < msg.data.length; ++i){
                    textArea.append(msg.data[i]);
                }
                reportWindow.setVisible(true);
                break;
            }
        }
        onStatusChanged: {
            console.debug(socket.status);
            if(socket.status != WebSocket.Connecting && socket.status != WebSocket.Open)
                Qt.quit();
        }
        active: true
    }

    Label {
        id: labelID
        x: 50
        y: 84
        width: 75
        height: 23
        text: qsTr("Client ID")
        verticalAlignment: Text.AlignVCenter
        horizontalAlignment: Text.AlignHCenter
    }

    TextField {
        id: input
        x: 131
        y: 84
        width: 125
        height: 23
        font.pointSize: 10
        horizontalAlignment: Text.AlignLeft
        focus: true
    }

    Button {
        id: button1
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
        id: button2
        x: 174
        y: 182
        text: qsTr("查看详单")
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
        title: qsTr("Report")
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

    BusyIndicator {
        z: 1
        anchors.fill: parent
        anchors.margins: 60
        running: socket.status == WebSocket.Connecting || socket.status == WebSocket.Closing
    }
}
