==================
Speech2DartCounter
==================

This project is a speech recognizer for the dart web application DartCounter (https://dartcounter.net/, x01 and single training is supported).

The program runs in parallel to the web application on the desktop PC.

After recognizing (Google Speech Recognition API) the score, the browser window (DartCounter) is put in foreground and keystrokes are sent to enter the points.

Installation of requirements for Windows:
 - ``pip install SpeechRecognition``
 - ``pip install pywinauto``
 - ``pip install PyAudio-0.2.11-cp37-cp37m-win_amd64.whl`` (see https://stackoverflow.com/a/55630212, and https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio)
 - ``pip install pyinstaller``
     - to be able to generate executables: ``pyinstaller --onefile --i icon.ico --name Speech2DartCounter_version speech2dartcounter/main.py``)
     - alternative with ``.spec``-file: ``pyinstaller Speech2DartCounter_vX_X.spec``
     - to generate executables without console window (in ``.spec`` file ``console=False``), one has to include the parameter ``stderr=subprocess.DEVNULL`` in both functions ``subprocess.Popen`` in file ``Lib/site-packages/speech_recognition/__init__.py``