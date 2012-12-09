import pipes
import os
import types
import logging
import time


def fileList(paths, relative=False, folders=False):
    """
    Generate a recursive list of files from a given path.
    """

    if not type(paths) == types.ListType:
        paths = [paths]

    files = []

    for path in paths:
        for fileName in os.listdir(path):
            if fileName.startswith('.'):
                continue

            filePath = os.path.join(path, fileName)

            if os.path.isdir(filePath):
                if folders:
                    files.append(filePath)
                files += fileList(filePath)
            else:
                files.append(filePath)

        if relative:
            files = map(lambda x: x[len(path) + 1:], files)

    return files


def parseValues(data, splitChar=':'):
    """
    Values like

    name: koen
    age: 29

    will be converted in a dict: {'name': 'koen', 'age': '29'}
    """

    values = {}
    lines = data.splitlines()

    if not lines:
        return {}, ''

    for i in xrange(len(lines)):
        line = lines[i]

        if not line:
            continue

        elif splitChar in line:
            line = line.split(splitChar)
            values[line[0].strip()] = (splitChar.join(line[1:])).strip()

        else:
            break

    return values, '\n'.join(lines[i:])


def retry(ExceptionToCheck, tries=4, delay=3, backoff=2):
    def deco_retry(f):
        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay
            try_one_last_time = True
            while mtries > 1:
                try:
                    return f(*args, **kwargs)
                    try_one_last_time = False
                    break
                except ExceptionToCheck, e:
                    logging.warning(
                        "%s, Retrying in %.1f seconds..." % (str(e), mdelay)
                    )
                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            if try_one_last_time:
                return f(*args, **kwargs)
            return

        return f_retry  # true decorator

    return deco_retry


def shell_escape(path):
    if os.name == "nt":
        return '"{0}"'.format(path)
    else:
        return pipes.quote(path)
