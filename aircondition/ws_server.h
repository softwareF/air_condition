#ifndef WS_SERVER_H
#define WS_SERVER_H
#include <QObject>
#include <QList>
#include <QByteArray>

QT_FORWARD_DECLARE_CLASS(QWebSocketServer)
QT_FORWARD_DECLARE_CLASS(QWebSocket)

class ws_server : public QObject
{
    Q_OBJECT
public:
    explicit ws_server(quint16 port, bool debug = false, QObject *parent = Q_NULLPTR);
    ~ws_server();

Q_SIGNALS:
    void closed();

private Q_SLOTS:
    void onNewConnection();
    void processTextMessage(QString message);
    void processBinaryMessage(QByteArray message);
    void socketDisconnected();

private:
    QWebSocketServer *m_pWebSocketServer;
    QList<QWebSocket *> m_clients;
    bool m_debug;
};

#endif // WS_SERVER_H
