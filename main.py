import serial
import time
import numpy as np
import matplotlib.pyplot as plt
def main():
    from firebase import firebase
    connected = False
    try:
        firebase = firebase.FirebaseApplication('https://smartclips.firebaseio.com/', None)
        result = firebase.get('/Users', None)
        print("\n\n Hello "+ result['Name'] + ". Ready for your workout? \n\n");
    except:
        print("Error connecting to firebase");
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