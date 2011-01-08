#ifndef COMICIMAGES_H
#define COMICIMAGES_H

#include <QString>
#include <QStringList>
#include <QObject>
#include <QProcess>
#include <QDir>
#include "fileformat.h"

namespace tintz {

    class ComicImages : public QObject
    {
        Q_OBJECT
    private:
        QString program;
        QString tmpDir;
        QString fileName;
        QProcess* process;

        QStringList parameters;

    public:
        ComicImages(QString fileName){this->fileName = fileName;  process = NULL;}
        virtual ~ComicImages(){}

        QString Program(){ return program; }
        void RunCommand( FILETYPE type );

        void CreateThumbnailsForDir( QDir dirName );
        void CreateThumbnailForImage( QString fileName, int width=150, int height=200 );
        QString RemoveSpecialChars(QString str);
        bool IsImage( QString fileName );

        void PrepareRar();
        void PrepareZip();
        void PreparePdf();

    public slots:
        void Started();
        void Finished();
        void Error(QProcess::ProcessError error);
    };

}

#endif // COMICMAGES_H
