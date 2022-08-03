import csv
import math
import os
import random

import PySimpleGUI as sg
import cv2 as cv
import numpy as np
from PIL import Image


# This function is to open up the file picker for the user to choose an image to annotate
# Return value: the chosen image
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


# This function is to create the csv file with the header inputted. It will be used in the future to fill in the rows
# with information about each annotated tile
def createCSV(pathOfNewDirParam):
    header = ["Tile file name", "Midpoint", "Angle", "X Size of Tile", "Y Size of Tile", "OffsetX", "OffsetY", "Offset"]

    with open(pathOfNewDirParam + "/Direction_Annotation.csv", "w") as csvFile:
        writer = csv.writer(csvFile)
        writer.writerow(header)


# Due to PySimpleGUI's convention of only using png's this function converts the desired image to a PNG to be used
# throughout the rest of the program
# Return values: path of newly converted image, height, width, path of new directory
def convertImageToPNG(filepath):
    im1 = Image.open(filepath)
    openCvProcessedImage = cv.imread(filepath)
    imgHeightLocal = openCvProcessedImage.shape[0]
    imgWidthLocal = openCvProcessedImage.shape[1]

    resizedPNGImage = im1.resize((imgWidthLocal // 2, imgHeightLocal // 2))
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

    parentDir = os.getcwd()  # Finding path of parent dictionary
    nameOfNewDirectory = nameOfFileCut + "DIR"

    path = os.path.join(parentDir, nameOfNewDirectory)  # Creating new directory

    if not os.path.isdir(path):
        os.mkdir(path)

    pathOfNewDirLocal = path + "/"

    editedFilePath = pathOfNewDirLocal + nameOfFileCut + "Edited.png"

    resizedPNGImage.save(editedFilePath)  # Saving new png image to new directory

    return editedFilePath, imgHeightLocal // 2, imgWidthLocal // 2, pathOfNewDirLocal


# This function uses the image that the user selected and promtps the user to enter the tile parameters
# Return values: width of tile, height of tile, space in between tiles, widht and height of space from the edge of
# the image
def imagePreviewAndTileSize(pngFilePathParam, imgHeightParam, imgWidthParam):
    imagePreviewLayout = [[sg.Text("Image Preview", text_color="blue")],  # Layout of window
                          [sg.Text("Size of Image: " + str(imgHeightParam) + " x " + str(imgWidthParam))],
                          [sg.Image(pngFilePathParam)],
                          [sg.Text("X size of tile:"), sg.Input(key='-XTile-', do_not_clear=True, size=(5, 1)),
                           sg.Text("Y size of tile:"), sg.Input(key='-YTile-', do_not_clear=True, size=(5, 1))],
                          [sg.Text("Shift:"),
                           sg.Input(key='-Shift-', do_not_clear=True, size=(5, 1))],
                          [sg.Text("OffsetX:"),
                           sg.Input(key='-OffsetX-', do_not_clear=True, size=(5, 1))],

                          [sg.Text("OffsetY:"),
                           sg.Input(key='-OffsetY-', do_not_clear=True, size=(5, 1))],

                          [sg.Button("Quit"), sg.Button("Process!")]]

    imagePreviewWindow = sg.Window("Image Preview", imagePreviewLayout, modal=True)

    while True:
        event, values = imagePreviewWindow.read()
        if event in (None, 'Quit'):
            break
        elif event == "Process!":

            imagePreviewWindow.close()

            xTile = int(values["-XTile-"])  # Extracting each value inputted to then be used for calculations
            yTile = int(values["-YTile-"])
            shift = int(values["-Shift-"])
            offsetX = int(values["-OffsetX-"])
            offsetY = int(values["-OffsetY-"])

            if shift >= xTile or shift >= yTile or xTile < 0 or yTile < 0 or offsetX < 0 or offsetY < 0 or shift < 0:
                # Checks to see that none of the values inputted are less than 0
                sg.Popup('Cannot have any value(s) less than 0!', keep_on_top=True)
                imagePreviewAndTileSize(pngFilePath, imgHeight, imgWidth)

            return xTile, yTile, shift, offsetX, offsetY

    imagePreviewWindow.close()


# This window is run after the user inputs the tile parameters. It's main goal is to show the user the tiled image
# based on the parameters inputted
def tilePreviewWindowBackend(xTile, yTile, shift, offsetX, offsetY, pngImagePath, pathOfNewDirParam, midpointDict):
    cvImage = cv.imread(pngImagePath)

    imgHeightLocal = cvImage.shape[0]  # Extracting height and width
    imgWidthLocal = cvImage.shape[1]

    shiftNew = int(shift)

    xTileNew, yTileNew = int(xTile), int(yTile)  # Casting

    if shiftNew >= 0:

        numCols = imgWidthLocal // xTileNew  # Calculating how many rows and columns will be in the image
        numRows = imgHeightLocal // yTileNew

        for i in range(numRows):

            for j in range(numCols):
                # Base x and y coordinate based on formula
                rootX = (shiftNew * (j + 1)) + (xTileNew * j) - shiftNew + (offsetX // 2)
                rootY = (shiftNew * (i + 1)) + (yTileNew * i) - shiftNew + (offsetY // 2)

                if j == 0:
                    rootX = offsetX // 2

                    if i == 0:
                        rootY = (offsetY // 2)

                # Parameters for cv.line()
                color = (0, 0, 0)
                thickness = 3

                # Coordinates for each tile
                bottomLeft = (rootX, rootY)
                bottomRight = (rootX + xTileNew, rootY)
                topLeft = (rootX, rootY + yTileNew)
                topRight = (rootX + xTileNew, rootY + yTileNew)

                # Checks to make sure the coordinates do not exceed the image
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
        cv.imwrite(pathOfNewDirParam + "TiledImageWhole.png", cvImage)

        showTiledImageWhole(pathOfNewDirParam + "TiledImageWhole.png")

        tileNum = 0

        for i in range(numRows):
            for j in range(numCols):

                # Base x and y coordinate based on formula
                rootX = (shiftNew * (j + 1)) + (xTileNew * j) - shiftNew + (offsetX // 2)
                rootY = (shiftNew * (i + 1)) + (yTileNew * i) - shiftNew + (offsetY // 2)

                if j == 0:
                    rootX = offsetX // 2

                    if i == 0:
                        rootY = (offsetY // 2)

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

                tileNumFullString = "Tile" + tileNumString + "_MID(" + midpointCoordinates + ")" + ".png"

                # save tiled image to pathOfNewDir
                pathToTile = pathOfNewDir + tileNumFullString

                cv.imwrite(pathToTile, tile)

                tileNum = tileNum + 1

                defineAngleWindow(pathToTile, pathToTile, xTileNew, yTileNew, tileNum, pathOfNewDir,
                                  midpointCoordinateX, midpointCoordinateY, offsetX, offsetY, shift, 0)

    else:
        print("Error")
        return None


# This function displays the tiled image created from tilePreviewWindowBackend()
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


# This is the main function of the annotation software, where the user is able to manually annotate the tiles
def defineAngleWindow(tiledImagePathOriginal, tiledImagePath, xTile, yTile, tileNumber, newDIRPath,
                      midPointX, midPointY, offsetX, offsetY, shift, prevAngleInput):
    annotatedTilesDIR = "AnnotatedTiles"

    finalPath = os.path.join(newDIRPath,
                             annotatedTilesDIR)  # Creating a new directory containing the finally annotated images

    if not os.path.isdir(finalPath):
        os.mkdir(finalPath)

    imagePreviewLayout = [[sg.Text("Define Angle for Tile" + str(tileNumber), text_color="blue")],
                          # Window layout for the annotating process
                          [sg.Image(tiledImagePath)],
                          [sg.Text("Angle of the directionality:"),
                           sg.Input(key='-Angle-', do_not_clear=True, size=(5, 1)), sg.Button("Show Angle")
                           ],
                          [sg.Button("-10°"), sg.Button("-1°"), sg.Text(str(prevAngleInput) + "°"), sg.Button("+1°"),
                           sg.Button("+10°")],
                          [sg.Button("Quit"), sg.Button("Reset"), sg.Button("Next")]]
    imagePreviewWindow = sg.Window("Image Preview", imagePreviewLayout, modal=True)

    while True:
        event, values = imagePreviewWindow.read()
        if event in (None, 'Quit'):
            break

        # The -10, -1, +1, +10 annotations apply the exact same logic
        elif event == "-10°":  # "Quick annotate" of -10 degrees
            imagePreviewWindow.close()

            midPointX = xTile // 2  # Getting the midpoint of the tile
            midPointY = yTile // 2

            prevAngleInputChange = int(
                prevAngleInput) - 10  # Subtracting 10 degrees from previously inputted angle (default is 0 degrees)

            c = (xTile // 3)  # Length of the line

            angleToRadians = prevAngleInputChange * (math.pi / 180)  # Converting angles to radians

            pointY = int(c * math.sin(angleToRadians))  # Calculating the a and b sides of triangle
            pointX = int(c * math.cos(angleToRadians))

            point1 = (
                (midPointX + pointX), (midPointY - pointY))  # Adding and subtracting to midpoint to get desired points
            point2 = ((midPointX - pointX), (midPointY + pointY))

            # Parameters for drawing the angle
            color = (0, 0, 0)
            thickness = 2

            ImageCV = cv.imread(tiledImagePathOriginal)  # Reading the image to copy

            copiedImage = np.copy(ImageCV)

            cv.line(copiedImage, point1, point2, color, thickness)  # Draw line on tile

            cutCopiedFullPath = tiledImagePath.replace(".png", "")

            copiedFullPath = cutCopiedFullPath + "COPY_ANG" + str(prevAngleInputChange) + ".png"

            cv.imwrite(copiedFullPath, copiedImage)  # Save annotated image

            defineAngleWindow(tiledImagePathOriginal, copiedFullPath, xTile, yTile, tileNumber, newDIRPath,
                              midPointX, midPointY, offsetX, offsetY, shift, prevAngleInputChange)  # Show changes

        elif event == "-1°":
            imagePreviewWindow.close()

            midPointX = xTile // 2
            midPointY = yTile // 2

            prevAngleInputChange = int(prevAngleInput) - 1

            c = (xTile // 3)

            angleToRadians = prevAngleInputChange * (math.pi / 180)

            pointY = int(c * math.sin(angleToRadians))
            pointX = int(c * math.cos(angleToRadians))

            point1 = ((midPointX + pointX), (midPointY - pointY))
            point2 = ((midPointX - pointX), (midPointY + pointY))

            color = (0, 0, 0)
            thickness = 2

            ImageCV = cv.imread(tiledImagePathOriginal)

            copiedImage = np.copy(ImageCV)

            cv.line(copiedImage, point1, point2, color, thickness)

            cutCopiedFullPath = tiledImagePath.replace(".png", "")

            copiedFullPath = cutCopiedFullPath + "COPY_ANG" + str(prevAngleInputChange) + ".png"

            cv.imwrite(copiedFullPath, copiedImage)

            defineAngleWindow(tiledImagePathOriginal, copiedFullPath, xTile, yTile, tileNumber, newDIRPath,
                              midPointX, midPointY, offsetX, offsetY, shift, prevAngleInputChange)

        elif event == "+1°":
            imagePreviewWindow.close()

            midPointX = xTile // 2
            midPointY = yTile // 2

            prevAngleInputChange = int(prevAngleInput) + 1

            c = (xTile // 3)

            angleToRadians = prevAngleInputChange * (math.pi / 180)

            pointY = int(c * math.sin(angleToRadians))
            pointX = int(c * math.cos(angleToRadians))

            point1 = ((midPointX + pointX), (midPointY - pointY))
            point2 = ((midPointX - pointX), (midPointY + pointY))

            color = (0, 0, 0)
            thickness = 2

            ImageCV = cv.imread(tiledImagePathOriginal)

            copiedImage = np.copy(ImageCV)

            cv.line(copiedImage, point1, point2, color, thickness)

            cutCopiedFullPath = tiledImagePath.replace(".png", "")

            copiedFullPath = cutCopiedFullPath + "COPY_ANG" + str(prevAngleInputChange) + ".png"

            cv.imwrite(copiedFullPath, copiedImage)

            defineAngleWindow(tiledImagePathOriginal, copiedFullPath, xTile, yTile, tileNumber, newDIRPath,
                              midPointX, midPointY, offsetX, offsetY, shift, prevAngleInputChange)

        elif event == "+10°":
            imagePreviewWindow.close()

            midPointX = xTile // 2
            midPointY = yTile // 2

            prevAngleInputChange = int(prevAngleInput) + 10

            c = (xTile // 3)

            angleToRadians = prevAngleInputChange * (math.pi / 180)

            pointY = int(c * math.sin(angleToRadians))
            pointX = int(c * math.cos(angleToRadians))

            point1 = ((midPointX + pointX), (midPointY - pointY))
            point2 = ((midPointX - pointX), (midPointY + pointY))

            color = (0, 0, 0)
            thickness = 2

            ImageCV = cv.imread(tiledImagePathOriginal)

            copiedImage = np.copy(ImageCV)

            cv.line(copiedImage, point1, point2, color, thickness)

            cutCopiedFullPath = tiledImagePath.replace(".png", "")

            copiedFullPath = cutCopiedFullPath + "COPY_ANG" + str(prevAngleInputChange) + ".png"

            cv.imwrite(copiedFullPath, copiedImage)

            defineAngleWindow(tiledImagePathOriginal, copiedFullPath, xTile, yTile, tileNumber, newDIRPath,
                              midPointX, midPointY, offsetX, offsetY, shift, prevAngleInputChange)

        elif event == "Show Angle":

            imagePreviewWindow.close()

            midPointX = xTile // 2
            midPointY = yTile // 2

            angleString = values["-Angle-"]

            prevAngleInputChange = int(angleString)

            c = (xTile // 3)

            angleToRadians = prevAngleInputChange * (math.pi / 180)

            pointY = int(c * math.sin(angleToRadians))
            pointX = int(c * math.cos(angleToRadians))

            point1 = ((midPointX + pointX), (midPointY - pointY))
            point2 = ((midPointX - pointX), (midPointY + pointY))

            color = (0, 0, 0)
            thickness = 2

            ImageCV = cv.imread(tiledImagePathOriginal)

            copiedImage = np.copy(ImageCV)

            cv.line(copiedImage, point1, point2, color, thickness)

            cutCopiedFullPath = tiledImagePath.replace(".png", "")

            copiedFullPath = cutCopiedFullPath + "COPY_ANG" + str(prevAngleInputChange) + ".png"

            cv.imwrite(copiedFullPath, copiedImage)

            defineAngleWindow(tiledImagePathOriginal, copiedFullPath, xTile, yTile, tileNumber, newDIRPath,
                              midPointX, midPointY, offsetX, offsetY, shift, prevAngleInputChange)

        elif event == "Reset":  # this shows the original tiled image with no annotation
            imagePreviewWindow.close()
            defineAngleWindow(tiledImagePathOriginal, tiledImagePathOriginal, xTile, yTile, tileNumber,
                              newDIRPath, midPointX, midPointY, offsetX, offsetY, shift, prevAngleInput)

        elif event == "Next":  # this goes on to the next tile to be annotated

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

            FINALImg = cv.imread(tiledImagePath)

            copiedFullPathFINAL = newDIRPath + "AnnotatedTiles/" + str(tileNumber) + "TileFINAL(" + str(midPointXReal) + \
                                  ", " + str(midPointYReal) + "ANG" + str(prevAngleInput) + ").png"

            midpointDict["Tile" + str(tileNumber - 1)] = (midPointXReal, midPointYReal, prevAngleInput)

            cv.imwrite(copiedFullPathFINAL, FINALImg)

            # Writing to the CSV file for user
            newTileRow = ["Tile" + str(tileNumber - 1), (midPointX, midPointY), prevAngleInput, xTile, yTile, offsetX,
                          offsetY, shift]

            with open(newDIRPath + "/Direction_Annotation.csv", 'a', newline='') as csvFile:
                CSVwriter = csv.writer(csvFile)
                CSVwriter.writerow(newTileRow)

            return None

    imagePreviewWindow.close()


# Putting all the tiles together to show final annotated image
def tileBackImage(xTile, tiledImage, pathOfNewDirParam, midpointDict):
    tiledImageCV = cv.imread(tiledImage)

    for tileElem in midpointDict:
        angleToRadians = midpointDict[tileElem][2] * (math.pi / 180)

        c = int(xTile) // 3  # Declaring size of angle

        pointY = int(c * math.sin(angleToRadians))
        pointX = int(c * math.cos(angleToRadians))

        # Using the midpoint dictionary and calculations to create line
        point1 = ((midpointDict[tileElem][0] + pointX), (midpointDict[tileElem][1] - pointY))
        point2 = ((midpointDict[tileElem][0] - pointX), (midpointDict[tileElem][1] + pointY))

        # Parameters for drawing the line
        color = 0, 0, 0
        thickness = 2

        cv.line(tiledImageCV, point1, point2, color, thickness)

    pathOfFinalImage = pathOfNewDirParam + "Final_Annotated_Tiled_Image.png"
    cv.imwrite(pathOfFinalImage, tiledImageCV)


# This function is just showing the final annotated image to the user
def showFinalAnnotatedImage(tiledImagePath):
    annotatedImagePreviewLayout = [[sg.Text("Final Annotated Image", text_color="blue")],  # Window layout
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

    createCSV(pathOfNewDir)

    tileSize = imagePreviewAndTileSize(pngFilePath, imgHeight, imgWidth)

    tilePreviewWindowBackend(tileSize[0], tileSize[1], tileSize[2], tileSize[3], tileSize[4], pngFilePath, pathOfNewDir,
                             midpointDict)

    tileBackImage(tileSize[0], pathOfNewDir + "TiledImageWhole.png", pathOfNewDir, midpointDict)

    showFinalAnnotatedImage(pathOfNewDir + "Final_Annotated_Tiled_Image.png")
