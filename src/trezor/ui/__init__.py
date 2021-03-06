from micropython import const

import sys
import math
import utime

from trezorui import Display

from trezor import io
from trezor import loop
from trezor import res

display = Display()

# for desktop platforms, we need to refresh the display after each frame
if sys.platform != 'trezor':
    loop.after_step_hook = display.refresh

# import constants from modtrezorui

SIZE = Display.FONT_SIZE
NORMAL = Display.FONT_NORMAL
BOLD = Display.FONT_BOLD
MONO = Display.FONT_MONO
SCREEN = Display.WIDTH  # used also for height as we have square display


def lerpi(a: int, b: int, t: float) -> int:
    return int(a + t * (b - a))


def rgb(r: int, g: int, b: int) -> int:
    return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | ((b & 0xF8) >> 3)


def blend(ca: int, cb: int, t: float) -> int:
    return rgb(
        lerpi((ca >> 8) & 0xF8, (cb >> 8) & 0xF8, t),
        lerpi((ca >> 3) & 0xFC, (cb >> 3) & 0xFC, t),
        lerpi((ca << 3) & 0xF8, (cb << 3) & 0xF8, t))


from trezor.ui.style import *


def contains(area: tuple, pos: tuple) -> bool:
    x, y = pos
    ax, ay, aw, ah = area
    return ax <= x <= ax + aw and ay <= y <= ay + ah


def rotate(pos: tuple) -> tuple:
    r = display.orientation()
    if r == 0:
        return pos
    x, y = pos
    if r == 90:
        return (y, 240 - x)
    if r == 180:
        return (240 - x, 240 - y)
    if r == 270:
        return (240 - y, x)


def pulse(delay: int):
    while True:
        # normalize sin from interval -1:1 to 0:1
        yield 0.5 + 0.5 * math.sin(utime.ticks_us() / delay)


async def alert(count: int=3):
    short_sleep = loop.sleep(20000)
    long_sleep = loop.sleep(80000)
    current = display.backlight()
    for i in range(count * 2):
        if i % 2 == 0:
            display.backlight(BACKLIGHT_MAX)
            yield short_sleep
        else:
            display.backlight(BACKLIGHT_NORMAL)
            yield long_sleep
    display.backlight(current)


async def click() -> tuple:
    touch = loop.select(io.TOUCH)
    while True:
        ev, *pos = yield touch
        if ev == io.TOUCH_START:
            break
    while True:
        ev, *pos = yield touch
        if ev == io.TOUCH_END:
            break
    return pos


async def backlight_slide(val: int, delay: int=20000, step: int=1):
    sleep = loop.sleep(delay)
    current = display.backlight()
    for i in range(current, val, -step if current > val else step):
        display.backlight(i)
        yield sleep


def layout(f):
    delay = const(35000)  # 35ms
    step = const(20)

    async def inner(*args, **kwargs):
        await backlight_slide(BACKLIGHT_DIM, delay, step)
        slide = backlight_slide(BACKLIGHT_NORMAL, delay, step)
        try:
            loop.schedule(slide)
            return await f(*args, **kwargs)
        finally:
            loop.close(slide)

    return inner


def header(title: str,
           icon: bytes=ICON_RESET,
           fg: int=BG,
           bg: int=BG,
           ifg: int=BG):
    if icon is not None:
        display.icon(14, 17, res.load(icon), ifg, bg)
    display.text(44, 35, title, BOLD, fg, bg)


VIEWX = const(6)
VIEWY = const(9)
VIEW = const(228)  # SCREEN - 2 * VIEWX


def grid(i: int,
         n_x: int=3,
         n_y: int=5,
         start_x: int=VIEWX,
         start_y: int=VIEWY,
         end_x: int=(VIEWX + VIEW),
         end_y: int=(VIEWY + VIEW),
         cells_x: int=1,
         cells_y: int=1,
         spacing: int=0):
    w = (end_x - start_x) // n_x
    h = (end_y - start_y) // n_y
    x = (i % n_x) * w
    y = (i // n_x) * h
    return (x + start_x, y + start_y, (w - spacing) * cells_x, (h - spacing) * cells_y)


class Widget:
    def render(self):
        pass

    def touch(self, event, pos):
        pass

    def __iter__(self):
        touch = loop.select(io.TOUCH)
        result = None
        while result is None:
            self.render()
            event, *pos = yield touch
            result = self.touch(event, pos)
        return result
