from qterminal.mux import mux
from qterminal.screen import QTerminalScreen
from qterminal.stream import QTerminalStream
import paramiko
import threading
import time
import uuid
from LibraryImport import *
import os


class BaseBackend(object):

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.screen = QTerminalScreen(
            width, height, history=9999, ratio=.000001)
        self.stream = QTerminalStream(self.screen)
        self.id = str(uuid.uuid4())
        self.connected = False

    def write_to_screen(self, data):
        self.stream.feed(data)

    def read(self):
        pass

    def reconnect(self):
        pass

    def resize(self, width, height):
        self.width = width
        self.height = height
        self.screen.resize(columns=width, lines=height)

    def connect(self):
        pass

    def get_read_wait(self):
        pass

    def cursor(self):
        return self.screen.cursor

    def close(self):
        pass


class PtyBackend(BaseBackend):
    pass


class TelnetBackend(BaseBackend):
    def __init__(self, width, height, host):
        super(TelnetBackend, self).__init__(width, height)
        self.host = host
        self.thread = threading.Thread(target=self.connect)
        self.ssh_client = None
        self.channel = None
        self.isProtectionActive = False
        self.thread.start()
        pass

    def connect(self):
        try:
            host = self.host.split(':')
            # self.tn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # self.tn.connect((host[0], int(host[1])))
            self.connected = True
            self.tn = Telnet_(host[0], host[1], timeout=1)
            mux.add_backend(self)
            self.isProtectionActive = True
        except:
            print(self.connected)
            if self.isProtectionActive:
                self.reconnect()
            else:
                self.connected = False
        return super().connect()

    def get_read_wait(self):
        return self.tn

    def write(self, data):
        try:
            if isinstance(data, str):
                self.tn.write(data.encode("utf-8"))
            else:
                self.tn.write(data)
        except AttributeError as e:
            print(e)
            pass
        except:
            self.connected = False
            pass

    def read(self):
        try:
            # for i in range(1024):
            output = self.tn.read_eager()
            self.write_to_screen(output)
        except Exception as e:
            print(e)
            if self.isProtectionActive:
                self.reconnect()
            else:
                self.connected = False

    def reconnect(self):
        self.close()
        del self.thread
        self.thread = threading.Thread(target=self.connect)
        self.thread.start()

    def close(self):
        try:
            mux.remove_and_close(self)
            self.tn.close()
        except:
            pass


class SSHBackend(BaseBackend):

    def __init__(self, width, height, ip, username=None, password=None):
        super(SSHBackend, self).__init__(width, height)
        self.ip = ip
        self.GotUserNameAndPassword = False
        self.username = ""
        self.password = ""
        self.tries = 3
        if username != None:
            self.username = username
            self.GotUserNameAndPassword = True
        if password != None:
            self.password = password
        else:
            self.GotUserNameAndPassword = False
        self.thread = threading.Thread(target=self.connect)
        self.ssh_client = None
        self.channel = None
        if self.GotUserNameAndPassword:
            self.thread.start()
        else:
            self.GetUserNameAndPassword()

    def GetUserNameAndPassword(self):
        self.connected = True
        if self.username == '':
            self.write_to_screen(b'login:')
        else:
            self.write_to_screen(b'password:')

    def connect(self):
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            self.ssh_client.connect(
                self.ip, username=self.username, password=self.password, timeout=1)
            self.tries = 3
            self.connected = True
        except Exception as e:
            print(e)
            if self.tries:
                self.tries -= 1
                self.username = ''
                self.password = ''
                self.GotUserNameAndPassword = False
                self.write_to_screen(b'\r\n')
                del self.thread
                self.thread = threading.Thread(target=self.connect)
                self.GetUserNameAndPassword()
            else:
                self.connected = False
            return
        self.channel = self.ssh_client.get_transport().open_session()
        self.channel.get_pty(width=self.width, height=self.height)
        self.channel.invoke_shell()

        timeout = 2
        while not self.channel.recv_ready() and timeout > 0:
            time.sleep(1)
            timeout -= 1

        self.channel.resize_pty(width=self.width, height=self.height)

        mux.add_backend(self)

    def reconnect(self):
        self.thread = threading.Thread(target=self.connect)
        self.tries = 3
        self.thread.start()
        return super().reconnect()

    def get_read_wait(self):
        return self.channel

    def write(self, data):
        if self.GotUserNameAndPassword:
            try:
                if isinstance(data, str):
                    self.channel.send(data.encode("utf-8"))
                else:
                    self.channel.send(data)
            except:
                self.connected = False
                pass
        else:
            if self.username == '' or self.username[-1] != '\r':
                if data == '\x7f':
                    if self.username != '':
                        self.username = self.username[:-1]
                        self.write_to_screen(b'\x08 \x08')
                else:
                    self.username += data
                    self.write_to_screen(data.encode('utf-8'))
                if data == '\r' and self.password == '':
                    self.write_to_screen(b'\npassword:')
                elif data == '\r':
                    self.thread.start()
            elif self.password == '' or self.password[-1] != '\r':
                if data == '\x7f':
                    if self.password != '':
                        self.password = self.password[:-1]
                else:
                    self.password += data
                if data == '\r':
                    self.write_to_screen(b'\n')
                    self.GotUserNameAndPassword = True
                    self.username, self.password = self.username[:-
                                                                 1], self.password[:-1]
                    self.thread.start()
            else:
                self.username, self.password = self.username[:-
                                                             1], self.password[-1]
                self.GotUserNameAndPassword = True

    def read(self):
        try:
            output = self.channel.recv(1024)
            self.write_to_screen(output)
        except:
            self.connected = False

    def resize(self, width, height):
        super(SSHBackend, self).resize(width, height)
        if self.channel:
            self.channel.resize_pty(width=width, height=height)

    def close(self):
        try:
            mux.remove_and_close(self)
            self.ssh_client.close()
        except:
            pass
