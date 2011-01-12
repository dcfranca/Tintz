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

    if ( !comic.RunCommand(realType) )
        return Py_BuildValue("i", 0);
    
    return Py_BuildValue("i", 1);
}

static PyMethodDef TintzMethods[] = {
    {"TintzConvertToImages",  TintzConvertToImages, METH_VARARGS,
     "Convert comic files to images."},
    {NULL, NULL, 0, NULL}        
};

PyMODINIT_FUNC initlibtintz(void)
{
    (void) Py_InitModule("libtintz", TintzMethods);
}


