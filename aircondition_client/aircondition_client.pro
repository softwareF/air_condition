#-------------------------------------------------
#
# Project created by QtCreator 2015-05-10T22:00:06
#
#-------------------------------------------------

QT       += core websockets

QT       -= gui

TARGET = aircondition_client
CONFIG   += console
CONFIG   -= app_bundle

TEMPLATE = app


SOURCES += main.cpp \
    ws_client.cpp

HEADERS += \
    ws_client.h
