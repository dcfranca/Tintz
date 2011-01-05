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
    FILETYPE type;
    type = GetFileTypeFromData( "/home/danielfranca/Downloads/Homem Aranha.pdf" );
    QCOMPARE( type, TYPE_PDF );

    type = GetFileTypeFromData( "/home/danielfranca/Downloads/PDFSPEC.pDF" );
    QCOMPARE( type, TYPE_PDF );

    type = GetFileTypeFromData( "/home/danielfranca/Downloads/Star_Wars_-_Blood_Ties_03__2010___GreenGiant-DCP_.cbr" );
    QCOMPARE( type, TYPE_RAR );

    type = GetFileTypeFromData( "/home/danielfranca/Downloads/Velocity_01__Jun_2010_Image_-_Cover_B___noads___OllietheOx___Archangel_.cbr" );
    QCOMPARE( type, TYPE_RAR );

    type = GetFileTypeFromData( "/home/danielfranca/Downloads/na_verdade_eh_rar.cbz" );
    QCOMPARE( type, TYPE_RAR );

    type = GetFileTypeFromData( "/home/danielfranca/Downloads/Gen13_38__2010___Minutemen-TwiztiD-T_.cbz" );
    QCOMPARE( type, TYPE_ZIP );

    type = GetFileTypeFromData( "/home/danielfranca/Downloads/pyUnRAR2-0.99.2.zip" );
    QCOMPARE( type, TYPE_ZIP );

    type = GetFileTypeFromData( "/home/danielfranca/Downloads/na_verdade_eh_zip.cbr" );
    QCOMPARE( type, TYPE_ZIP );

    type = GetFileTypeFromData( "/home/danielfranca/Downloads/papai-noel-malvado.jpg" );
    QCOMPARE( type, TYPE_IMG );

    type = GetFileTypeFromData( "/home/danielfranca/Downloads/Snoopy-Comic-Strip-peanuts-256343.GiF" );
    QCOMPARE( type, TYPE_IMG );

}

FILETYPE TestGuessType::GetFileTypeFromData(QString fileName)
{
    std::cout << "\nArquivo: " << fileName.toStdString() << std::endl;

    QFile* fp = new QFile(fileName);

    if ( !fp->open( QFile::ReadOnly ) )
    {
        std::cout << "\nErro ao abrir o arquivo: " << fileName.toStdString() << std::endl;
        return TYPE_ERROR;
    }

    FILETYPE fileType = FileFormat::GuessType( fp );

    fp->close();

    return fileType;
}
