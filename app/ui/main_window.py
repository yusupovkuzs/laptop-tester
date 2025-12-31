import tkinter as tk
from tkinter import scrolledtext
from app.hardware.system_info import collect_all_info
from app.hardware.usb_test import run_usb_tests
from app.audio.audio_test import play_sample, list_output_devices
import threading
from app.controller.test_controller import TestController

# Colors
BG_COLOR = "#F4F6F8"
BTN_MAIN = "#2E86C1"
BTN_SECONDARY = "#95A5A6"
BTN_SUCCESS = "#27AE60"
BTN_DANGER = "#C0392B"
TEXT_COLOR = "#2C3E50"


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Laptop Tester")
        self.geometry("720x640")
        self.configure(bg=BG_COLOR)
        self.controller = None

        self.create_header()
        self.create_tests_panel()
        self.create_session_controls()
        self.create_log()

        # self.btn_load = tk.Button(
        #     self,
        #     text="Показать информацию о ноутбуке",
        #     command=self.load_system_info
        # )
        # self.btn_load.pack(pady=10)

        # self.btn_start_tests = tk.Button(
        #     self,
        #     text="Начать тестирование",
        #     command=self.start_tests
        # )
        # self.btn_start_tests.pack(pady=10)

        # self.btn_finish_tests = tk.Button(
        #     self,
        #     text="Завершить тестирование",
        #     command=self.finish_tests
        # )
        # self.btn_finish_tests.pack(pady=10)

        # self.btn_usb = tk.Button(
        #     self,
        #     text="Тест USB",
        #     command=self.run_usb_test
        # )
        # self.btn_usb.pack(pady=5)

        # self.audio_label = tk.Label(self, text="Аудио тест")
        # self.audio_label.pack(pady=5)

        # self.devices = list_output_devices()
        # self.device_map = {f"{d['name']} ({d['hostapi']})": d["id"] for d in self.devices}
        # self.selected_device = tk.StringVar()
        # self.selected_device.set(next(iter(self.device_map)))
        # self.device_menu = tk.OptionMenu(self, self.selected_device, *self.device_map.keys())
        # self.device_menu.pack(pady=5)
        # self.btn_left = tk.Button(self, text="Левый канал", command=lambda: self.play_audio("left.wav", "LEFT"))
        # self.btn_left.pack(pady=2)
        # self.btn_right = tk.Button(self, text="Правый канал", command=lambda: self.play_audio("right.wav", "RIGHT"))
        # self.btn_right.pack(pady=2)

        # self.text_area = scrolledtext.ScrolledText(self, wrap=tk.WORD, width=110, height=35)
        # self.text_area.pack(padx=10, pady=10)

    def create_header(self):
        header = tk.Label(
            self,
            text="Laptop Tester",
            font=("Segoe UI", 18, "bold"),
            bg=BG_COLOR,
            fg=TEXT_COLOR
        )
        header.pack(pady=10)

    def create_session_controls(self):
        frame = tk.Frame(self, bg=BG_COLOR)
        frame.pack(pady=10)

        self.btn_start_tests = tk.Button(
            frame,
            text="Начать тестирование",
            width=25,
            bg=BTN_MAIN,
            fg="white",
            font=("Segoe UI", 10, "bold"),
            command=self.start_tests
        )
        self.btn_start_tests.grid(row=0, column=0, padx=5)

        self.btn_finish_tests = tk.Button(
            frame,
            text="Завершить тестирование",
            width=25,
            bg=BTN_SECONDARY,
            fg="white",
            font=("Segoe UI", 10),
            command=self.finish_tests,
            state=tk.DISABLED
        )
        self.btn_finish_tests.grid(row=0, column=1, padx=5)

    def create_log(self):
        frame = tk.Frame(self, bg=BG_COLOR)
        frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.text_area = tk.Text(
            frame,
            height=15,
            font=("Consolas", 10),
            bg="white",
            fg=TEXT_COLOR
        )
        self.text_area.pack(fill="both", expand=True)


    def start_tests(self):
        # self.controller = TestController()
        # self.text_area.insert(tk.END, "Сессия тестирования начата\n")
        self.controller = TestController()
        self.log("Сессия начата")

        self.btn_start_tests.config(state=tk.DISABLED)
        self.btn_finish_tests.config(state=tk.NORMAL)
        self.btn_usb.config(state=tk.NORMAL)
        self.btn_left.config(state=tk.NORMAL)
        self.btn_right.config(state=tk.NORMAL)

    def create_tests_panel(self):
        frame = tk.LabelFrame(
            self,
            text="Тесты",
            font=("Segoe UI", 10, "bold"),
            bg=BG_COLOR,
            fg=TEXT_COLOR,
            padx=10,
            pady=10
        )
        frame.pack(fill="x", padx=20, pady=10)

        # --- USB ---
        self.btn_usb = tk.Button(
            frame,
            text="USB тест",
            width=20,
            bg=BTN_MAIN,
            fg="white",
            command=self.run_usb_test,
            state=tk.DISABLED
        )
        self.btn_usb.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        # --- AUDIO DEVICES ---
        tk.Label(
            frame,
            text="Аудио устройство:",
            bg=BG_COLOR,
            fg=TEXT_COLOR
        ).grid(row=1, column=0, sticky="w", pady=(10, 2))

        self.audio_devices = list_output_devices()
        self.device_map = {
            d["name"]: d["id"] for d in self.audio_devices
        }

        self.selected_device = tk.StringVar()
        if self.device_map:
            self.selected_device.set(next(iter(self.device_map)))

        self.device_menu = tk.OptionMenu(
            frame,
            self.selected_device,
            *self.device_map.keys()
        )
        self.device_menu.config(width=40)
        self.device_menu.grid(row=2, column=0, columnspan=2, sticky="w")

        # --- AUDIO BUTTONS ---
        self.btn_left = tk.Button(
            frame,
            text="Аудио LEFT",
            width=20,
            bg=BTN_MAIN,
            fg="white",
            command=lambda: self.play_audio("left.wav", "LEFT"),
            state=tk.DISABLED
        )
        self.btn_left.grid(row=3, column=0, padx=5, pady=10)

        self.btn_right = tk.Button(
            frame,
            text="Аудио RIGHT",
            width=20,
            bg=BTN_MAIN,
            fg="white",
            command=lambda: self.play_audio("right.wav", "RIGHT"),
            state=tk.DISABLED
        )
        self.btn_right.grid(row=3, column=1, padx=5, pady=10)

    def load_system_info(self):
        self.text_area.delete("1.0", tk.END)
        info = collect_all_info()
        self.text_area.insert(tk.END, self.format_info(info))

    def run_usb_test(self):
        # self.text_area.delete("1.0", tk.END)
        results = run_usb_tests()

        self.text_area.insert(tk.END, "=== USB ТЕСТ ===\n")

        for res in results:
            if res.get("status") == "NO_USB_FOUND":
                self.text_area.insert(tk.END, "USB-устройства не обнаружены\n")
                continue

            self.text_area.insert(tk.END, f"Диск: {res['drive']}\n")
            self.text_area.insert(tk.END, f"Статус: {res['status']}\n")

            if res["status"] == "OK":
                self.text_area.insert(tk.END, f"Скорость записи (MB/s): {res['write_speed_mb_s']}\n")
                self.text_area.insert(tk.END, f"Скорость чтения (MB/s): {res['read_speed_mb_s']}\n")
                self.text_area.insert(tk.END, f"Контрольная сумма OK: {res['checksum_match']}\n")
            else:
                self.text_area.insert(tk.END, f"Ошибка: {res.get('error')}\n")

            self.text_area.insert(tk.END, "-" * 40 + "\n")
            self.controller.save_usb(res)

    def play_audio(self, sample_file, channel):
        device_id = self.device_map[self.selected_device.get()]
        def _play():
            try:
                play_sample(sample_file, device=device_id)
                self.text_area.insert(tk.END, f"Аудио тест OK: {sample_file}\n")
                self.controller.save_audio(str(self.selected_device), channel, True)
            except Exception as e:
                self.text_area.insert(tk.END, f"Ошибка аудио: {e}\n")
                self.controller.save_audio(str(self.selected_device), channel, False, str(e))
        threading.Thread(target=_play, daemon=True).start()

    def finish_tests(self):
        # self.controller.finish()
        self.controller.finish()
        self.log("Сессия завершена")

        self.btn_start_tests.config(state=tk.NORMAL)
        self.btn_finish_tests.config(state=tk.DISABLED)
        self.btn_usb.config(state=tk.DISABLED)
        self.btn_left.config(state=tk.DISABLED)
        self.btn_right.config(state=tk.DISABLED)

    def log(self, message, ok=True):
        color = BTN_SUCCESS if ok else BTN_DANGER
        self.text_area.insert(tk.END, message + "\n")
        self.text_area.tag_add(color, "end-2l", "end-1l")
        self.text_area.tag_config(color, foreground=color)
        self.text_area.see(tk.END)

    
    @staticmethod
    def format_info(info: dict) -> str:
        lines = []

        lines.append("=== ОС ===")
        for k, v in info["os"].items():
            lines.append(f"{k}: {v}")

        lines.append("\n=== CPU ===")
        for k, v in info["cpu"].items():
            lines.append(f"{k}: {v}")

        lines.append("\n=== RAM ===")
        for k, v in info["ram"].items():
            lines.append(f"{k}: {v}")

        lines.append("\n=== ДИСКИ ===")
        for disk in info["disks"]:
            lines.append(f"\nУстройство: {disk['device']}")
            for k, v in disk.items():
                if k != "device":
                    lines.append(f"  {k}: {v}")

        lines.append("\n=== БАТАРЕЯ ===")
        if info["battery"]:
            for k, v in info["battery"].items():
                lines.append(f"{k}: {v}")
        else:
            lines.append("Батарея не обнаружена")

        lines.append("\n=== СЕТЬ ===")
        for net in info["network"]:
            lines.append(f"{net['interface']}: {net['ip_address']}")

        lines.append("\n=== GPU ===")
        for gpu in info["gpu"]:
            lines.append(gpu)

        return "\n".join(lines)
