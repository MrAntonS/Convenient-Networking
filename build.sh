#!/usr/bin/sh
rm -f $PWD/output/Mainwindow
pyinstaller --noconfirm --onefile --windowed --specpath ./output/ --distpath ./output/ --workpath ./output/build  "/home/bigbon/Documents/Convenient-Networking/MainWindow.py"
convnet