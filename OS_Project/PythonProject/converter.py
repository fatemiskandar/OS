import struct
class Converter:
    @staticmethod
    def stringTobyte(string):
        return string.encode('utf-8')
    @staticmethod
    def byteTostring(byte_data):
        return byte_data.decode('utf-8')