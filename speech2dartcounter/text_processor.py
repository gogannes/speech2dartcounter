import json


class TextProcessor():
    def __init__(self, logging, file='languages.json'):
        self.language = "not set"
        self.logging = logging

        self.logging.info("loading and re-formatting config: " + file)

        with open(file, 'r', encoding='UTF-8') as f:
            self.config = json.load(f, encoding='UTF-8')
        # write it again, to maintain nice formatting
        with open(file, 'w', encoding='UTF-8') as f:
            json.dump(self.config, indent=2, fp=f, ensure_ascii=False)

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
