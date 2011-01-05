#ifndef TESTGUESSTYPE_H
#define TESTGUESSTYPE_H

#include <QObject>
#include <Qt/QtTest>
#include "fileformat.h"

class TestGuessType : public QObject
{
    Q_OBJECT
public:
    explicit TestGuessType(QObject *parent = 0);

signals:

private slots:
    void TestFileType();
    tintz::FILETYPE GetFileTypeFromData(QString fileName);
};

#endif // TESTGUESSTYPE_H
