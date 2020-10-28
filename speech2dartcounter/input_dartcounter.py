from pywinauto.findwindows import find_window
from win32gui import SetForegroundWindow
from tkinter import messagebox as mbox
import time
import win32com.client
from pprint import pprint


class InputDartCounter():
    def __init__(self, window_title='DartCounter*'):
        # https://stackoverflow.com/a/2791979
        self.shell = win32com.client.Dispatch("WScript.Shell")
        self.window_title = window_title
        self.numberOfEnters = 1

    def checkWindow(self):
        try:
            find_window(title_re=self.window_title)
            return True
        except:
            return False

    def setForeground(self):
        success = False
        while success == False:
            try:
                # https://stackoverflow.com/a/28548677
                SetForegroundWindow(find_window(title_re=self.window_title))
                success = True
            except:
                mbox.showwarning("Warning", "I could not bring window in foreground! Is it open only once?\n"
                                            "Try to open browser window 'DartCounter...' (dartcounter.net) and then press 'OK'")

    def enter(self):
        time.sleep(0.1)
        self.shell.SendKeys("{ENTER}")

    def enterPoints(self, points):
        time.sleep(0.1)
        self.shell.SendKeys(str(points))
        time.sleep(0.05)
        for i in range(0, self.numberOfEnters):
            if i > 0:
                time.sleep(0.3)
            self.shell.SendKeys("{ENTER}")


if __name__ == "__main__":
    import time

    dc = InputDartCounter()
    t1 = time.time()
    check = dc.checkWindow()
    print("check took %.2f sec" % (time.time() - t1))
    print("found window? %s" % check)
    if check == True:
        t2 = time.time()
        print(dc.setForeground())
        print("forground took %.2f sec" % (time.time() - t2))
