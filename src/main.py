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
windowX, windowY = 1440, 810
placementX = int((screenX/2) - (windowX/2))
placementY = int((screenY/2) - (windowY/2))
# Path to folder holding all other folders
mugPath = "M:\OneDrive\Mugs\\"
iconPath = "res\icons\Mugbox_Icon_4"
darkIcon = iconPath+".png"
lightIcon = iconPath+"_light.png"
listColumnCount = 7
listLimit = listColumnCount * 10
thumnailSize = 190
titleBarX = 0
titleBarY = 0
loop = QEventLoop()

#############################################################################################
#############################################################################################
# Helper Functions

# getfiles -
# Returns a list of the most recent files in a given folder and two subfolders deeper


def getFiles():
    listOfFiles = glob.glob(mugPath+"*\\*\\*\\*") + \
        glob.glob(mugPath+"\\*\\*\\*") + \
        glob.glob(mugPath+"\\*\\*")
    # Exclude the folders
    listOfFiles = [file for file in listOfFiles if os.path.isfile(file)]
    return sorted(listOfFiles, key=os.path.getctime, reverse=True)

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

# addHundred -
# Adds 100 more items to the list

# TODO: Change instead of adding 100, add the number of items that will fill our chosen number of columns and rows


def addImagesToGrid(imageCount, givenGrid, givenOrderedFiles, isExpedited=False):
    global listLimit
    i = listLimit - imageCount
    while i < listLimit:
        file = givenOrderedFiles.pop(0).split("\Mugs\\", 1)[1]
        if addThumbnail(givenGrid, file, i, listColumnCount, isExpedited):
            i += 1
    listLimit += imageCount

# addThumbnail -
# Adds a thumbnail to the grid
def addThumbnail(givenGrid, givenFile, ndx, rowLen, isExpedited=False):
    fullPath = mugPath+givenFile
    fileExtension = fullPath.split(".")[-1]
    supportedFileTypes = ["png", "jpg", "jpeg", "gif", "bmp", "webp", "jfif"]
    if (fileExtension not in supportedFileTypes):
        print(f"Found unsupported file type for file: {givenFile}. Skipping...")
        return False
    # Create an instance of an image from file in img folder
    image = QPixmap(fullPath)
    # Save the image's original size to show as info later
    originalSize = image.size()
    # Crop the image to a square, centered on the image
    image = cropAtCenter(image)
    # Resize the image to thumbnailsize x thumbnailsize
    image = image.scaled(thumnailSize, thumnailSize, Qt.KeepAspectRatio)
    # Add the image's extension type to the bottom right corner of the image
    image = addImageType(image, fullPath.split(".")[-1])
    # Now, add the original dimensions right above the extension type, also with a dark blue rectangle behind it
    image = addDimensions(image, originalSize)
    # Modify the image to have rounded corners
    image = roundImage(image, 15)
    # Add the image to the grid by creating a label and setting the image
    imageLabel = QLabel()
    imageLabel.setPixmap(image)
    imageLabel.setObjectName(givenFile)
    # Connect the label to the openItem function when double clicked
    imageLabel.mouseDoubleClickEvent = lambda event: openItem(
        imageLabel.objectName(), True)
    # Add the thumbnails in rows of length given
    givenGrid.addWidget(imageLabel, int(ndx/rowLen), ndx % rowLen)
    if (not isExpedited):
        QTimer.singleShot(50, loop.quit)
        loop.exec_()
    return True

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

# addDimentions -
# Adds the original dimensions right above the extension type, also with a dark blue rectangle behind it


def addDimensions(givenImage, givenSize):
    painter = QPainter(givenImage)
    painter.setPen(QPen(QColor(0, 0, 0, 0)))
    painter.setBrush(QBrush(QColor(0, 0, 0, 100)))
    painter.drawRect(0, givenImage.height() - 20, 100, 20)
    painter.setPen(QPen(Qt.white))
    painter.setFont(QFont("Arial", 12))
    painter.drawText(0, givenImage.height() - 20, 100, 20,
                     Qt.AlignCenter, str(givenSize.width()) + "x" + str(givenSize.height()))
    painter.end()
    return givenImage

# addDragAbility -
# Adds the ability to drag the title bar and move the window


def addDragAbility(draggableRegionWidget, window):
    # Set the draggable region's position to be the same as the draggable region widget
    draggableRegionWidget.move(draggableRegionWidget.pos())
    # first save the position of the mouse with titleBarX and titleBarY
    draggableRegionWidget.mousePressEvent = lambda event: saveMousePos(event)
    # then move the window to the new position
    draggableRegionWidget.mouseMoveEvent = lambda event: moveWindow(
        event, window)


# saveMousePos -
# Saves the position of the mouse when the mouse is pressed
def saveMousePos(event):
    global titleBarX, titleBarY
    titleBarX = event.globalX()
    titleBarY = event.globalY()

# moveWindow -
# Moves the window to the new position


