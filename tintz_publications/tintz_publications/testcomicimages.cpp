#include <iostream>

#include <Qt/QtTest>

#include "testcomicimages.h"
#include "comicimages.h"
#include "fileformat.h"

using namespace tintz;

TestComicImages::TestComicImages(QObject *parent) :
    QObject(parent)
{
}

void TestComicImages::TestRun()
{

    //QFile* fpFileNames = new QFile("../tintz_publications/filenames.txt");
    QFile* fpFileNames = new QFile("../tintz_publications/temp.txt");

    fpFileNames->open(QIODevice::ReadOnly|QIODevice::Text);

    QVERIFY( fpFileNames->isOpen() );

    while( !fpFileNames->atEnd() )
    {
        QString line( QString::fromUtf8( fpFileNames->readLine( ) ) );

        if ( line.startsWith( "#" ) )
            continue;

        QString fileName = line.left( line.size()-2 );

        FILETYPE realType = FileFormat::GetFileTypeFromData( fileName );

        ComicImages comic( fileName );

        comic.RunCommand(realType);
    }

    fpFileNames->close();
}
