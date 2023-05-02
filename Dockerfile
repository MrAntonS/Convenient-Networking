FROM  python
COPY . /ConvNet

CMD ['python', "/ConvNet/MainWindow.py"]
