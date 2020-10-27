import sys
import json
import winreg
import webbrowser


def getCurrentPath():
    return sys.executable if getattr(sys, 'frozen', False) else __file__


def openDocumentation():
    webbrowser.open('https://github.com/MongoWobbler/giffer', new=2)


def toSeconds(time, text=True):
    seconds = float(time) / 1000.0
    return f'{seconds:0.3}' if text else seconds


def subtractStrings(a, b):
    return f'{float(a) - float(b):0.3}'


def isAdmin():
    """
    Gets whether the user is an admin or not.

    Returns:
        (boolean): True if admin, False if not admin.
    """
    try:
        with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, r'*\shell', 0, winreg.KEY_ALL_ACCESS) as _:
            pass

        return True
    except PermissionError:
        return False


def keyExists(path):
    """
    Checks whether given path exists in the registry's classes root.

    Args:
        path (string): Path to check and see if exists in registry.

    Returns:
        (boolean): True if exists, False if it doesnt.
    """
    try:
        with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, path, 0, winreg.KEY_READ) as _:
            pass

        return True
    except WindowsError:
        return False


def createKey(path):
    """
    Creates a new key with no names or values.

    Args:
        path (string): Path to create key at.
    """
    winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, path)


def createAndSetKey(path, name, value):
    """
    Creates a windows registry key at the given registry path. Then sets a sub key with given name and value.

    Args:
        path (string): Path to the registry key to create.

        name (string): Name for the value, pass empty string for default

        value (string): Value to give sub key associated with given name.
    """
    winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, path)
    with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, path, 0, winreg.KEY_WRITE) as key:
        winreg.SetValueEx(key, name, 0, winreg.REG_SZ, value)


def deleteKey(path):
    """
    Deletes registry key from given path.

    Args:
        path (string): Path to remove key from.
    """
    with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, path, 0, winreg.KEY_ALL_ACCESS) as key:
        winreg.DeleteKey(key, '')


def writeJson(file_name, data):
    """
    Writes given dict data to given file_name as json.

    Args:
        file_name (string): Path to write data to.

        data (dict): dict to write to given file_name.

    Returns:
        (string): full path where json file is.
    """
    with open(file_name, 'w') as open_file:
        json.dump(data, open_file, indent=4)

    return file_name


def readJson(file_name, hook=None):
    """
    Gets the dictionary data from the given json file.

    Args:
        file_name (string): Path to json file.

        hook (orderedDict): if orderedDict is passed, json loads dict in order.

    Returns:
        (dict): Data loaded from given file_name.
    """
    with open(file_name, 'r') as open_file:
        data = json.load(open_file, object_pairs_hook=hook)

    return data
