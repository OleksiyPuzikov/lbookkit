# dvi

import os

#from parsers import *

__storage = {}

def start():
    pass

def stop():
    pass

def bus(callback):
    global __storage
    __storage["callback"] = callback

    callback("dvi loaded")

def event(ev):
    global __storage

    url = ""

    pages = __storage["allpages"]
    page = __storage["curpages"]
    path = os.path.normpath(__storage["path"]).replace(os.path.sep*2, os.path.sep)

    if ev == "NEXT":
        if page < pages:
            page = page + 1
            url = "dvi://%s?page=%s" % (path, str(page))
    elif ev == "PREV":
        if page > 1:
            page = page - 1
            url = "dvi://%s?page=%s" % (path, str(page))

    return url

def get(url):
    global __storage

    path = url.split('?')[0]
    params = "?" in url and dict(p.split("=") for p in url[url.index("?") + 1:].split("&")) or {}

#    print "path", path
#    print "params", params

    page = int(params.get("page", 1))-1

    pages = 10

    tpl      = __storage["callback"]("/templates/reader")
    tpl_css  = __storage["callback"]("/templates/css")

    library_path = os.path.normpath(__storage["callback"]("/system/library_path"))
    pathr = os.path.normpath(path).replace(library_path, "").replace(os.path.sep*2, os.path.sep)

    tpl = tpl.replace("%css", tpl_css)
    tpl = tpl.replace("%path", pathr)

    import subprocess

    selfpath = os.path.sep.join(__file__.split(os.path.sep)[:-1])
    pngpath = path.replace(".dvi", ".png")

    cmd = "%s/dvii -u %s" % (selfpath, path)
    file = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).communicate()[0]

    for f in file.split("\n"):
        if "Page count" in f:
            ff = f.split(":")[-1].strip()
            pages = int(ff)

    cmd = "%s/dvipng -q -pp %s -T bbox --noghostscript -D 150 -o %s %s" % (selfpath, page+1, pngpath, path)

#    print cmd

    file = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).communicate()[0]

#    print file

    lines = """<center><img style="margin-top: 16px;" src="file://%s"></center>""" % pngpath

    tpl = tpl.replace("%lines", lines)

    tpl = tpl.replace("%curpage", str(page+1))
    tpl = tpl.replace("%allpages", str(pages))

#    print tpl

    __storage["allpages"] = pages
    __storage["curpages"] = page+1
    __storage["path"]     = path

    return tpl