import os
import sys
import time
import datetime
import difflib

import pyttsx3
from halo import Halo
import keyboard
import win32gui
from win32gui import GetWindowText, GetForegroundWindow

from Speech2Text import online
from WakeWord.picoWW import computerWW

engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)
engine.setProperty('rate', 162)
engine.setProperty('volume', 1)


def speak(audio):
    print(audio)
    engine.say(audio)
    engine.runAndWait()


def getAll_programs(program_path):
    tempList = []
    tempList_paths = []
    for program in os.listdir(program_path):
        # program_path2 = os.path.join(os.path.dirname(program_path), program)
        program_path2 = os.path.join(program_path, program)
        if os.path.isdir(program_path2):
            secList, secList_paths = getAll_programs(program_path2)
            for temp_Program in secList:
                tempList.append((str(temp_Program).lower()).split('.')[0])
            for temp_paths in secList_paths:
                tempList_paths.append(temp_paths)
        else:
            if 'lnk' in program:
                tempList.append((str(program).lower()).split('.')[0])
                tempList_paths.append(program_path2)
    return tempList, tempList_paths


def getProgramsList():
    programs, programPaths = list(), list()

    programs_path = r'C:/ProgramData/Microsoft/Windows/Start Menu/Programs/'
    programs_path2 = r'C:/Users/tanmay/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/'

    programs1, programPaths1 = getAll_programs(programs_path)
    programs2, programPaths2 = getAll_programs(programs_path2)

    for temp in programs1:
        programs.append(temp)
    for temp in programs2:
        programs.append(temp)

    for temp in programPaths1:
        programPaths.append(temp)
    for temp in programPaths2:
        programPaths.append(temp)

    return programs, dict(zip(programs, programPaths))


class dodo():
    def __init__(self):
        self.setPrint = True
        self.newList = list()

    def run(self):
        win32gui.EnumWindows(self.winEnumHandler, None)
        return self.newList

    def winEnumHandler(self, hwnd, ctx):
        if win32gui.IsWindowVisible(hwnd):
            # print(hex(hwnd), win32gui.GetWindowText(hwnd))
            txt = win32gui.GetWindowText(hwnd)
            if txt:
                if 'Microsoft Text Input Application' in txt:
                    self.setPrint = False
                else:
                    if self.setPrint:
                        # print(txt)
                        self.newList.append(txt)


if __name__ == "__main__":
    errors = 0
    isClosed = False

    print('\rProgram started.')
    real_path = os.path.realpath(__file__)
    while True:
        try:
            # speak("Computer is booting.")
            spinner = Halo(text='Loading Models', spinner='dots')
            spinner.start()

            speechON = online.Speech2TextON(real_path)
            wakeWord = computerWW()
            programs_names, programsList = getProgramsList()

            spinner.stop()

            os.system('cls')
            speak("Computer is ready sir.")
            while True:
                wakeWord.run()

                # viper.start()
                st = time.time()
                text = str(speechON.run()).lower()
                # viper.stop()
                print(f"{text}, Time: {time.time() - st}.")

                if 'open' in text:
                    text = text.replace('open', '')
                    matches = difflib.get_close_matches(
                        text, programs_names, n=6, cutoff=.5
                    )
                    if len(matches):
                        speak(f"Opening {matches[0]}.")
                        os.startfile(programsList.get(matches[0]))
                    else:
                        speak("FILE NOT FOUND.")
                elif 'start' in text:
                    text = text.replace('start', '')
                elif 'mute' in text:
                    active_window = GetWindowText(GetForegroundWindow())
                    if 'chrome' in str(active_window).lower():
                        keyboard.press_and_release('m')
                elif 'unmute' in text:
                    active_window = GetWindowText(GetForegroundWindow())
                    if 'chrome' in str(active_window).lower():
                        keyboard.press_and_release('m')
                elif 'switch tab' in text:
                    keyboard.press('alt')
                    keyboard.press('tab')
                    keyboard.release('tab')
                    keyboard.release('alt')
                elif 'shutdown' in text or 'shut down' in text:
                    speak('Shutting down the computer.')
                    for item in dodo().run():
                        keyboard.press_and_release('alt + f4')
                        time.sleep(.3)
                    os.system("shutdown /s /t 1")
                elif 'close' in text and 'computer' in text:
                    speak("Program is closing.")
                    time.sleep(.5)
                    # sys.exit()
                    isClosed = True
                    break
        except Exception as e:
            if errors == 0:
                speak("Some error occurred. Saving Logs.")
                logs_path = os.path.join(
                    os.path.dirname(real_path), 'logs.txt'
                )
                with open(logs_path, 'a') as f:
                    f.write(f"({datetime.datetime.now()})Error: {e}\n")
                speak("Trying to restart computer.")
                os.system('cls')
                errors += 1
            else:
                speak("Fail to restart computer. Program is closing")
                break
                # sys.exit()

        if isClosed:
            break
