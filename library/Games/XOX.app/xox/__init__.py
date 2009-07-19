# xox game
import os

__storage = {}

def start():
    global __storage

    state = [" "]*10

    state[1] = "x"
    state[5] = "o"

    __storage["state"] = state

def stop():
    pass

def bus(callback):
    global __storage
    __storage["callback"] = callback

    callback("xox loaded")

def event(ev): # game logic here
    global __storage

    state = __storage["state"]

    url = ""

#    path = __storage["path"]
    path = os.path.normpath(__storage["path"]).replace(os.path.sep*2, os.path.sep)

    if ev in "0123456789":
        cell = int(ev)
        state[cell] = "x"

#        print "new state", state

        # computer turn is almost random

        for s in reversed(range(1, 10)):
            if state[s] == " ":
                state[s] = "o"
                break

        url = "xox://%s?state=%s" % (path, "".join(state))

    __storage["state"] = state

    return url

def get(url): # game view here
    global __storage

    state = __storage["state"]

    path = url.split('?')[0]
    params = "?" in url and dict(p.split("=") for p in url[url.index("?") + 1:].split("&")) or {}

    lines = """

    <style>

    .xoxo { border: 0px; width: 400px; height: 400px; margin: auto auto; padding: 100px 0px;  }
    .xoxo td { margin: 0px; padding: 10px; width: 128px; height: 128px; border: 1px solid #eee; }
    .x {  background:url('file://%localpath/xox/x.png') center center no-repeat; }
    .o {  background:url('file://%localpath/xox/o.png') center center no-repeat; }
    .e {  background-color; #eee; }

    </style>

    <table class="xoxo">
        <tr><td class="%c1">1</td><td class="%c2">2</td><td class="%c3">3</td></tr>
        <tr><td class="%c4">4</td><td class="%c5">5</td><td class="%c6">6</td></tr>
        <tr><td class="%c7">7</td><td class="%c8">8</td><td class="%c9">9</td></tr>
    </table>

    """

    tpl      = __storage["callback"]("/templates/gm")
    tpl_css  = __storage["callback"]("/templates/css")

    tpl = tpl.replace("%css", tpl_css)
    tpl = tpl.replace("%path", "X0X0 game :)")

    lines = lines.replace("%localpath", path)

    for c in range(1, 10):
        img = state[c]
        if img == " ":
            img = "e"

        lines = lines.replace("%c"+str(c), img)

    tpl = tpl.replace("%lines", lines)

    tpl = tpl.replace("%curpage", "")
    tpl = tpl.replace("%allpages", "")

    __storage["path"]     = path

    return tpl
