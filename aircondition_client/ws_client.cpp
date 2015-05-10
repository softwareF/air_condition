#include "ws_client.h"
#include <QtCore/QDebug>

QT_USE_NAMESPACE

ws_client::ws_client(const QUrl &url, bool debug, QObject *parent) :
    QObject(parent),
    m_url(url),
    m_debug(debug)
{
    if (m_debug)
        qDebug() << "WebSocket server:" << url;
    connect(&m_webSocket, &QWebSocket::connected, this, &ws_client::onConnected);
    connect(&m_webSocket, &QWebSocket::disconnected, this, &ws_client::closed);
    m_webSocket.open(QUrl(url));
}

void ws_client::onConnected()
{
    if (m_debug)
        qDebug() << "WebSocket connected";
    connect(&m_webSocket, &QWebSocket::textMessageReceived,
            this, &ws_client::onTextMessageReceived);
    m_webSocket.sendTextMessage(QStringLiteral("Hello, world!"));
}

void ws_client::onTextMessageReceived(QString message)
{
    if (m_debug)
        qDebug() << "Message received:" << message;
    m_webSocket.close();
}