def moveWindow(event, window):
    global titleBarX, titleBarY
    # Get the new position of the mouse
    newX = event.globalX()
    newY = event.globalY()
    # Move the window to the new position
    window.move(window.x() + (newX - titleBarX),
                window.y() + (newY - titleBarY))
    # Update the position of the mouse
    titleBarX = newX
    titleBarY = newY

# populateMenu -
# Fills out the menu with a scrollable list of all the top level folders inside the root folder


def populateMenu(containerLayout):
    # Create a list of all the top level folders inside the root folder
    folders = os.listdir(mugPath)
    newContainer = QWidget()
    initializeWidget(newContainer, folders)
    containerLayout.addWidget(newContainer)

def initializeWidget(self, items):
    listBox = QVBoxLayout(self)
    self.setLayout(listBox)

    scroll = QScrollArea(self)
    listBox.addWidget(scroll)
    scroll.setWidgetResizable(True)
    scrollContent = QWidget(scroll)

    scrollLayout = QVBoxLayout(scrollContent)
    scrollContent.setLayout(scrollLayout)
    for item in items:
        itemLabel = QLabel(item)
        scrollLayout.addWidget(itemLabel)
    scroll.setWidget(scrollContent)


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
    grid.setHorizontalSpacing(0)
    grid.setVerticalSpacing(2)
    # Creat scroll area for grid
    scrollArea = QScrollArea(objectName="scrollArea")
    scrollArea.setWidgetResizable(True)
    scrollArea.setAutoFillBackground(True)
    # Create a widget to hold the grid
    client = QWidget()
    client.setLayout(grid)
    # Set the widget of the scroll area to the grid
    scrollArea.setWidget(client)

    # Add the first 10 rows of items to the list
    addImagesToGrid(listColumnCount * 10, grid, newestOrderedFiles, True)

    # Create a button to add 100 more items to the list
    addHundredButton = QPushButton(
        parent=window, text="Load next 5 rows", objectName="addHundredButton")
    # Connect the button to the addHundred function
    addHundredButton.clicked.connect(
        lambda: addImagesToGrid(5 * listColumnCount, grid, newestOrderedFiles))
    # Set the size of the button
    addHundredButton.setFixedHeight(60)

    # Create a vertical box layout and add the list and button to it
    vBox = QVBoxLayout(window)

    # Create a custom title bar that be used to close the program
    draggableBar = QWidget(objectName="draggableBar")
    draggableBar.setFixedHeight(30)
    dragBarHbox = QHBoxLayout(objectName="titleBarLayout")
    draggableBar.setLayout(dragBarHbox)
    # Add some space to the left of the icon
    dragBarHbox.addSpacing(10)

    # Create application icon to go in the title bar
    appIcon = QLabel()
    appIcon.setPixmap(QPixmap(darkIcon).scaled(
        20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation))
    dragBarHbox.addWidget(appIcon)
    dragBarHbox.addStretch(1)
    programNameText = QLabel("MugBox", objectName="titleText")
    programNameText.setAlignment(Qt.AlignCenter)
    programNameText.setEnabled(False)
    dragBarHbox.addWidget(programNameText)
    dragBarHbox.addStretch(1)
    # Now we can make the title section draggable
    addDragAbility(draggableBar, window)

    # Separate the close and minimize buttons to avoid them also having the drag ability
    fullBar = QWidget(objectName="fullBar")
    fullBarHbox = QHBoxLayout()
    fullBar.setLayout(fullBarHbox)
    fullBarHbox.addWidget(draggableBar)
    # Remove spacing between buttons in this hbox
    fullBarHbox.setSpacing(0)
    # Remove any padding or margins
    fullBarHbox.setContentsMargins(0, 0, 0, 0)  # left, top, right, bottom

    # Create a minimize button
    minimizeButton = QPushButton("—", objectName="minimizeButton")
    minimizeButton.setProperty("class", "titleBarButton")
    minimizeButton.setFixedSize(30, 30)
    minimizeButton.clicked.connect(window.showMinimized)
    # Make the minimize action be animated
    minimizeButton.setProperty("animate", True)
    fullBarHbox.addWidget(minimizeButton)
    # Create a close button
    closeButton = QPushButton("✕", objectName="closeButton")
    closeButton.setProperty("class", "titleBarButton")
    closeButton.setFixedSize(30, 30)
    closeButton.clicked.connect(app.quit)
    fullBarHbox.addWidget(closeButton)
    # the button still gets clipped off the bottom of the title bar, fix it
    dragBarHbox.setContentsMargins(0, 0, 0, 0)
    # remove the padding between the minimize and close buttons
    dragBarHbox.setSpacing(0)

    # Create a hamburger menu button to open the drawer menu
    hamburgerMenuOpenButton = QPushButton(
        "☰", objectName="hamburgerMenuOpenButton")
    hamburgerMenuOpenButton.setProperty("class", "titleBarButton")
    hamburgerMenuOpenButton.setFixedSize(30, 30)
    # Create a back arrow menu button to close the drawer menu
    hamburgerMenuCloseButton = QPushButton(
        "◀", objectName="hamburgerMenuCloseButton")
    hamburgerMenuCloseButton.setProperty("class", "titleBarButton")
    hamburgerMenuCloseButton.setFixedSize(30, 30)

    # Create hbox holding hamburger menu on the left and the scrollarea and add hundred button on the right
    hbox = QHBoxLayout()
    hbox.addWidget(hamburgerMenuOpenButton)
    vMenu = QWidget(objectName="vMenu")
    vMenuBox = QVBoxLayout()
    vMenuBox.setContentsMargins(0, 0, 0, 0)
    vMenu.setLayout(vMenuBox)
    vMenuBox.addWidget(hamburgerMenuCloseButton)
    vMenu.setFixedWidth(int(windowY/4))
    populateMenu(vMenuBox)
    hbox.addWidget(vMenu)
    vMenu.hide()
    vScrollBox = QVBoxLayout()
    vScrollBox.addWidget(scrollArea)
    vScrollBox.addWidget(addHundredButton)
    vScrollBox.setSpacing(10)
    hbox.addLayout(vScrollBox)
    # Align the hamburger menu button to the top left
    hbox.setAlignment(hamburgerMenuOpenButton, Qt.AlignTop)
    # Remove spacing between buttons in this hbox
    hbox.setSpacing(0)

    # Make hamburger button show menu when clicked
    hamburgerMenuOpenButton.clicked.connect(
        lambda: (hamburgerMenuOpenButton.hide(),
                 vMenu.show(),
                 ))
    # Make hamburger button hide menu when clicked
    hamburgerMenuCloseButton.clicked.connect(
        lambda: (hamburgerMenuOpenButton.show(),
                 vMenu.hide(),))

    # Put all 3 in a container which can be colored
    container = QWidget(objectName="container")
    containerLayout = QVBoxLayout(objectName="containerLayout")
    container.setLayout(containerLayout)
    # containerLayout.addWidget(fullBar)
    containerLayout.addLayout(hbox)
    # Remove any padding or margins on the top of the container
    containerLayout.setContentsMargins(
        5, 0, 10, 10)  # left, top, right, bottom

    outerContainer = QWidget(objectName="outerContainer")
    outerContainerLayout = QVBoxLayout(objectName="outerContainerLayout")
    outerContainer.setLayout(outerContainerLayout)
    outerContainerLayout.addWidget(fullBar)
    outerContainerLayout.addWidget(container)
    outerContainerLayout.setContentsMargins(0, 0, 0, 0)
    outerContainerLayout.setSpacing(0)
    vBox.addWidget(outerContainer)

    # Make the window semi-transparent
    window.setAttribute(Qt.WA_TranslucentBackground, True)
    window.setWindowFlags(Qt.FramelessWindowHint)

    # Set application icon for the taskbar
    app.setWindowIcon(QIcon(lightIcon))
    app.setStyleSheet(open("res/styles/style.css").read())

    # Show the window and run the application
    window.show()
    # print(f"Size of Add Hundred Button: {addHundredButton.size()}")
    app.exec_()


