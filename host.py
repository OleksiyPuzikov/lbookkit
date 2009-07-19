import os
import sys
import urlparse
import glob
import inspect

from PyQt4 import QtCore, QtGui, QtWebKit

hardcoded_path_to_library = "/local1/seq6/library/"

keymap = {}

keymap[QtCore.Qt.Key_Escape] = "ESC"
keymap[QtCore.Qt.Key_Return] = "MENU"
keymap[QtCore.Qt.Key_Enter]  = "MENU"
keymap[QtCore.Qt.Key_Left]   = "PREV"
keymap[QtCore.Qt.Key_Right]  = "NEXT"
keymap[QtCore.Qt.Key_Q]      = "POWER"

keymap[QtCore.Qt.Key_0] = "0"
keymap[QtCore.Qt.Key_1] = "1"
keymap[QtCore.Qt.Key_2] = "2"
keymap[QtCore.Qt.Key_3] = "3"
keymap[QtCore.Qt.Key_4] = "4"
keymap[QtCore.Qt.Key_5] = "5"
keymap[QtCore.Qt.Key_6] = "6"
keymap[QtCore.Qt.Key_7] = "7"
keymap[QtCore.Qt.Key_8] = "8"
keymap[QtCore.Qt.Key_9] = "9"

class NewWebView(QtWebKit.QWebView):

    def __init__(self, parent = None):
        QtWebKit.QWebView.__init__(self, parent)

        self.resize(QtCore.QSize(600, 800)) # just like E-Ink screens
#        self.move(QtCore.QPoint(500, 350)) # to be under my mouse when launched

        self.page().setForwardUnsupportedContent(True)
        self.connect(self.page(), QtCore.SIGNAL("unsupportedContent(QNetworkReply *)"), self.handleUnsupported)

        self.modh = None # current plugin handle
        self.currentModule = "" # current plugin name

        self.templates = {}
        self.history = []

        self.basepath = os.path.join(os.getcwd(), os.path.dirname(inspect.getfile(sys._getframe(0))))

        sys.path.append("%s/apps" % self.basepath) # for us to be able to import the preinstalled applications...

    def handleUnsupported(self, reply):
        """ Misc PyQT thing that allows loading URLs with unrecognized schema  """
        self.nav(str(reply.url().toString()))

    def loadTheme(self, name = "default"):
        """ Scan the 'themes' directory and load the requested theme. I only have 'default' by now, but this can change. """
        themes = os.listdir("themes")
        if name in themes:
            self.templates = {}
            files = glob.glob("themes/%s/*.tpl" % name)
            for file in files:
                f = open(file)
                data = "\n".join(f.readlines())
                f.close()

                key = file.replace(".tpl", "").split(os.path.sep)[-1]
                self.templates[key] = data

    def changeCurrentModule(self, modName, url):
        """ Loading the plugin by name and enabling it's functionality """
        if modName != self.currentModule:

            modPath = ""

            apps = os.listdir("apps")
            if modName in apps: # built-in application
                modPath = modName
            else: # one supplied by user
                sys.path.append(url.replace(self.basepath, ""))
                modPath = modName
                
            self.currentModule = modName

            if self.modh != None:
                self.modh.stop()

            self.modh = __import__(modPath)

            self.modh.start()
            self.modh.bus(self.bus_callback)

    def bus_callback(self, event):
        """ Handling the callback messaging between plugins and main shell.
            'Bus' is [theoretical] bidirectional connection that allows plugin to get
            the data from host or send it back [for example, using the a=b syntax].

            Only simple things implemented here for now.
        """
        print "bus callback", event

        if "/templates/" in event:
            ev = event.replace("/templates/", "")
            return self.templates[ev]

        if "/system/" in event:
            ev = event.replace("/system/", "")
            if ev == "library_path":
                return hardcoded_path_to_library

    def keyPressEvent(self, event):
        """ Send the keyboard events to plugin, and depending on the results - reload the view.
            In this prototype events are mapped from Qt to text descriptions of buttons.
        """

        global keymap

        k = event.key()
        mapped = keymap.get(k, None)

        if mapped != None:
            res = self.modh.event(mapped)
            if res not in ["", None]: # "" -> do nothing, None -> handle yourself
                self.nav(res)
            else: # got None
                if mapped == "POWER":
                    self.nav("bye://bye")
                if mapped == "ESC":
                    try:
                        url = self.history[-2]
                        self.history = self.history[:-2]
                        self.nav(url)
                    except:
                        pass

    def nav(self, url):
        """ Handles the actual navigation between plugins and within selected plugin
            by parsing the URLs and then loading corresponding plugin and executing it
        """

        self.history.append(url)

        fu = urlparse.urlparse(url)
        scheme = fu.scheme
        u = fu.path

        self.changeCurrentModule(scheme, u)

        html = self.modh.get(u)

        if type(html) == str:
            s = self.tr(html)
        else:
            s = html
        self.setHtml(s)


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)

    QtGui.QFontDatabase.addApplicationFont(app.tr("res/DroidSans.ttf")) # just because I like it :)
    QtGui.QFontDatabase.addApplicationFont(app.tr("res/DroidSans-Bold.ttf"))
#    QtGui.QFontDatabase.addApplicationFont(app.tr("res/DroidSerif-Regular.ttf"))

    view = NewWebView()

    view.loadTheme()
    view.load(QtCore.QUrl(view.tr("menu://%s" % hardcoded_path_to_library))) # yeah, I've hardcoded the path to my library

    view.show()
    view.raise_() # otherwise it will be in background on Mac machines

    app.exec_()

