import serial
import time
import requests
import numpy as np
import matplotlib.pyplot as plt
import urllib3
urllib3.disable_warnings()

from firebase import firebase
firebase = firebase.FirebaseApplication('https://smartclips.firebaseio.com/', None)
userId = ""
username = ""
connected = False
def main():
    global userId
    global usernamew
   # try:
    result = firebase.get('/Users', None)
    print("Hello, please select a user or type NEW to create a new user")
    namedict = [];
    count = 0;
    for res in result:
        namedict.append(res)
        children = firebase.get('/Users/'+res, None)
        print(str(count) +" - " + children["name"])
        
        count = count + 1;
    user = raw_input("Select user by number: ")
    if user == "NEW":
        createNewUser()
    else:
        userId = namedict[int(user)]
        username = firebase.get('/Users/'+userId + "/name", None)
    print("User " + username + " logged in with id" + userId)
    # except Exception:
    #     print("Error connecting to firebase - check internet connection");
    printHelp()
    dict = {'1' : arduinoConnect, '2': manualInput, '3':viewLifts,
            '4':addCalories,'5':foodLog, "HELP": printHelp}
    while(1):
        the_input = raw_input("Choose a number: ")
        try:
            if the_input == "QUIT":
                print("Goodbye")
                return
            dict[the_input]()
        except Exception:
            print("Malformed Input")
    #func()
    arduinoConnect()

def foodLog():
    global userId
    logs = firebase.get('/DayFoodLog', None)
    for day in logs:
        dayInfo = firebase.get('/DayFoodLog/'+day, None)
        if dayInfo["UserID"] == userId:
            print("Date: " + dayInfo["date"] + " Intake: " + dayInfo['CaloricIntake'])

def addCalories():
    global userId
    date = raw_input("Enter Date in mm/dd/yyyy: ")
    intake = raw_input("Enter Calories: ")
    newFood = {"date":date,"CaloricIntake":intake, "UserID":userId}
    res = firebase.post("/DayFoodLog", newFood)
    print("Food Log Recorded")

def printHelp():
    print("Commands: \n 1 - Begin Counting Reps \n 2 - Manually Add Lift \n 3 - View lifts \n 4 - Add daily calories \n 5 - Show food log \n HELP - see this message \n QUIT - Quit the program");

def viewLifts():
    global userId
    lifts = firebase.get('/Lifts', None)
    for lift in lifts:
        liftInfo = firebase.get('/Lifts/'+lift, None)
        if liftInfo["UserID"] == userId:
            print("Date: " + liftInfo["date"] + " Lift: " + liftInfo['name'] + " Sets: " + liftInfo['sets'] + " Weight: " + liftInfo['weight'])


def createNewUser():
    global userId
    global username
    name = raw_input("Enter Name: ")
    email = raw_input("Enter Email: ")
    weight = raw_input("Enter Weight: ")
    age = raw_input("Enter Age: ")
    newUser = {"name":name,"email":email,"weight":weight,"age":age}
    username = name;
    res = firebase.post("/Users", newUser)
    userId = res

def manualInput():
    global userId
    global usernamew
    name = raw_input("Enter Lift Name: ")
    reps = raw_input("Enter Reps: ")
    sets = raw_input("Enter Sets: ")
    weight = raw_input("Enter Weight: ")
    date = raw_input("Enter Date in mm/dd/yyyy: ")
    newLif = {"name":name,"reps":reps,"weight":weight,"sets":sets,"date":date, "UserID":userId}
    res = firebase.post("/Lifts", newLif)
    print("Lift Recorded")


def arduinoConnect():
    print("Connecting to Arduino Board");
    try:
        arduino = serial.Serial('COM27', 57600, timeout=.1)
        time.sleep(2) #give the connction a second to settle
        while not connected:
            serin = arduino.read()
            connected = True
        plt.ion()                    #sets plot to animation mode
        
        length = 500                 #determines length of data taking session (in data points)
        x = [0]*length               #create empty variable of length of test
        y = [0]*length
        z = [0]*length
        
        xline, = plt.plot(x)         #sets up future lines to be modified
        yline, = plt.plot(y)
        zline, = plt.plot(z)
        plt.ylim(0,15)    
        
        
        while True:
            data = arduino.readline()
            if(data != ""):
                print(data)
                sep = data.split() 
                print(sep)
                x.append(sep[0])
                y.append(sep[1])
                z.append(sep[2])
              
                del x[0]
                del y[0]
                del z[0]
               
                xline.set_xdata(np.arange(len(x))) #sets xdata to new list length
                yline.set_xdata(np.arange(len(y)))
                zline.set_xdata(np.arange(len(z)))
               
                xline.set_ydata(x)                 #sets ydata to new list
                yline.set_ydata(y)
                zline.set_ydata(z)
             
                plt.pause(0.002)                   #in seconds
                plt.draw()                         #draws new plot
        
        
        
        arduino.close() #closes serial connection (very important to do this! if you have an error partway through the code, type this into the cmd line to close the connection)
    except Exception:
        print("Error connectiong to Arduino Board");

if  __name__ =='__main__':
    main()