import time


class Listener:
    def __init__(self, sr, r, audio_queue, info_label, logging):
        self._running = False
        self.sr = sr
        self.r = r
        self.audio_queue = audio_queue
        self.logging = logging
        self.info_label = info_label
        self.is_recording = False
        self.rec_started = None

    def stop(self):
        self._running = False

    def start(self):
        self._running = True

    def run(self):
        with self.sr.Microphone() as source:
            while True:  # repeatedly listen for phrases and put the resulting audio on the audio processing job queue
                if self._running:
                    # self.logging.info("start listening..")

                    self.info_label.config(text="Listening", bg="green")
                    done = False
                    while done == False:
                        self.rec_started = time.time()
                        self.is_recording = True
                        try:
                            if self._running:
                                self.audio_queue.put(self.r.listen(source, timeout=3.0, phrase_time_limit=7))
                            #         This is done by waiting until the audio has an energy above
                            #         ``recognizer_instance.energy_threshold`` (the user has
                            #         started speaking), and then recording until it encounters
                            #         ``recognizer_instance.pause_threshold`` seconds of
                            #         non-speaking or there is no more audio input. The ending
                            #         silence is not included.
                            #
                            #         The ``timeout`` parameter is the maximum number of seconds
                            #         that this will wait for a phrase to start before giving up
                            #         and throwing an ``speech_recognition.WaitTimeoutError``
                            #         exception. If ``timeout`` is ``None``, there will be no
                            #         wait timeout.
                            #
                            #         The ``phrase_time_limit`` parameter is the maximum number
                            #         of seconds that this will allow a phrase to continue
                            #         before stopping and returning the part of the phrase
                            #         processed before the time limit was reached. The
                            #         resulting audio will be the phrase cut off at the
                            #         time limit. If ``phrase_timeout`` is ``None``, there
                            #         will be no phrase time limit.
                            #
                            #         This operation will always complete within
                            #         ``timeout + phrase_timeout`` seconds if both are
                            #         numbers, either by returning the audio data, or by
                            #         raising a ``speech_recognition.WaitTimeoutError``
                            #         exception.
                            done = True
                        except self.sr.WaitTimeoutError as e:
                            # self.logging.info("recording timeout.. redo!")
                            pass

                    self.is_recording = False
                    self.info_label.config(text="Not listening", bg="#f0f0f0")
                    elapsed_time = time.time() - self.rec_started
                    text = "I listend for %.2f sec" % elapsed_time
                    # self.rec_label.config("text")
                    self.logging.info(text)
