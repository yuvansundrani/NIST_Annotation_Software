
import PySimpleGUI as sg
import cv2 as cv
import numpy as np

sg.theme("BrightColors")

layout = [[sg.Text("NIST CNN Annotation Software", text_color="blue")],
          [sg.T("")], [sg.Text("Choose a file: "), sg.Input(), sg.FileBrowse(key="-IN-")],
          [sg.Button("Submit")]]

window = sg.Window('Choose an image', layout, size=(800, 200))

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == "Exit":
        break
    elif event == "Submit":
        chosenImage = values["-IN-"]
        if chosenImage.__contains__(".png") or chosenImage.__contains__(".jpg"):
            # sg.popup('Valid image!', keep_on_top=True)

            layout2 = [[sg.Text("Valid Image!", text_color="red")],
                       [sg.Image(values["-IN-"], size=(800, 200))],
                       [sg.Button("Re-pick"), sg.Button("Process!")]]

            window2 = sg.Window("Valid Image!", layout2, modal=True)

            while True:
                event2, window = window2.read()
                if event2 == sg.WIN_CLOSED:
                    break

                elif event2 == "Process!":
                    # sg.Popup("Processing Now!")
                    img = cv.imread(chosenImage)
                    grayScale = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
                    ret, binary = cv.threshold(grayScale, 150, 255, cv.THRESH_BINARY)

                    contours, hierarchy = cv.findContours(binary, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

                    cv.drawContours(img, contours, 1, (0, 0, 255), 2)

                    #approx = cv.approxPolyDP(contours[0], 20, True)

                    #cv.drawContours(img, [approx], 0, (0, 255, 0), 2)
                    cv.imshow('Image', img)

                    cv.waitKey(0)
                    cv.destroyAllWindows()







# process image

                elif event2 == "Re-pick":
                    sg.Popup("Restart the application to choose new image!")


        else:
            sg.popup('invalid image!', keep_on_top=True)
