/****************************************************************************
** Meta object code from reading C++ file 'comicimages.h'
**
** Created: Sat Jan 15 20:27:18 2011
**      by: The Qt Meta Object Compiler version 62 (Qt 4.7.0)
**
** WARNING! All changes made in this file will be lost!
*****************************************************************************/

#include "../tintz_publications/comicimages.h"
#if !defined(Q_MOC_OUTPUT_REVISION)
#error "The header file 'comicimages.h' doesn't include <QObject>."
#elif Q_MOC_OUTPUT_REVISION != 62
#error "This file was generated using the moc from 4.7.0. It"
#error "cannot be used with the include files from this version of Qt."
#error "(The moc has changed too much.)"
#endif

QT_BEGIN_MOC_NAMESPACE
static const uint qt_meta_data_tintz__ComicImages[] = {

 // content:
       5,       // revision
       0,       // classname
       0,    0, // classinfo
       2,   14, // methods
       0,    0, // properties
       0,    0, // enums/sets
       0,    0, // constructors
       0,       // flags
       0,       // signalCount

 // slots: signature, parameters, type, tag, flags
      29,   20,   19,   19, 0x0a,
      49,   43,   19,   19, 0x0a,

       0        // eod
};

static const char qt_meta_stringdata_tintz__ComicImages[] = {
    "tintz::ComicImages\0\0exitCode\0Finished(int)\0"
    "error\0Error(QProcess::ProcessError)\0"
};

const QMetaObject tintz::ComicImages::staticMetaObject = {
    { &QObject::staticMetaObject, qt_meta_stringdata_tintz__ComicImages,
      qt_meta_data_tintz__ComicImages, 0 }
};

#ifdef Q_NO_DATA_RELOCATION
const QMetaObject &tintz::ComicImages::getStaticMetaObject() { return staticMetaObject; }
#endif //Q_NO_DATA_RELOCATION

const QMetaObject *tintz::ComicImages::metaObject() const
{
    return QObject::d_ptr->metaObject ? QObject::d_ptr->metaObject : &staticMetaObject;
}

void *tintz::ComicImages::qt_metacast(const char *_clname)
{
    if (!_clname) return 0;
    if (!strcmp(_clname, qt_meta_stringdata_tintz__ComicImages))
        return static_cast<void*>(const_cast< ComicImages*>(this));
    return QObject::qt_metacast(_clname);
}

int tintz::ComicImages::qt_metacall(QMetaObject::Call _c, int _id, void **_a)
{
    _id = QObject::qt_metacall(_c, _id, _a);
    if (_id < 0)
        return _id;
    if (_c == QMetaObject::InvokeMetaMethod) {
        switch (_id) {
        case 0: Finished((*reinterpret_cast< int(*)>(_a[1]))); break;
        case 1: Error((*reinterpret_cast< QProcess::ProcessError(*)>(_a[1]))); break;
        default: ;
        }
        _id -= 2;
    }
    return _id;
}
QT_END_MOC_NAMESPACE
