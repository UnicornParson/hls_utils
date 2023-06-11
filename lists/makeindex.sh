#!/usr/bin/env bash

rm -vf index.txt

pushd Tvlist-awesome-m3u-m3u8/m3u
cat * | egrep "^http" >> ../../index.txt
popd

pushd iptv/streams
cat * | egrep "^http" >> ../../index.txt
popd

count=$(wc -l < index.txt)
echo "imported $count urls"