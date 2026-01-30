pip install -r requirements.txt
python -m app.main

-- exe --
pip install pyinstaller
pyinstaller --onefile -w --add-data "app/audio/samples/left.wav;app/audio/samples" --add-data "app/audio/samples/right.wav;app/audio/samples" app/main.py

-- TODO --

1. добавлять в usb_tests и audio_test несколько полей для одного серийника
2. подумать что выводить в админке

final: изменить requirements.txt и удалить ненужные файлы