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

        switch( type )
        {
        case TYPE_RAR:
            PrepareRar();
            break;
        case TYPE_ZIP:
            PrepareZip();
            break;
        case TYPE_PDF:
            PreparePdf();
            break;
        case TYPE_IMG:
            PrepareImage();
            break;
        case TYPE_ERROR:
            std::cout << "Erro ao tentar descobrir tipo do arquivo" << std::endl;
            break;
        case TYPE_UNKNOWN:
            std::cout << "Formato de arquivo invalido" << std::endl;
            break;
        }

        if ( program.length() )
        {

            if ( process )
            {
                delete process;
                process = NULL;
            }

            process = new QProcess();

            //Change to use 7z, not Rar or ZIP
            connect( process, SIGNAL( finished(int, QProcess::ExitStatus) ), this, SLOT(Finished()) );
            connect( process, SIGNAL( readyReadStandardOutput() ), this, SLOT(ReadStandardOutput()) );
            connect( process, SIGNAL( error(QProcess::ProcessError) ), this, SLOT(Error(QProcess::ProcessError)) );

            process->start( program, parameters );
            process->waitForFinished();
        }

    }

    void ComicImages::Finished()
    {
        std::cout << "Processamento externo efetuado com sucesso: " << std::endl;

        fileName = RemoveSpecialChars( fileName );

        CreateThumbnailsForDir( QDir( tmpDir.toUtf8() ) );

        if ( process )
        {
            delete process;
            process = NULL;
        }
    }

    void ComicImages::ReadStandardOutput()
    {
        QByteArray out = process->readAllStandardOutput();

        if ( out.size() == 0 )
            return;

        out = out.split(EOF)[0];

        QImage img;
        img.fromData(out);

        if (img.isNull())
            return;

        QFileInfo inf(this->fileName);

        QString newFileName = tmpDir + QDir::separator() + inf.baseName() + "_" + "001.png";
        img.save( newFileName, "PNG" );

    }

    void ComicImages::CreateThumbnailsForDir( QDir dirName )
    {
        QStringList listFiles = dirName.entryList( QDir::NoDotAndDotDot|QDir::Dirs|QDir::Files, QDir::Name|QDir::LocaleAware );
        bool firstPage = true;

        QString fileName;
        int pageNo = 0;
        foreach( fileName, listFiles )
        {
            QString fullPath = dirName.absolutePath() + QDir::separator() + fileName;
            if ( QFileInfo(fullPath).isDir() )
                CreateThumbnailsForDir( QDir( fullPath.toUtf8() ) );
            else if ( IsImage(fileName) )
            {
                std::cout << "[" << fileName.toStdString() << "]" << std::endl;

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
        }
    }

    void ComicImages::CreateThumbnailForImage(QString fileName, int width, int height, int pageNo)
    {
        QImageReader img_reader(fileName);
        int img_width = img_reader.size().width();
        int img_height = img_reader.size().height();

        int widthDisplay = width;

        if ( img_width < width )
            width = img_width;
        height = ( width*img_height )/img_width;

        QFileInfo inf(this->fileName);

        img_reader.setScaledSize(QSize(width, height));
        QImage thumb = img_reader.read();
        QString newFileName = tmpDir + QDir::separator() + inf.baseName() + "_thumb" + QString().sprintf( "%03d", widthDisplay ) + "_" + QString().sprintf("%03d", pageNo) + ".png";
        thumb.save( newFileName, "PNG" );
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

    void ComicImages::PrepareImage()
    {
        QFileInfo fileInfo(fileName);
        QString baseName = fileInfo.baseName();
        QString dirName  = fileInfo.absoluteDir().absolutePath();
        tmpDir = dirName + QDir::separator() + baseName + "_" + QDateTime::currentDateTime().toString();

        if ( !QDir(tmpDir).exists() )
            QDir().mkdir( tmpDir );

        QString fullPath = tmpDir + QDir::separator() + fileName;

        //fileName = RemoveSpecialChars( fileName );

        //Full Viewer
        CreateThumbnailForImage( fullPath, 700, 1400, 1 );
        //Side Thumbnails
        CreateThumbnailForImage( fullPath, 64, 128, 1 );

        CreateThumbnailForImage( fullPath, 150, 200, 1 );
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
        //parameters.push_back( "-q" );
        //parameters.push_back( "-o" );
        parameters.push_back( "-p" );
        parameters.push_back( "-C" );
        parameters.push_back( fileName );
        //parameters.push_back( "-d" );
        //parameters.push_back( tmpDir );

        program = "/usr/bin/unzip";
    }

    void ComicImages::PreparePdf()
    {
        parameters.push_back( "-q" );
        parameters.push_back( "-dSAFER" );
        parameters.push_back( "-dBATCH" );
        parameters.push_back( "-dNOPAUSE" );
        parameters.push_back( "-sDEVICE=jpeg" );
        parameters.push_back( "-r150" );
        parameters.push_back( "-dTextAlphaBits=4" );
        parameters.push_back( "-sOutputFile="+tmpDir+QDir::separator()+QFileInfo( fileName ).baseName()+"_%03d.jpg" );
        parameters.push_back( fileName );

        program = "/usr/bin/gs";
    }

}
