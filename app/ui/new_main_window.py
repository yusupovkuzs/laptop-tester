import customtkinter as ctk
from tkinter import messagebox

from app.controller.test_session import TestSession
from app.hardware.usb_test import run_usb_tests
from app.audio.audio_test import play_sample, list_output_devices
# from app.db.repository import commit_session_to_db
import threading
from tkinter import messagebox
from app.db.repository import finish_test_session, save_usb_test, save_audio_test, get_all_sessions, get_session_by_serial 


class MainWindow(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Laptop QC Tester")
        self.geometry("700x500")

        self.session = None  # временная тестовая сессия

        self.show_role_selection()

    # ================== ЭКРАН ВЫБОРА РОЛИ ==================

    def show_role_selection(self):
        self.clear()

        ctk.CTkLabel(self, text="Кто вы?", font=("Arial", 22)).pack(pady=40)

        ctk.CTkButton(self, text="ТЕСТЕР", width=200,
                      command=self.show_tester_screen).pack(pady=10)

        ctk.CTkButton(self, text="АДМИН", width=200,
                      command=self.show_admin_login).pack(pady=10)

    # ================== АДМИН ==================

    def show_admin_login(self):
        self.clear()

        ctk.CTkLabel(self, text="Вход администратора", font=("Arial", 20)).pack(pady=20)

        self.admin_login = ctk.CTkEntry(self, placeholder_text="Логин")
        self.admin_login.pack(pady=5)

        self.admin_pass = ctk.CTkEntry(self, placeholder_text="Пароль", show="*")
        self.admin_pass.pack(pady=5)

        ctk.CTkButton(self, text="Войти", command=self.admin_auth).pack(pady=20)

    def admin_auth(self):
        login = self.admin_login.get()
        password = self.admin_pass.get()

        if login == "admin" and password == "admin":  # временно
            messagebox.showinfo("OK", "Вход выполнен")
            admin_window = AdminPanel(self)
            admin_window.grab_set()
        else:
            messagebox.showerror("Ошибка", "Неверные данные")

    # ================== ТЕСТЕР ==================

    def show_tester_screen(self):
        self.clear()

        ctk.CTkLabel(self, text="Сканируйте серийный номер",
                     font=("Arial", 18)).pack(pady=20)

        self.serial_entry = ctk.CTkEntry(self, width=300)
        self.serial_entry.pack(pady=10)
        self.serial_entry.bind("<Return>", self.start_testing)

    def start_testing(self, event=None):
        serial = self.serial_entry.get().strip()

        if not serial:
            return

        self.session = TestSession(serial)

        self.clear()

        ctk.CTkLabel(self, text=f"SN: {serial}", font=("Arial", 16)).pack(pady=5)

        self.status_label = ctk.CTkLabel(self, text="USB тестирование...", text_color="yellow")
        self.status_label.pack(pady=10)

        self.update()

        # --- USB ТЕСТ ---
        usb_results = run_usb_tests()
        print(usb_results)
        
        for res in usb_results:
            if res.get("status") == "NO_USB_FOUND":
                self.status_label.configure(text="USB не найдены", text_color="green")
                break
            
            if res["status"] == "FAIL":
                ctk.CTkLabel(self, text=f"USB тест провален\n{res['drive']} {res['error']}", text_color="red").pack(pady=5)

            self.session.add_usb_result(res)

        print("USB TEST RESULTS:", self.session.usb_results)
        self.status_label.configure(text="USB тест завершён", text_color="green")

        # --- КНОПКИ АУДИО ---
        self.show_audio_controls()
        self.audio_results = {
            "left": None,
            "right": None
        }

    # ================== АУДИО ==================

    def audio_test(self, channel, sample_file):
        device_id = self.device_map[self.selected_device.get()]
        if channel == "left":
            channel_text = "левом"
        else:
            channel_text = "правом"

        def _play():
            try:
                play_sample(sample_file, device=device_id)
                self.after(0, lambda: self.ask_audio_result(channel, channel_text))
                self.audio_results[channel] = "done"
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Ошибка аудио", str(e)))
                self.audio_results[channel] = "done"

        threading.Thread(target=_play, daemon=True).start()

    def show_audio_controls(self):
        ctk.CTkLabel(self, text="Аудио тест").pack(pady=10)

        # --- СПИСОК УСТРОЙСТВ ---
        self.audio_devices = list_output_devices()
        self.device_map = {
            d["name"]: d["id"] for d in self.audio_devices
        }

        self.selected_device = ctk.StringVar()
        if self.device_map:
            self.selected_device.set(next(iter(self.device_map)))
        if self.device_map:
            self.selected_device.set(next(iter(self.device_map)))

        ctk.CTkLabel(self, text="Устройство вывода:").pack()
        ctk.CTkOptionMenu(
            self,
            variable=self.selected_device,
            values=list(self.device_map.keys()),
            width=350
        ).pack(pady=5)

        # --- КНОПКИ ---
        ctk.CTkButton(self, text="▶ LEFT",
                    command=lambda: self.audio_test("left", "left.wav")).pack(pady=5)

        ctk.CTkButton(self, text="▶ RIGHT",
                    command=lambda: self.audio_test("right", "right.wav")).pack(pady=5)

        ctk.CTkButton(self, text="Завершить тестирование",
                    fg_color="red",
                    command=self.finish_tests).pack(pady=25)

    def ask_audio_result(self, channel, channel_text):
        """
        Вызывается ТОЛЬКО в главном потоке
        """
        result = messagebox.askyesno(
            title="Аудио тест",
            message=f"Слышен ли звук в {channel_text} канале?"
        )

        status = "PASS" if result else "FAIL"

        # 🔹 сохраняем В ПАМЯТЬ, НЕ В БД
        self.session.add_audio_result(
            channel=channel,
            status=status,
            device=self.selected_device.get()
        )

    # ================== ЗАВЕРШЕНИЕ ==================

    def finish_tests(self):
        summary = self.session.build_summary()

        left_done = self.audio_results.get("left") is not None
        right_done = self.audio_results.get("right") is not None

        if not left_done or not right_done:
            messagebox.showwarning(
                "Тест не завершён",
                "Необходимо проверить оба аудио канала (LEFT и RIGHT)"
            )
            return

        confirm = messagebox.askyesno("Итоги тестов",
                                      summary + "\n\nСохранить результаты?")

        if confirm:
            if all(r["status"] == "PASS" for r in self.session.usb_results):
                save_usb_test(
                    laptop_serial=self.session.serial_number,
                    checksum_ok=True,
                    status="PASS",
                    error=None
                )
            else:
                save_usb_test(
                    laptop_serial=self.session.serial_number,
                    checksum_ok=False,
                    status="FAIL",
                    error="Один или несколько USB тестов провалены"
                )

            save_audio_test(
                laptop_serial=self.session.serial_number,
                device_name=", ".join({r["device"] for r in self.session.audio_results}),
                left_status=next((r["status"] for r in self.session.audio_results if r["channel"] == "left"), "FAIL"),
                right_status=next((r["status"] for r in self.session.audio_results if r["channel"] == "right"), "FAIL"),
                error=None
            )

            finish_test_session(
                laptop_serial=self.session.serial_number,
                tester_name="tester1",  # временно
                overall_status="PASS" if all(r["status"] == "PASS" for r in self.session.usb_results) and \
                                       all(r["status"] == "PASS" for r in self.session.audio_results) else "FAIL"
            )

            messagebox.showinfo("OK", "Данные сохранены")
            self.show_role_selection()
        else:
            messagebox.showwarning("Отмена", "Тесты начнутся заново")
            self.show_tester_screen()

    # ================== УТИЛИТЫ ==================

    def clear(self):
        for widget in self.winfo_children():
            widget.destroy()

# ================== ПАНЕЛЬ ДЛЯ АДМИНА ==================

class AdminPanel(ctk.CTkToplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Панель администратора")
        self.geometry("700x500")
        
        # ------------------ Поиск ------------------
        self.label_search = ctk.CTkLabel(self, text="Серийный номер:")
        self.label_search.pack(pady=(10, 0))
        
        self.entry_search = ctk.CTkEntry(self, placeholder_text="Введите серийный номер", width=200)
        self.entry_search.pack(pady=5)
        
        self.btn_search = ctk.CTkButton(self, text="Поиск", command=self.search_serial)
        self.btn_search.pack(pady=(0, 10))
        
        # ------------------ Кнопка все устройства ------------------
        self.btn_all = ctk.CTkButton(self, text="Посмотреть все устройства", command=self.show_all)
        self.btn_all.pack(pady=(0, 10))
        
        # ------------------ Поле для вывода ------------------
        self.text_area = ctk.CTkTextbox(self, width=650, height=350)
        self.text_area.pack(pady=5)
    
    # ------------------ Функции ------------------
    def show_all(self):
        self.text_area.delete("1.0", ctk.END)
        sessions = get_all_sessions()
        if not sessions:
            self.text_area.insert(ctk.END, "Нет данных.\n")
            return
        for s in sessions:
            self.text_area.insert(ctk.END, f"Серийный номер: {s['laptop_serial']}\n")
            self.text_area.insert(ctk.END, f"Тестер: {s['tester_name']}\n")
            self.text_area.insert(ctk.END, f"Статус: {s['overall_status']}\n")
            self.text_area.insert(ctk.END, "--------------------------\n")
    
    def search_serial(self):
        serial = self.entry_search.get().strip()
        if not serial:
            messagebox.showwarning("Ошибка", "Введите серийный номер")
            return
        self.text_area.delete("1.0", ctk.END)
        session = get_session_by_serial(serial)
        if not session:
            self.text_area.insert(ctk.END, f"Данные для серийного номера {serial} не найдены.\n")
            return
        # выводим общую информацию
        self.text_area.insert(ctk.END, f"Серийный номер: {session['laptop_serial']}\n")
        self.text_area.insert(ctk.END, f"Тестер: {session['tester_name']}\n")
        self.text_area.insert(ctk.END, f"Статус сессии: {session['overall_status']}\n\n")
        # USB тесты
        self.text_area.insert(ctk.END, "USB тесты:\n")
        for usb in session['usb_tests']:
            self.text_area.insert(ctk.END, f"  {usb['drive']}: {usb['status']}\n")
        # Аудио тесты
        self.text_area.insert(ctk.END, "\nАудио тесты:\n")
        audio = session['audio_tests']
        if audio:
            self.text_area.insert(ctk.END, f"  Device: {audio['device_name']}\n")
            self.text_area.insert(ctk.END, f"  LEFT: {audio['left_status']}\n")
            self.text_area.insert(ctk.END, f"  RIGHT: {audio['right_status']}\n")
        self.text_area.insert(ctk.END, "--------------------------\n")
