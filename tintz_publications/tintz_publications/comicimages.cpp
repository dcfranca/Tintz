#include "comicimages.h"
#include <QFileInfo>
#include <QDateTime>
#include <iostream>
#include <QDir>
#include <Qt/qimagereader.h>
#include <Qt/qimage.h>

namespace tintz
{

    void ComicImages::RunCommand(FILETYPE type)
    {
        QFileInfo fileInfo(fileName);
        QString baseName = fileInfo.baseName();
        QString dirName  = fileInfo.absoluteDir().absolutePath();
        tmpDir = dirName + QDir::separator() + baseName + "_" + QDateTime::currentDateTime().toString();

        if ( !QDir(tmpDir).exists() )
            QDir().mkdir( tmpDir );

        program.clear();

        if ( type == TYPE_RAR )
            PrepareRar();
        else if ( type == TYPE_ZIP )
            PrepareZip();
        else if ( type == TYPE_PDF )
            PreparePdf();

        if ( program.length() )
        {

            if ( process )
                delete process;

            process = new QProcess();

            connect( process, SIGNAL( started() ), this, SLOT(Started()) );
            connect( process, SIGNAL( finished(int, QProcess::ExitStatus) ), this, SLOT(Finished()) );
            connect( process, SIGNAL( error(QProcess::ProcessError) ), this, SLOT(Error(QProcess::ProcessError)) );

            process->start( program, parameters );
            process->waitForFinished();
        }

    }

    void ComicImages::Started()
    {
        std::cout << "Processamento iniciado com sucesso: " << std::endl;
    }

    void ComicImages::Finished()
    {
        std::cout << "Processamento externo efetuado com sucesso: " << std::endl;

        CreateThumbnailsForDir( QDir( tmpDir ) );

        if ( process )
        {
            delete process;
            process = NULL;
        }
    }

    void ComicImages::CreateThumbnailsForDir( QDir dirName )
    {
        QStringList listFiles = dirName.entryList( QDir::NoDotAndDotDot|QDir::Dirs|QDir::Files, QDir::Name );
        bool firstPage = true;

        QString fileName;
        foreach( fileName, listFiles )
        {
            QString fullPath = dirName.absolutePath() + QDir::separator() + fileName;
            if ( QFileInfo(fullPath).isDir() )
                CreateThumbnailsForDir( QDir( fullPath ) );
            else if ( IsImage(fileName) )
            {
                std::cout << "[" << fileName.toStdString() << "]" << std::endl;

                /**Create thumbnails - Gerar thumbnails**/

                //Full Viewer
                CreateThumbnailForImage( fullPath, 700, 1400 );

                //Side Thumbnails
                CreateThumbnailForImage( fullPath, 64, 128 );

                //Cover of the comic
                if ( firstPage )
                {
                    CreateThumbnailForImage( fullPath, 150, 200 );
                    firstPage = false;
                }
            }
        }
    }

    void ComicImages::CreateThumbnailForImage(QString fileName, int width, int height)
    {
        QImageReader img_reader(fileName);
        int img_width = img_reader.size().width();
        int img_height = img_reader.size().height();

        if ( img_width > img_height )
        {
            img_height = static_cast<double>( width )/ img_width * img_height;
            img_width = width;
        }
        else if ( img_height > img_width )
        {
            img_height = static_cast<double>( height )/ img_height * img_width;
            img_height = height;
        }
        else
        {
            img_width = width;
            img_height = height;
        }

        QFileInfo inf(fileName);

        img_reader.setScaledSize(QSize(img_width, img_height));
        QImage thumb = img_reader.read();
        QString newFileName = inf.absoluteDir().absolutePath() + QDir::separator() + inf.baseName() + "_" + QString().sprintf( "%03d", width ) + "." + inf.suffix();
        thumb.save( newFileName, "JPG" );
    }

    bool ComicImages::IsImage(QString fileName)
    {
        return ( fileName.endsWith(".jpg", Qt::CaseInsensitive) || fileName.endsWith(".png", Qt::CaseInsensitive) ||
             fileName.endsWith(".gif", Qt::CaseInsensitive));
    }

    QString ComicImages::RemoveSpecialChars(QString str)
    {
        return str.replace("-","_").replace("#","_");
    }

    void ComicImages::Error(QProcess::ProcessError error)
    {
        std::cout << "Erro ao processar imagens: " << error << std::endl;
        if ( process )
        {
            delete process;
            process = NULL;
        }
    }

    void ComicImages::PrepareRar()
    {
        parameters.push_back( "e" ); //Extraia - Extract
        parameters.push_back( "-c-" ); //Nao mostre comentários - Disable comments show
        parameters.push_back( "-y" ); //Sim para tudo - Yes for all
        parameters.push_back( "-p-" ); //Sem perguntar por password - Don't ask for password
        parameters.push_back( fileName );
        parameters.push_back( tmpDir );

        program = "/usr/bin/unrar";

    }

    void ComicImages::PrepareZip()
    {
        parameters.push_back( fileName );
        parameters.push_back( "-d" );
        parameters.push_back( tmpDir );

        program = "/usr/bin/unzip";
    }

    void ComicImages::PreparePdf()
    {
        //TODO: Implement
    }

}
