//Qt Headers
#include <QFile>
#include <Qt/QtTest>
#include <QString>

//Test headers
#include "testguesstype.h"
#include "testcomicimages.h"

//C/C++ standard headers
#include <iostream>
#include <cwchar>

//Tintz headers
#include "fileformat.h"
#include "comicimages.h"

//Python interface header
#include <python2.6/Python.h>

using namespace tintz;

//QTEST_MAIN(TestGuessType)
//QTEST_MAIN(TestComicImages)

static PyObject* TintzConvertToImages(PyObject *self, PyObject *args)
{
    const char *fileName;

    if (!PyArg_ParseTuple(args, "s", &fileName))
        return NULL;

    QString qFileName( (const char*)fileName );

    FILETYPE realType = FileFormat::GetFileTypeFromData( qFileName );

    ComicImages comic( qFileName );
    
    int ret = comic.RunCommand(realType);
    int nrPages = comic.NrPages();

    char* newFileName = comic.FullPathFileName().toAscii().data();
    
    newFileName[ comic.FullPathFileName().length() ] = 0x00;
    
    std::cout << "********NEW FILE NAME************* [" << newFileName << "]";
    
    return Py_BuildValue("iis", ret, nrPages, newFileName );
}

static PyMethodDef TintzMethods[] = {
    {"ConvertToImages",  TintzConvertToImages, METH_VARARGS,
     "Convert comic files to images."},
    {NULL, NULL, 0, NULL}        
};

PyMODINIT_FUNC initlibtintz(void)
{
    (void) Py_InitModule("libtintz", TintzMethods);
}


