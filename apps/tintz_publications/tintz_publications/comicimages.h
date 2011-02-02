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
        QString fullPathFileName;
        
        int nrPages;
        
    public:
        ComicImages(QString fileName){this->fileName = fileName; this->nrPages = 0; fullPathFileName.clear();  process = NULL;}
        virtual ~ComicImages(){}

        QString Program(){ return program; }
        bool RunCommand( FILETYPE type );

        void CreateThumbnailsForDir( QDir dirName );
        void CreateThumbnailForImage( QString fileName, int width=150, int height=200, int pageNo = 1 );
        void CreateThumbnailForImage( QImageReader* imgReader, int width, int height, int pageNo);
        void RemoveSpecialChars(QString& str);
        bool IsImage( QString fileName );

        void PrepareImage();
        void Prepare7z();
        void PreparePdf();
        
        int NrPages(){return nrPages;}
        QString FullPathFileName(){return fullPathFileName;}

    public slots:
        void Finished(int exitCode);
        void Error(QProcess::ProcessError error);
    };

}

#endif // COMICMAGES_H
