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


private slots:
    void TestFileType();
};

#endif // TESTGUESSTYPE_H
