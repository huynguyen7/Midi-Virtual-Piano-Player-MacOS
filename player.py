from pynput.keyboard import Key, Controller
from pynput import keyboard
import threading


global isPlaying
global infoTuple
global song
global playback_speed_rate  # Get from user input

controller = Controller()
isPlaying = False
storedIndex = 0
conversionCases = {'!': '1', '@': '2', '£': '3', '$': '4', '%': '5', '^': '6', '&': '7', '*': '8', '(': '9', ')': '0'}

scan_code_delete = Key.delete
scan_code_shift = Key.shift
scan_code_end = Key.end
scan_code_home = Key.home

def onDelPress():
    global isPlaying
    isPlaying = not isPlaying

    if isPlaying:
        print("Playing...")
        playNextNote()
    else:
        print("Stopping...")

    return True

def isShifted(charIn):
    asciiValue = ord(charIn)
    if(asciiValue >= 65 and asciiValue <= 90):
        return True
    if(charIn in "!@#$%^&*()_+{}|:\"<>?"):
        return True
    return False

def pressLetter(strLetter):
    if isShifted(strLetter):
        # we have to convert all symbols to numbers
        if strLetter in conversionCases:
            strLetter = conversionCases[strLetter]
        controller.release(strLetter.lower())
        controller.press(scan_code_shift)
        controller.press(strLetter.lower())
        controller.release(scan_code_shift)
    else:
        controller.release(strLetter)
        controller.press(strLetter)
    return
    
def releaseLetter(strLetter):
    if isShifted(strLetter):
        if strLetter in conversionCases:
                strLetter = conversionCases[strLetter]
        controller.release(strLetter.lower())
    else:
        controller.release(strLetter)
    return
    
def processFile():
    global playback_speed
    global playback_speed_rate
    global song
    with open(song,"r") as macro_file:
        lines = macro_file.read().split("\n")
        tOffsetSet = False
        tOffset = 0
        playback_speed = float(lines[0].split("=")[1]) * playback_speed_rate
        print("Playback speed is set to %.2f" % playback_speed)
        tempo = 60/float(lines[1].split("=")[1])
        
        processedNotes = []
        
        for l in lines[1:]:
            l = l.split(" ")
            if(len(l) < 2):
                # print("INVALID LINE")
                continue
            
            waitToPress = float(l[0])
            notes = l[1]
            processedNotes.append([waitToPress,notes])
            if(not tOffsetSet):
                tOffset = waitToPress
                print("Start time offset =",tOffset)
                tOffsetSet = True

    return [tempo,tOffset,processedNotes]

def floorToZero(i):
    if(i > 0):
        return i
    else:
        return 0

# for this method, we instead use delays as l[0] and work using indexes with delays instead of time
# we'll use recursion and threading to press keys
def parseInfo():
    
    tempo = infoTuple[0]
    notes = infoTuple[2][1:]
    
    # parse time between each note
    # while loop is required because we are editing the array as we go
    i = 0
    while i < len(notes)-1:
        note = notes[i]
        nextNote = notes[i+1]
        if "tempo" in note[1]:
            tempo = 60/float(note[1].split("=")[1])
            notes.pop(i)

            note = notes[i]
            if i < len(notes)-1:
                nextNote = notes[i+1]
        else:
            note[0] = (nextNote[0] - note[0]) * tempo
            i += 1

    # let's just hold the last note for 1 second because we have no data on it
    notes[len(notes)-1][0] = 1.00

    return notes

def playNextNote():
    global isPlaying
    global storedIndex
    global playback_speed

    notes = infoTuple[2]
    if isPlaying and storedIndex < len(infoTuple[2]):
        noteInfo = notes[storedIndex]
        delay = floorToZero(noteInfo[0])

        if noteInfo[1][0] == "~":
            #release notes
            for n in noteInfo[1][1:]:
                releaseLetter(n)
        else:
            #press notes
            for n in noteInfo[1]:
                pressLetter(n)
        if("~" not in noteInfo[1]):
            print("%10.2f %15s" % (delay,noteInfo[1]))
        #print("%10.2f %15s" % (delay/playback_speed,noteInfo[1]))
        storedIndex += 1
        if(delay == 0):
            playNextNote()
        else:
            threading.Timer(delay/playback_speed, playNextNote).start()
    elif storedIndex > len(infoTuple[2])-1:
        isPlaying = False
        storedIndex = 0

def rewind():
    global storedIndex
    if storedIndex - 10 < 0:
        storedIndex = 0
        
    else:
        storedIndex -= 10
    print("Rewound to %.2f" % storedIndex)

def skip():
    global storedIndex
    if storedIndex + 10 > len(infoTuple[2]):
        isPlaying = False
        storedIndex = 0
    else:
        storedIndex += 10
    print("Skipped to %.2f" % storedIndex)

def on_press(key):
    if key == Key.delete:
        onDelPress()
    elif key == Key.home:
        rewind()
    elif key == Key.end:
        skip()

def main():
    import sys
    import os

    global song
    global playback_speed_rate
    playback_speed_rate = 1.0

    if len(sys.argv) >= 2:
        song = "./sheets/%s_song.txt" % sys.argv[1]

        if not os.path.exists(song):
            print(f"Error: file not found '{song}'")
            return 1

        if len(sys.argv) == 3 and sys.argv[2] != None:
            try:
                playback_speed_rate = float(sys.argv[2])
            except:
                print('[Error] Input playback speed rate is not a float.')
                return 1
    else:
        print('Please input a song name that available in your sheets folder.')
        return 1

    global isPlaying
    global infoTuple
    global playback_speed
    infoTuple = processFile()
    infoTuple[2] = parseInfo()
    
    with keyboard.Listener(on_press=on_press) as listener:
        try:
            listener.join()
        except Exception as e:
            print('EXITED.')
    
    print()
    print("Controls")
    print("-"*20)
    print("Press DELETE to play/pause")
    print("Press HOME to rewind")
    print("Press END to advance")
    while True:
        input("Press Ctrl-C to exit\n\n")
        
if __name__ == "__main__":
    main()
