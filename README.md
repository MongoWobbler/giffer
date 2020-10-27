# giffer
Tool to quickly extract a .gif from a video using ffmpeg and PySide2

**Requires**:  
* FFmpeg - https://ffmpeg.org/download.html
* K-Lite Codec Pack (Basic) - https://codecguide.com/download_kl.htm

*Optional*:  
* Imagemagick - https://imagemagick.org/script/download.php
* Gifsicle - https://www.lcdf.org/gifsicle/

Get the binary for Windows from the releases! Or run the script yourself, or freeze/build the binary with pyinstaller. More instructions on running script and building/freezing further down.

-------------------------------------------------------------

![giffer Main Window](https://i.imgur.com/ZJpjCIW.png)

To use:
1. Launch giffer.exe
1. Set the path to FFmpeg.exe using the settings. File>Settings>**Set ffmpeg**
1. Use File>Open to open a video.
1. Set where you would like the .gif to start with the "Set Start" button.
1. Set where you would like the .gif to end with the "Set End" button.
1. Press "Export Gif"!

Launch a video with giffer.exe by using the settings to create a right click shortcut.  
**Must have launched giffer.exe as Administrator to create right click shortcut**  
*File>Settings>Create Right Click Shortcut*  
Go to a video file, right click, and press "Launch with Giffer".

--------------------------------------------------------------

**DOCUMENTATION**

I suggest only exporting with ffmpeg.exe, but feel free to expirement using convert.exe and/or gifsicle.exe

![giffer Settings Window](https://i.imgur.com/olKRV2L.png)

Buttons:
* Set Start - Set where the .gif should start playing
* Set End - Set where the .gif should stop playing.
* Play button - Toggle between play and pause.
* Export Gif - Exports the gif to the path in the "Exporting to:" line.

Settings:  
* Set ffmpeg - Opens file dialog to choose where ffmpeg.exe is located
* Set convert - Opens file dialog to choose where imagemagick's convert.exe is located
* Set gifsicle - Opens file dialog to choose where gifsicle.exe is located
* Clear/Set Export Directory - Pick the directory where you would like .gifs to be exported to
* Close giffer.exe after exporting - If checked, will close giffer.exe after performing an export
* Create Right Click Shortcut - Note: Must be an administrator since this will modify Windows Registry. Will create a shortcut to launch giffer.exe when right clicking on a file.
* Remove Right Click Shortcut - Note: Must be an administrator since this will modify Windows Registry. WIll remove the right click shortcut for giffer.exe

Shortcuts:  
* Ctrl+O: Open video
* Ctrl+S: Save video as .gif
* Space: Play/Pause
* D: Play/Pause
* E: Go to start of video
* S: Set Start Frame
* F: Set End Frame
* ,: Move back one frame
* .: Move forward one frame
* Left arrow: Skip backward
* Right arrow: Skip forward

---------------------------------------------------------------

To run script instead of binary, use Python 3.7.x and run "build_giffer.py".  
Requires:  
* PySide2
* opencv-python

To freeze/build the binary using pyinstaller, run the following command in the terminal where build.giffer.py is located  
```pyinstaller "build_giffer.py" -F --noconsole --name giffer```

----------------------------------------------------------------

Potential Future Features:
- [ ] Multi Threading so UI doesnt freeze up on export, etc.
- [ ] Specify other formats to export, rather than just .gif
- [ ] Custom slider that has start and end marks
- [ ] Add more export sliders to export multiple files at once
- [ ] Move everything to C++
