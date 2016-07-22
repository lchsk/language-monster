#!/bin/sh

cd ./api && ./lint.sh
cd ./core && ./lint.sh
cd ./ctasks && ./lint.sh
cd ./management && ./lint.sh
cd ./userprofile && ./lint.sh
cd ./utility && ./lint.sh
cd ./vocabulary && ./lint.sh
