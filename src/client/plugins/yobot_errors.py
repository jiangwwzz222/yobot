# coding=utf-8
class File_error(IOError):
    def __init__(self, s="file error"):
        self.error_msg = s

class Server_error(Exception)
    def __init__(self, s="server error"):
        self.error_msg = s