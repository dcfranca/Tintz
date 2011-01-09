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
    QFile* fpFileNames = new QFile("../tintz_publications/filenames.txt");

    fpFileNames->open(QIODevice::ReadOnly|QIODevice::Text);

    QVERIFY( fpFileNames->isOpen() );

    while( !fpFileNames->atEnd() )
    {
        QString line( fpFileNames->readLine( ) );

        if ( line.startsWith( "#" ) )
            continue;

        QString fileName = line.left( line.size()-2 );

        FILETYPE realType = FileFormat::GetFileTypeFromData( fileName );

        ComicImages comic( fileName );

        comic.RunCommand(realType);
    }

    fpFileNames->close();
}
