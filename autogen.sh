#!/bin/sh

aclocal
automake --add-missing; autoreconf -sfi -v
./configure $@
