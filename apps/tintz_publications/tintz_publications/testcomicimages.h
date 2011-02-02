#ifndef TESTCOMICIMAGES_H
#define TESTCOMICIMAGES_H

#include <QObject>

class TestComicImages : public QObject
{
    Q_OBJECT
public:
    explicit TestComicImages(QObject *parent = 0);

private slots:
    void TestRun();

};

#endif // TESTCOMICIMAGES_H
