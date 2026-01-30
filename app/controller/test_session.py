from datetime import datetime


class TestSession:
    def __init__(self, serial_number: str):
        self.serial_number = serial_number
        self.start_time = datetime.now()

        self.usb_results = []
        self.audio_results = []

    # ================= USB =================

    def add_usb_result(self, result: dict):
        """
        result = {
            "drive": "E:\\",
            "read_speed": 120,
            "write_speed": 80,
            "status": "PASS" / "FAIL"
        }
        """
        self.usb_results.append(result)

    # ================= AUDIO =================

    def add_audio_result(self, channel, status, device):
        self.audio_results.append({
            "channel": channel,
            "status": status,
            "device": device
        })


    # ================= SUMMARY =================

    def build_summary(self) -> str:
        usb_pass = sum(1 for r in self.usb_results if r["status"] == "PASS")
        usb_fail = sum(1 for r in self.usb_results if r["status"] == "FAIL")

        audio_summary = "\n".join(
            f"{r['channel'].upper()} — {r['status']}"
            for r in self.audio_results
        )

        return (
            f"СЕРИЙНЫЙ НОМЕР: {self.serial_number}\n\n"
            f"USB ТЕСТЫ:\n"
            f"PASS: {usb_pass}\nFAIL: {usb_fail}\n\n"
            f"АУДИО:\n{audio_summary if audio_summary else 'Нет данных'}"
        )
