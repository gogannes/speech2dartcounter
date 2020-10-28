class TextProcessor():
    def __init__(self, logging):
        self.language = "not set"
        self.logging = logging

    def setLanguage(self, language):
        self.language = language
        if self.language == "de":
            self.stringsAnd = ["plus", "+", "und"]
            self.stringsTimes = ["mal", "*", "x"]
            self.stringsPoints = ["punkte", "punkt", "punkten", "."]
            self.numbers = {"null": 0, "eins": 1, "ein": 1, "einen": 1, "einem": 1, "einmal": 1, "zwei": 2, "drei": 3,
                            "vier": 4, "fünf": 5, "fuenf": 5, "sechs": 6, "sex": 6, "sieben": 7, "acht": 8, "neun": 9,
                            "zehn": 10, "elf": 11, "zwölf": 12, "zwoelf": 12, "dreizehn": 13}
        elif self.language == "en":
            self.stringsAnd = ["plus", "+", "and"]
            self.stringsTimes = ["times", "time", "*", "x"]
            self.stringsPoints = ["pints", "lbs", "points", "point", ".", "pounds"]
            self.numbers = {"zero": 0, "one": 1, "once": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
                            "sex": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12,
                            "thirteen": 13, "twenty": 20, "thirty": 30, "fourty": 40, "fifty": 50, "sixty": 60,
                            "seventy": 70, "eighty": 80, "ninety": 90}
        elif self.language == "it":
            self.stringsAnd = ["et", "e", "+"]
            self.stringsTimes = ["volta", "volte", "*", "x"]
            self.stringsPoints = ["punto", "punti", "ponti", "."]
            self.numbers = {"zero": 0, "alcuni": 0, "nero": 0, "yahoo": 0, "uno": 1, "un": 1, "una": 1, "due": 2,
                            "tre": 3, "quattro": 4, "cinque": 5, "sei": 6, "sette": 7, "otto": 8, "nove": 9,
                            "dieci": 10, "undici": 11, "dodici": 12, "tredici": 13}

        else:
            raise Exception('Unsupported Language' + self.language)

    def getInt(self, string):
        try:
            return int(string)
        except:
            try:
                return self.numbers[string.lower()]
            except:
                raise ValueError

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
            if (i + 2) < len(words) and words[i + 1].lower() in self.stringsAnd:
                product = self.getInt(words[i]) + self.getInt(words[i + 2])
                new_wordlist.append(str(product))
                new_text_for_display.append((text_for_display[i]) + "+" + (text_for_display[i + 2]))
                i = i + 3
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
        # first some "strange" manual fixes
        if self.language == "en":
            text = self.fix_pounds(text)
        if self.language == "it":
            if text == "0punti": text = "0 punti"
            if text == "hotmail.it": text = "8 punti"
            if text == "occhio.it": text = "8 punti"
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
