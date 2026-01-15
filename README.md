pip install -r requirements.txt
python -m app.main

-- exe --
pip install pyinstaller
pyinstaller --onefile -w   --add-data "app/audio/samples/left.wav;app/audio/samples"   --add-data "app/audio/samples/right.wav;app/audio/samples"   app/main.py
