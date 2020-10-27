import os
import cv2
import shutil
import tempfile
import threading
import subprocess
import giffer.gifutil as gifutil
from giffer.about import AboutWindow
from giffer.settings import Settings
from PySide2 import QtWidgets, QtGui, QtCore, QtMultimedia, QtMultimediaWidgets


# dependencies:
# K-Lite Codec Pack (Basic)
# ffmpeg.exe


# Future features:
# multi threading so slider updates constantly
# specify other formats to export, rather than just .gif
# Create a custom slider than has start frame and end frame slider marker
# Add ability to add more of these custom sliders so user can export multiple clips to multiple paths in multiple formats
# move everything over to c++?

class ExportingWindow(QtWidgets.QWidget):
    """
    Temporary solution to notify user of export happening until threading gets rolled out.
    """
    def __init__(self, parent=None):
        super(ExportingWindow, self).__init__(parent=parent)
        self.setWindowTitle('Exporting')
        self.setWindowFlags(QtCore.Qt.Tool)
        exporting = QtWidgets.QPushButton('Exporting')
        exporting.setEnabled(False)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(exporting)


class MainWindow(QtWidgets.QDialog):
    """
    Main window of giffer.exe
    """
    def __init__(self, parent=None, starting_video=''):
        super(MainWindow, self).__init__(parent=parent)
        self.setWindowTitle('Giffer')
        self.missing_ffmpeg_text = 'ffmpeg.exe is not set. Use the settings to set it\'s location before exporting.'
        self.video_width = 540
        self.video_height = 960
        self.video_fps = 30
        self.video_fpms = 1000.0 / float(self.video_fps)
        self.skip_range = 5000
        self.current_video = starting_video
        self.exporting_window = ExportingWindow()

        # all variables that class will define
        self.player = None
        self.start_slider = None
        self.slider = None
        self.end_slider = None
        self.play_button = None
        self.start_label = None
        self.current_length_label = None
        self.end_label = None
        self.current_time = None
        self.video_duration_label = None
        self.playing_line = None
        self.export_line = None
        self.info_label = None
        self.timer = None

        # settings and about window ready, build ui and play video if any
        self.settings = Settings(self.updateDisplayInfo, self.clearInfoDisplay)
        self.about = AboutWindow()
        self.build()
        self.setVideoAndPlay(self.current_video)

    def build(self):
        """
        Builds the UI
        """
        # layouts
        main_layout = QtWidgets.QVBoxLayout(self)
        play_layout = QtWidgets.QHBoxLayout()
        slider_layout = QtWidgets.QVBoxLayout()
        frame_cut_layout = QtWidgets.QHBoxLayout()
        current_video_layout = QtWidgets.QHBoxLayout()
        export_gif_layout = QtWidgets.QHBoxLayout()
        info_layout = QtWidgets.QVBoxLayout()

        # menu
        menu = QtWidgets.QMenuBar()
        file_button = menu.addMenu('File')
        help_button = menu.addMenu('Help')

        # open new video action
        open_action = QtWidgets.QAction(QtGui.QIcon.fromTheme('document-open'), '&Open...', parent=file_button)
        open_action.setShortcuts(QtGui.QKeySequence.Open)
        open_action.triggered.connect(self.openFile)
        file_button.addAction(open_action)

        # save action
        save_action = QtWidgets.QAction(QtGui.QIcon.fromTheme('document-save'), '&Save', parent=file_button)
        save_action.setShortcuts(QtGui.QKeySequence.Save)
        save_action.triggered.connect(self.saveGif)
        file_button.addAction(save_action)

        # export action
        export_action = QtWidgets.QAction('Export', parent=file_button)
        export_action.triggered.connect(self.exportGif)
        file_button.addAction(export_action)
        file_button.addSeparator()

        # settings action
        settings_action = QtWidgets.QAction('Settings', parent=file_button)
        settings_action.triggered.connect(self.settings.show)
        file_button.addAction(settings_action)
        file_button.addSeparator()

        # exit the app action
        exit_action = QtWidgets.QAction(QtGui.QIcon.fromTheme("application-exit"), "&Exit", parent=file_button)
        exit_action.triggered.connect(self.close)
        file_button.addAction(exit_action)

        # documentation action
        documentation_action = QtWidgets.QAction('Documentation', parent=help_button)
        documentation_action.triggered.connect(gifutil.openDocumentation)
        help_button.addAction(documentation_action)

        # about action
        about_action = QtWidgets.QAction('About', parent=help_button)
        about_action.triggered.connect(self.about.show)
        help_button.addAction(about_action)

        # player
        video = QtMultimediaWidgets.QVideoWidget()
        video.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.player = QtMultimedia.QMediaPlayer()
        self.player.setVideoOutput(video)

        # start cut label
        self.start_label = QtWidgets.QLabel('0')
        frame_cut_layout.addWidget(self.start_label, alignment=QtGui.Qt.AlignLeft)

        # set start button
        set_start_button = QtWidgets.QPushButton('Set Start')
        set_start_button.setShortcut(QtGui.QKeySequence('S'))
        set_start_button.clicked.connect(self.setStartFrame)
        frame_cut_layout.addWidget(set_start_button)
        frame_cut_layout.addStretch()

        # current length label text
        current_length_label_text = QtWidgets.QLabel('Current .gif length = ')
        frame_cut_layout.addWidget(current_length_label_text)

        # current length label
        self.current_length_label = QtWidgets.QLabel('')
        frame_cut_layout.addWidget(self.current_length_label)
        frame_cut_layout.addStretch()

        # set end button
        set_end_button = QtWidgets.QPushButton('Set End')
        set_end_button.setShortcut(QtGui.QKeySequence('F'))
        set_end_button.clicked.connect(self.setEndFrame)
        frame_cut_layout.addWidget(set_end_button)

        # end cut label
        self.end_label = QtWidgets.QLabel('0')
        frame_cut_layout.addWidget(self.end_label, alignment=QtGui.Qt.AlignLeft)

        # current video playing label
        playing_label = QtWidgets.QLabel('Current Video:')
        playing_label.setFixedWidth(100)
        current_video_layout.addWidget(playing_label, alignment=QtGui.Qt.AlignRight)

        # current video playing line edit
        self.playing_line = QtWidgets.QLineEdit()
        self.playing_line.setReadOnly(True)
        current_video_layout.addWidget(self.playing_line)
        info_layout.addLayout(current_video_layout)

        # current export path label
        export_label = QtWidgets.QLabel('Exporting to:')
        export_label.setFixedWidth(100)
        export_gif_layout.addWidget(export_label, alignment=QtGui.Qt.AlignRight)

        # current export path line edit
        self.export_line = QtWidgets.QLineEdit()
        export_gif_layout.addWidget(self.export_line)
        info_layout.addLayout(export_gif_layout)

        # play button
        self.play_button = QtWidgets.QPushButton()
        self.play_button.setShortcut(QtGui.QKeySequence('Space'))
        self.play_button.clicked.connect(self.togglePlay)
        self.play_button.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_MediaPlay))
        play_layout.addWidget(self.play_button)

        # current time label
        self.current_time = QtWidgets.QLabel('0')
        play_layout.addWidget(self.current_time)
        self.current_time.setFixedWidth(50)

        # create slider
        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider.setRange(0, 0)
        self.slider.valueChanged.connect(self.player.setPosition)
        slider_layout.addWidget(self.slider)

        # start slider
        self.start_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.start_slider.setEnabled(False)
        self.start_slider.setRange(0, 0)
        slider_layout.addWidget(self.start_slider)

        # end slider
        self.end_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.end_slider.setEnabled(False)
        self.end_slider.setRange(0, 0)
        slider_layout.addWidget(self.end_slider)
        play_layout.addLayout(slider_layout)

        # video duration label
        self.video_duration_label = QtWidgets.QLabel('0')
        play_layout.addWidget(self.video_duration_label)

        # finish layouts
        main_layout.addWidget(menu)
        main_layout.addWidget(video)
        main_layout.addLayout(frame_cut_layout)
        main_layout.addLayout(play_layout)
        main_layout.addLayout(info_layout)

        # export button
        export_button = QtWidgets.QPushButton('Export GIF')
        export_button.setShortcut(QtGui.QKeySequence('Ctrl+E'))
        export_button.clicked.connect(self.exportGif)
        export_button.setDefault(True)
        export_button.setFocus()
        main_layout.addWidget(export_button)

        # info label
        self.info_label = QtWidgets.QLabel('')
        main_layout.addWidget(self.info_label)

        # connect callbacks of player at end to avoid errors
        self.player.stateChanged.connect(self.onPlayStateChanged)
        self.player.positionChanged.connect(self.onVideoFrameChange)
        self.player.durationChanged.connect(self.onDurationChanged)

        # will usually show up first time user launches giffer.exe
        # to notify them to set the ffmpeg.exe path
        data = self.settings.getData()
        if not data['ffmpeg'] or not os.path.exists(data['ffmpeg']):
            self.displayError('Invalid ffmpeg.exe path! Please set the location of ffmpeg.exe in the settings')

    def openFile(self):
        """
        Opens a dialog for user to pick video file to play in giffer.exe
        Updates data and plays the video if user picked video.
        """
        data = self.settings.getData()
        starting_directory = data['last_opened']

        dialog = QtWidgets.QFileDialog()
        video_path, _ = dialog.getOpenFileName(self, 'Please select video', starting_directory)

        if not video_path:
            return

        data['last_opened'] = os.path.dirname(video_path)
        self.settings.updateData(data)
        self.setVideoAndPlay(video_path)

    def displayError(self, error_message, raise_error=False):
        """
        Convenience method for displaying error on bottom of giffer.exe

        Args:
            error_message (string): Error message to display.

            raise_error (boolean): Will raise given error message as ValueError if True.
        """
        self.info_label.setText(error_message)
        self.info_label.setStyleSheet('color: red')

        if raise_error:
            raise ValueError(error_message)

    def clearInfoDisplay(self):
        """
        Convenience method for clearing the info display at bottom of giffer.exe
        """
        self.info_label.setStyleSheet('color: black')
        self.info_label.setText('')
        self.timer = None

    def updateDisplayInfo(self):
        """
        Updates the display info that includes current video playing and current export path.
        """
        self.playing_line.setText(self.current_video)
        self.export_line.setText(self.getExportPath())

    def updateVideoInfo(self, new_video):
        """
        Updates what we know about the video with the info from given new video.

        Args:
            new_video (string): Path to video.
        """
        self.current_video = new_video

        if not new_video:
            return

        open_video = cv2.VideoCapture(new_video)
        self.video_width = int(open_video.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.video_height = int(open_video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.video_fps = int(open_video.get(cv2.CAP_PROP_FPS))
        self.video_fpms = 1000.0 / float(self.video_fps)
        self.skip_range = 5000 if self.player.duration() / 10.0 > 5000 else self.player.duration() / 10.0
        open_video.release()

        self.setGeometry(200, 200, self.video_width, self.video_height)

    def setVideoAndPlay(self, file_path, update_video_info=True):
        """
        Plays the video at the given file_path, updates icons, video info, display info.

        Args:
            file_path (string): Path of video to play.

            update_video_info (boolean): If true will update video info.
        """
        if not file_path:
            return

        if update_video_info:
            self.updateVideoInfo(file_path)

        self.player.setMedia(QtMultimedia.QMediaContent(QtCore.QUrl.fromLocalFile(file_path)))
        self.play_button.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_MediaPause))
        self.updateDisplayInfo()
        self.player.play()

    def togglePlay(self):
        """
        Toggles whether we play the video or pause it.
        """
        if self.player.state() == QtMultimedia.QMediaPlayer.PlayingState:
            self.player.pause()
        else:
            self.player.play()

    def pauseVideo(self):
        """
        Pauses the current video being played
        """
        if self.player.state() == QtMultimedia.QMediaPlayer.PlayingState:
            self.player.pause()

    def skipForward(self, amount, pause=True):
        """
        Skips forward in the video the given amount of milliseconds. May pause the video.

        Args:
            amount (int or float): milliseconds to add to current time. Will not go past video duration

            pause (boolean): If True, will pause video.
        """
        if pause:
            self.pauseVideo()

        position = self.player.position()
        duration = self.player.duration()
        if position < duration:
            new_position = position + amount
            new_position = duration if position > duration else new_position
            self.player.setPosition(new_position)

    def skipBackward(self, amount, pause=True):
        """
        Skips backward in the video the given amount of milliseconds. May pause the video.

        Args:
            amount (int or float): milliseconds to subtract from current time. Will not go past video start.

            pause (boolean): If True, will pause video.
        """
        if pause:
            self.pauseVideo()

        position = self.player.position()
        if position > 0:
            new_position = position - amount
            new_position = 0 if new_position < 0 else new_position
            self.player.setPosition(new_position)

    def onPlayStateChanged(self, state):
        """
        Called when video state is changed, this updated the icon of whether is paused or playing.

        Args:
            state (boolean): If True, video is playing, if False video is paused.
        """
        if state == QtMultimedia.QMediaPlayer.PlayingState:
            self.play_button.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_MediaPause))
        else:
            self.play_button.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_MediaPlay))

    def onVideoFrameChange(self, position):
        """
        Updates the slider position and the current time text

        Args:
            position (int): Time in milliseconds video is at.
        """
        self.slider.setValue(position)
        self.current_time.setText(gifutil.toSeconds(position))

    def onDurationChanged(self, duration):
        """
        Usually happens when video is changed, this updates all time values and sliders of video.

        Args:
            duration (int): New duration of video in milliseconds.
        """
        new_duration = gifutil.toSeconds(duration)
        self.slider.setRange(0, duration)
        self.start_slider.setRange(0, duration)
        self.end_slider.setRange(0, duration)
        self.end_slider.setValue(duration)
        self.end_label.setText(new_duration)
        self.video_duration_label.setText(new_duration)
        self.start_slider.setValue(0)
        self.start_label.setText('0')
        self.updateCurrentLength()

    def updateCurrentLength(self):
        """
        Updates the current length of the export gif label. Subtracts end cut with start cut.
        """
        a = self.end_label.text()
        b = self.start_label.text()
        subtracted = gifutil.subtractStrings(a, b)
        subtracted = subtracted if subtracted else '0'
        self.current_length_label.setText(subtracted)

    def setStartFrame(self):
        """
        Sets the start cut for where the .gif should start.
        """
        position = gifutil.toSeconds(self.player.position(), text=False)
        end_position = float(self.end_label.text())

        if position >= end_position:
            position = end_position - 0.01

        self.start_label.setText(f'{position:0.3}')
        self.start_slider.setValue(position * 1000.0)
        self.updateCurrentLength()

    def setEndFrame(self):
        """
        Sets the end cut for when the .gif should end.
        """
        position = gifutil.toSeconds(self.player.position(), text=False)
        start_position = float(self.start_label.text())

        if position <= start_position:
            position = start_position + 0.01

        self.end_label.setText(f'{position:0.3}')
        self.end_slider.setValue(position * 1000.0)
        self.updateCurrentLength()

    def validatePath(self, path, name, raise_error=False, gifsicle=False):
        """
        Mainly used to validate the path of ffmpeg, convert, and/or gifsicle.

        Args:
            path (string): Path to check and see if exists.

            name (string): Name of program we are validating, used to display error for user.

            raise_error (boolean): If True, will raise error to console.

            gifsicle (boolean): Adds extra string to tell user we export and unoptimized gif.

        Returns:
            (boolean): True if path exists, False if path does NOT exist.
        """
        if os.path.exists(path):
            return True
        else:
            error_message = 'Invalid ' + name + ' path! Please set the location of ' + name + ' in the settings!'
            error_message = error_message + ' Exported UNOPTIMIZED .gif' if gifsicle else error_message
            self.displayError(error_message)
            if raise_error:
                raise ValueError(error_message)
            else:
                return False

    def finishedExporting(self):
        """
        Displays that video finished exporting, closes export window.
        """
        if self.timer:
            self.timer.cancel()

        self.exporting_window.close()
        self.info_label.setText('Finished Exporting')
        self.info_label.setStyleSheet('color: black')
        self.timer = threading.Timer(5.0, self.clearInfoDisplay)
        self.timer.start()

    def writeGif(self, path, colors=256):
        """
        This is where the magic happens. Writes a .gif from to given path using ffmpeg.

        Args:
            path (string): Where we should write the .gif to.

            colors (int): Must be exponent of 2. Used to optimize .gif when using gifsicle.exe
        """
        if not path:
            self.displayError('No video has been loaded! Please load video.', raise_error=True)

        # get the data
        data = self.settings.getData()
        ffmpeg_path = data['ffmpeg']
        convert_path = data['convert']
        gifsicle_path = data['gifsicle']
        use_convert = data['use_convert']
        use_gifsicle = data['use_gifsicle']

        # ffmpeg.exe is required for gif conversion to work
        if not self.validatePath(ffmpeg_path, 'ffmpeg.exe'):
            return

        # make temp directory to store everything we could make
        temp_directory = tempfile.mkdtemp()
        png_directory = os.path.join(temp_directory, 'pngs')
        temp_gif_path = os.path.join(temp_directory, 'Temp.gif')
        temp_gifsicle_path = os.path.join(temp_directory, 'TempOptimized.gif')
        png_path = os.path.join(png_directory, 'temp_image%04d.png')
        os.makedirs(png_directory)

        # if True, we convert video to .png and then make a .gif from the .pngs
        if use_convert:

            # validate that convert.exe has been set correctly
            if not self.validatePath(convert_path, 'convert.exe'):
                shutil.rmtree(temp_directory)
                return

            # convert video to .png using ffmpeg.exe, then convert .png to .gif using convert.exe
            try:
                self.exporting_window.show()
                self.ffmpegVideoToPng(ffmpeg_path, self.current_video, png_path)
                self.convertPngToGif(convert_path, png_directory, temp_gif_path)
            except Exception:
                # clean up and display error before raising error
                shutil.rmtree(temp_directory)
                self.displayError('Using ffmpeg.exe and/or convert.exe failed! ')
                self.exporting_window.close()
                raise

        # if False, we convert video to .gif without extracting each frame
        else:
            try:
                # convert video to .gif using ffmpeg.exe
                self.exporting_window.show()
                self.ffmpegCreateGif(ffmpeg_path, self.current_video, temp_gif_path)
            except Exception:
                # clean up and display error before raising error
                shutil.rmtree(temp_directory)
                self.displayError('ffmpeg.exe failed! ')
                self.exporting_window.close()
                raise

        # gifsicle attempts to optimize .gif size
        if use_gifsicle:
            if not self.validatePath(gifsicle_path, 'gifsicle.exe', gifsicle=True):
                return

            # use gifsicle to create new optimized .gif
            try:
                self.gifsicleOptimize(gifsicle_path, temp_gif_path, temp_gifsicle_path, colors)
                temp_gif_path = temp_gifsicle_path
            except Exception:
                # display failure in case we fail, but continue to export unoptimized gif
                self.displayError('gifsicle.exe failed! Exported UNOPTIMIZED .gif')

        # this is essentially overwriting the path
        if os.path.exists(path):
            os.remove(path)

        # move exported .gif to desired path, remove temp directories, print finished
        os.rename(temp_gif_path, path)
        shutil.rmtree(temp_directory)
        self.finishedExporting()

        if data['auto_close']:
            self.close()

    def ffmpegCreateGif(self, ffmpeg_path, input_path, output):
        """
        Creates .gif using ffmpeg.exe only

        Args:
            ffmpeg_path (string): Path to ffmpeg.exe

            input_path (string): Path to video that we are grabbing footage from.

            output (string): Path to export .gif to. NOTE: Will NOT overwrite.
        """
        ffmpeg_command = '"%(FFMPEG_PATH)s" -ss %(START_TIME)s -t %(LENGTH)s -i "%(INPUT_PATH)s" -filter_complex "[0:v] fps=%(FPS)i,split [a][b];[a] palettegen [p];[b][p] paletteuse" "%(OUTPUT_PATH)s"' % \
                         {
                             'FFMPEG_PATH': ffmpeg_path,
                             'START_TIME': self.start_label.text(),
                             'LENGTH': str(float(self.end_label.text()) - float(self.start_label.text())),
                             'INPUT_PATH': input_path,
                             'FPS': self.video_fps,
                             'OUTPUT_PATH': output
                         }
        subprocess.check_call(ffmpeg_command, shell=True)

    def ffmpegVideoToPng(self, ffmpeg_path, input_path, output):
        """
        Converts given input_path to a .png image sequence.

        Args:
            ffmpeg_path (string): Path to ffmpeg.exe

            input_path (string): Path to video that we are grabbing footage from.

            output (string): Path to export .png image sequence to. NOTE the file name convention, e.g: temp_image%04d.png
        """
        ffmpeg_command = '"%(FFMPEG_PATH)s" -ss %(START_TIME)s -t %(LENGTH)s -i "%(INPUT_PATH)s" "%(OUTPUT_PATH)s"' % \
                         {
                             'FFMPEG_PATH': ffmpeg_path,
                             'START_TIME': self.start_label.text(),
                             'LENGTH': str(float(self.end_label.text()) - float(self.start_label.text())),
                             'INPUT_PATH': input_path,
                             'OUTPUT_PATH': output
                         }
        subprocess.check_call(ffmpeg_command, shell=True)

    def convertPngToGif(self, convert_path, png_directory, output_gif):
        """
        Converts a directory filled with an image sequence to .gif using convert.exe

        Args:
            convert_path (string): Path to imagemagick's convert.exe

            png_directory (string): Path to directory with image sequence in it.

            output_gif (string): Path to export .gif to.
        """
        create_gif_command = '"%(CONVERT_PATH)s" -background gray -alpha remove -alpha off -delay 1x%(FPS)i "%(TEMP)s" "%(OUTPUT_GIF_FILENAME)s"' % \
                             {
                                 'CONVERT_PATH': convert_path,
                                 'FPS': self.video_fps,
                                 'TEMP': os.path.join(png_directory, '*.png'),
                                 'OUTPUT_GIF_FILENAME': output_gif
                             }
        subprocess.check_call(create_gif_command, shell=True)

    @staticmethod
    def gifsicleOptimize(gifsicle_path, input_path, output_path, colors=256):
        """
        Runs gifsicle.exe on given input_path .gif to optimize it. Works sometimes. Especially if colors is <= 64

        Args:
            gifsicle_path (string): Path to gifsicle.exe

            input_path (string): Path of .gif to optimize.

            output_path (string): Path to export .gif to. NOTE: will NOT overwrite, must be different than input path.

            colors (int): Must be exponent of 2. Colors that final .gif will have.
        """
        subprocess.check_call('"' + gifsicle_path + '" -i "' + input_path + '" -O3 --colors ' + str(colors) + ' -o "' + output_path + '"', shell=True)

    def saveGif(self):
        """
        Opens file dialog window for user to choose where to save .gif
        Will export .gif
        """
        dialog = QtWidgets.QFileDialog()
        save_path = dialog.getSaveFileName(self, 'Save Gif')

        if not save_path:
            return

        save_path = save_path if save_path.endswith('.gif') else save_path + '.gif'
        self.writeGif(save_path)

    def getExportPath(self):
        """
        Gets where giffer should export .gif to. If export directory is not set,
        Exports to same location as current video file.

        Returns:
            (string): Path to where .gif should export to.
        """
        if not self.current_video:
            return ''

        data = self.settings.getData()
        export_directory = data['export'] if data['export'] else os.path.dirname(self.current_video)
        file_name, _ = os.path.splitext(self.current_video)
        export_path = os.path.join(export_directory, os.path.basename(file_name + '.gif'))
        export_path = export_path.replace('\\', '/')
        return export_path

    def exportGif(self):
        """
        Convenience method for exporting .gif to correct path.
        """
        self.writeGif(self.getExportPath())

    def keyPressEvent(self, event):
        """
        Overwriting function to create keyboard shortcuts.

        Args:
            event (QEvent): Used to figure out what is happening. Should run event.accept() when finished overwriting.
        """

        key = event.key()

        if key == QtCore.Qt.Key_D:
            # pause/play video
            self.togglePlay()
        elif key == QtCore.Qt.Key_E:
            # move to beginning
            self.player.setPosition(0)
        elif key == QtCore.Qt.Key_Left:
            # move back range
            self.skipBackward(self.skip_range, False)
        elif key == QtCore.Qt.Key_Right:
            # move forward range
            self.skipForward(self.skip_range, False)
        elif key == QtCore.Qt.Key_Period:
            # pause video, move forward one frame
            self.skipForward(self.video_fpms)
        elif key == QtCore.Qt.Key_Comma:
            # pause video, move back one frame
            self.skipBackward(self.video_fpms)

        event.accept()

    def closeEvent(self, event):
        """
        Overwriting close event to close possible about or settings windows that may be open.

        Args:
            event (QEvent): Accepting when other windows are closed.
        """
        self.settings.close()
        self.settings.deleteLater()

        self.about.close()
        self.about.deleteLater()

        event.accept()
