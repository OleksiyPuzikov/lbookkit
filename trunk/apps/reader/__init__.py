# basic reader app for fb2 and epub files...

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

    callback("reader loaded")

def event(ev):
    global __storage

    url = ""

    pages = __storage["allpages"]
    page = __storage["curpages"]
    path = os.path.normpath(__storage["path"]).replace(os.path.sep*2, os.path.sep)

    if ev == "NEXT":
        if page < pages:
            page = page + 1
            url = "reader://%s?page=%s" % (path, str(page))
    elif ev == "PREV":
        if page > 1:
            page = page - 1
            url = "reader://%s?page=%s" % (path, str(page))

    return url

def getFb2String(filename):
    from xml.dom.minidom import parseString, Node
    import zipfile

    result = []
    data = u""

    def findAll(elem, what):
        res = []
        for x in elem.childNodes:
            if x.nodeType == Node.ELEMENT_NODE and x.tagName==what:
                res.append(x)
        return res

    if filename.endswith(".fb2.zip"):
        zf = zipfile.ZipFile(filename)
        for fname in zf.namelist():
            if fname.endswith(".fb2"):
                data = zf.read(fname)
    else:
        f = open(filename, 'r')
        data = "\n".join(f.readlines())
        f.close()

    soup = parseString(data)
    soup.normalize()

    fb = soup.documentElement

    body = findAll(fb, "body")
    for b in body:
#        result.append(b.toxml().encode('utf-8'))
        result.append(b.toxml())

#    return u"\n".join(result)
#    print type(result[0])

    return result[0]

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

#    lines = """<center><img style="margin-top: 16px;" src="file://%s"></center>""" % pngpath

    lines = getFb2String(path)

    tpl = tpl.replace("%lines", lines)

    tpl = tpl.replace("%curpage", str(page+1))
    tpl = tpl.replace("%allpages", str(pages))

#    print tpl
#    print type(tpl)

    __storage["allpages"] = pages
    __storage["curpages"] = page+1
    __storage["path"]     = path

    return tpl