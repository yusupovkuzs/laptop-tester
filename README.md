pip install -r requirements.txt
Change DATABASE_DIR in config.py

удалить старые таблицы в бд
uncomment init_db in main.py for the first run
python -m app.main

-- exe --
pyinstaller --onefile -w --add-data "app/audio/samples/left.wav;app/audio/samples" --add-data "app/audio/samples/right.wav;app/audio/samples" app/main.py

-- TODO --

1. обязательно наушники