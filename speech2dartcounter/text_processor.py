import json
import os.path
from tkinter import messagebox as mbox


class TextProcessor():
    def __init__(self, logging, file='languages.json'):
        self.language = "not set"
        self.logging = logging

        try:
            if os.path.isfile(file):
                self.logging.info("loading and re-formatting config: " + file)
                with open(file, 'r', encoding='UTF-8') as f:
                    self.config = json.load(f, encoding='UTF-8')
                # write it again, to maintain nice formatting
                with open(file, 'w', encoding='UTF-8') as f:
                    json.dump(self.config, indent=2, fp=f, ensure_ascii=False)
            else:
                self.logging.info("file '%s' not found. Create it." % file)
                self.config = self.setConfig()
                with open(file, 'w', encoding='UTF-8') as f:
                    json.dump(self.config, indent=2, fp=f, ensure_ascii=False)
        except:
            mbox.showerror("Error", "Could not read 'languages.json' properly. Delete this file and start again!")

    def setConfig(self):
        config = dict()
        config = {
            "de": {
                "and": [
                    "plus",
                    "+",
                    "und"
                ],
                "times": [
                    "mal",
                    "*",
                    "x"
                ],
                "points": [
                    "punkte",
                    "punkt",
                    "punkten",
                    "."
                ],
                "numbers": {
                    "null": 0,
                    "eins": 1,
                    "ein": 1,
                    "einen": 1,
                    "einem": 1,
                    "einmal": 1,
                    "zwei": 2,
                    "drei": 3,
                    "vier": 4,
                    "fünf": 5,
                    "fuenf": 5,
                    "sechs": 6,
                    "sex": 6,
                    "sieben": 7,
                    "acht": 8,
                    "neun": 9,
                    "zehn": 10,
                    "elf": 11,
                    "zwölf": 12,
                    "zwoelf": 12,
                    "dreizehn": 13
                },
                "enter": [
                    "enter",
                    "ok",
                    "okay",
                    "eingabe",
                    "ente"
                ],
                "undo": [
                    "rückgängig",
                    "falsch",
                    "zurück"
                ],
                "replace": {
                    "nullpunkt": "0 punkte",
                    "nullpunkte": "0 punkte"
                }
            },
            "en": {
                "and": [
                    "plus",
                    "+",
                    "and"
                ],
                "times": [
                    "times",
                    "time",
                    "*",
                    "x"
                ],
                "points": [
                    "pints",
                    "lbs",
                    "points",
                    "point",
                    ".",
                    "pounds"
                ],
                "numbers": {
                    "zero": 0,
                    "one": 1,
                    "once": 1,
                    "two": 2,
                    "three": 3,
                    "four": 4,
                    "five": 5,
                    "six": 6,
                    "sex": 6,
                    "seven": 7,
                    "eight": 8,
                    "nine": 9,
                    "ten": 10,
                    "eleven": 11,
                    "twelve": 12,
                    "thirteen": 13,
                    "twenty": 20,
                    "thirty": 30,
                    "fourty": 40,
                    "fifty": 50,
                    "sixty": 60,
                    "seventy": 70,
                    "eighty": 80,
                    "ninety": 90
                },
                "enter": [
                    "enter",
                    "ok",
                    "okay"
                ],
                "undo": [
                    "undo",
                    "back"
                ],
                "replace": {}
            },
            "it": {
                "and": [
                    "et",
                    "e",
                    "+"
                ],
                "times": [
                    "volta",
                    "volte",
                    "*",
                    "x"
                ],
                "points": [
                    "punto",
                    "punti",
                    "ponti",
                    "."
                ],
                "numbers": {
                    "zero": 0,
                    "alcuni": 0,
                    "nero": 0,
                    "yahoo": 0,
                    "uno": 1,
                    "un": 1,
                    "una": 1,
                    "due": 2,
                    "tre": 3,
                    "quattro": 4,
                    "cinque": 5,
                    "sei": 6,
                    "sette": 7,
                    "otto": 8,
                    "nove": 9,
                    "dieci": 10,
                    "undici": 11,
                    "dodici": 12,
                    "tredici": 13
                },
                "enter": [
                    "enter",
                    "ok",
                    "okay",
                    "invio",
                    "penta"
                ],
                "undo": [
                    "annullare",
                    "indietro"
                ],
                "replace": {
                    "0punti": "0 punti",
                    "hotmail.it": "8 punti",
                    "occhio.it": "8 punti"
                }
            }
        }
        return config

    def setLanguage(self, language):
        self.language = language
        self.stringsAnd = self.config[self.language]["and"]
        self.stringsTimes = self.config[self.language]["times"]
        self.stringsPoints = self.config[self.language]["points"]
        self.numbers = self.config[self.language]["numbers"]

        self.enter = self.config[self.language]["enter"]
        self.undo = self.config[self.language]["undo"]

        self.replace = self.config[self.language]["replace"]

    def getInt(self, string):
        try:
            return int(string)
        except:
            try:
                return self.numbers[string.lower()]
            except:
                raise ValueError

    def isInt(self, string):
        try:
            self.getInt(string)
            return True
        except:
            return False

    def multiply(self, words):
        new_wordlist = []
        new_text_for_display = []
        i = 0
        while i < len(words):
            if (i + 2) < len(words) and words[i + 1].lower() in self.stringsTimes:
                product = self.getInt(words[i]) * self.getInt(words[i + 2])
                new_wordlist.append(str(product))
                new_text_for_display.append(words[i] + "*" + words[i + 2])
                i = i + 3
            else:
                new_wordlist.append(words[i])
                new_text_for_display.append(words[i])
                i = i + 1
        return (new_wordlist, new_text_for_display)

    def adding(self, words, text_for_display):
        i = 0
        new_wordlist = []
        new_text_for_display = []
        while i < len(words):
            if i + 2 < len(words):
                # check whether 'and' is there, and
                # check whether at least one of the surrounding words is a number,
                # else the 'and' might just have been part of an ordinary sentence...
                if (words[i + 1].lower() in self.stringsAnd) and \
                        (self.isInt(words[i]) or self.isInt((words[i + 2]))):

                    product = self.getInt(words[i]) + self.getInt(
                        words[i + 2])  # if it doesn't work, an exception is thrown
                    new_wordlist.append(str(product))
                    new_text_for_display.append((text_for_display[i]) + "+" + (text_for_display[i + 2]))
                    i = i + 3
                else:
                    new_wordlist.append(words[i])
                    new_text_for_display.append((text_for_display[i]))
                    i = i + 1
            else:
                new_wordlist.append(words[i])
                new_text_for_display.append((text_for_display[i]))
                i = i + 1
        return (new_wordlist, new_text_for_display)

    def fix_due_punti(self, text):
        # ":" -> "2."
        i = 0
        new_text = []
        while i < len(text):
            c = text[i]
            if c == ":":
                new_text.append("2")
                new_text.append(".")
            else:
                new_text.append(c)
            i = i + 1
        new_text = "".join(new_text)
        return new_text

    def fix_pounds(self, text):
        # "£49"-> " 49."
        text = text + " "
        i = 0
        while i < len(text):
            c = text[i]
            if c == "£":
                temp = list(text)
                temp[i] = " "
                text = "".join(temp)
                # print("text:   " + text)
                # print("remain: " + text[(i + 1):len(text)])
                for ii, cc in enumerate(text[(i + 1):len(text)]):
                    if cc == " ":
                        temp = list(text)
                        temp[i + ii + 1] = "."
                        text = "".join(temp)
                        break
            i = i + 1
        return text

    def process(self, text):
        for key in self.replace.keys():
            text = text.lower().replace(key, self.replace[key])

        # some "strange" manual fixes
        if self.language == "en":
            text = self.fix_pounds(text)
        if self.language == "it":
            text = self.fix_due_punti(text)

        text = text.replace("+", " + ")
        text = text.replace(".", " . ")
        text = text.replace("*", " * ")
        words = text.split()
        try:
            if words[0].lower() in (self.stringsTimes + self.stringsAnd):
                print("seems that I missed the beginning...")
                return (-1, "")
            (words, text_for_display) = self.multiply(words)
            # print(words)
            (words, text_for_display) = self.adding(words, text_for_display)
            # print(words)
            (words, text_for_display) = self.adding(words, text_for_display)
            # print(words)
            points = None
            for i in range(0, len(words)):
                if words[i].lower() in self.stringsPoints:
                    if (i - 1) >= 0:
                        points = self.getInt(words[i - 1])
                        displaytext = text_for_display[i - 1]
                        if ("+" in displaytext) or ("*" in displaytext):
                            pass
                        else:
                            displaytext = str(self.getInt(displaytext))
            if points is None:
                self.logging.info("Keyword POINTS not found.")
                return (-1, "")
            else:
                # print(displaytext)
                # print(points)
                return (points, displaytext)
        except ValueError as e:
            # print(e)
            self.logging.info("Wrong grammar.")
            return (-1, "")


if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.INFO)

    processor = TextProcessor(logging)

    processor.setLanguage("de")
    text = "jetzt habe ich 10 Punkte und dieses und sowie dieses und hat nichts zu sagen"
    assert processor.process(text) == (10, "10"), processor.process(text)

    processor.setLanguage("de")
    text = "aads ötext 12 plus 40 * 2 plus 23 punkte"
    assert processor.process(text) == (115, "12+40*2+23"), processor.process(text)

    processor.setLanguage("de")
    text = "asd drei  punkte "
    assert processor.process(text) == (3, "3"), processor.process(text)

    processor.setLanguage("en")
    text = "12 + £49 "
    assert processor.process(text) == (61, "12+49"), processor.process(text)

    processor.setLanguage("it")
    text = "4 + : "
    assert processor.process(text) == (6, "4+2"), processor.process(text)
