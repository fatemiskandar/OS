import struct
import fat_table_manager
import converter
import virtual_disk

def load_fat_disk(self):
    with open(self.disk_path, 'rb') as f:
        for i, cluster in enumerate(self.fat_clusters):
            f.seek(cluster * self.disk_size)
            cluster_data = f.read(self.disk_size)
            for j in range (self.disk_size//4):
                index = i * (self.disk_size//4) + j
                if index < len(self.fat):
                    self.fat[index] = struct.unpack('<i',cluster_data[j*4:(j+1)*4])[0]

def flush_fat_disk(self):
    with open(self.disk_image_path, 'r+b') as f:
        for i, cluster in enumerate(self.fat_clusters):
            data = bytearray()
            for j in range(self.cluster_size // 4):
                index = i * (self.cluster_size // 4) + j
                if index < len(self.fat):
                    data += struct.pack('<i', self.fat[index])
                else:
                    data += struct.pack('<i', 0)
            if len(data) < self.cluster_size:
                data += b'\x00' * (self.cluster_size - len(data))
            f.seek(cluster * self.cluster_size)
            f.write(data)

def get_fat_entry(self, index):
    self._check_reserved(index)
    return self.fat[index]

def set_fat_entry(self, index, value):
    self._check_reserved(index)
    self.fat[index] = value

def read_all_fat(self):
    return self.fat.copy()

def write_all_fat(self, entries):
    if len(entries) != len(self.fat):
        raise ValueError("Entries length must be 1024")
    self.fat = entries.copy()

def follow_chain(self, start_cluster):
    self._check_reserved(start_cluster)
    chain = []
    current = start_cluster
    while current != -1:
        chain.append(current)
        next_cluster = self.fat[current]
        if next_cluster == current:
            raise ValueError("Circular reference detected")
        current = next_cluster
    return chain

def allocate_chain(self, required_clusters):
    free_clusters = [i for i, val in enumerate(self.fat) if val == 0 and i > 4]
    if len(free_clusters) < required_clusters:
        raise ValueError("Not enough free clusters")
    allocated = free_clusters[:required_clusters]
    for i in range(len(allocated)-1):
        self.fat[allocated[i]] = allocated[i+1]
    self.fat[allocated[-1]] = -1
    return allocated[0]

def free_chain(self, start_cluster):
    self._check_reserved(start_cluster)
    current = start_cluster
    while current != -1:
        next_cluster = self.fat[current]
        self.fat[current] = 0
        current = next_cluster
