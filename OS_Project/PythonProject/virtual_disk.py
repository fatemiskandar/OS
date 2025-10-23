import os

class VirtualDisk:
    CLUSTER_SIZE = 1024
    CLUSTERS_NUMBER = 1024

    def __init__(self):
        self.disk_size = 0
        self.disk_path = None
        self.disk_file = None
        self.is_open = False

    def initialize(self, path, create_if_missing=True):
        if self.is_open:
            raise RuntimeError("Disk is already initialized")

        self.disk_path = path
        self.disk_size = self.CLUSTERS_NUMBER * self.CLUSTER_SIZE

        try:
            if not os.path.exists(self.disk_path):
                if create_if_missing:
                    self._create_empty_disk(path)
                else:
                    raise FileNotFoundError("Couldn't find the specified disk path")

            self.disk_file = open(path, "r+b")
            self.is_open = True

        except Exception as ex:
            self.is_open = False
            raise IOError(f"Failed to open disk: {ex}") from ex

    def _create_empty_disk(self, path):
        f = None
        try:
            f = open(path, "wb")
            empty_cluster = bytes(self.CLUSTER_SIZE)
            for _ in range(self.CLUSTERS_NUMBER):
                f.write(empty_cluster)
            f.flush()
        except Exception as ex:
            raise IOError(f"Failed to create disk file: {ex}") from ex
        finally:
            if f is not None:
                f.close()