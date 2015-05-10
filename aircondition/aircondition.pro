#-------------------------------------------------
#
# Project created by QtCreator 2015-05-10T21:03:04
#
#-------------------------------------------------

QT       += core websockets

QT       -= gui

TARGET = aircondition
CONFIG   += console
CONFIG   -= app_bundle

TEMPLATE = app


SOURCES += main.cpp \
    ws_server.cpp

HEADERS += \
    ws_server.h
