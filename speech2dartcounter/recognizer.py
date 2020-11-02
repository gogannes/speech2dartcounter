import time
import winsound
from tkinter import DISABLED, END
import tkinter.font as tkFont

from speech2dartcounter.text_processor import TextProcessor


class Recognizer:
    def __init__(self, sr, r, audio_queue, dc,
                 history_text_queue, points_label_queue, google_label_queue,
                 logging):
        self._running = False
        self.sr = sr
        self.r = r
        self.audio_queue = audio_queue
        self.processor = TextProcessor(logging)
        self.dc = dc
        self.points_label_queue = points_label_queue
        self.google_label_queue = google_label_queue
        self.history_text_queue = history_text_queue
        self.logging = logging
        self.language = None
        self.kill = False  # if true, infinite loop is stopped
        self.is_finished = False

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

    def is_running(self):
        if self.is_finished:
            return False
        else:
            return True

    def run(self):
        while self.kill == False:
            if self.audio_queue.qsize() > 0:
                self.logging.info("queue size: " + str(self.audio_queue.qsize()))

            audio = self.audio_queue.get()  # retrieve the next audio processing job from the main thread
            if audio is None: break  # stop processing if the main thread is done
            if self._running is False: break
            self.logging.info('processing..')

            # received audio data, now we'll recognize it using Google Speech Recognition
            try:
                # for testing purposes, we're just using the default API key
                # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
                # instead of `r.recognize_google(audio)`
                start_time = time.time()

                self.points_label_queue.put({
                    "text": "Google... (%i in queue)" % self.audio_queue.qsize() if self.audio_queue.qsize() > 0 else "Google...",
                    "size": 16})
                text = self.r.recognize_google(audio, language=self.language, logging=self.logging)

                self.points_label_queue.put({"text": "", "size": 24})
            except self.sr.UnknownValueError as e:
                self.logging.info("Google didn't understand.")
                self.history_text_queue.put("Google didn't understand.\n")
                elapsed_time = time.time() - start_time
                self.google_label_queue.put({"text": "Google: %.2f sec" % elapsed_time, })
                self.points_label_queue.put({"text": "?", "size": 24})
                continue
            except self.sr.RequestError as e:
                self.logging.info("Could not request results from Google Speech Recognition service; {0}".format(e))
                self.points_label_queue.put({"text": "Google Error", "size": 24})
                continue
            except Exception as e:
                self.logging.error(e)

            self.audio_queue.task_done()  # mark the audio processing job as completed in the queue
            elapsed_time = time.time() - start_time
            self.logging.info("Google Speech Recognition took %.2f sec" % elapsed_time)
            self.google_label_queue.put({"text": "Google: %.2f sec" % elapsed_time, })
            self.logging.info("I understood: '%s'" % text)
            self.history_text_queue.put("'%s' -> " % text)

            if ("enter" in text.lower()) or \
                    ("ente" in text.lower()) or \
                    ("penta" in text.lower()) or \
                    ("okay" in text.lower()) or \
                    ("ok" in text.lower()):
                self.logging.info("word 'enter' detected, I just press enter.")
                self.history_text_queue.put("Press Enter\n")
                self.points_label_queue.put({"text": "Enter!"})
                self.dc.setForeground()
                time.sleep(0.1)
                self.dc.enter()
                continue
            if ("rückgängig" in text.lower()) or \
                    ("falsch" in text.lower()) or \
                    ("undo" in text.lower()) or \
                    ("back" in text.lower()) or \
                    ("annullare" in text.lower()):
                self.logging.info("word 'undo' detected, I just press enter.")
                self.history_text_queue.put("Undo\n")
                self.points_label_queue.put({"text": "Enter!"})

                self.dc.setForeground()
                frequency = 440 * 2  # Set Frequency To 2500 Hertz
                duration = 150  # Set Duration To 1000 ms == 1 second
                winsound.Beep(frequency, duration)
                self.dc.undo()
                continue

            (punkte, punkte_str) = self.processor.process(text)
            if punkte != -1:
                if self._running:
                    if ("+" in punkte_str) or ("*" in punkte_str):
                        self.logging.info('I enter: %s = %s ' % (punkte_str, str(punkte)))
                        self.history_text_queue.put("%s = %s\n" % (punkte_str, str(punkte)))

                        punkte_str = punkte_str + " \n= " + str(punkte)
                    else:
                        self.logging.info('I enter: %s ' % str(punkte))
                        self.history_text_queue.put("%s\n" % (str(punkte)))

                    self.points_label_queue.put({"text": punkte_str})

                    self.dc.setForeground()
                    time.sleep(0.1)
                    self.dc.enterPoints(points=punkte)
                else:
                    self.logging.info('I don''t enter results as stopped by user')
            else:
                self.history_text_queue.put("?\n")
                self.points_label_queue.put({"text": "?"})
        self.is_finished = True
