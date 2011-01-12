#-------------------------------------------------
#
# Project created by QtCreator 2011-01-05T14:04:02
#
#-------------------------------------------------

QT       += core

QT       += gui

TARGET = tintz
TEMPLATE = lib
#TEMPLATE = app
DEFINES += TINTZ_LIBRARY

CONFIG   += qtestlib

SOURCES += main.cpp \
    fileformat.cpp \
    testguesstype.cpp \
    comicimages.cpp \
    testcomicimages.cpp

HEADERS += \
    fileformat.h \
    testguesstype.h \
    comicimages.h \
    testcomicimages.h

OTHER_FILES += \
    filenames.txt \
    temp.txt
