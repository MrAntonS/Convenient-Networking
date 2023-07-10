#!/usr/bin/sh
rm -f $PWD/src/output/Convnet
pipenv run pyinstaller --noconfirm --onefile --windowed --specpath $PWD/src/output/ --distpath $PWD/src/output/ --workpath $PWD/src/output/build -n ConvNet "$PWD/src/main/MainWindow.py"
convnet