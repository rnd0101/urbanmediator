#!/bin/bash

for i in `find . -name '*.po'`
do
  bn=`basename $i .po`.mo
  dn=`dirname $i`
  echo "msgfmt -o $dn/$bn $i"
  msgfmt -o $dn/$bn $i
done
