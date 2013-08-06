import webbrowser
from cactus.utils import run_subprocess
import os
import platform
from threading import Thread


s1 = """
tell application "Google Chrome"
    set windowsList to windows as list
    repeat with currWindow in windowsList
        set tabsList to currWindow's tabs as list
        repeat with currTab in tabsList
            if "%s" is in currTab's URL then execute currTab javascript "%s"
        end repeat
    end repeat
end tell
"""

s2 = """
tell application "Safari"
    if (count of windows) is greater than 0 then
        set windowsList to windows as list
        repeat with currWindow in windowsList
            set tabsList to currWindow's tabs as list
            repeat with currTab in tabsList
                if "%s" is in currTab's URL then
                    tell currTab to do JavaScript "%s"
                end if
            end repeat
        end repeat
    end if
end tell
"""


def applescript(input):
    return
    """
    # Bail if we're not on mac os for now
    if platform.system() != "Darwin":
        return

    command = "osascript<<END%sEND" % input
    return run_subprocess(command)
    """


def _insertJavascript(urlMatch, js):
    apps = appsRunning(['Safari', 'Google Chrome'])

    if apps['Google Chrome']:
        try:
            applescript(s1 % (urlMatch, js))
        except Exception:
            pass

    if apps['Safari']:
        try:
            applescript(s2 % (urlMatch, js))
        except Exception:
            pass


def browserReload(url, site):
    if platform.system() != "Darwin":
        if site.browser is None:
            openurl(url, site)
        else:
            site.browser.refresh()
    else:
        _insertJavascript(url, "window.location.reload()")


def browserReloadCSS(url, site):
    if platform.system() != "Darwin":
        browserReload(url, site)
    else:
        _insertJavascript(url, "var links = document.getElementsByTagName('link'); for (var i = 0; i < links.length;i++) { var link = links[i]; if (link.rel === 'stylesheet') {link.href += '?'; }}")


def appsRunning(l):
    if os.name == "nt":
        psdata = run_subprocess(
            ['wmic', 'process', 'get', 'description']
        )
    else:
        psdata = run_subprocess(['ps aux'])
    retval = {}
    for app in l:
        retval[app] = app in psdata
    return retval

def openurl(url, site):
    if platform.system() != "Darwin":
        if site.browser is None:
            t = Thread(target=init_selenium, args=(site, url,))
            t.start()
        else:
            site.browser.get(url)
    else:
        webbrowser.open(url)

def init_selenium(site, url):
    from selenium import webdriver
    b = site.config.get("common").get("browser", "chrome")
    if b == "firefox":
        site.browser = webdriver.Firefox()
    elif b == "opera":
        site.browser = webdriver.Opera()
    elif b == "ie":
        site.browser = webdriver.Ie()
    else:
        site.browser = webdriver.Chrome()
    site.browser.get(url)
