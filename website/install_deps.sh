#!/bin/sh
set -e

TOP=$PWD
PREFIX=$PWD/local

which virtualenv2 > /dev/null || (
    echo virtualenv2 is requires; exit 1
)

virtualenv2 $PREFIX
for PKG in Cheetah PIL; do
    $PREFIX/bin/pip -E $PREFIX install --use-mirrors $PKG
done

mkdir -p $PREFIX/tmp
. $PREFIX/bin/activate

# Tahchee
tar xvzf lib/tahchee-1.0.0.tar.gz -C $PREFIX/tmp
(cd $PREFIX/tmp/Tahchee-1.0.0; patch -p1 < $TOP/lib/tahchee.patch)
(cd $PREFIX/tmp/Tahchee-1.0.0; python setup.py install)
