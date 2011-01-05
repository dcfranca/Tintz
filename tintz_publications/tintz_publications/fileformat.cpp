#include "fileformat.h"

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
        bool wrongExt = false;
        int tryes = 0;
        do
        {
            if ( (!wrongExt && (fp->fileName().endsWith( ".cbr", Qt::CaseInsensitive ) || fp->fileName().endsWith( ".rar", Qt::CaseInsensitive )) ) || wrongExt )
            {
                if ( IsRar(fp) )
                    return TYPE_RAR;
                wrongExt = true;
                fp->seek(0);
            }
            if ( ( !wrongExt && (fp->fileName().endsWith( ".cbz", Qt::CaseInsensitive ) || fp->fileName().endsWith( ".zip", Qt::CaseInsensitive )) ) || wrongExt )
            {
                if ( IsZip(fp) )
                    return TYPE_ZIP;
                wrongExt = true;
                fp->seek(0);
            }
            if ( ( !wrongExt && (fp->fileName().endsWith( ".pdf", Qt::CaseInsensitive ))) || wrongExt )
            {
                if ( IsPdf(fp) )
                    return TYPE_PDF;
                wrongExt = true;
                fp->seek(0);
            }

            //Para imagem levar em consideração apenas a extensão
            if (  ( !wrongExt && (fp->fileName().endsWith( ".png", Qt::CaseInsensitive ) || fp->fileName().endsWith( ".gif", Qt::CaseInsensitive ) || fp->fileName().endsWith( ".jpg", Qt::CaseInsensitive )) ) )
                return TYPE_IMG;

            if ( ++tryes == 2 )
                break;

        } while(wrongExt); //Executa em loop para verificar se o arquivo possa estar nomeado com a extensão errada

        return TYPE_UNKNOWN;
    }

}
