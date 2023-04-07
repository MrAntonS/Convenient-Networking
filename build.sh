#!/usr/bin/sh
source $PWD/venv/bin/activate
rm -f $PWD/output/Convnet
pyinstaller --noconfirm --onefile --windowed --specpath ./output/ --distpath ./output/ --workpath ./output/build -n ConvNet "$PWD/MainWindow.py"
convnet