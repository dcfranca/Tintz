#ifndef COMICIMAGES_H
#define COMICIMAGES_H

#include <QString>
#include <QStringList>
#include <QObject>
#include <QProcess>
#include <QDir>
#include <QtAlgorithms>
#include <QImageReader>
#include "fileformat.h"

namespace tintz {
    
    struct Page {
        QString fileName;
        long fileSize;
        int pageNo;
        
        bool operator <( const Page& other ) const
        {
            return this->pageNo < other.pageNo;
        }
        
    };

    class ComicImages : public QObject
    {
        Q_OBJECT
    private:
        QString program;
        QString tmpDir;
        QString fileName;
        QProcess* process;
        QProcess* process7z;
        QStringList parameters;
        
        QList<Page> pages;

    public:
        ComicImages(QString fileName){this->fileName = fileName;  process = NULL;}
        virtual ~ComicImages(){}

        QString Program(){ return program; }
        bool RunCommand( FILETYPE type );

        void CreateThumbnailsForDir( QDir dirName );
        void CreateThumbnailForImage( QString fileName, int width=150, int height=200, int pageNo = 1 );
        void CreateThumbnailForImage( QImageReader* imgReader, int width, int height, int pageNo);
        QString RemoveSpecialChars(QString str);
        bool IsImage( QString fileName );

        void PrepareImage();
        void Prepare7z();
        void PreparePdf();

    public slots:
        void Finished();
        void Error(QProcess::ProcessError error);
    };

}

#endif // COMICMAGES_H
