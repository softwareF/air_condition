#include <QtCore/QCoreApplication>
#include <QtCore/QCommandLineParser>
#include <QtCore/QCommandLineOption>
#include "ws_server.h"

int main(int argc, char *argv[])
{
    QCoreApplication a(argc, argv);

    QCommandLineParser parser;
    parser.setApplicationDescription("QTwebSockets server:");
    parser.addHelpOption();

    QCommandLineOption dbgOption(QStringList() << "d" << "debug", QCoreApplication::translate("mina","Debug output [default:off]."));
    parser.addOption(dbgOption);
    QCommandLineOption portOption(QStringList() << "p" << "port",QCoreApplication::translate("main","Port for server [default:1234]."),
                                  QCoreApplication::translate("main","port"),QLatin1Literal("1234"));
    parser.addOption(portOption);
    parser.process(a);
    bool debug = parser.isSet(dbgOption);
    int port = parser.value(portOption).toInt();

    ws_server *server = new ws_server(port,debug);
    QObject::connect(server,&ws_server::closed,&a,&QCoreApplication::quit);

    return a.exec();
}
