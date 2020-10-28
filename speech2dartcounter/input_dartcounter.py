from pywinauto.findwindows import find_window
from win32gui import SetForegroundWindow
import time
import win32com.client
from pprint import pprint


class InputDartCounter():
    def __init__(self, window_title='DartCounter*'):
        # https://stackoverflow.com/a/2791979
        self.shell = win32com.client.Dispatch("WScript.Shell")

        self.window_title = window_title

    def checkWindow(self):
        try:
            find_window(title_re=self.window_title)
            return True
        except:
            return False

    def setForeground(self):
        # https://stackoverflow.com/a/28548677
        SetForegroundWindow(find_window(title_re=self.window_title))

    def enter(self, sleep=0.05):
        time.sleep(sleep)
        self.shell.SendKeys("{ENTER}")

    def enterPoints(self, points, noEnters=1, sleep=0.05):
        time.sleep(sleep)
        self.shell.SendKeys(str(points))
        for i in range(0, noEnters):
            time.sleep(sleep)
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
