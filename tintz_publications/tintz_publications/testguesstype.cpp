    #include "testguesstype.h"
#include "fileformat.h"
#include <iostream>

 using namespace tintz;


TestGuessType::TestGuessType(QObject *parent) :
    QObject(parent)
{
}

void TestGuessType::TestFileType()
{
    QFile* fpFileNames = new QFile("../tintz_publications/filenames.txt");

    fpFileNames->open(QIODevice::ReadOnly|QIODevice::Text);

    QVERIFY( fpFileNames->isOpen() );

    while( !fpFileNames->atEnd() )
    {
        QString line( fpFileNames->readLine( ) );
        QString fileName = line.left( line.size()-2 );
        QString typeFile = line.right(2);

        FILETYPE typeCompare = TYPE_UNKNOWN;

        if ( typeFile.compare( "R\n" ) == 0 )
            typeCompare = TYPE_RAR;
        else if ( typeFile.compare( "Z\n" ) == 0 )
            typeCompare = TYPE_ZIP;
        else if ( typeFile.compare( "P\n" ) == 0 )
            typeCompare = TYPE_PDF;
        else if ( typeFile.compare( "I\n" ) == 0 )
            typeCompare = TYPE_IMG;

        FILETYPE realType = FileFormat::GetFileTypeFromData( fileName );
        QCOMPARE( realType, typeCompare );
    }

    fpFileNames->close();
}


