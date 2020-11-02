import time
from tkinter import *
import tkinter.font as tkFont
from tkinter.messagebox import showerror, showinfo
import speech_recognition as sr
from threading import Thread
from queue import Queue, Empty
import logging
from speech2dartcounter.listener import Listener
from speech2dartcounter.recognizer import Recognizer
from speech2dartcounter.input_dartcounter import InputDartCounter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(threadName)s: [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("log.txt"),  # logging to file
        logging.StreamHandler()  # logging to console
    ]
)

window = Tk()


def start_action():
    start_button.config(state="disabled")
    stop_button.config(state="normal")
    listener.start()
    recognizer.start()


def stop_action():
    stop_button.config(state="disabled")
    start_button.config(state="normal")
    listener.stop()
    recognizer.stop()


def set_topmost():
    window.attributes('-topmost', bool(var_foreground.get()))
    logging.info("Set window topmost: %s" % bool(var_foreground.get()))


def change_sensitivity(var):
    r.energy_threshold = int(var)  # energy_threshold.get()
    logging.info("Set energy_threshold to: %.1f" % r.energy_threshold)


def change_language(var):
    recognizer.setLanguage(var)
    logging.info("Set language to: %s" % var)


def change_no_enters():
    dc.numberOfEnters = int(enter_spinbox.get())
    logging.info("Set number of enters to: %s" % dc.numberOfEnters)


def update_label(queue, label):
    try:
        content_dict = queue.get_nowait()  # retrieve the next audio processing job from the main thread
    except Empty:
        pass
    else:
        for key in content_dict:
            # print(key, '->', content_dict[key])
            if key == "text":
                label.config(text=content_dict[key])
            elif key == "fg":
                label.config(fg=content_dict[key])
            elif key == "bg":
                label.config(bg=content_dict[key])
            elif key == "font":
                label.config(font=tkFont.Font(size=content_dict[key]))


def update_history_text(text_queue, history_text):
    try:
        text = text_queue.get_nowait()  # retrieve the next audio processing job from the main thread
    except Empty:
        pass
    else:
        history_text.config(state='normal')
        history_text.insert(END, text)
        history_text.config(state=DISABLED)
        history_text.see("end")


def updater():
    update_label(info_label_queue, info_label)
    update_label(points_label_queue, points_label)
    update_label(google_label_queue, google_label)
    update_history_text(history_text_queue, history_text)

    if listener.is_recording:
        elapsed = time.time() - listener.rec_started
        rec_label.config(text="Record: %.1f sec" % elapsed)

    # check whether all threads are alive
    if not recognize_thread.is_alive():
        logging.error("Recognize thread not running!")
        points_label.config(text="ERROR RESTART!",
                            font=tkFont.Font(size=14), fg="red", bg="black", anchor='c')
    elif not listen_thread.is_alive():
        logging.error("Listen thread not running!")
        points_label.config(text="ERROR RESTART!",
                            font=tkFont.Font(size=14), fg="red", bg="black", anchor='c')
    else:
        window.after(25, updater)


def on_closing():
    logging.info("Cleanup...")

    listener.stop()  # -> _running=False
    listener.kill = True
    recognizer.stop()  # -> _running=False
    recognizer.kill = True

    # end listening
    if listener.is_running():
        logging.info("listener function is still recording...")
        info_label.config(text="Waiting until recording\nhas finished...",
                          font=tkFont.Font(size=14), fg="red", bg="black", anchor='c')
        window.update()
    while listener.is_running():
        time.sleep(.1)
    logging.info("Listening function finished.")

    while listen_thread.is_alive():
        time.sleep(0.1)
    logging.info("Listening thread finished.")

    # end recognizing
    audio_queue.put(None)  # tell the recognize_thread to stop

    if recognizer.is_running():
        logging.info("recognizer function is still running...")
        info_label.config(text="Waiting until recognizing\nhas finished...",
                          font=tkFont.Font(size=14), fg="red", bg="black", anchor='c')
        window.update()
    while recognizer.is_running():
        time.sleep(.1)
    logging.info("Recognizer function finished.")

    while recognize_thread.is_alive():
        time.sleep(0.1)
    logging.info("Recognizer thread finished.")

    recognize_thread.join()  # wait for the recognize_thread to actually stop
    listen_thread.join()

    window.destroy()


language_optionList = ('de-DE', 'en-GB', 'en-US', 'it-IT')
lang_var = StringVar()
lang_var.set(language_optionList[0])  # initialize with german language

enters_var = StringVar()
enters_var.set("1")

info_label_queue = Queue()
points_label_queue = Queue()
google_label_queue = Queue()
history_text_queue = Queue()

window.title("Speech 2 DartCounter")
totalwith = 550
totalheight = 1000
posx = 2000
posy = 100
window.geometry(str(totalwith) + "x" + str(totalheight) + "+" + str(posx) + "+" + str(posy))
window.attributes('-topmost', True)
window.resizable(0, 0)
# window.attributes('-toolwindow', True)
window.iconbitmap('../icon.ico')

