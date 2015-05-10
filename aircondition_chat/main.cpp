#include <QtCore/QCoreApplication>
#include "chatserver.h"

int main(int argc, char *argv[])
{
    QCoreApplication a(argc, argv);
    ChatServer server(1234);

    return a.exec();
}
