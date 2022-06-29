import PySimpleGUI as sg
import cv2 as cv
import numpy as np
from PIL import Image
import io
import matplotlib.pyplot as plt


def mainWindow():
    mainLayout = [[sg.Text("NIST CNN Annotation Software", text_color="blue")],
                  [sg.T("")], [sg.Text("Choose a file: "), sg.Input(), sg.FileBrowse(key="-IN-")],
                  [sg.Button("Submit")]]

    window = sg.Window('Choose an image', mainLayout, size=(800, 200))

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == "Exit":
            break
        elif event == "Submit":
            chosenImage = values["-IN-"]
            return chosenImage


file_types = [("JPEG (*.jpg)", "*.jpg"),
              ("All files (*.*)", "*.*")]


def convertImageToPNG(filepath):
    im1 = Image.open(filepath)
    openCvProcessedImage = cv.imread(filepath)
    imgHeight = openCvProcessedImage.shape[0]
    imgWidth = openCvProcessedImage.shape[1]
    print(imgHeight)
    print(imgWidth)
    resizedPNGImage = im1.resize((imgHeight, imgWidth))
    slashedList = filepath.split('/')
    nameOfFile = slashedList[-1]
    if nameOfFile.__contains__(".jpeg"):
        nameOfFileCut = nameOfFile.replace(".jpeg", "")
    elif nameOfFile.__contains__(".jpg"):
        nameOfFileCut = nameOfFile.replace(".jpg", "")
    elif nameOfFile.__contains__(".svg"):
        nameOfFileCut = nameOfFile.replace(".svg", "")
    else:
        nameOfFileCut = nameOfFile.replace(".png", "")

    editedFilePath = "/Users/yuvansundrani/Documents/Python Side Projects/NIST_CNN_Software/" + nameOfFileCut + "Edited.png"

    resizedPNGImage.save(editedFilePath)

    # test = Image.open(editedFilePath)
    # print("New image size: " + str(test.size)) #should be 500 by 500

    return editedFilePath, imgHeight, imgWidth


def imagePreviewAndTileSize(pngFilePathParam, imgHeightParam, imgWidthParam):
    # imagePrev = cv.imread(filepath)
    # cv.imshow("Image Preview", imagePrev)

    imagePreviewLayout = [[sg.Text("Image Preview", text_color="blue")],
                          [sg.Text("Size of Image: " + str(imgHeightParam) + " x " + str(imgWidthParam))],
                          [sg.Image(pngFilePathParam, size=(imgHeightParam, imgWidthParam))],
                          [sg.Text("X size of tile:"), sg.Input(key='-XTile-', do_not_clear=True, size=(5, 1)),
                           sg.Text("Y size of tile:"), sg.Input(key='-YTile-', do_not_clear=True, size=(5, 1))],
                          [sg.Button("Quit"), sg.Button("Process!")]]
    imagePreviewWindow = sg.Window("Image Preview", imagePreviewLayout,
                                   size=(imgHeightParam + 300, imgWidthParam + 300),
                                   modal=True)
    while True:
        event, values = imagePreviewWindow.read()
        if event in (None, 'Quit'):
            break
        elif event == "Process!":
            # image = Image.open(filepath)
            # image.thumbnail((400, 400))
            # bio = io.BytesIO()
            # image.save(bio, format="PNG")
            # imagePreviewWindow["-IMAGE-"].update(data=bio.getvalue())

            xTile = values["-XTile-"]
            yTile = values["-YTile-"]

            print("-XTile-: " + xTile)
            print("-YTile-: " + yTile)

            return xTile, yTile

    imagePreviewWindow.close()


def tilePreviewWindow(xTile, yTile, pngImagePath):
    # grid of tiling image using xTile and yTile
    tiledImg = plt.imread(pngImagePath)

    # Grid lines at these intervals (in pixels)
    # dx and dy can be different
    dx, dy = int(xTile), int(yTile)

    # Custom (rgb) grid color
    grid_color = 0

    # Modify the image to include the grid
    tiledImg[:, ::dy, :] = grid_color
    tiledImg[::dx, :, :] = grid_color
    plt.imshow(tiledImg, 'gray', vmin=-1, vmax=1)

    plt.show()

    # imagePreviewLayout = [sg.Text("Tiling Preview", text_color="blue")], \
    #                      [[sg.Image(tiledImg, size=(300, 300))],
    #                       [sg.Button("Quit"), sg.Button("Annotate")]]
    #
    # window = sg.Window("Tiling preview", imagePreviewLayout, size=(700, 700))
    #
    # while True:
    #     event, values = window.read()
    #     if event == sg.WIN_CLOSED or event == "Quit":
    #         break
    #     elif event == "Annotate":
    #         tileProcessingWindow(xTile, yTile, pngImagePath)


def tileProcessingWindow(xTile, yTile, rawFilePath):
    # numRows = 500 % yTile
    # numColumns = 500 % xTile
    xTile = int(xTile)
    yTile = int(yTile)

    tilingImg = cv.imread(rawFilePath)

    imgHeightLocal = tilingImg.shape[0]
    imgWidthLocal = tilingImg.shape[1]

    numCols = imgWidthLocal // xTile
    numRows = imgHeightLocal // yTile
    # print("cols " + str(numCols))
    # print("rows " + str(numRows))

    cv.imshow("image", tilingImg)

    for i in range(numRows):
        rowCoord1 = i * yTile
        rowCoord2 = (i + 1) * yTile

        for j in range(numCols):
            print((i, j))
            colCoord1 = j * xTile
            colCoord2 = (j + 1) * xTile
            tile = tilingImg[rowCoord1: rowCoord2, colCoord1: colCoord2]
            annotateTile(tile)
            # I would call annotateTile function here
            #cv.imshow("Tile", tile)
            #cv.waitKey(0)
            #cv.destroyAllWindows()
    # Put all the annotated tiles back together and save, most likely another function


def annotateTile(tile):

    #tile2 = cv.imread(tile)

    # image = np.ones(shape=(512,512,3), dtype=np.int16)
    pt1 = (100, 100)
    pt2 = (400, 350)
    color = (0, 250, 0)
    #
    thickness = 10
    #
    cv.line(tile, pt1, pt2, color, thickness)
    cv.imshow("img w line", tile)
    cv.waitKey(0)
    cv.destroyAllWindows()


if __name__ == "__main__":
    rawChosenImage = mainWindow()
    pngFilePath, imgHeight, imgWidth = convertImageToPNG(rawChosenImage)
    tileSize = imagePreviewAndTileSize(pngFilePath, imgHeight, imgWidth)
    tilePreviewWindow(tileSize[0], tileSize[1], pngFilePath)
    tileProcessingWindow(tileSize[0], tileSize[1], rawChosenImage)
