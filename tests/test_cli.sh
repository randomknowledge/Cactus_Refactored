#!/bin/sh

rm -rf .tmp/testcli
mkdir -p .tmp/testcli
cd .tmp/testcli
cactus create testproject
cd testproject
cactus build
