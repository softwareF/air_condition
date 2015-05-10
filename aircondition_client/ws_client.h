#ifndef WS_CLIENT_H
#define WS_CLIENT_H
#include <QtCore/QObject>
#include <QtWebSockets/QWebSocket>

class ws_client : public QObject
{
    Q_OBJECT
public:
    explicit ws_client(const QUrl &url, bool debug = false, QObject *parent = Q_NULLPTR);

Q_SIGNALS:
    void closed();

private Q_SLOTS:
    void onConnected();
    void onTextMessageReceived(QString message);

private:
    QWebSocket m_webSocket;
    QUrl m_url;
    bool m_debug;
};

#endif // WS_CLIENT_H
