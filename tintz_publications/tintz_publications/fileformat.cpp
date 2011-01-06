#include "fileformat.h"
#include <iostream>

namespace tintz {

    bool FileFormat::IsRar( QFile* fp )
    {
        char header[7];
        fp->read(header,7);
        return ( *((short*)header) == 0x6152 && header[2] == 0x72 );
    }

    bool FileFormat::IsZip( QFile* fp )
    {
        char header[4];
        fp->read(header,4);
        return ( *((int*)header) == 0x04034b50 );
    }

    bool FileFormat::IsPdf( QFile* fp )
    {
        char header[5];
        memset(header, 0x00, 5);
        fp->read(header,4);

        return ( strcmp( header,"%PDF" ) == 0 );
    }

    /***
      Adivinha o formato de arquivo de acordo com seu conteúdo ou extensão
      Guess file type from its data content or extension
      ***/
    FILETYPE FileFormat::GuessType(QFile *fp)
    {
        for ( int tryes=0; tryes<2; tryes++ )
        {
            if ( (!tryes && (fp->fileName().endsWith( ".cbr", Qt::CaseInsensitive ) || fp->fileName().endsWith( ".rar", Qt::CaseInsensitive )) ) || tryes )
            {
                if ( IsRar(fp) )
                    return TYPE_RAR;
                fp->seek(0);
            }
            if ( ( !tryes && (fp->fileName().endsWith( ".cbz", Qt::CaseInsensitive ) || fp->fileName().endsWith( ".zip", Qt::CaseInsensitive )) ) || tryes )
            {
                if ( IsZip(fp) )
                    return TYPE_ZIP;
                fp->seek(0);
            }
            if ( ( !tryes && (fp->fileName().endsWith( ".pdf", Qt::CaseInsensitive ))) || tryes )
            {
                if ( IsPdf(fp) )
                    return TYPE_PDF;
                fp->seek(0);
            }

            //Para imagem levar em consideração apenas a extensão
            if (  ( !tryes && (fp->fileName().endsWith( ".png", Qt::CaseInsensitive ) || fp->fileName().endsWith( ".gif", Qt::CaseInsensitive ) || fp->fileName().endsWith( ".jpg", Qt::CaseInsensitive )) ) )
                return TYPE_IMG;

            //File with wrong Extension
        }

        return TYPE_UNKNOWN;
    }

    FILETYPE FileFormat::GetFileTypeFromData(QString fileName)
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

}
