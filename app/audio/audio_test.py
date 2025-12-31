import os
import numpy as np
import sounddevice as sd
import soundfile as sf
from scipy.signal import resample


BASE_DIR = os.path.dirname(__file__)
SAMPLES_DIR = os.path.join(BASE_DIR, "samples")

def list_output_devices():
    """
    Возвращает список доступных устройств вывода:
    - с >= 2 каналами
    - только DirectSound
    """
    devices = sd.query_devices()
    hostapis = sd.query_hostapis()
    result = []

    for idx, dev in enumerate(devices):
        hostapi_name = hostapis[dev["hostapi"]]["name"]
        if dev["max_output_channels"] >= 2 and "DirectSound" in hostapi_name:
            result.append({
                "id": idx,
                "name": dev["name"],
                "hostapi": hostapi_name,
                "default_samplerate": int(dev["default_samplerate"])
            })

    return result

def play_sample(sample_name: str, device=None):
    """
    Воспроизводит WAV-файл через выбранное устройство.
    Автоматически ресемплирует под частоту устройства.
    Каналы приводятся к стерео.
    """
    file_path = os.path.join(SAMPLES_DIR, sample_name)
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Файл {sample_name} не найден в {SAMPLES_DIR}")

    data, samplerate = sf.read(file_path, dtype='float32')

    # Нормализация каналов
    if data.ndim == 1:
        data = np.column_stack((data, data))  # моно → стерео
    elif data.shape[1] > 2:
        data = data[:, :2]  # если >2 каналов, берем первые два

    # Получаем частоту устройства
    if device is not None:
        dev_info = sd.query_devices(device)
        target_sr = int(dev_info['default_samplerate'])
        # Ресемплирование если частоты не совпадают
        if samplerate != target_sr:
            num_samples = round(len(data) * target_sr / samplerate)
            data = resample(data, num_samples)
            samplerate = target_sr

    # Воспроизведение
    sd.play(data, samplerate, device=device)
    sd.wait()
