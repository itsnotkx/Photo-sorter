#UI
from tkinter import *
from tkinter import messagebox
from tkinter import filedialog

#image processing
from PIL import Image
from PIL import UnidentifiedImageError

#file processing
import os
import shutil

#DBSCAN
import numpy as np
from sklearn.cluster import DBSCAN


def fileSorter(chosenFolder,scale,locationBased):
    dataMap = {}
    try:
        os.mkdir(os.path.join(chosenFolder,"notRecognised"))
    except OSError:
        messagebox.showwarning(title = "Oops", message = "Error: there exists a folder named 'notRecognised' in the given directory. Please rename or delete the folder and try again.")
        quit()

    if locationBased == True:
        for file in os.listdir(chosenFolder):
            if file == "notRecognised":
                continue
            absfileName = os.path.join(chosenFolder,file)
            location = getLocation(chosenFolder,scale,absfileName)
            if location is not None:
                dataMap[absfileName] = location
        return clusteringAlg(chosenFolder,dataMap)
    
    else:
        for file in os.listdir(chosenFolder):
            if file == "notRecognised":
                continue
            absfileName = os.path.join(chosenFolder,file)
            time = getTime(chosenFolder,absfileName)
            if time is not None:
                dataMap[absfileName] = time
        return createDateFolders(chosenFolder,dataMap)

def getTime(chosenFolder,absfileName):
    dateTimeOriginal = 36867
    dateTime = 306
    try:
        im = Image.open(absfileName)
        exif = im.getexif()
        if exif.get(dateTimeOriginal) is not None:
            im.close()
            return exif.get(dateTimeOriginal)
        elif exif.get(dateTime) is not None:
            im.close()
            return exif.get(dateTime)
        else:
            im.close()
            shutil.move(absfileName,os.path.join(chosenFolder,"notRecognised"))
    except UnidentifiedImageError:
        shutil.move(absfileName,os.path.join(chosenFolder,"notRecognised"))

def getLocation(chosenFolder,scale,absfileName):
    gpsTag = 34853
    errorShown = False
    try:
        im = Image.open(absfileName)
        location = im.getexif().get_ifd(gpsTag)
        try:
            lat = location[2]
            longi = location[4]
            Dlatitude = float(lat[0]) + float(lat[1])/60 + float(lat[2])/3600
            Dlongitude = float(longi[0]) + float(longi[1])/60 + float(longi[2])/3600
            DDgps = [round(Dlatitude,int(scale)),round(Dlongitude,int(scale))]
            im.close()
            return DDgps
            
        except KeyError:
            im.close()
            if errorShown == False:
                errorShown = True
                messagebox.showwarning(title = "Oops", message = "Error: One or more photos without geolocation data has been detected, these photos have been moved to the notRecognised folder.")
            shutil.move(absfileName,os.path.join(chosenFolder,"notRecognised"))
            
    except UnidentifiedImageError:
        shutil.move(absfileName,os.path.join(chosenFolder,"notRecognised"))

def clusteringAlg(chosenFolder,dataMap):
    i = 0
    data = []
    for coords in dataMap.values():
        data.append(coords)
    data = np.array(data)
    dbscan = DBSCAN(eps = 0.01 , min_samples = 2) #give option to choose this in configs
    cluster_labels = dbscan.fit_predict(data)
    sortedData = [[] for _ in range(max(cluster_labels)+2)]
    items = list(dataMap.items())
    for i in range(len(cluster_labels)):
        sortedData[cluster_labels[i]].append(items[i])
    return createLocationFolders(chosenFolder,sortedData)

def createLocationFolders(chosenFolder,sortedData):
    i = 0
    for cluster in sortedData:
        os.mkdir(os.path.join(chosenFolder,"cluster" + str(i)))
        for tup in cluster:
            shutil.move(tup[0],os.path.join(chosenFolder,"cluster" + str(i)))
        i += 1
    messagebox.showinfo(title = "Success!", message = "Photos have been successfully organised!")
    return None

def createDateFolders(chosenFolder,dataMap):
    dates = set()
    for key,value in dataMap.items():
        timeStamp = value.split(" ")
        date = timeStamp.pop(0).replace(":", "-")
        if date in dates:
            shutil.move(key,os.path.join(chosenFolder,date))
        else:
            dates.add(date)
            os.mkdir(os.path.join(chosenFolder,date))
            shutil.move(key,os.path.join(chosenFolder,date))
    messagebox.showinfo(title = "Success!", message = "Photos have been successfully organised!")
    return None
    

def gui():
    #SETUP
    root = Tk()
    root.title("A")
    root.geometry("570x150")
    

    #OPTIONS MENU
    optionsList = ["neighbourhood","city","country"]
    converttoScale = {
        "neighbourhood":3,
        "city":2,
        "country":1,
    }
    selectedOption = StringVar(root)
    selectedOption.set("neighbourhood")
    
    optionMenu = OptionMenu(root, selectedOption, *optionsList)


    #CHECKBUTTON
    var = BooleanVar()


    #INITIALLY HIDDEN OPTIONS MENU
    def hideMenu():
        if var.get():
            optionMenu.grid(row = 3, column = 3)
            scaleLabel.grid(row = 3, column = 2)
        else:
            optionMenu.grid_forget()
            scaleLabel.grid_forget()


    checkButton = Checkbutton(
        text = "Sort by location?",
        variable = var,
        command = hideMenu,
    ).grid(row = 2, column = 3)




    #FILE TITLE TEXTBOX
    fileText = Text(
        root,
        height = 1,
        width = 52,
        wrap = "none"
    )

    fileText.grid(row = 1, column = 1, columnspan = 2)


    def openFolder():
        fileText.config(state = NORMAL)
        chosenFolder = filedialog.askdirectory(title = "Select Photo Directory", mustexist = True)
        if not chosenFolder:
            messagebox.showwarning(title = "Oops", message = "Error: folder not selected")
        else:
            selectedFolder.set(chosenFolder)
            fileText.insert(END,selectedFolder.get())   
            fileText.config(state = DISABLED)
        
        

    #SELECT FILE BUTTON
    selectFileButton = Button(
        root,
        text = "Select Folder",
        command = openFolder,
    )
    
    selectFileButton.grid(row = 1, column = 3)


    selectedFolder = StringVar()


    def begin():
        theFile = selectedFolder.get()
        scale = converttoScale[selectedOption.get()]
        locationBased = var.get()
        fileSorter(theFile,scale,locationBased)



    #SUBMIT BUTTON
    submitButton = Button(
        root,
        text = "Begin",
        command = begin,
    ).grid(row = 3, column = 1)


    #LABELS
    titleText = StringVar()
    titleText.set("PHOTO SORTER")
    mainTitle = Label(
        root,
        textvariable=titleText,
        font = ("Segoe UI",20,"bold")
    )

    filestr = StringVar()
    filestr.set("File:")
    fileLabel = Label(
        root,
        textvariable=filestr,
    )

    scaleStr = StringVar()
    scaleStr.set("Scale:")
    scaleLabel = Label(
        root,
        textvariable=scaleStr
    )

    fileLabel.grid(row = 1, column = 0)
    mainTitle.grid(row = 0, column = 1)
    
    root.mainloop()  

if __name__ == "__main__":
    gui()