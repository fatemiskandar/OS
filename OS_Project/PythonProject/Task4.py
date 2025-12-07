import struct
from converter import Converter

class DirectoryEntry:
    def __init__(self, name="", attr=0, first_cluster=0, file_size=0):
        self.name = name
        self.attr = attr
        self.first_cluster = first_cluster
        self.file_size = file_size

    def to_bytes(self):
        raw_name = Converter.string_to_bytes(self.name.ljust(11)[:11])
        attr_bytes = struct.pack("<B", self.attr)
        first_cluster_bytes = struct.pack("<I", self.first_cluster)
        file_size_bytes = struct.pack("<I", self.file_size)
        padding = b'\x00' * (32 - 11 - 1 - 4 - 4)
        return raw_name + attr_bytes + first_cluster_bytes + file_size_bytes + padding

    @staticmethod
    def from_bytes(data):
        raw_name = data[:11]
        name = Converter.bytes_to_string(raw_name).rstrip()
        attr = struct.unpack("<B", data[11:12])[0]
        first_cluster = struct.unpack("<I", data[12:16])[0]
        file_size = struct.unpack("<I", data[16:20])[0]
        return DirectoryEntry(name, attr, first_cluster, file_size)

class Directory:
    def __init__(self, fat_manager, cluster_size=4096):
        self.fat_manager = fat_manager
        self.cluster_size = cluster_size

    def read_directory(self, start_cluster):
        entries = []
        chain = self.fat_manager.FollowChain(start_cluster)
        with open(self.fat_manager.disk_image_path, "rb") as f:
            for cluster in chain:
                f.seek(cluster * self.cluster_size)
                cluster_data = f.read(self.cluster_size)
                for i in range(self.cluster_size // 32):
                    entry_data = cluster_data[i*32:(i+1)*32]
                    if entry_data[0] != 0x00:
                        entry = DirectoryEntry.from_bytes(entry_data)
                        entries.append(entry)
        return entries

    def find_directory_entry(self, start_cluster, name):
        name = name.upper()
        entries = self.read_directory(start_cluster)
        for entry in entries:
            if entry.name.upper() == name:
                return entry
        return None

    def add_directory_entry(self, start_cluster, new_entry):
        chain = self.fat_manager.FollowChain(start_cluster)
        with open(self.fat_manager.disk_image_path, "r+b") as f:
            for cluster in chain:
                f.seek(cluster * self.cluster_size)
                cluster_data = f.read(self.cluster_size)
                for i in range(self.cluster_size // 32):
                    entry_data = cluster_data[i*32:(i+1)*32]
                    if entry_data[0] == 0x00:
                        f.seek(cluster * self.cluster_size + i*32)
                        f.write(new_entry.to_bytes())
                        return
            new_cluster = self.fat_manager.AllocateChain(1)
            if new_cluster == -1:
                raise Exception("Disk Full - Cannot allocate new directory cluster")
            f.seek(new_cluster * self.cluster_size)
            f.write(new_entry.to_bytes())
            self.fat_manager.SetFatEntry(chain[-1], new_cluster)
            self.fat_manager.SetFatEntry(new_cluster, -1)
            self.fat_manager.FlushFatToDisk()

    def remove_directory_entry(self, start_cluster, name):
        name = name.upper()
        chain = self.fat_manager.FollowChain(start_cluster)
        with open(self.fat_manager.disk_image_path, "r+b") as f:
            for cluster in chain:
                f.seek(cluster * self.cluster_size)
                cluster_data = f.read(self.cluster_size)
                for i in range(self.cluster_size // 32):
                    entry_data = cluster_data[i*32:(i+1)*32]
                    entry = DirectoryEntry.from_bytes(entry_data)
                    if entry.name.upper() == name:
                        f.seek(cluster * self.cluster_size + i*32)
                        f.write(b'\x00'*32)
                        if entry.first_cluster != 0:
                            self.fat_manager.FreeChain(entry.first_cluster)
                            self.fat_manager.FlushFatToDisk()
                        return
        raise Exception(f"Entry {name} not found")

    @staticmethod
    def format_name_8dot3(name):
        parts = name.split(".")
        name_part = parts[0][:8].upper()
        ext_part = parts[1][:3].upper() if len(parts) > 1 else ""
        return name_part.ljust(8) + ext_part.ljust(3)

    @staticmethod
    def parse_8dot3_name(raw_name):
        return raw_name[:8].rstrip() + ('.' + raw_name[8:11].rstrip() if raw_name[8:11].strip() else "")
