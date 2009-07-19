# menu.app

import glob
import datetime
import os
import stat

from parsers import *

__storage = {}

def start():
    global __storage
    menu_items = [0]*9

    __storage["menu_items"] = menu_items

def stop():
    pass

def bus(callback):
    global __storage
    __storage["callback"] = callback

    callback("menu loaded")

def event(ev):
    global __storage

    url = None

    pages = __storage["allpages"]
    page = __storage["curpages"]
    menu_items = __storage["menu_items"]
    path = os.path.normpath(__storage["path"]).replace(os.path.sep*2, os.path.sep)

    if ev == "NEXT":
        if page < pages:
            page = page + 1
            url = "menu://%s?page=%s" % (path, str(page))
    elif ev == "PREV":
        if page > 1:
            page = page - 1
            url = "menu://%s?page=%s" % (path, str(page))
    elif ev in "0123456789":
        cell = int(ev)
        url = menu_items[cell-1]

    return url

def get(url):
    global __storage

    folder_icons = { "music" : "folder_music", "games" : "folder_games", "themes" : "folder_themes", "books" : "folder_books" }
    book_apps = { ".fb2.zip" : "reader", ".fb2" : "reader", ".epub" : "reader", ".dvi" : "dvi" }

    path = url.split('?')[0]
    params = "?" in url and dict(p.split("=") for p in url[url.index("?") + 1:].split("&")) or {}

    library_path = os.path.normpath(__storage["callback"]("/system/library_path"))
    pathr = os.path.normpath(path).replace(library_path, "").replace(os.path.sep*2, os.path.sep)

    menu_items = __storage["menu_items"]

    if pathr == "":
        pathr = "/" # and add special menu items to the list?

    page = int(params.get("page", 1))-1

    files = glob.glob(str(path+"/*"))
    list = files[page*8:(page+1)*8]
    pages = len(files)/8+1

    tpl      = __storage["callback"]("/templates/gm")
    tpl_css  = __storage["callback"]("/templates/css")
    tpl_line = __storage["callback"]("/templates/gmline")

    tpl = tpl.replace("%css", tpl_css)
    tpl = tpl.replace("%path", pathr)

    lines = ""
    for c, l in enumerate(list):
        line = tpl_line

        custom_line_style = ""
        app = "menu"

        if os.path.isfile(l): # file
            bauthor = bgenre = btitle = ""
            st = os.stat(l)
            bdate = datetime.datetime.fromtimestamp(st[stat.ST_MTIME]).strftime('%Y-%m-%d') # %x %X
            bsize = "%d kb" % ( int(st[stat.ST_SIZE])/1024 )

            (bauthor, btitle, bgenre) = parseFile(l)

            btype = "book"

            for ext in book_apps:
                if l.endswith(ext):
                    app = book_apps[ext]

        else: # folder or app
            btitle = l.replace(path, "")
            bdate = bsize = bauthor = ""

            btype = folder_icons.get(btitle.lower(), "folder")

            if btitle.endswith(".app"): # provide custom icons for applications...
                custom_line_style = "background:url('file://%s/icon.png') center left no-repeat" % l
                btitle = btitle.replace(".app", "")

                app = btitle.lower().replace("/", "")
                
            if btitle.startswith("/"):
                btitle = btitle[1:]

        line = line.replace("%filename", "%d.&nbsp;%s" % (c+1, btitle))
        line = line.replace("%author", "&nbsp;&nbsp;&nbsp;"+bauthor)
        line = line.replace("%date", bdate)
        line = line.replace("%size", bsize)

        line = line.replace("%custom_line", custom_line_style)

        line = line.replace("%url", "%s:%s" % (app, l))

        menu_items[c] = "%s:%s" % (app, l)

        line = line.replace("%type", btype)

        lines += line

    tpl = tpl.replace("%lines", lines)

    tpl = tpl.replace("%curpage", str(page+1))
    tpl = tpl.replace("%allpages", str(pages))


    __storage["allpages"] = pages
    __storage["curpages"] = page+1
    __storage["path"]     = path

#    print tpl

    print menu_items

    return tpl