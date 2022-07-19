import math
import os
import random

import PySimpleGUI as sg
import cv2
import cv2 as cv
import numpy as np
from PIL import Image, ImageTk
import io
import matplotlib.pyplot as plt


def mainWindow():
    mainLayout = [[sg.Text("NIST CNN Annotation Software", text_color="blue")],
                  [sg.T("")], [sg.Text("Choose a file: "), sg.Input(), sg.FileBrowse(key="-IN-")],
                  [sg.Button("Submit")]]

    mainWindowWindow = sg.Window('Choose an image', mainLayout, size=(800, 200))

    while True:
        event, values = mainWindowWindow.read()
        if event == sg.WIN_CLOSED or event == "Exit":
            break
        elif event == "Submit":
            mainWindowWindow.close()
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
    resizedPNGImage = im1.resize((imgWidth // 2, imgHeight // 2))
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

    parentDir = os.getcwd()
    nameOfNewDirectory = nameOfFileCut + "DIR"

    path = os.path.join(parentDir, nameOfNewDirectory)

    print(path)

    if not os.path.isdir(path):
        os.mkdir(path)

    pathOfNewDirLocal = path + "/"

    editedFilePath = pathOfNewDirLocal + nameOfFileCut + "Edited.png"

    resizedPNGImage.save(editedFilePath)

    # test = Image.open(editedFilePath)
    # print("New image size: " + str(test.size)) #should be 500 by 500

    return editedFilePath, imgHeight // 2, imgWidth // 2, pathOfNewDirLocal


def imagePreviewAndTileSize(pngFilePathParam, imgHeightParam, imgWidthParam):
    # imagePrev = cv.imread(filepath)
    # cv.imshow("Image Preview", imagePrev)

    imagePreviewLayout = [[sg.Text("Image Preview", text_color="blue")],
                          [sg.Text("Size of Image: " + str(imgHeightParam) + " x " + str(imgWidthParam))],
                          [sg.Image(pngFilePathParam)],
                          [sg.Text("X size of tile:"), sg.Input(key='-XTile-', do_not_clear=True, size=(5, 1)),
                           sg.Text("Y size of tile:"), sg.Input(key='-YTile-', do_not_clear=True, size=(5, 1))],
                          [sg.Text("Offset (can be negative):"),
                           sg.Input(key='-Offset-', do_not_clear=True, size=(5, 1))],
                          [sg.Button("Quit"), sg.Button("Process!")]]

    imagePreviewWindow = sg.Window("Image Preview", imagePreviewLayout, modal=True)

    while True:
        event, values = imagePreviewWindow.read()
        if event in (None, 'Quit'):
            break
        elif event == "Process!":

            imagePreviewWindow.close()

            xTile = values["-XTile-"]
            yTile = values["-YTile-"]
            offset = values["-Offset-"]

            print("-XTile-: " + xTile)
            print("-YTile-: " + yTile)
            print("-Offset-: " + offset)

            if offset >= xTile or offset >= yTile:
                print("This is invalid, prompt again")
                #

            return xTile, yTile, offset

    imagePreviewWindow.close()


def tilePreviewWindow(xTile, yTile, offset, pngImagePath, pathOfNewDir, midpointDict):
    # grid of tiling image using xTile and yTile
    cvImage = cv.imread(pngImagePath)

    imgHeightLocal = cvImage.shape[0]
    imgWidthLocal = cvImage.shape[1]

    offsetNew = int(offset)

    xTileNew, yTileNew = int(xTile), int(yTile)

    if offsetNew >= 0:

        numCols = imgWidthLocal // xTileNew
        numRows = imgHeightLocal // yTileNew

        for i in range(numRows):

            for j in range(numCols):
                # Base x and y coordinate based on formula
                rootX = (offsetNew * (j + 1)) + (xTileNew * j)
                rootY = (offsetNew * (i + 1)) + (yTileNew * i)

                # Parameters for cv.line()
                color = (0, 0, 0)
                thickness = 3

                # Coordinates for each tile
                bottomLeft = (rootX, rootY)
                bottomRight = (rootX + xTileNew, rootY)
                topLeft = (rootX, rootY + yTileNew)
                topRight = (rootX + xTileNew, rootY + yTileNew)

                if bottomLeft[0] > imgWidthLocal or bottomRight[0] > imgWidthLocal or topLeft[0] > imgWidthLocal or \
                        topRight[0] > imgWidthLocal:
                    break

                if bottomLeft[1] > imgHeightLocal or bottomRight[1] > imgHeightLocal or topLeft[1] > imgHeightLocal or \
                        topRight[1] > imgHeightLocal:
                    break

                # Graphing/drawing the tile
                cv.line(cvImage, bottomLeft, bottomRight, color, thickness)
                cv.line(cvImage, bottomRight, topRight, color, thickness)
                cv.line(cvImage, topRight, topLeft, color, thickness)
                cv.line(cvImage, topLeft, bottomLeft, color, thickness)

        # write tiled image to directory
        cv2.imwrite(pathOfNewDir + "TiledImageWhole.png", cvImage)

        showTiledImageWhole(pathOfNewDir + "TiledImageWhole.png")

        tileNum = 0

        for i in range(numRows):
            for j in range(numCols):
                # Base x and y coordinate based on formula
                rootX = (offsetNew * (j + 1)) + (xTileNew * j)
                rootY = (offsetNew * (i + 1)) + (yTileNew * i)

                if rootX > imgWidthLocal or (rootX + xTileNew) > imgWidthLocal:
                    break
                if rootY > imgHeightLocal or (rootY + yTileNew) > imgHeightLocal:
                    break

                tile = cvImage[rootY: rootY + yTileNew, rootX: rootX + xTileNew]

                tileNumString = str(tileNum)

                bottomLeft = (rootX, rootY)
                bottomRight = (rootX + xTileNew, rootY)
                topLeft = (rootX, rootY + yTileNew)

                midpointCoordinateX = (bottomLeft[0] + bottomRight[0]) // 2
                midpointCoordinateY = (bottomLeft[1] + topLeft[1]) // 2
                midpointCoordinates = "x" + str(midpointCoordinateX) + "x_y" + str(midpointCoordinateY) + "y"
                print(midpointCoordinates)

                tileNumFullString = "Tile" + tileNumString + "_MID(" + midpointCoordinates + ")" + ".png"

                # save tiled image to pathOfNewDir

                pathToTile = pathOfNewDir + tileNumFullString

                cv2.imwrite(pathToTile, tile)

                tileNum = tileNum + 1

                defineAngleWindow(pathToTile, pathToTile, xTileNew, yTileNew, tileNum, pathOfNewDir,
                                  midpointCoordinateX, midpointCoordinateY, 0)


    else:

        # coef = ((xTileNew + yTileNew) / 2) / offsetNew
        # numCols = int((imgWidthLocal // xTileNew) * coef * -1)
        # numRows = int((imgHeightLocal // yTileNew) * coef * -1)

        numCols = imgWidthLocal // xTileNew
        numRows = imgHeightLocal // yTileNew

        print(numCols)
        print(numRows)

        for i in range(numRows + 2):

            for j in range(numCols + 2):
                # Base x and y coordinate based on formula
                rootX = (offsetNew * (j + 1)) + (xTileNew * j)
                rootY = (offsetNew * (i + 1)) + (yTileNew * i)

                # Parameters for cv.line()
                color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                thickness = 3

                # Coordinates for each tile
                bottomLeft = (rootX, rootY)
                bottomRight = (rootX + xTileNew, rootY)
                topLeft = (rootX, rootY + yTileNew)
                topRight = (rootX + xTileNew, rootY + yTileNew)

                # Graphing/drawing the tile
                cv.line(cvImage, bottomLeft, bottomRight, color, thickness)
                cv.line(cvImage, bottomRight, topRight, color, thickness)
                cv.line(cvImage, topRight, topLeft, color, thickness)
                cv.line(cvImage, topLeft, bottomLeft, color, thickness)

        # cv.imshow("Tiled Image", cvImage)

        # write tiled image to directory

        cv2.imwrite(pathOfNewDir + "TiledImageWhole.png", cvImage)

        showTiledImageWhole(pathOfNewDir + "TiledImageWhole.png")

        # show tiled image in GUI

        tileNum = 0

        for i in range(numRows + 2):
            for j in range(numCols):
                # Base x and y coordinate based on formula
                rootX = (offsetNew * (j + 1)) + (xTileNew * j)
                rootY = (offsetNew * (i + 1)) + (yTileNew * i)

                tile = cvImage[rootY: rootY + yTileNew, rootX: rootX + xTileNew]

                tileNumString = str(tileNum)
                tileNumFullString = pathOfNewDir + "NegativeTile" + tileNumString + ".png"

                cv2.imwrite(tileNumFullString, tile)

                tileNum = tileNum + 1

                pathToTile = pathOfNewDir + tileNumFullString + ".png"

                defineAngleWindow(pathToTile, pathToTile, xTileNew, yTileNew, tileNum, 0)


def showTiledImageWhole(tiledImageWholePath):
    tiledImagePreviewLayout = [[sg.Text("Tiled Image", text_color="blue")],
                               [sg.Image(tiledImageWholePath)],
                               [sg.Button("Exit"), sg.Button("Process")]]

    tiledImagePreviewWindow = sg.Window("Tiled Image Final", tiledImagePreviewLayout, modal=True)

    while True:
        event, values = tiledImagePreviewWindow.read()
        if event in (None, 'Exit', 'Process'):
            tiledImagePreviewWindow.close()
            break
        else:
            break


def defineAngleWindow(tiledImagePathOriginal, tiledImagePath, xTile, yTile, tileNumber, newDIRPath,
                      midPointX, midPointY, prevAngleInput):
    annotatedTilesDIR = "AnnotatedTiles"

    finalPath = os.path.join(newDIRPath, annotatedTilesDIR)

    if not os.path.isdir(finalPath):
        os.mkdir(finalPath)

    imagePreviewLayout = [[sg.Text("Define Angle for Tile" + str(tileNumber), text_color="blue")],
                          [sg.Image(tiledImagePath)],
                          [sg.Text("Angle of the directionality:"),
                           sg.Input(key='-Angle-', do_not_clear=True, size=(5, 1)),
                           ],
                          [sg.Button("Quit"), sg.Button("Reset"), sg.Button("Show Angle"), sg.Button("Next")]]
    imagePreviewWindow = sg.Window("Image Preview", imagePreviewLayout, modal=True)

    while True:
        event, values = imagePreviewWindow.read()
        if event in (None, 'Quit'):
            break

        elif event == "Show Angle":

            imagePreviewWindow.close()

            # extracting the midpoint coordinates from tile name
            # stringx1 = "MID(x"
            # stringx2 = "x_"
            # indexX1 = tiledImagePath.index(stringx1)
            # indexX2 = tiledImagePath.index(stringx2)
            #
            # midPointXString = tiledImagePath[indexX1 + 5:indexX2]
            #
            # stringy1 = "x_y"
            # stringy2 = "y)"
            # indexY1 = tiledImagePath.index(stringy1)
            # indexY2 = tiledImagePath.index(stringy2)
            #
            # midPointYString = tiledImagePath[indexY1 + 3:indexY2]
            #
            # midPointX = int(midPointXString)
            # midPointY = int(midPointYString)

            midPointX = xTile // 2
            midPointY = yTile // 2

            print(midPointX, midPointY)

            # draw angle on copied tile using midpoint and angle
            angleString = values["-Angle-"]

            prevAngleInputChange = int(angleString)

            c = (xTile // 3)

            angleToRadians = prevAngleInputChange * (math.pi / 180)

            pointY = int(c * math.sin(angleToRadians))
            pointX = int(c * math.cos(angleToRadians))

            point1 = ((midPointX + pointX), (midPointY - pointY))
            point2 = ((midPointX - pointX), (midPointY + pointY))

            print(point1, point2)

            color = (0, 0, 0)
            thickness = 2

            Image = cv.imread(tiledImagePath)

            copiedImage = np.copy(Image)

            # copiedImageCV = cv.imread(copiedImage)

            cv.line(copiedImage, point1, point2, color, thickness)

            cutCopiedFullPath = tiledImagePath.replace(".png", "")

            copiedFullPath = cutCopiedFullPath + "COPY_ANG" + str(prevAngleInputChange) + ".png"

            cv.imwrite(copiedFullPath, copiedImage)

            # imagePreviewWindow.close()

            defineAngleWindow(tiledImagePathOriginal, copiedFullPath, xTile, yTile, tileNumber, newDIRPath,
                              midPointX, midPointY, prevAngleInputChange)

        elif event == "Reset":
            imagePreviewWindow.close()
            defineAngleWindow(tiledImagePathOriginal, tiledImagePathOriginal, xTile, yTile, tileNumber,
                              newDIRPath, midPointX, midPointY, prevAngleInput)

        elif event == "Next":

            # extracting the midpoint coordinates from tile name
            stringx1 = "MID(x"
            stringx2 = "x_"
            indexX1 = tiledImagePath.index(stringx1)
            indexX2 = tiledImagePath.index(stringx2)

            midPointXString = tiledImagePath[indexX1 + 5:indexX2]

            stringy1 = "x_y"
            stringy2 = "y)"
            indexY1 = tiledImagePath.index(stringy1)
            indexY2 = tiledImagePath.index(stringy2)

            midPointYString = tiledImagePath[indexY1 + 3:indexY2]

            midPointXReal = int(midPointXString)
            midPointYReal = int(midPointYString)

            imagePreviewWindow.close()

            # angle = values["-Angle-"]

            FINALImg = cv.imread(tiledImagePath)

            copiedFullPathFINAL = newDIRPath + "AnnotatedTiles/" + str(tileNumber) + "TileFINAL(" + str(midPointXReal) + \
                                  ", " + str(midPointYReal) + "ANG" + str(prevAngleInput) + ").png"

            # print("Angle" + str(angleGlobal))

            midpointDict["Tile" + str(tileNumber - 1)] = (midPointXReal, midPointYReal, prevAngleInput)
            # print(str(midpointDict["Tile" + str(tileNumber)]))

            cv.imwrite(copiedFullPathFINAL, FINALImg)

            return None

    imagePreviewWindow.close()


# Put all the annotated tiles back together and save, most likely another function

def tileBackImage(xTile, tiledImage, pathOfNewDirParam, midpointDict):
    tiledImageCV = cv.imread(tiledImage)

    for tileElem in midpointDict:
        angleToRadians = midpointDict[tileElem][2] * (math.pi / 180)

        c = int(xTile) // 3

        pointY = int(c * math.sin(angleToRadians))
        pointX = int(c * math.cos(angleToRadians))

        point1 = ((midpointDict[tileElem][0] + pointX), (midpointDict[tileElem][1] - pointY))
        point2 = ((midpointDict[tileElem][0] - pointX), (midpointDict[tileElem][1] + pointY))
        color = 0, 0, 0
        thickness = 2

        cv.line(tiledImageCV, point1, point2, color, thickness)

    pathOfFinalImage = pathOfNewDirParam + "Final_Annotated_Tiled_Image.png"
    cv.imwrite(pathOfFinalImage, tiledImageCV)


def showFinalAnnotatedImage(tiledImagePath):
    annotatedImagePreviewLayout = [[sg.Text("Final Annotated Image", text_color="blue")],
                                   [sg.Image(tiledImagePath)],
                                   [sg.Button("Exit"), sg.Button("Upload to Database")]]

    annotatedImagePreviewWindow = sg.Window("Final Annotated Image", annotatedImagePreviewLayout, modal=True)

    while True:
        event, values = annotatedImagePreviewWindow.read()
        if event in (None, 'Exit'):
            break
        elif event == "Upload to Database!":
            print("Uploading to database...")


if __name__ == "__main__":
    midpointDict = dict()

    rawChosenImage = mainWindow()

    pngFilePath, imgHeight, imgWidth, pathOfNewDir = convertImageToPNG(rawChosenImage)

    tileSize = imagePreviewAndTileSize(pngFilePath, imgHeight, imgWidth)

    tilePreviewWindow(tileSize[0], tileSize[1], tileSize[2], pngFilePath, pathOfNewDir, midpointDict)

    tileBackImage(tileSize[0], pathOfNewDir + "TiledImageWhole.png", pathOfNewDir, midpointDict)

    showFinalAnnotatedImage(pathOfNewDir + "Final_Annotated_Tiled_Image.png")
