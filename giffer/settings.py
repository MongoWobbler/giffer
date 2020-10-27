import os
from PySide2 import QtWidgets, QtCore
from giffer import gifutil as gifutil


class Settings(QtWidgets.QWidget):
    """
    Handles caching data in .json to remember giffer.exe settings.
    """
    def __init__(self, update_display, clear_display, parent=None):

        super(Settings, self).__init__(parent=parent)
        self.setWindowTitle('Settings')
        self.data_path = os.path.join(os.path.dirname(gifutil.getCurrentPath()), 'giffer_data.json')
        self.registry_name_key = r'*\shell\Open with Giffer'
        self.registry_name_command = r'*\shell\Open with Giffer\Command'
        self.registered_text = 'giffer.exe is registered to Windows. Right click to on Video file for quick giffer launch option!'
        self.setWindowFlags(QtCore.Qt.Tool | QtCore.Qt.WindowStaysOnTopHint)
        self.update_main_display = update_display
        self.clear_main_display = clear_display
        self.use_convert = None
        self.use_gifsicle = None
        self.ffmpeg_line = None
        self.convert_line = None
        self.gifsicle_line = None
        self.export_line = None
        self.auto_close_checkbox = None
        self.info = None
        self.build()
        self.updateDisplay()
        self.isRegistered()

    def build(self):
        """
        Builds the UI.
        """
        main_layout = QtWidgets.QVBoxLayout(self)
        grid_layout = QtWidgets.QGridLayout()
        registry_layout = QtWidgets.QHBoxLayout()

        # set ffmpeg location button
        ffmpeg_button = QtWidgets.QPushButton('Set ffmpeg')
        ffmpeg_button.clicked.connect(self.setFfmpegPath)
        grid_layout.addWidget(ffmpeg_button, 1, 1)

        # holds the path to the ffmpeg.exe
        self.ffmpeg_line = QtWidgets.QLineEdit()
        self.ffmpeg_line.setPlaceholderText('Path to the location of ffmpeg.exe')
        self.ffmpeg_line.setReadOnly(True)
        grid_layout.addWidget(self.ffmpeg_line, 1, 2)

        # use convert checkbox
        self.use_convert = QtWidgets.QCheckBox('Use convert.exe')
        self.use_convert.setChecked(False)
        self.use_convert.clicked.connect(self.onUseConvertChecked)
        grid_layout.addWidget(self.use_convert, 2, 0)

        # set the convert location button
        convert_button = QtWidgets.QPushButton('Set convert')
        convert_button.clicked.connect(self.setConvertPath)
        grid_layout.addWidget(convert_button, 2, 1)

        # holds the path to the convert.exe
        self.convert_line = QtWidgets.QLineEdit()
        self.convert_line.setPlaceholderText('Path to the location of convert.exe')
        self.convert_line.setReadOnly(True)
        grid_layout.addWidget(self.convert_line, 2, 2)

        # use gifsicle checkbox
        self.use_gifsicle = QtWidgets.QCheckBox('Use gifsicle.exe')
        self.use_gifsicle.setChecked(False)
        self.use_gifsicle.clicked.connect(self.onUseGifsicleChecked)
        grid_layout.addWidget(self.use_gifsicle, 3, 0)

        # set the gifsicle location button
        gifsicle_button = QtWidgets.QPushButton('Set gifsicle')
        gifsicle_button.clicked.connect(self.setGifsiclePath)
        grid_layout.addWidget(gifsicle_button, 3, 1)

        # holds the path to the gifsicle.exe
        self.gifsicle_line = QtWidgets.QLineEdit()
        self.gifsicle_line.setPlaceholderText('Path to the location of gifsicle.exe')
        self.gifsicle_line.setReadOnly(True)
        grid_layout.addWidget(self.gifsicle_line, 3, 2)

        # clear export path
        clear_export_path_button = QtWidgets.QPushButton('Clear Export Directory')
        clear_export_path_button.clicked.connect(self.clearExport)
        grid_layout.addWidget(clear_export_path_button, 4, 0)

        # set the export path
        export_path_button = QtWidgets.QPushButton('Export Directory')
        export_path_button.clicked.connect(self.setExportDirectory)
        grid_layout.addWidget(export_path_button, 4, 1)

        # holds the path to the gifsicle.exe
        self.export_line = QtWidgets.QLineEdit()
        self.export_line.setPlaceholderText('(OPTIONAL): Consistent directory to export to.')
        self.export_line.setReadOnly(True)
        grid_layout.addWidget(self.export_line, 4, 2)

        # auto close checkbox
        self.auto_close_checkbox = QtWidgets.QCheckBox('Close giffer.exe after exporting')
        self.auto_close_checkbox.setChecked(False)
        self.auto_close_checkbox.clicked.connect(self.setAutoClose)
        grid_layout.addWidget(self.auto_close_checkbox, 5, 2)
        main_layout.addLayout(grid_layout)

        # set registry button
        set_registry_button = QtWidgets.QPushButton('Create Right Click Shortcut')
        set_registry_button.clicked.connect(self.addToRegistry)
        registry_layout.addWidget(set_registry_button)

        # remove registry button
        remove_registry_button = QtWidgets.QPushButton('Remove Right Click Shortcut')
        remove_registry_button.clicked.connect(self.removeFromRegistry)
        registry_layout.addWidget(remove_registry_button)
        main_layout.addLayout(registry_layout)

        # separator
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        main_layout.addWidget(line)

        # close and accept button
        close_button = QtWidgets.QPushButton('Close and Accept')
        close_button.clicked.connect(self.close)
        main_layout.addWidget(close_button)

        # info label
        self.info = QtWidgets.QLabel('')
        main_layout.addWidget(self.info)

    def onUseConvertChecked(self, new_state):
        """
        Updates data when use convert.exe is checked on or off.

        Args:
            new_state (boolean): State of use convert.exe checkbox.
        """
        data = self.getData()
        data['use_convert'] = new_state
        self.updateData(data)

    def onUseGifsicleChecked(self, new_state):
        """
        Updates data when use gifsicle.exe is checked on or off.

        Args:
            new_state (boolean): State of use gifsicle.exe checkbox.
        """
        data = self.getData()
        data['use_gifsicle'] = new_state
        self.updateData(data)

    def clearExport(self):
        """
        Updates data when clear export button is pressed.
        """
        data = self.getData()
        data['export'] = ''
        self.updateData(data)

    def setAutoClose(self, state):
        """
        Updates data when use set auto close is checked on or off.

        Args:
            state (boolean): State of use set auto close checkbox.
        """
        data = self.getData()
        data['auto_close'] = state
        self.updateData(data)

    def getData(self):
        """
        Gets the cached data from the .json file. Creates .json with default settings if it does not exist.

        Returns:
            (dictionary): Setting name as key.
        """
        if os.path.exists(self.data_path):
            return gifutil.readJson(self.data_path)
        else:
            user_directory = os.path.expanduser('~')
            starting_directory = user_directory if os.path.exists(user_directory) else ''
            data = {
                    'last_opened': starting_directory,
                    'use_convert': False,
                    'use_gifsicle': False,
                    'ffmpeg': '',
                    'convert': '',
                    'gifsicle': '',
                    'export': '',
                    'auto_close': False
                   }

            gifutil.writeJson(self.data_path, data)
            return data

    def updateData(self, new_data):
        """
        Convenience method for writing the .json file and updating the display with new data.

        Args:
            new_data (dictionary): Data to cache in .json.
        """
        gifutil.writeJson(self.data_path, new_data)
        self.updateDisplay(new_data)

    def updateDisplay(self, new_data=None):
        """
        Updates the settings display with either the given new_data or the data in the .json

        Args:
            new_data (dictionary): Data to use to update display. If None, will use .json
        """
        data = new_data if new_data else self.getData()

        self.use_convert.setChecked(data['use_convert'])
        self.use_gifsicle.setChecked(data['use_gifsicle'])
        self.ffmpeg_line.setText(data['ffmpeg'])
        self.convert_line.setText(data['convert'])
        self.convert_line.setEnabled(data['use_convert'])
        self.gifsicle_line.setText(data['gifsicle'])
        self.gifsicle_line.setEnabled(data['use_gifsicle'])
        self.export_line.setText(data['export'])
        self.auto_close_checkbox.setChecked(data['auto_close'])

    def setFfmpegPath(self):
        """
        Sets the path to the ffmpeg.exe
        """
        dialog = QtWidgets.QFileDialog()
        ffmpeg_path, _ = dialog.getOpenFileName(self, 'Please select location of ffmpeg.exe')

        if not ffmpeg_path:
            return

        data = self.getData()
        data['ffmpeg'] = ffmpeg_path
        self.updateData(data)
        self.clear_main_display()

    def setConvertPath(self):
        """
        Sets the path to imagemagick's convert.exe
        """
        dialog = QtWidgets.QFileDialog()
        convert_path, _ = dialog.getOpenFileName(self, 'Please select location of convert.exe')

        if not convert_path:
            return

        data = self.getData()
        data['convert'] = convert_path
        self.updateData(data)
        self.clear_main_display()

    def setGifsiclePath(self):
        """
        Sets the path to gifsicle.exe
        """
        dialog = QtWidgets.QFileDialog()
        gifsicle_path, _ = dialog.getOpenFileName(self, 'Please select location of gifsicle.exe')

        if not gifsicle_path:
            return

        data = self.getData()
        data['gifsicle'] = gifsicle_path
        self.updateData(data)
        self.clear_main_display()

    def setExportDirectory(self):
        """
        Sets the directory the .gif should be exported to.
        """
        dialog = QtWidgets.QFileDialog()
        directory = dialog.getExistingDirectory(self, 'Choose directory to export to')

        if not directory:
            return

        data = self.getData()
        data['export'] = directory
        self.updateData(data)

    def displayInfo(self, text, color='black'):
        """
        Sets the display text at the bottom of the setting's window.

        Args:
            text (string): Text to display for user to read.

            color (string): Color of text, normally "black", or "red."
        """
        self.info.setText(text)
        self.info.setStyleSheet('color: ' + color)

    def isRegistered(self):
        """
        Gets whether giffer.exe if registered in the windows registry to have the right click shortcut.
        Will display info to let the user know it is registered or not.

        Returns:
            (boolean): True if right click shortcut is available, False if it is not.
        """
        is_registered = gifutil.keyExists(self.registry_name_command)
        text = self.registered_text if is_registered else ''
        self.displayInfo(text)
        return is_registered

    def addToRegistry(self):
        """
        Adds giffer.exe to the windows registry to have a right click shortcut.
        """
        if not gifutil.isAdmin():
            self.displayInfo('Launch giffer.exe as admin to create shortcut!', color='red')
            return

        current_path = gifutil.getCurrentPath().replace('/', '\\')
        command = current_path + ' "%1"'
        gifutil.createAndSetKey(self.registry_name_command, '', command)

        self.displayInfo(self.registered_text)

    def removeFromRegistry(self):
        """
        Removes giffer.exe from the registry.
        """
        if not gifutil.isAdmin():
            self.displayInfo('Launch giffer.exe as admin to remove shortcut!', color='red')
            return

        if gifutil.keyExists(self.registry_name_command):
            gifutil.deleteKey(self.registry_name_command)

        if gifutil.keyExists(self.registry_name_key):
            gifutil.deleteKey(self.registry_name_key)

        self.displayInfo('Removed right click shortcut.')

    def closeEvent(self, event):
        """
        Overwriting the close event so giffer can update the main display with the new settings on close.

        Args:
            event (QEvent): Accepted after updating main display.
        """
        self.update_main_display()
        event.accept()
