QUICK-START GUIDE:

NOTES: This works for MacOS X. Windows is not tested.

1) Install requirements python modules and build resources folders:
$ pip install requirements.txt
$ mkdir mid-src > /dev/null
$ mkdir sheets > /dev/null

2) Download your favourite Midi files and put them into mid-src folder

NOTES: $(song) is the file name (don't include .mid at the end), sensitive case!
3) Change your directory to the project root folder. Then run:
$ python3 converter.py $(song)

4) Run the player:
# python3 player.py $(song)

5) Key binding for player:
* Ctrl-C: Quit
* Delete: Play/Stop
* Home: Restart the track.
* End: Advance
