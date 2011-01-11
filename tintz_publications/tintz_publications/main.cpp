#include <QtCore/QCoreApplication>
#include <QMimeData>
#include <QFile>
#include <Qt/QtTest>
#include <iostream>
#include "fileformat.h"
#include "testguesstype.h"
#include "testcomicimages.h"
#include "comicimages.h"
#include <iostream>
#include <wchar.h>
#include <QString>
#include <fileformat.h>
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

