import customtkinter as ctk
from tkinter import messagebox, ttk

from app.controller.test_session import TestSession
from app.hardware.usb_test import run_usb_tests
from app.audio.audio_test import play_sample, list_output_devices
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
            self.show_admin_screen()
        else:
            messagebox.showerror("Ошибка", "Неверные данные")
    
    def show_admin_screen(self):
        self.clear()

        ctk.CTkLabel(self, text="Админ панель", font=("Arial", 20)).pack(pady=20)

        ctk.CTkButton(self, text="Показать все протестированные устройства", command=self.show_all_devices).pack(pady=10)
        self.search_entry = ctk.CTkEntry(self, placeholder_text="Введите серийный номер")
        self.search_entry.pack(pady=5)

        self.search_btn = ctk.CTkButton(
            self,
            text="Найти устройство",
            command=self.search_device
        )
        self.search_btn.pack(pady=5)

        ctk.CTkButton(self, text="Выйти", command=self.show_role_selection).pack(pady=20)
    
    def show_all_devices(self):
        sessions = get_all_sessions()

        if not sessions:
            messagebox.showinfo("Информация", "Записей нет")
            return

        window = ctk.CTkToplevel(self)
        window.title("Все протестированные устройства")
        window.geometry("800x400")

        # ==== СТИЛЬ ====
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview",
                        background="#2b2b2b",
                        foreground="white",
                        rowheight=28,
                        fieldbackground="#2b2b2b",
                        font=("Arial", 12))
        style.map("Treeview", background=[("selected", "#1f6aa5")])

        # ==== ТАБЛИЦА ====
        columns = ("serial", "tester", "time", "status")

        tree = ttk.Treeview(window, columns=columns, show="headings")

        tree.heading("serial", text="Серийный номер")
        tree.heading("tester", text="Тестер")
        tree.heading("time", text="Время записи")
        tree.heading("status", text="Статус")

        tree.column("serial", width=200, anchor="center")
        tree.column("tester", width=120, anchor="center")
        tree.column("time", width=220, anchor="center")
        tree.column("status", width=100, anchor="center")

        # Цвет статуса
        tree.tag_configure("PASS", foreground="lightgreen")
        tree.tag_configure("FAIL", foreground="red")

        # ==== ДАННЫЕ ====
        for s in sessions:
            status = s["overall_status"]
            tree.insert(
                "",
                "end",
                values=(
                    s["laptop_serial"],
                    s["tester_name"],
                    s["finished_at"].strftime("%Y-%m-%d %H:%M"),
                    status
                ),
                tags=(status,)
            )

        tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Скролл
        scrollbar = ttk.Scrollbar(window, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

    def search_device(self):
        serial = self.search_entry.get().strip()
        if not serial:
            messagebox.showerror("Ошибка", "Введите серийный номер")
            return

        session_row, audio_rows, usb_rows = get_session_by_serial(serial)

        if not session_row:
            messagebox.showinfo("Не найдено", "Устройство не найдено")
            return

        self.show_device_details(session_row, audio_rows, usb_rows)

    def show_device_details(self, session_row, audio_rows, usb_rows):
        window = ctk.CTkToplevel(self)
        window.title(f"Информация об устройстве {session_row['laptop_serial']}")
        window.geometry("900x600")

        # ==== ОБЩАЯ ИНФА ====
        info = (
            f"Серийный номер: {session_row['laptop_serial']}\n"
            f"Тестер: {session_row['tester_name']}\n"
            f"Время теста: {session_row['finished_at']}\n"
            f"Статус: {session_row['overall_status']}"
        )

        label = ctk.CTkLabel(window, text=info, justify="left")
        label.pack(pady=10)

        # ================= AUDIO TABLE =================
        ctk.CTkLabel(window, text="AUDIO ТЕСТЫ").pack()

        audio_tree = ttk.Treeview(
            window,
            columns=("device_name", "left_status", "right_status", "error"),
            show="headings",
            height=4
        )

        audio_tree.heading("device_name", text="Устройство")
        audio_tree.heading("left_status", text="Левый канал")
        audio_tree.heading("right_status", text="Правый канал")
        audio_tree.heading("error", text="Ошибка")

        audio_tree.tag_configure("PASS", foreground="lightgreen")
        audio_tree.tag_configure("FAIL", foreground="red")

        for row in audio_rows:
            audio_tree.insert(
                "",
                "end",
                values=(row["device_name"], row["left_status"], row["right_status"], row["error"]),
                tags=(row["left_status"], row["right_status"])
            )

        audio_tree.pack(fill="x", padx=10, pady=5)

        # ================= USB TABLE =================
        ctk.CTkLabel(window, text="USB ТЕСТЫ").pack()

        usb_tree = ttk.Treeview(
            window,
            columns=("drive", "write", "read", "status", "error"),
            show="headings",
            height=6
        )

        usb_tree.heading("drive", text="Диск")
        usb_tree.heading("write", text="Запись MB/s")
        usb_tree.heading("read", text="Чтение MB/s")
        usb_tree.heading("status", text="Статус")
        usb_tree.heading("error", text="Ошибка")

        usb_tree.tag_configure("PASS", foreground="lightgreen")
        usb_tree.tag_configure("FAIL", foreground="red")

        for row in usb_rows:
            usb_tree.insert(
                "",
                "end",
                values=(
                    row["drive"],
                    row["write_speed"],
                    row["read_speed"],
                    row["status"],
                    row["error"]
                ),
                tags=(row["status"],)
            )

        usb_tree.pack(fill="both", expand=True, padx=10, pady=5)


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
            save_usb_test(
                laptop_serial=self.session.serial_number,
                usb_results=self.session.usb_results
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
