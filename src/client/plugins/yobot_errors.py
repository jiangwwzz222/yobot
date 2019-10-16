# coding=utf-8
class File_error(IOError):
    def __init__(self, s="file error"):
        self.error_filename = s