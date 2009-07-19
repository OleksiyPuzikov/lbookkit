# CuteHack is a cute rework of NetHack game :)
import random
import os

__storage = {}

def start():
    global __storage

    state = []

    for v in range(1, 80):
        ty = random.randint(7, 9) # just the flowers
        x = random.randint(0, 600)
        y = random.randint(0, 600)

        state.append((ty, x, y))

    for v in range(1, 20):
        ty = random.randint(1, 15)
        x = random.randint(0, 600)
        y = random.randint(0, 600)

        state.append((ty, x, y))

    heropos = (250, 250)

    __storage["state"] = state
    __storage["heropos"] = heropos

def stop():
    pass

def bus(callback):
    global __storage
    __storage["callback"] = callback

    callback("cutehack loaded")

def event(ev): # game logic here
    global __storage

    state = __storage["state"]
    heropos = __storage["heropos"]

    x, y = heropos

    url = ""

    path = os.path.normpath(__storage["path"]).replace(os.path.sep*2, os.path.sep)

    if ev in "1267":
        cell = int(ev)

        if cell == 1: # left top
            heropos = (x-50, y-50)
        elif cell == 2: # right top
            heropos = (x+50, y-50)
        elif cell == 6: # left bottom
            heropos = (x-50, y+50)
        elif cell == 7: # right bottom
            heropos = (x+50, y+50)

        url = "cutehack://%s?heropos=%s" % (path, ":".join([str(l) for l in list(heropos)]))
        print url

    __storage["state"] = state
    __storage["heropos"] = heropos

    return url

def get(url): # game view here
    global __storage

    state = __storage["state"]
    heropos = __storage["heropos"]

    path = url.split('?')[0]
    params = "?" in url and dict(p.split("=") for p in url[url.index("?") + 1:].split("&")) or {}

    lines = """

    <style>

    .field { background-color: #96AF33; width: 600px; height: 700px; }
    .item { background:url('file://%localpath/cutehack/tiles.png') 0 0 no-repeat; width: 100px; height: 100px; }

    .i1 { background-position: 0px 0px; }
    .i2 { background-position: -100px 0px; }
    .i3 { background-position: -200px 0px; }

    .i4 { background-position: 0px -100px; }
    .i5 { background-position: -100px -100px; }
    .i6 { background-position: -200px -100px; }

    .i7 { background-position: 0px -200px; }
    .i8 { background-position: -100px -200px; }
    .i9 { background-position: -200px -200px; }

    .i10 { background-position: 0px -300px; }
    .i11 { background-position: -100px -300px; }
    .i12 { background-position: -200px -300px; }

    .i13 { background-position: 0px -400px; }
    .i14 { background-position: -100px -400px; }
    .i15 { background-position: -200px -400px; }

    .hero {  background:url('file:///%localpath/cutehack/boy.png') bottom left no-repeat; width: 100px; height: 120px;  }

    .text { height: 76px; width: 600px; position: absolute; top: 724px; left: 0px; text-align: center; padding: 10px; }

    </style>

    <div class="field"></div>
    <div class="text">You're standing in the middle of some place.<br />And there's nowhere you can actually go.<br />Use 1,2,6,7 to navigate.</div>

    """

    tpl      = __storage["callback"]("/templates/reader")
    tpl_css  = __storage["callback"]("/templates/css")

    tpl = tpl.replace("%css", tpl_css)
    tpl = tpl.replace("%path", "Welcome to CuteHack")

    lines = lines.replace("%localpath", path)

    for c in state:
        lines += """<div class="item i%d" style="position: absolute; left: %dpx; top: %dpx;"></div>""" % c

    lines += """<div class="hero" style="position: absolute; left: %dpx; top: %dpx;"></div>""" % heropos

    tpl = tpl.replace("%lines", lines)

    tpl = tpl.replace("%curpage", "")
    tpl = tpl.replace("%allpages", "")

    __storage["path"]     = path

    return tpl
