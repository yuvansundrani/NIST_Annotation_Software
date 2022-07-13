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


def tilePreviewWindow(xTile, yTile, offset, pngImagePath, pathOfNewDir):
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

        cv.imshow("Tiled Image", cvImage)

        # write tiled image to directory
        cv2.imwrite(pathOfNewDir + "TiledImageWhole.png", cvImage)

        cv.waitKey(0)

        tileNum = 0

        for i in range(numRows):
            for j in range(numCols):
                # Base x and y coordinate based on formula
                rootX = (offsetNew * (j + 1)) + (xTileNew * j)
                rootY = (offsetNew * (i + 1)) + (yTileNew * i)
                print("row: " + str(i))
                print("col: " + str(j))

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

                tileNumFullString = pathOfNewDir + "Tile" + tileNumString + "_MID(" + midpointCoordinates + ")" + ".png"
                print(tileNumFullString)

                # save tiled image to pathOfNewDir
                cv2.imwrite(tileNumFullString, tile)

                tileNum = tileNum + 1

                pathToTile = pathOfNewDir + tileNumFullString + ".png"

                # defineAngleWindow(pathToTile, xTileNew, yTileNew, tileNum)

                # showing just for testing
                # cv2.imshow(tileNumFullString, tile)
                # cv.waitKey(0)
                # cv.destroyAllWindows()
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

        cv.imshow("Tiled Image", cvImage)

        # write tiled image to directory
        cv2.imwrite(pathOfNewDir + "TiledImageWhole.png", cvImage)

        cv.waitKey(0)

        tileNum = 0

        for i in range(numRows + 2):
            for j in range(numCols):
                # Base x and y coordinate based on formula
                rootX = (offsetNew * (j + 1)) + (xTileNew * j)
                rootY = (offsetNew * (i + 1)) + (yTileNew * i)
                print("row: " + str(i))
                print("col: " + str(j))

                tile = cvImage[rootY: rootY + yTileNew, rootX: rootX + xTileNew]

                tileNumString = str(tileNum)
                tileNumFullString = pathOfNewDir + "NegativeTile" + tileNumString + ".png"
                print(tileNumFullString)

                # save tiled image to pathOfNewDir

                cv2.imwrite(tileNumFullString, tile)

                tileNum = tileNum + 1

                pathToTile = pathOfNewDir + tileNumFullString + ".png"

                defineAngleWindow(pathToTile, pathToTile, xTileNew, yTileNew, tileNum)

                # showing just for testing
                # cv2.imshow(tileNumFullString, tile)
                # cv.waitKey(0)
                # cv.destroyAllWindows()


# def tileProcessingWindow(xTile, yTile, offset, rawFilePath):
#     xTileNew, yTileNew = int(xTile), int(yTile)
#     offsetNew = int(offset)
#
#     tilingImg = cv.imread(rawFilePath)
#
#     imgHeightLocal = tilingImg.shape[0]
#     imgWidthLocal = tilingImg.shape[1]
#
#     if offset >= 0:
#
#         numCols = imgWidthLocal // xTileNew
#         numRows = imgHeightLocal // yTileNew
#
#         for i in range(numRows):
#             rowCoord1 = (i * yTileNew) + (offsetNew * (i + 1))
#             rowCoord2 = ((i + 1) * yTileNew) + (offsetNew * (i + 1))
#
#             if rowCoord1 >= int(imgHeightLocal):
#                 break
#
#             elif rowCoord2 >= int(imgHeightLocal):
#                 rowCoord2 = imgHeightLocal - 1
#
#             for j in range(numCols):
#                 print((i, j))
#                 colCoord1 = (j * xTileNew) + (offsetNew * (j + 1))
#                 colCoord2 = ((j + 1) * xTileNew) + (offsetNew * (j + 1))
#
#                 if colCoord1 >= int(imgWidthLocal):
#                     break
#
#                 elif colCoord2 >= int(imgWidthLocal):
#                     rowCoord2 = imgWidth - 1
#
#                 tile = tilingImg[rowCoord1: rowCoord2, colCoord1: colCoord2]
#                 cv.imshow("Tile", tile)
#                 cv.waitKey(0)
#                 cv.destroyAllWindows()
#
#     else:
#         coef = ((xTileNew + yTile) / 2) / offsetNew
#         numCols = (imgWidthLocal // xTileNew) * coef
#         numRows = (imgHeightLocal // yTileNew) * coef
#
#         print(numCols)
#         print(numRows)
#
#         for i in range(numRows + 3):
#             rowCoord1 = (i * yTileNew) + (offsetNew * (i + 1))
#             rowCoord2 = ((i + 1) * yTileNew) + (offsetNew * (i + 1))
#
#             if rowCoord1 >= int(imgHeightLocal):
#                 break
#
#             elif rowCoord2 >= int(imgHeightLocal):
#                 rowCoord2 = imgHeightLocal - 1
#
#             for j in range(numCols + 3):
#                 print((i, j))
#                 colCoord1 = (j * xTileNew) + (offsetNew * (j + 1))
#                 colCoord2 = ((j + 1) * xTileNew) + (offsetNew * (j + 1))
#
#                 if colCoord1 >= int(imgWidthLocal):
#                     break
#
#                 elif colCoord2 >= int(imgWidthLocal):
#                     rowCoord2 = imgWidth - 1
#
#                 tile = tilingImg[rowCoord1: rowCoord2, colCoord1: colCoord2]
#                 cv.imshow("Tile", tile)
#                 cv.waitKey(0)
#                 cv.destroyAllWindows()


