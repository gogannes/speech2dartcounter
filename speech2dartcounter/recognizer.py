import time
from tkinter import DISABLED, END

from speech2dartcounter.text_processor import TextProcessor


class Recognizer:
    def __init__(self, sr, r, audio_queue, dc, history_text, points_label, google_label, logging):
        self._running = False
        self.sr = sr
        self.r = r
        self.audio_queue = audio_queue
        self.processor = TextProcessor(logging)
        self.dc = dc
        self.points_label = points_label
        self.google_label = google_label
        self.history_text = history_text
        self.logging = logging
        self.language = None

    def add_history_text(self, text):
        self.history_text.config(state='normal')
        self.history_text.insert(END, text)
        self.history_text.config(state=DISABLED)
        self.history_text.see("end")

    def setLanguage(self, language):
        self.language = language
        if language == "de-DE":
            self.processor.setLanguage("de")
        elif language == "en-GB" or language == "en-US":
            self.processor.setLanguage("en")
        elif language == "it-IT":
            self.processor.setLanguage("it")

    def stop(self):
        self._running = False

    def start(self):
        self._running = True

    def run(self):
        while True:
            if self.audio_queue.qsize() > 0:
                self.logging.info("queue size: " + str(self.audio_queue.qsize()))
            audio = self.audio_queue.get()  # retrieve the next audio processing job from the main thread
            if audio is None: break  # stop processing if the main thread is done
            self.logging.info('processing..')

            # received audio data, now we'll recognize it using Google Speech Recognition
            try:
                # for testing purposes, we're just using the default API key
                # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
                # instead of `r.recognize_google(audio)`
                start_time = time.time()
                text = self.r.recognize_google(audio, language=self.language)
            except self.sr.UnknownValueError:
                self.logging.info("Google didn't understand.")
                self.add_history_text("Google didn't understand.\n")
                continue
            except self.sr.RequestError as e:
                self.logging.info("Could not request results from Google Speech Recognition service; {0}".format(e))
                continue

            self.audio_queue.task_done()  # mark the audio processing job as completed in the queue
            elapsed_time = time.time() - start_time
            self.logging.info("Google Speech Recognition took %.2f sec" % elapsed_time)
            self.google_label.config(text="Google: %.2f sec" % elapsed_time)
            self.logging.info("I understood: '%s'" % text)
            self.add_history_text("'%s' -> " % text)

            if ("enter" in text.lower()) or \
                    ("ente" in text.lower()) or \
                    ("penta" in text.lower()) or \
                    ("okay" in text.lower()) or \
                    ("ok" in text.lower()):
                self.logging.info("word 'enter' detected, I just press enter.")
                self.add_history_text("Press Enter\n")
                self.dc.setForeground()
                self.dc.enter()
                continue

            (punkte, punkte_str) = self.processor.process(text)
            if punkte != -1:
                if self._running:
                    self.dc.setForeground()
                    self.dc.enterPoints(points=punkte)
                    if ("+" in punkte_str) or ("*" in punkte_str):
                        self.logging.info('I enter: %s = %s ' % (punkte_str, str(punkte)))
                        self.add_history_text("%s = %s\n" % (punkte_str, str(punkte)))

                        punkte_str = punkte_str + " \n= " + str(punkte)
                    else:
                        self.logging.info('I enter: %s ' % str(punkte))
                        self.add_history_text("%s\n" % (str(punkte)))

                    self.points_label.config(text=punkte_str)
                else:
                    self.logging.info('I don''t enter results as stopped by user')
            else:
                self.add_history_text("?\n")
