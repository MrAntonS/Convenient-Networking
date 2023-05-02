#!/usr/bin/sh
rm -f $PWD/src/output/Convnet
pipenv run pyinstaller --noconfirm --onefile --windowed --specpath ./src/output/ --distpath ./src/output/ --workpath ./src/output/build -n ConvNet "$PWD/src/main/MainWindow.py"
convnet