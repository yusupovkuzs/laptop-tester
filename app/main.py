# from app.ui.main_window import MainWindow
from app.db.init_db import init_db
from app.ui.new_main_window import MainWindow

def main():
    # init_db()
    app = MainWindow()
    app.mainloop()

if __name__ == "__main__":
    main()