start_button = Button(window, text="Start", command=start_action)
stop_button = Button(window, text="Stop", command=stop_action)
info_label = Label(window, text="Not listening", bg="#f0f0f0", font=tkFont.Font(size=14), anchor='c')
points_label = Label(window, text=" - ", font=tkFont.Font(size=24), anchor='c')
language_label = Label(window, text="Language:", bg="#f0f0f0", anchor='w')
language_om = OptionMenu(window, lang_var, *language_optionList, command=change_language)
enter_spinbox = Spinbox(window, from_=0, to=3, textvariable=enters_var, command=change_no_enters)
spinbox_label = Label(window, text="No. of enters:", bg="#f0f0f0", anchor='w')
var_foreground = IntVar()
var_foreground.set(1)
topmost_checkbutton = Checkbutton(window, text="Keep foreground",
                                  variable=var_foreground, command=set_topmost,
                                  anchor="w")

sensitivity_label = Label(window, text="Threshold:", bg="#f0f0f0", anchor='w')
sensitivity_scale = Scale(window, from_=0, to=4000, orient=HORIZONTAL, command=change_sensitivity)
google_label = Label(window, text="Google: - sec", bg="#f0f0f0", anchor='w')
rec_label = Label(window, text="Record: - sec", bg="#f0f0f0", anchor='w')
mail_label = Label(window, text="gogannes@gmail.com", bg="#f0f0f0", anchor='c')

history_scrollbar = Scrollbar(window)
history_text = Text(window, height=4, width=50)
history_scrollbar.config(command=history_text.yview)
history_text.config(yscrollcommand=history_scrollbar.set)

history_text.insert(END, "Press start and say something!\n")
history_text.config(state=DISABLED)

mleft = 10
start_button.place(x=mleft, y=10, width=totalwith / 2 - 2 * mleft, height=100)
stop_button.place(x=mleft + totalwith / 2, y=10, width=totalwith / 2 - 2 * mleft, height=100)

start_at = 130
info_label.place(x=mleft, y=start_at, width=totalwith - 2 * mleft, height=100)
points_label.place(x=mleft, y=start_at + 100, width=totalwith - 2 * mleft, height=150)

start_at = start_at + 250
language_label.place(x=mleft, y=start_at, width=120, height=35)
language_om.place(x=140, y=start_at, width=150, height=35)
enter_spinbox.place(x=totalwith - mleft - 50, y=start_at, width=50, height=35)
spinbox_label.place(x=mleft + totalwith / 2 + 30, y=start_at, width=150, height=35)

start_at = start_at + 40
sensitivity_label.place(x=mleft, y=start_at, width=totalwith / 2 - mleft, height=35)
topmost_checkbutton.place(x=mleft + totalwith / 2 + 30, y=start_at)
sensitivity_scale.place(x=mleft, y=start_at + 35, width=totalwith / 2 - mleft, height=70)

start_at = start_at + 110
rec_label.place(x=mleft, y=start_at, width=totalwith / 2 - 2 * mleft, height=35)
google_label.place(x=mleft + totalwith / 2, y=start_at, width=totalwith / 2 - 2 * mleft, height=35)

start_at = start_at + 40
width_scrollbar = 30
history_scrollbar.place(x=totalwith - mleft - width_scrollbar, y=start_at, width=width_scrollbar, height=300)
history_text.place(x=mleft, y=start_at, width=totalwith - 2 * mleft - width_scrollbar, height=385)

mail_label.place(x=mleft, y=totalheight - 40, width=totalwith - 2 * mleft, height=35)

r = sr.Recognizer()
r.energy_threshold = 2000  # minimum audio energy to consider for recording
# Typical values for a silent room are 0 to 100, and typical values for
# speaking are between 150 and 3500
sensitivity_scale.set(int(r.energy_threshold))
r.dynamic_energy_threshold = False
r.pause_threshold = 0.6  # seconds of non-speaking audio before a phrase is considered complete

audio_queue = Queue()
dc = InputDartCounter(logging=logging, window_title='DartCounter*')

recognizer = Recognizer(sr, r, audio_queue, dc, history_text_queue, points_label_queue, google_label_queue, logging)
recognizer.setLanguage(lang_var.get())
recognize_thread = Thread(target=recognizer.run)
recognize_thread.daemon = True
recognize_thread.name = "Analyzer"
recognize_thread.start()

listener = Listener(sr, r, audio_queue, info_label_queue, logging)
listen_thread = Thread(target=listener.run)
listen_thread.daemon = True
listen_thread.name = "Listener"
listen_thread.start()

updater()
stop_button.config(state="disabled")

dc.numberOfEnters = int(enter_spinbox.get())

window.protocol("WM_DELETE_WINDOW", on_closing)

window.mainloop()

logging.info("Exiting...")
