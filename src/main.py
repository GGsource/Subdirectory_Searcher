from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import os
import glob
import ctypes
myappid = 'torimato.subdirectory_searcher'  # arbitrary string
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)


# To get screen resolution & place window at center of screen
user32 = ctypes.windll.user32
screenX, screenY = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
windowX, windowY = 1600, 900
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
def addHundred(givenGrid, givenOrderedFiles):
    global listLimit
    i = listLimit - 100
    while i < listLimit:
        file = givenOrderedFiles.pop(0).split("\Mugs\\", 1)[1]
        # givenListWidget.addItem(QListWidgetItem(
        #     str(i+1) + ". " + file))
        addThumbnail(givenGrid, file, i, 7)
        i += 1
    listLimit += 100

# addThumbnail -
# Adds a thumbnail to the grid


def addThumbnail(givenGrid, givenFile, ndx, rowLen):
    fullPath = mugPath+givenFile
    # Create an instance of an image from file in img folder
    image = QPixmap(fullPath)
    # Crop the image to a square, centered on the image
    image = cropAtCenter(image)
    # Resize the image to 200x200
    image = image.scaled(200, 200, Qt.KeepAspectRatio)
    # Add the image's extension type to the bottom right corner of the image
    image = addImageType(image, fullPath.split(".")[-1])
    # Modify the image to have rounded corners
    image = roundImage(image, 15)
    # Add the image to the grid by creating a label and setting the image
    imageLabel = QLabel()
    imageLabel.setPixmap(image)
    imageLabel.setObjectName(givenFile)
    # Connect the label to the openItem function when double clicked
    imageLabel.mouseDoubleClickEvent = lambda event: openItem(
        imageLabel.objectName(), True)

    # Add the thumbnails in rows of length 5
    givenGrid.addWidget(imageLabel, int(ndx/rowLen), ndx % rowLen)

# cropAtCenter -
# Crops the image to a square, centered on the image, keeping in mind whether the image is landscape or portrait


def cropAtCenter(givenImage):
    if givenImage.width() > givenImage.height():
        givenImage = givenImage.copy(int((givenImage.width() - givenImage.height()) / 2), 0,
                                     givenImage.height(), givenImage.height())
    else:
        givenImage = givenImage.copy(0, int((givenImage.height() - givenImage.width()) / 2),
                                     givenImage.width(), givenImage.width())
    return givenImage

# roundImage -
# Modifies the image to have rounded corners


def roundImage(givenImage, radius):
    # FIXME: Fix anti-aliasing on the edges of the image
    mask = QBitmap(givenImage.size())
    mask.fill(Qt.color0)
    painter = QPainter(mask)
    painter.setBrush(Qt.color1)
    painter.setPen(Qt.color1)
    painter.drawRoundedRect(mask.rect(), radius, radius)
    givenImage.setMask(mask)
    painter.end()
    return givenImage

# addImageType -
# Adds the image's extension type with a dark blue rectangle behind it. All of this is in the bottom right corner of the image


def addImageType(givenImage, givenType):
    painter = QPainter(givenImage)
    painter.setPen(QPen(QColor(0, 0, 0, 0)))
    painter.setBrush(QBrush(QColor(0, 0, 0, 100)))
    painter.drawRect(givenImage.width() - 50, givenImage.height() -
                     20, 50, 20)
    painter.setPen(QPen(Qt.white))
    painter.setFont(QFont("Arial", 12))
    painter.drawText(givenImage.width() - 50, givenImage.height() -
                     20, 50, 20, Qt.AlignCenter, givenType)
    painter.end()
    return givenImage

# openItem -
# Opens the file that was double clicked


def openItem(item, isRelative=False):
    if (not isRelative):
        relativePath = item.text().split(" ", 1)
        fullPath = mugPath+relativePath[1]
    else:
        fullPath = f"{mugPath}{item}"
    print(f"Opening: '{fullPath}'")
    os.startfile(fullPath, 'open')

#############################################################################################
#############################################################################################

# Main Function


def main():
    # Create the application
    app = QApplication([])  # Create an instance of QtWidgets.QApplication
    app.setApplicationName("MugBox")  # Set the name of the application
    window = QWidget()  # Create an instance of QtWidgets.QWidget
    # Set size and position of window
    window.setGeometry(placementX, placementY, windowX, windowY)

    # Create a list of the most recent files
    newestOrderedFiles = getFiles()  # Get a list of the most recent files
    # Create an instance of QtWidgets.QListWidget
    # listWidget = QListWidget(window)
    # # Set the list's width to be 1/4th of the window's width
    # listWidget.setFixedWidth(int(window.width()/4))
    # # Create an instance of QtWidgets.QScrollBar
    # scrollBar = QScrollBar(window)
    # # Set the vertical scroll bar to the one we just created
    # listWidget.setVerticalScrollBar(scrollBar)
    # # Connect item activation to the openItem function
    # listWidget.itemActivated.connect(openItem)

    # Create a grid layout
    grid = QGridLayout()
    # Creat scroll area for grid
    scrollArea = QScrollArea()
    scrollArea.setWidgetResizable(True)
    # Create a widget to hold the grid
    client = QWidget()
    client.setLayout(grid)
    # Set the widget of the scroll area to the grid
    scrollArea.setWidget(client)

    # Add the first 100 items to the list
    addHundred(grid, newestOrderedFiles)

    # Create a button to add 100 more items to the list
    addHundredButton = QPushButton(parent=window, text="Add 100 more to list")
    # Connect the button to the addHundred function
    addHundredButton.clicked.connect(
        lambda: addHundred(grid, newestOrderedFiles))
    # addHundredButton.setFixedSize(100, 20)  # Set the size of the button
    addHundredButton.setFixedHeight(60)

    # Create a vertical box layout and add the list and button to it
    vBox = QVBoxLayout(window)

    # Create a horizontal box layout and add the list and a new grid to it
    # hBox = QHBoxLayout()
    # hBox.addWidget(listWidget)

    # hBox.addWidget(scrollArea)

    # Create a custom title bar that be used to close the program
    titleBar = QWidget()
    titleBar.setFixedHeight(30)
    titleBarLayout = QHBoxLayout()
    titleBar.setLayout(titleBarLayout)
    closeButton = QPushButton("X")
    closeButton.setFixedSize(30, 30)
    closeButton.clicked.connect(app.quit)
    titleBarLayout.addWidget(closeButton)

    vBox.addWidget(titleBar)
    vBox.addWidget(scrollArea)  # Add the list to the layout
    vBox.addWidget(addHundredButton)  # Add the button to the layout

    # Set application icon for the taskbar
    app.setWindowIcon(QIcon("res/icons/laugh.png"))

    # Show the window and run the application
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()


# Features to add:
# TODO: Make custom look with semi-transparent background
# TODO: Make custom title bar
# TODO: Add a search bar
# TODO: Add a context menu to the items in the grid, so that you can right click on an item and open it in app, in explorer, or delete it
# TODO: Add ability to filter by folder names
# TODO: Add some visual indication if items next to each other are from the same folder
# TODO: Add ability to sort by folder name
# TODO: Replace opening image with a built in image viewer
# TODO: Exclude directories from the list, otherwise they show up as blank images
# TODO: Make gifs auto-play
# TODO: Put play button over videos if applicable
# TODO: Add "copy" button to context menu to copy the image to the clipboard
