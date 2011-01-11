#include "comicimages.h"
#include <QFileInfo>
#include <QDateTime>
#include <iostream>
#include <QDir>
#include <QImage>

#define EXTENSIONS << "*.jpg" << "*.jpeg" << "*.png" << "*.gif" << "*.tiff" << "*.tif" << "*.bmp"

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
            break;
        case TYPE_UNKNOWN:
            std::cout << "Formato de arquivo invalido" << std::endl;
            break;
        }

        if ( program.length() )
        {

            process = new QProcess();

            connect( process, SIGNAL( finished(int, QProcess::ExitStatus) ), this, SLOT(Finished()) );
            //connect( process, SIGNAL( readyReadStandardOutput() ), this, SLOT(ReadStandardOutput()) );
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

    /*********************************
      Load file sizes according to 
      7z infos
      *******************************/
    void ComicImages::LoadSizes()
    {
        QRegExp reg("[0-9]{4}-[0-9]{2}-[0-9]{2}[ ]+[0-9]{2}:[0-9]{2}:[0-9]{2}[ ]+.{5}[ ]+([0-9]+)[ ]+([0-9]+)[ ]+(.+)");

        QByteArray out = process->readAllStandardOutput();
        QList<QByteArray> lines = out.split('\n');
        QByteArray line;
        
        pages.clear();
        
        foreach(line,lines)
        {
                if(reg.indexIn(QString(line))!=-1)
                {       
                    Page pg;
                    pg.fileSize = reg.cap(1).toInt();
                    pg.fileName = reg.cap(3).trimmed();
                    
                    pages.push_back( pg );
                }
        }
        if(pages.size()==0)
            return;

        //sort?        
        
        //qSort( pages.begin(), pages.end() );
        
        process7z = new QProcess();
        
        Prepare7z();        
        
        connect(process7z,SIGNAL(error(QProcess::ProcessError)),this,SLOT(Error(QProcess::ProcessError)));
        connect(process7z,SIGNAL(readyReadStandardOutput()),this,SLOT(LoadImages()));
        connect(process7z,SIGNAL(finished(int,QProcess::ExitStatus)),this,SLOT(LoadFinished(void)));
        process7z->start(program,parameters);
        
        process7z->waitForFinished();
    }
    
    /*******************************************
      Load Images from STDOUT
      *****************************************/
    void ComicImages::LoadImages()
    {
        QByteArray out = process7z->readAllStandardOutput();
        int ind = 0;        
        while(out.size()>0)
        {
            int offset = pages[ind].fileSize;
            QByteArray bytesImage = out.left( offset );
            QImage img;
            img.fromData( bytesImage );
            
            QFileInfo inf( fileName );
            QString newFileName = tmpDir + QDir::separator() + inf.baseName() + "_" + "001.png";
            
            if ( img.isNull() )
                std::cerr << "Imagem invalida para o arquivo: " << pages[ind].fileName.toStdString() << std::endl;
            else if ( !img.save( newFileName, "PNG" ) )
                std::cerr << "Erro ao salvar imagem: " << pages[ind].fileName.toStdString() << std::endl;
            
            out.remove( 0, pages[ind++].fileSize );
        }           

    }
    
    void ComicImages::LoadFinished()
    {
        std::cout << "Processamento finalizado com sucesso" << std::endl;
        
        if (process7z)
        {
            delete process7z;
            process7z = NULL;
        }        
    }

    void ComicImages::ReadStandardOutput()
    {
        /*QByteArray out = process->readAllStandardOutput();

        if ( out.size() == 0 )
            return;

        out = out.split(EOF)[0];

        QImage img;
        img.fromData(out);

        if (img.isNull())
            return;

        QFileInfo inf(this->fileName);

        QString newFileName = tmpDir + QDir::separator() + inf.baseName() + "_" + "001.png";
        img.save( newFileName, "PNG" );*/

    }

    /*********************************************************
      Creating thumbnails for images in dirname, recursive
      *******************************************************/
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
        parameters.clear();
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
        parameters.clear();
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
        parameters.clear();
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

    void ComicImages::Prepare7zSizes()
    {
        parameters.clear();
        parameters << "l" << "-ssc-" << "-r" << fileName EXTENSIONS;        
        program = "/usr/bin/7z";
    }

    void ComicImages::Prepare7z()
    {
        parameters.clear();
        parameters.push_back( "e" );
        parameters.push_back( "-ssc-" );
        parameters.push_back( "-o"+tmpDir );
        parameters << fileName EXTENSIONS;
        program = "/usr/bin/7z";
    }
}