def defineAngleWindow(tiledImagePathOriginal, tiledImagePath, tileWidth, tileHeight, tileNumber):
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

            midPointX = int(midPointXString)
            midPointY = int(midPointYString)

            print(midPointX, midPointY)

            # draw angle on copied tile using midpoint and angle
            angleString = values["-Angle-"]

            angle = int(angleString)

            c = (tileWidth // 10)

            pointY = int(c * math.sin(angle))
            pointX = int(c * math.cos(angle))

            point1 = ((midPointX + pointX), (midPointY + pointY))
            point2 = ((midPointX - pointX), (midPointY - pointY))

            color = (0, 0, 0)
            thickness = 3

            OGImage = cv.imread(tiledImagePath)

            copiedImage = np.copy(OGImage)

            # copiedImageCV = cv.imread(copiedImage)

            cv.line(copiedImage, point1, point2, color, thickness)

            cutCopiedFullPath = tiledImagePath.replace(".png", "")

            copiedFullPath = cutCopiedFullPath + "COPY_ANG" + str(angle) + ".png"

            cv.imwrite(copiedFullPath, copiedImage)

            defineAngleWindow(tiledImagePathOriginal, copiedFullPath, tileWidth, tileHeight, tileNumber)








            # override the tileName with the same name plus angle
            # show the new annotated tile

        elif event == "Reset":
            print("reset")
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
            # tiledImagePathOriginal = "Tile" + str(tileNumber) + "_MID(x" + midPointXString + "x_y" + midPointYString + "y).png"
            defineAngleWindow(tiledImagePathOriginal, tiledImagePathOriginal, tileWidth, tileHeight, tileNumber)

            # load OG pic


        elif event == "Next":
            angle = values["-Angle-"]

            newTileFileName = "DEG:" + angle + tiledImagePath

            # default to OG pic
            # override the tileName with the same name plus angle

            print("-Angle-: " + angle)

            return angle

    imagePreviewWindow.close()


# Put all the annotated tiles back together and save, most likely another function


# def annotateTile(tile):
#
#     #tile2 = cv.imread(tile)
#
#     # image = np.ones(shape=(512,512,3), dtype=np.int16)
#     pt1 = (100, 100)
#     pt2 = (400, 350)
#     color = (0, 250, 0)
#     #
#     thickness = 10
#     #
#     cv.line(tile, pt1, pt2, color, thickness)
#     cv.imshow("img w line", tile)
#     cv.waitKey(0)
#     cv.destroyAllWindows()


if __name__ == "__main__":
    # make copy of image and use that for annotation
    #rawChosenImage = mainWindow()
    #pngFilePath, imgHeight, imgWidth, pathOfNewDir = convertImageToPNG(rawChosenImage)
    #tileSize = imagePreviewAndTileSize(pngFilePath, imgHeight, imgWidth)
    #tilePreviewWindow(tileSize[0], tileSize[1], tileSize[2], pngFilePath, pathOfNewDir)
    defineAngleWindow("Tile0_MID(x110x_y110y).png","Tile0_MID(x110x_y110y).png", 400, 253, 0)
