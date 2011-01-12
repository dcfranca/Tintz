#include "comicimages.h"

#include <QFileInfo>
#include <QDateTime>
#include <iostream>
#include <QDir>
#include <QImage>
#include <QWaitCondition>
#include <QMutex>

namespace tintz
{

    bool ComicImages::RunCommand(FILETYPE type)
    {        
        QFileInfo fileInfo(fileName);
        QString baseName = fileInfo.baseName();
        QString dirName  = fileInfo.absoluteDir().absolutePath();
        tmpDir = dirName + QDir::separator() + baseName + "_" + QDateTime::currentDateTime().toString();
        RemoveSpecialChars(tmpDir);

        if ( !QDir(tmpDir).exists() )
            QDir().mkdir( tmpDir );

        program.clear();

        switch( type )
        {
        case TYPE_RAR:
        case TYPE_ZIP:
            Prepare7z();
            break;
        case TYPE_PDF:
            PreparePdf();
            break;
        case TYPE_IMG:
            PrepareImage();
            break;
        case TYPE_ERROR:
            std::cerr << "Erro ao tentar descobrir tipo do arquivo" << std::endl;
            return false;
        case TYPE_UNKNOWN:
            std::cout << "Formato de arquivo invalido" << std::endl;
            return false;
        }

        if ( program.length() )
        {
            if ( process )
                delete process;
            
            process = new QProcess();

            connect( process, SIGNAL( finished(int, QProcess::ExitStatus) ), this, SLOT(Finished(int)) );
            connect( process, SIGNAL( error(QProcess::ProcessError) ), this, SLOT(Error(QProcess::ProcessError)) );
            
            process->start( program, parameters );
            process->waitForFinished(100000);
        }
        
        if ( process )
        {
            delete process;
            process = NULL;
        }
        
        return true;

    }

    void ComicImages::Finished(int exitCode)
    {
        std::cout << "Processamento externo com retorno:" << exitCode << std::endl;

        RemoveSpecialChars( fileName );
        CreateThumbnailsForDir( QDir( tmpDir ) );
    }

    /*********************************************************
      Creating thumbnails for images in dirname, recursive
      *******************************************************/
    void ComicImages::CreateThumbnailsForDir( QDir dirName )
    {
        QStringList listFiles = dirName.entryList( QDir::NoDotAndDotDot|QDir::Dirs|QDir::Files, QDir::Name|QDir::LocaleAware );
        bool firstPage = true;
        
        std::cout << "Thumbnails para Dir: [" <<  dirName.absolutePath().toStdString() << "]" << std::endl;

        QString fileName;
        int pageNo = 0;
        foreach( fileName, listFiles )
        {
            QString fullPath = dirName.absolutePath() + QDir::separator() + fileName;
            if ( QFileInfo(fullPath).isDir() )
                CreateThumbnailsForDir( QDir( fullPath.toUtf8() ) );
            else if ( IsImage(fileName) )
            {
                //std::cout << "[" << fileName.toStdString() << "]" << std::endl;

                /**Create thumbnails - Gerar thumbnails**/

                pageNo++;

                //Full Viewer
                CreateThumbnailForImage( fullPath, 700, 1400, pageNo );

                //Side Thumbnails
                CreateThumbnailForImage( fullPath, 64, 128, pageNo );

                //Cover of the comic
                if ( firstPage )
                {
                    CreateThumbnailForImage( fullPath, 150, 200, pageNo );
                    firstPage = false;
                }
            }
            
            QFile::remove( fileName );
        }
        
        if (pageNo)
            std::cerr << pageNo << " imagens encontradas para " << this->fileName.toStdString() << std::endl;
        else
            std::cerr << "Nenhuma imagem encontrada no diretório [" << dirName.absolutePath().toStdString() << "]" << std::endl;
    }

    /*********************************************************************************************
      Create thumbnail for image fileName or QImage
      ********************************************************************************************/
    void ComicImages::CreateThumbnailForImage(QString fileName, int width, int height, int pageNo)
    {
        QImageReader imgReader(fileName);
        
        CreateThumbnailForImage(&imgReader, width, height, pageNo);
    }

    void ComicImages::CreateThumbnailForImage(QImageReader* imgReader, int width, int height, int pageNo)
    {
        int imgWidth = imgReader->size().width();
        int imgHeight = imgReader->size().height();

        int widthDisplay = width;

        if ( imgWidth < width )
            width = imgWidth;
        height = ( width*imgHeight )/imgWidth;

        QFileInfo inf(this->fileName);

        imgReader->setScaledSize(QSize(width, height));
        QImage thumb = imgReader->read();
        QString newFileName = tmpDir + QDir::separator() + inf.baseName() + "_thumb" + QString().sprintf( "%03d", widthDisplay ) + "_" + QString().sprintf("%03d", pageNo) + ".jpg";
        thumb.save( newFileName, "JPG" );
    }

    bool ComicImages::IsImage(QString fileName)
    {
        return ( fileName.endsWith(".jpg", Qt::CaseInsensitive) || fileName.endsWith(".png", Qt::CaseInsensitive) ||
             fileName.endsWith(".gif", Qt::CaseInsensitive));
    }

    void ComicImages::RemoveSpecialChars(QString& str)
    {
        str.replace("-","_").replace("#","_");
    }

    void ComicImages::Error(QProcess::ProcessError error)
    {
        std::cerr << "Erro ao processar imagens: " << error << std::endl;
        if ( process )
        {
            delete process;
            process = NULL;
        }
    }
    
    void ComicImages::PrepareImage()
    {
        QFileInfo fileInfo(fileName);
        QString baseName = fileInfo.baseName();
        QString dirName  = fileInfo.absoluteDir().absolutePath();
        tmpDir = dirName + QDir::separator() + baseName + "_" + QDateTime::currentDateTime().toString();
     
        if ( !QDir(tmpDir).exists() )
            QDir().mkdir( tmpDir );

        //QString fullPath = tmpDir + QDir::separator() + fileName;

        //fileName = RemoveSpecialChars( fileName );

        //Full Viewer
        CreateThumbnailForImage( fileName, 700, 1400, 1 );
        //Side Thumbnails
        CreateThumbnailForImage( fileName, 64, 128, 1 );

        CreateThumbnailForImage( fileName, 150, 200, 1 );
    }

    void ComicImages::PreparePdf()
    {
        parameters.clear();
        parameters << "-q" << "-dSAFER" << "-dBATCH" << "-dNOPAUSE" << "-sDEVICE=jpeg" << "-r150" << "-dTextAlphaBits=4";
        parameters << "-sOutputFile="+tmpDir+QDir::separator()+QFileInfo( fileName ).baseName()+"_%03d.jpg" << fileName;
        program = "/usr/bin/gs";
    }

    void ComicImages::Prepare7z()
    {
        parameters.clear();
        parameters << "e" << "-y" << "-ssc-" << "-o"+tmpDir << fileName;
        program = "/usr/bin/7z";
    }
}
