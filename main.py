from PyQt5.QtWidgets import *
import os
import glob
import ctypes
import subprocess

# To get screen resolution & place window at center of screen
user32 = ctypes.windll.user32
screenX, screenY = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
windowX, windowY = 1280, 720
placementX = int((screenX/2) - (windowX/2))
placementY = int((screenY/2) - (windowY/2))

# Path to folder holding all other folders
mugPath = "M:\OneDrive - University of Illinois Chicago\Mugs\\"
#
listLimit = 100

#############################################################################################
#############################################################################################
# Helper Functions

# getfiles -
# Returns a list of the most recent files in a given folder and two subfolders deeper


def getFiles():
    listOfFiles = glob.glob(mugPath+"*\\*\\*\\*") + \
        glob.glob(mugPath+"\\*\\*\\*") + \
        glob.glob(mugPath+"\\*\\*")
    return sorted(listOfFiles, key=os.path.getctime, reverse=True)

# PrintList -
# Prints out a list one item at a time.


def printList(list):
    for item in list:
        print(item)


# addHundred -
# Adds 100 more items to the list
def addHundred(givenListWidget, givenOrderedFiles):
    global listLimit
    i = listLimit - 100
    while i < listLimit:
        file = givenOrderedFiles.pop(0).split("\Mugs\\", 1)[1]
        givenListWidget.addItem(QListWidgetItem(
            str(i+1) + ". " + file))
        i += 1
    listLimit += 100


def openItem(item):
    relativePath = item.text().split(" ", 1)
    fullPath = mugPath+relativePath[1]
    print(f"Opening: '{fullPath}'")
    os.startfile(fullPath, 'open')


#############################################################################################
#############################################################################################

# Main Function
def main():

    app = QApplication([])
    app.setApplicationName("MugBox")
    window = QWidget()
    window.setGeometry(placementX, placementY, windowX, windowY)

    newestOrderedFiles = getFiles()
    listWidget = QListWidget(window)
    scrollBar = QScrollBar(window)
    listWidget.setVerticalScrollBar(scrollBar)
    listWidget.itemDoubleClicked.connect(openItem)
    addHundred(listWidget, newestOrderedFiles)

    addHundredButton = QPushButton(parent=window, text="Add 100 more to list")
    addHundredButton.clicked.connect(
        lambda: addHundred(listWidget, newestOrderedFiles))
    addHundredButton.resize(100, 100)

    vertBox = QVBoxLayout(window)
    vertBox.addWidget(listWidget)
    vertBox.addWidget(addHundredButton)

    window.setStyleSheet("background-color: rgb(40, 44, 52); color: white")
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
