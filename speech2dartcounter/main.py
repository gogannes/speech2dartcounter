import os
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
import os.path

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
    listener.start_recording_loop()
    recognizer.start()


def stop_action():
    stop_button.config(state="disabled")
    start_button.config(state="normal")
    listener.stop_recording_loop()
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
            elif key == "size":
                label.config(font=tkFont.Font(size=content_dict[key]))
            else:
                raise Exception("unknown key! " + key)


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
        pass
    window.after(25, updater)


def on_closing():
    logging.info("Cleanup...")

    listener.stop_recording_loop()
    listener.kill = True
    recognizer.stop()
    recognizer.kill = True

    # end listening
    if listener.is_running():
        logging.info("listener function is still recording...")
        info_label.config(text="Waiting until recording\nhas finished...",
                          font=tkFont.Font(size=14), fg="red", bg="black", anchor='c')
        window.update()
    while listener.is_running():
        if listener.is_recording:
            elapsed = time.time() - listener.rec_started
            rec_label.config(text="Record: %.1f sec" % elapsed)
        window.after(100)
        window.update()
    logging.info("Listening function finished.")

    while listen_thread.is_alive():
        window.after(100)
    logging.info("Listening thread finished.")

    # end recognizing
    audio_queue.put(None)  # tell the recognize_thread to stop

    if recognizer.is_running():
        logging.info("recognizer function is still running...")
        info_label.config(text="Waiting until recognizing\nhas finished...",
                          font=tkFont.Font(size=14), fg="red", bg="black", anchor='c')
        window.update()
    while recognizer.is_running():
        window.after(100)
    logging.info("Recognizer function finished.")

    while recognize_thread.is_alive():
        window.after(100)
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

window.title("Speech2DartCounter")

window.attributes('-topmost', True)
# window.resizable(0, 0)
# window.attributes('-toolwindow', True)

if os.path.isfile('icon.ico'):
    window.iconbitmap('icon.ico')
else:
    logging.info("'icon.ico' not found.")

start_button = Button(window, text="Start", command=start_action, width=25, height=3)
stop_button = Button(window, text="Stop", command=stop_action, width=25, height=3)
info_label = Label(window, text="Not listening", bg="#f0f0f0", font=tkFont.Font(size=14), anchor='c', width=20,
                   height=4)
points_label = Label(window, text=" - ", bg="#f0f0f0", font=tkFont.Font(size=24), anchor='c', width=20, height=4)

language_label = Label(window, text="Language:", bg="#f0f0f0", anchor='w')
language_om = OptionMenu(window, lang_var, *language_optionList, command=change_language)

enter_spinbox = Spinbox(window, from_=0, to=3, textvariable=enters_var, command=change_no_enters, width=2)
spinbox_label = Label(window, text="No. of enters:", bg="#f0f0f0", anchor='w')

var_foreground = IntVar()
var_foreground.set(1)
topmost_checkbutton = Checkbutton(window, text="Keep this window in foreground",
                                  variable=var_foreground, command=set_topmost,
                                  compound="left")

sensitivity_label = Label(window, text="Threshold:", bg="#f0f0f0", anchor='w')
sensitivity_scale = Scale(window, from_=0, to=4000, orient=HORIZONTAL, command=change_sensitivity)

google_label = Label(window, text="Google: - sec", bg="#f0f0f0", anchor='w')
rec_label = Label(window, text="Record: - sec", bg="#f0f0f0", anchor='w')
mail_label = Label(window, text="gogannes@gmail.com", bg="#f0f0f0", anchor='c')

frame_history = Frame(window)
history_scrollbar = Scrollbar(frame_history)
history_text = Text(frame_history, height=8, width=45)
history_scrollbar.config(command=history_text.yview)
history_text.config(yscrollcommand=history_scrollbar.set)

history_text.insert(END, "Press start and say something!\n")
history_text.config(state=DISABLED)

frame_history.grid_columnconfigure(0, minsize=0, weight=1)
frame_history.grid_columnconfigure(1, minsize=0, weight=1)
frame_history.grid_rowconfigure(0, minsize=0, weight=1)
frame_history.grid_rowconfigure(1, minsize=0, weight=1)

history_text.pack(side=LEFT, fill="both")
history_scrollbar.pack(side=RIGHT, fill="both")

window.grid_columnconfigure(0, minsize=50, weight=1, pad=10)
window.grid_columnconfigure(1, minsize=50, weight=1, pad=10)
window.grid_rowconfigure(0, minsize=50, weight=1, pad=10)
window.grid_rowconfigure(1, minsize=50, weight=1, pad=10)

start_button.grid(column=0, row=0)
stop_button.grid(column=1, row=0)

info_label.grid(column=0, row=1, columnspan=2, pady=5)
points_label.grid(column=0, row=2, columnspan=2, )

language_label.grid(column=0, row=3, columnspan=1, sticky="E", padx=10)
language_om.grid(column=1, row=3, columnspan=1, sticky="W")
spinbox_label.grid(column=0, row=4, columnspan=1, sticky="E", padx=10)
enter_spinbox.grid(column=1, row=4, columnspan=1, sticky="W")
sensitivity_label.grid(column=0, row=5, columnspan=1, sticky="E", padx=10)
sensitivity_scale.grid(column=1, row=5, columnspan=1, sticky="W")
topmost_checkbutton.grid(column=0, row=6, columnspan=2)

google_label.grid(column=0, row=7, columnspan=1)
rec_label.grid(column=1, row=7, columnspan=1)

frame_history.grid(column=0, row=8, columnspan=2, padx=10, )

mail_label.grid(column=0, row=9, columnspan=2, padx=5, pady=5)

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
os._exit(0)
