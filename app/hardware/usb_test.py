import os
import time
import hashlib
import psutil


TEST_FILENAME = "usb_test_file.bin"
TEST_FILE_SIZE_MB = 5


def get_removable_drives():
    drives = []
    for part in psutil.disk_partitions(all=False):
        if "removable" in part.opts.lower():
            drives.append(part.mountpoint)
    return drives

def generate_test_data(size_mb):
    return os.urandom(size_mb * 1024 * 1024)

def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def test_usb_drive(mountpoint: str) -> dict:
    file_path = os.path.join(mountpoint, TEST_FILENAME)
    data = generate_test_data(TEST_FILE_SIZE_MB)

    try:
        # WRITE TEST
        start_write = time.time()
        with open(file_path, "wb") as f:
            f.write(data)
        write_time = time.time() - start_write

        # READ TEST
        start_read = time.time()
        with open(file_path, "rb") as f:
            read_data = f.read()
        read_time = time.time() - start_read

        os.remove(file_path)

        result = {
            "drive": mountpoint,
            "status": "PASS",
            "write_speed_mb_s": round(TEST_FILE_SIZE_MB / write_time, 2),
            "read_speed_mb_s": round(TEST_FILE_SIZE_MB / read_time, 2),
            "checksum_match": sha256(data) == sha256(read_data)
        }

    except Exception as e:
        result = {
            "drive": mountpoint,
            "status": "FAIL",
            "error": str(e)
        }

    return result

def run_usb_tests():
    results = []
    drives = get_removable_drives()

    if not drives:
        return [{"status": "NO_USB_FOUND"}]

    for drive in drives:
        results.append(test_usb_drive(drive))

    return results