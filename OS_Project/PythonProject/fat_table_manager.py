from converter import Converter
import struct
class fat_table_manager:
    def __init__(self,disk_path,cluster_size=4096):
        self.disk_path = disk_path
        self.cluster_size = cluster_size
        self.fat = [0] * 1024
        self.fat_clusters = [1, 2, 3, 4]