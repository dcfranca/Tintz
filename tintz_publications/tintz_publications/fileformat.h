#ifndef FILEFORMAT_H
#define FILEFORMAT_H

#include <QFile>

namespace tintz {
    typedef enum {
        TYPE_ERROR = -1,
        TYPE_UNKNOWN,
        TYPE_RAR,
        TYPE_ZIP,
        TYPE_PDF,
        TYPE_IMG
    } FILETYPE;

    class FileFormat
    {
    public:
        FileFormat(){}
        virtual ~FileFormat();

        static FILETYPE GuessType( QFile* fp );

        static bool IsRar( QFile* fp );
        static bool IsZip( QFile* fp );
        static bool IsPdf( QFile* fp );
    };
}

#endif // FILEFORMAT_H
