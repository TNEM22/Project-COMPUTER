import threading
import time
import math
import os

import ctypes
from ctypes import wintypes
from PIL import Image
from aggdraw import Draw, Brush, Pen

import pythoncom
import pywintypes
import win32gui
from win32com.shell import shell, shellcon
from typing import List

user32 = ctypes.WinDLL("user32")

SW_HIDE = 0
SW_SHOW = 5

user32.FindWindowW.restype = wintypes.HWND
user32.FindWindowW.argtypes = (
    wintypes.LPCWSTR,  # lpClassName
    wintypes.LPCWSTR)  # lpWindowName

user32.ShowWindow.argtypes = (
    wintypes.HWND,  # hWnd
    ctypes.c_int)  # nCmdShow


def _make_filter(class_name: str, title: str):
    """https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-enumwindows"""

    def enum_windows(handle: int, h_list: list):
        if not (class_name or title):
            h_list.append(handle)
        if class_name and class_name not in win32gui.GetClassName(handle):
            return True  # continue enumeration
        if title and title not in win32gui.GetWindowText(handle):
            return True  # continue enumeration
        h_list.append(handle)

    return enum_windows


def find_window_handles(parent: int = None, window_class: str = None, title: str = None) -> List[int]:
    cb = _make_filter(window_class, title)
    try:
        handle_list = []
        if parent:
            win32gui.EnumChildWindows(parent, cb, handle_list)
        else:
            win32gui.EnumWindows(cb, handle_list)
        return handle_list
    except pywintypes.error:
        return []


def force_refresh():
    user32.UpdatePerUserSystemParameters(1)


def enable_activedesktop():
    """https://stackoverflow.com/a/16351170"""
    try:
        progman = find_window_handles(window_class='Progman')[0]
        cryptic_params = (0x52c, 0, 0, 0, 500, None)
        user32.SendMessageTimeoutW(progman, *cryptic_params)
    except IndexError as e:
        raise WindowsError('Cannot enable Active Desktop') from e


def set_wallpaper(image_path: str, use_activedesktop: bool = True):
    if use_activedesktop:
        enable_activedesktop()
    pythoncom.CoInitialize()
    iad = pythoncom.CoCreateInstance(shell.CLSID_ActiveDesktop,
                                     None,
                                     pythoncom.CLSCTX_INPROC_SERVER,
                                     shell.IID_IActiveDesktop)
    iad.SetWallpaper(str(image_path), 0)
    iad.ApplyChanges(shellcon.AD_APPLY_ALL)
    force_refresh()


class HexagonGenerator(object):
    """Returns a hexagon generator for hexagons of the specified size."""

    def __init__(self, edge_length):
        self.edge_length = edge_length

    @property
    def col_width(self):
        return self.edge_length * 3

    @property
    def row_height(self):
        return math.sin(math.pi / 3) * self.edge_length

    def __call__(self, row, col):
        x = (col + 0.5 * (row % 2)) * self.col_width
        y = row * self.row_height
        for angle in range(0, 360, 60):
            x += math.cos(math.radians(angle)) * self.edge_length
            y += math.sin(math.radians(angle)) * self.edge_length
            yield x
            yield y


class Viper(object):
    def __init__(self, rows=9, columns=5):
        self.rows = rows
        self.columns = columns
        real_path = os.path.realpath(__file__)
        self.image_path = os.path.join(
            os.path.dirname(real_path), 'bin/temp.jpg'
        )
        # self.back_image = real_path.split(r'\anime')[0]+r'\functions\bg.jpg'
        self.back_image = os.path.join(
            os.path.dirname(real_path), 'bin/bg.jpg'
        )
        self.image_temp = os.path.join(
            os.path.dirname(real_path), 'bin/temp01.jpg'
        )

        self.image = Image.new('RGB', (1500, 800), 'white')
        self.draw = Draw(self.image)
        self.hexagon_generator = HexagonGenerator(105)

        for row in range(-1, rows):
            for col in range(columns):
                hexagon = self.hexagon_generator(row, col)
                self.draw.polygon(list(hexagon), Brush(
                    (0, 0, 0)), Pen('whitesmoke'))
        self.draw.flush()

        red = (140, 0, 0)
        green = (0, 140, 0)
        blue = (0, 0, 140)
        self.color_list = [red, green, blue]

        self._stop_show = None
        self._show_thread = None

    def render(self):
        self.image.save(self.image_path)
        set_wallpaper(self.image_path)
        time.sleep(1)

        i = 0
        reverse = False
        r, g, b = 0, 0, 0
        while not self._stop_show.is_set():
            i_r, i_g, i_b = self.color_list[i]
            while not self._stop_show.is_set():
                for row in range(-1, self.rows):
                    color = r, g, b
                    for col in range(self.columns):
                        hexagon = self.hexagon_generator(row, col)
                        self.draw.polygon(list(hexagon), Brush(
                            color), Pen('whitesmoke'))
                self.draw.flush()
                try:
                    self.image.save(self.image_path)
                    # ctypes.windll.user32.SystemParametersInfoW(
                    #     20, 0, self.image_path, 0)
                    set_wallpaper(self.image_path)
                except OSError:
                    self.image.save(self.image_temp)
                    # ctypes.windll.user32.SystemParametersInfoW(
                    #     20, 0, self.image_temp, 0)
                    set_wallpaper(self.image_temp)

                if r == i_r and g == i_g and b == i_b:
                    break
                else:
                    frame = 20
                    if r != i_r:
                        if r > i_r:
                            r -= frame
                        elif r < i_r:
                            r += frame
                    if g != i_g:
                        if g > i_g:
                            g -= frame
                        elif g < i_g:
                            g += frame
                    if b != i_b:
                        if b > i_b:
                            b -= frame
                        elif b < i_b:
                            b += frame
                time.sleep(.2)

            if i == 0:
                i += 1
                reverse = False
            elif reverse:
                i -= 1
            elif i >= 2:
                i -= 1
                reverse = True
            else:
                i += 1
            time.sleep(.1)

        time.sleep(1)
        set_wallpaper(self.back_image)

        return self

    def start(self):
        self._stop_show = threading.Event()
        self._show_thread = threading.Thread(target=self.render)
        self._show_thread.setDaemon(True)
        self._show_thread.start()

        return self

    def stop(self):
        if self._show_thread and self._show_thread.is_alive():
            self._stop_show.set()
            self._show_thread.join()

        return self


if __name__ == "__main__":
    print("Starting...")
    viper = Viper()
    viper.start()

    print("Running...")
    time.sleep(20)
    print(".Completed.")

    viper.stop()
    print("Done!")