if __name__ == '__main__':
    main()


# Features to add:
# DONE: Make custom look with semi-transparent background
# DONE: Make custom title bar
# DONE: Make title bar properly draggable, currently only the left half is draggable
# TODO: Add a context menu to the items in the grid, so that you can right click on an item and open it in app, in explorer, or delete it
# TODO: Add a search bar
# TODO: Add ability to filter by folder names
# TODO: Add some visual indication if items next to each other are from the same folder
# TODO: Add ability to sort by folder name
# TODO: Replace opening image with a built in image viewer
# DONE: Exclude directories from the list, otherwise they show up as blank images
# FIXME: Empty images are still being added to the list, look into this
# TODO: Make gifs auto-play
# TODO: Put play button over videos if applicable
# TODO: Add "copy" button to context menu to copy the image to the clipboard
# IDEA: move add 100 button to the left side of the window and add settings below it
# DONE: Make Sroll Area background transparent
# DONE: Make custom Scroll Bar
# FIXME: Distinguish app background from scroll area background more. Maybe make the scroll area background a little darker
# TODO: Add a reload button
# TODO: Add system for detecting which machine this is.
# If it is unknown machine then ask for root directory and save machine - directory pair into a map.
# TODO: Give previews for discord sizes on one of the pages
# FIXME: Fix image corners and image in general being pixelated
# TODO: Center the images in the grid
# TODO: Look into making background acrylic or blur
# TODO: Make program be resizable and have grid be responsive to window size
# TODO: Make left side drawer that can be opened and closed when clicking on the hamburger menu
# TODO: Make program work with Windows 11's snapping feature
# TODO: Make it so dragging an image from the built in image viewer will drop it to wherever the cursor is, such as discord
# TODO: Make a custom placeholder thumbnail for images of type .csp, .pdn, .psd, and krita files
# DONE: Create a custom application icon

# IDEA: Create better version of tiermaker site to add images in real time, click to zoom in, and link to each other
