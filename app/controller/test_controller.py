from app.db.repository import (
    create_session,
    finish_session,
    save_usb_test,
    save_audio_test
)

class TestController:
    def __init__(self, laptop_serial=None):
        self.session_id = create_session(laptop_serial)
        self.failed = False

    def save_usb(self, result):
        save_usb_test(self.session_id, result)
        if result.get("status") != "OK":
            self.failed = True

    def save_audio(self, device, channel, ok, error=None):
        save_audio_test(self.session_id, device, channel, ok, error)
        if not ok:
            self.failed = True

    def finish(self):
        finish_session(
            self.session_id,
            "FAIL" if self.failed else "PASS"
        )
