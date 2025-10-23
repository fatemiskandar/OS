from virtual_disk import VirtualDisk
def read (self,cluster_number):
        if not self.is_open:
            raise IOError("Not opened")
        if not (0<=cluster_number & cluster_number<self.cluster_number):
            raise IOError("Invalid cluster number")
        sett = self.cluster_number * self.cluster_size
        self.disk_file.seek(sett)
        data = self.disk_file.read(self.cluster_size)
        return data

def write(self, cluster_number, data):
    if not self.is_open:
            raise IOError("Not opened")
    if not (0 <= cluster_number & cluster_number < self.cluster_number):
        raise IOError("Invalid cluster number")
    if len(data) != self.cluster_size:
        raise IOError("Invalid cluster size")
    sett = self.cluster_number * self.cluster_size
    self.disk_file.seek(sett)
    self.disk_file.write(data)
    self.disk_file.flush()

def get_disk_size(self):
    return self.disk_size(self)

def close(self):
    if self.disk_file:
        self.disk_file.close()
        self.disk_file = None
        self.is_open = False