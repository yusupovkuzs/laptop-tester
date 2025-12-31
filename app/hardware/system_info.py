import platform
import psutil
import subprocess


def get_os_info():
    return {
        "os": platform.system(),
        "os_version": platform.version(),
        "architecture": platform.architecture()[0]
    }

def get_cpu_info():
    return {
        "physical_cores": psutil.cpu_count(logical=False),
        "total_cores": psutil.cpu_count(logical=True),
        "max_frequency_mhz": psutil.cpu_freq().max if psutil.cpu_freq() else None,
        "current_frequency_mhz": psutil.cpu_freq().current if psutil.cpu_freq() else None,
        "cpu_usage_percent": psutil.cpu_percent(interval=1)
    }

def get_ram_info():
    ram = psutil.virtual_memory()
    return {
        "total_gb": round(ram.total / (1024 ** 3), 2),
        "available_gb": round(ram.available / (1024 ** 3), 2),
        "used_gb": round(ram.used / (1024 ** 3), 2),
        "usage_percent": ram.percent
    }

def get_disk_info():
    disks = []
    for partition in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            disks.append({
                "device": partition.device,
                "mountpoint": partition.mountpoint,
                "filesystem": partition.fstype,
                "total_gb": round(usage.total / (1024 ** 3), 2),
                "used_gb": round(usage.used / (1024 ** 3), 2),
                "free_gb": round(usage.free / (1024 ** 3), 2),
                "usage_percent": usage.percent
            })
        except PermissionError:
            continue
    return disks

def get_battery_info():
    battery = psutil.sensors_battery()
    if battery is None:
        return None
    return {
        "percent": battery.percent,
        "plugged": battery.power_plugged,
        "time_left_sec": battery.secsleft
    }

def get_network_info():
    interfaces = []
    for name, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family.name == "AF_INET":
                interfaces.append({
                    "interface": name,
                    "ip_address": addr.address
                })
    return interfaces

def get_gpu_info():
    try:
        result = subprocess.check_output(
            ["wmic", "path", "win32_VideoController", "get", "name"],
            stderr=subprocess.DEVNULL,
            text=True
        )
        gpus = [line.strip() for line in result.split("\n") if line.strip() and "Name" not in line]
        return gpus
    except Exception:
        return []

def collect_all_info():
    return {
        "os": get_os_info(),
        "cpu": get_cpu_info(),
        "ram": get_ram_info(),
        "disks": get_disk_info(),
        "battery": get_battery_info(),
        "network": get_network_info(),
        "gpu": get_gpu_info()
    }
