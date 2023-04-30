#!/usr/bin/sh
rm -f $PWD/output/Convnet
pipenv run pyinstaller --noconfirm --onefile --windowed --specpath ./output/ --distpath ./output/ --workpath ./output/build -n ConvNet "$PWD/MainWindow.py"
convnet