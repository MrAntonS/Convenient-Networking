#!/usr/bin/sh
rm -f $PWD/output/Convnet
pyinstaller --noconfirm --onefile --windowed --specpath ./output/ --distpath ./output/ --workpath ./output/build -n ConvNet "/home/bigbon/Documents/Convenient-Networking/MainWindow.py"
convnet