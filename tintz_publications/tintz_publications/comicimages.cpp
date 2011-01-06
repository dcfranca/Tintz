#include "comicimages.h"
#include <QFileInfo>
#include <QDateTime>
#include <iostream>
#include <QDir>

namespace tintz
{

    void ComicImages::RunCommand(FILETYPE type)
    {
        QFileInfo fileInfo(fileName);
        QString baseName = fileInfo.baseName();
        QString dirName  = fileInfo.absoluteDir().absolutePath();
        tmpDir = dirName + QDir::separator() + baseName + QDateTime::currentDateTime().toString();

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
        std::cout << "Processamento efetuado com sucesso: " << std::endl;
        //TODO: Implement
        if ( process )
        {
            delete process;
            process = NULL;
        }
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
