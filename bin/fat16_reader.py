#!/usr/bin/env python3

import struct
import os

class FAT16Reader:
    def __init__(self, filename):
        self.f = open(filename, 'rb')
        self._parse_boot_sector()

    def _parse_boot_sector(self):
        self.f.seek(0)
        boot_sector = self.f.read(512)

        self.bytes_per_sector = struct.unpack('<H', boot_sector[11:13])[0]
        self.sectors_per_cluster = boot_sector[13]
        self.reserved_sectors = struct.unpack('<H', boot_sector[14:16])[0]
        self.num_fats = boot_sector[16]
        self.root_entries = struct.unpack('<H', boot_sector[17:19])[0]
        self.total_sectors = struct.unpack('<H', boot_sector[19:21])[0]
        if self.total_sectors == 0:
            self.total_sectors = struct.unpack('<L', boot_sector[32:36])[0]
        self.sectors_per_fat = struct.unpack('<H', boot_sector[22:24])[0]

        self.fat_start = self.reserved_sectors * self.bytes_per_sector
        self.root_dir_start = self.fat_start + (self.num_fats * self.sectors_per_fat * self.bytes_per_sector)
        self.data_start = self.root_dir_start + (self.root_entries * 32)

    def _cluster_to_offset(self, cluster):
        return self.data_start + (cluster - 2) * self.sectors_per_cluster * self.bytes_per_sector

    def _read_fat_entry(self, cluster):
        fat_offset = self.fat_start + cluster * 2
        self.f.seek(fat_offset)
        return struct.unpack('<H', self.f.read(2))[0]

    def _parse_dir_entry(self, entry):
        if len(entry) != 32 or entry[0] in (0x00, 0xE5):
            return None

        filename = entry[0:8].decode('ascii', errors='ignore').strip()
        extension = entry[8:11].decode('ascii', errors='ignore').strip()
        attributes = entry[11]
        first_cluster = struct.unpack('<H', entry[26:28])[0]
        file_size = struct.unpack('<L', entry[28:32])[0]

        if attributes & 0x08:  # Volume label
            return None

        full_name = filename
        if extension:
            full_name += '.' + extension

        return {
            'name': full_name,
            'size': file_size,
            'attributes': attributes,
            'is_dir': bool(attributes & 0x10),
            'first_cluster': first_cluster
        }

    def read_directory(self, cluster=0):
        entries = []

        if cluster == 0:  # Root directory
            self.f.seek(self.root_dir_start)
            for i in range(self.root_entries):
                entry = self.f.read(32)
                if len(entry) != 32:
                    break
                file_info = self._parse_dir_entry(entry)
                if file_info and not file_info['name'].startswith('.'):
                    entries.append(file_info)
        else:  # Subdirectory
            current_cluster = cluster
            while current_cluster < 0xFFF8:
                offset = self._cluster_to_offset(current_cluster)
                self.f.seek(offset)
                cluster_data = self.f.read(self.sectors_per_cluster * self.bytes_per_sector)

                for i in range(0, len(cluster_data), 32):
                    entry = cluster_data[i:i+32]
                    if len(entry) != 32:
                        break
                    file_info = self._parse_dir_entry(entry)
                    if file_info and not file_info['name'].startswith('.'):
                        entries.append(file_info)

                current_cluster = self._read_fat_entry(current_cluster)

        return entries

    def read_file(self, first_cluster, size):
        data = b''
        current_cluster = first_cluster

        while current_cluster < 0xFFF8 and len(data) < size:
            offset = self._cluster_to_offset(current_cluster)
            self.f.seek(offset)
            cluster_data = self.f.read(self.sectors_per_cluster * self.bytes_per_sector)

            remaining = size - len(data)
            data += cluster_data[:remaining]

            current_cluster = self._read_fat_entry(current_cluster)

        return data[:size]

    def list_all_files(self, cluster=0, path=""):
        entries = self.read_directory(cluster)
        all_files = []

        for entry in entries:
            full_path = os.path.join(path, entry['name']) if path else entry['name']

            if entry['is_dir']:
                all_files.append((full_path + '/', 0, True))
                subdirs = self.list_all_files(entry['first_cluster'], full_path)
                all_files.extend(subdirs)
            else:
                all_files.append((full_path, entry['size'], False))

        return all_files

    def close(self):
        self.f.close()

if __name__ == '__main__':
    reader = FAT16Reader('partition1.img')

    print("All files and directories:")
    all_files = reader.list_all_files()

    for path, size, is_dir in all_files:
        if is_dir:
            print(f"[DIR]  {path}")
        else:
            size_mb = size / (1024*1024)
            print(f"       {path:40} {size:>10} bytes ({size_mb:.1f} MB)")

    reader.close()