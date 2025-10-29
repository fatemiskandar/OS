
from virtual_disk import VirtualDisk
import fsConstant as fs

class super_block:
    def __init__(self, cluster_number, disk: VirtualDisk):
        self.disk = disk
        self.disk.write(fs.super_cluster,bytes(fs.cluster_size))

    def read_super_block(self):
        return self.disk.read(fs.super_cluster)
    def write_super_block(self,data):
        if len(data) != fs.super_cluster:
            raise ValueError("Super block size is not equal to cluster size")
        self.disk.write(data,fs.super_cluster,data)