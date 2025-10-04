import RPi.GPIO as GPIO
import time
import serial
import PCF8591 as ADC
import DHT11 as DHT
import urllib.request                  #import the urllib.request library
import PCF8591 as ADC                  #import ADC chip library
from datetime import datetime
from flask import Flask
from flask import send_file
from picamera import PiCamera
from keypadfunc import keypad
import LCD1602





#Camera configuration

Mycamera=PiCamera() #create an object called MYcamera using PiCamera class
Mycamera.resolution=(640,480) #This is the minimum resolution so that it prevents the camera to cover the whole screen of the monitor and only show a part of it
Mycamera.rotation=180 #This rotation property applied to the camera's input changes the rotation 





project=Flask(__name__) #flask instance -> project
LCD1602.init(0x27, 1)  # init LCD (slave address, background light)

ADC.setup(0x48)  #initialize ADC and setup I2C
m = 1
pas=0
#YLED=17 #Yellow LED is connected to Aout of ADC
RLED=12 #Red LED connected to GPIO 12
BLED=13 #BLue LED connected to GPIO 13
button=16 #push button connected to GPIO
TRIG=4 #ultrasonic sensor trigger to start ranging
ECHO=27 #ultrasonic sensor echo to start ranging
MSP=6 #MSP is a variable for PIR sensor to detect motion
valuestem=[] #value array for temperature values to read from thingspeak
valueshum=[] #value array for humidity values to read from thingspeak
API_KEY="IXM3SWRDTKKA34MQ" #Thingspeak channel Write API Key
CH_ID=2326173 #Channel ID
Field_No_Tem=0 #For displaying temperature
Field_No_Hum=1 #For displaying Humidity
Numberofreadings=5 #Read 5 elements from Thingspeak

GPIO.setmode(GPIO.BCM) #setmode to BCM Mode
GPIO.setwarnings(False) #To remove unecessary warnings
#GPIO.setup(YLED,GPIO.OUT)
GPIO.setup(RLED,GPIO.OUT) 
GPIO.setup(BLED,GPIO.OUT)
GPIO.setup(button,GPIO.IN)
GPIO.setup(MSP,GPIO.IN,pull_up_down=GPIO.PUD_UP) #Ultrasonic sensors echo and trigger configuration
GPIO.setup(ECHO,GPIO.IN) #echo is input
GPIO.setup(TRIG,GPIO.OUT) #trigger is output
GPIO.setup(5,GPIO.OUT) #set pin 5(Buzzer) to PWM signal
global buzz #Assign a global variable to replace GPIO.PWM
buzz=GPIO.PWM(5,1) #5 is the channel number and 1Hz is the inital frequency
buzz.start(50) #Duty cycle is 50%

#Validating RFID tag code  
SERIAL_PORT = '/dev/ttyS0' 
def validate_rfid(code): 
    s = code.decode("ascii")
    if (len(s) == 12) and (s[0] == "\n") and (s[11] == "\r"):
        return s[1:11]
    else:
        return False
ser = serial.Serial(baudrate = 2400,  bytesize = serial.EIGHTBITS,  parity = serial.PARITY_NONE,  port = SERIAL_PORT, stopbits = serial.STOPBITS_ONE,  timeout = 1)

#flask route for index page; it will display the following message        
@project.route('/')
def index():
    return 'Welcome/Marhaban Bikom/Khush-Aaamdeed to our Smart Home!'


#Dynamic routing concept for Forget RFID Scenario : Open/close door remotely

@project.route("/Door/<action>")  #dynamic route path on server's browser ('0.0.0.0:5020/Door/<action>) will control LED status
def userChoice(action):   #route function userChoice(action) will be called for route path ('0.0.0.0:5020/Door/<action>) and action is a parameter to the userChoice function
    newAction=int(action)   #caste the string action into an integer to compare   the value and control the LED
    if(newAction==1):   #if we access path 0.0.0.0:5020/Door/1 on server's web browser, it will unlock the door
        GPIO.output(BLED,GPIO.HIGH)   #if action is 1, turn ON the home lights shown by the BLUE LED
        status="***Door Open ; Lights ON***"   #the status will be displayed on web browser
    elif(newAction==0):   #if we access path 0.0.0.0:5020/showDoor/0 on server's web browser, it will close the door
        GPIO.output(BLED,GPIO.LOW)   #if action is 0, turn OFF the Home Lights
        status="***Door Closed ; Light OFF***"   #the status will be displayed on the web browser
    return status   #returns the new status to the web browser and displays it


def send():
    @project.route("/showImage")
    def myImage():

        Mycamera.rotation=180

        photo_path="/home/pi/Desktop/F23/Flaskpic1.jpeg"#set photo path where photo should be saved after capturing. 
        response=send_file(photo_path,mimetype="image/jpeg") #Images are stored as JPEG format 

        return response



@project.route("/Appliance/<action>") #dynamic route path on server's browser ('0.0.0.0:5020/Appliance/<action>) will control home appliances status
def userChoices(action):   #route function userChoice(action) will be called for route path ('0.0.0.0:5020/Appliance/<action>) and action is a parameter to the userChoice function
    newAction=int(action)   #caste the string action into an integer to compare the value and control the home appliances
    if(newAction==1):   #if we access path 0.0.0.0:5020/Appliance/1 on server's web browser, it will turn ON the RED LED
        GPIO.output(RLED,GPIO.HIGH)   #if action is 1, turn ON the RED LED indicating that the home appliances are deactivated
        status="*** Appliances Deactivated ***"   #the status will be displayed on web browser

    elif(newAction==0):   #if we access path 0.0.0.0:5020/Appliance/0 on server's web browser, it will turn OFF the LED 
        GPIO.output(RLED,GPIO.LOW)   #if action is 0, turn OFF the RED LED indicating that the home appliances are activated
        status="*** Appliances Activated ***"   #the status will be displayed on the web browser  
    return status   #returns the new status to the web browser and displays it



def action(self):
        #Callback function of interrrupt
    
        print("Home lights switched ON!")
        print("Rotate the knob to adjust the light intensity and press the button to set it") #prompt the user to rotate the knob
        ADC.write(255-ADC.read(1)) #Potentiometer controls intensity of Yellow LED
        
       # light=True

       
        

#function to capture picture / snap a picture
def snap():
    photo_path="/home/pi/Desktop/F23/Flaskpic1.jpeg"
    photoTimeStamp=datetime.now().isoformat()
    Mycamera.annotate_text="Picture taken at {}".format(photoTimeStamp)
    Mycamera.capture(photo_path)
    Mycamera.start_preview()
    time.sleep(3)
    Mycamera.stop_preview()

#To download values of temperature and humidity from thingspeak 
def downloadthingspeak ():
    Z = urllib.request.urlopen("https://api.thingspeak.com/channels/{}/fields/{}.csv?results={}".format(CH_ID,Field_No_Hum,Numberofreadings))
    datahum=x.read().decode('ascii')
    Y = urllib.request.urlopen("https://api.thingspeak.com/channels/{}/fields/{}.csv?results={}".format(CH_ID,2,Numberofreadings))
    datatemp=Y.read().decode('ascii')
    datahum=Z.read().decode('ascii')
                
    datatem=",".join(datatemp.split("\n"))
    time.sleep(1)
    datahum=",".join(datahum.split("\n"))
                
            
    for i in range(5,Numberofreadings*3+3,3):
        valuestem.append(datatem.split(",")[i])

    for i in range(5,Numberofreadings*3+3,3):
        valueshum.append(datahum.split(",")[i])
    #change later because values does not change
                
    Temperaturedownload=float(valuestem[3])
    Humiditydownload=float(valueshum[3])
    print("Temperature: {}, Humidity: {}%".format(Temperaturedownload,Humiditydownload))

#To record video from the camera
def recvideo():
    video_path="/home/pi/Desktop/F23/myVideo.h264" #set video path for video to be saved after capturing.
    Mycamera.start_preview()
    Mycamera.start_recording(video_path)
    time.sleep(3)
    Mycamera.stop_recording()
    Mycamera.stop_preview()
    

def shiftKey():
    Keyf,KeyS = keypad()
    if(GPIO.input(button)==1):
        KeyF=KeySMycamera.stop_preview()
    else:
        KeyF=Keyf
    return KeyF

#Activate the buzzer that represents an alarm sound 
def play_alarm_sound(note_frequency, duration):
    for i in range (0, 5):    

        buzz.ChangeFrequency(note_frequency)
        time.sleep(duration)
        buzz.ChangeFrequency(note_frequency/2)
        time.sleep(duration)
        buzz.ChangeFrequency(note_frequency/4)
        time.sleep(duration)
        buzz.ChangeFrequency(0.5)

#Function to flash
def flash(led):
    for x in range(0,4):
        GPIO.output(led,GPIO.HIGH)
        time.sleep(0.5)
        GPIO.output(led,GPIO.LOW)
        time.sleep(0.5)
        
#This represents the ultrasonic reading function
def distance():
    GPIO.output(TRIG, GPIO.LOW) 
    time.sleep(0.000002)
    GPIO.output(TRIG, 1)
    time.sleep(0.00001)
    GPIO.output(TRIG, 0)
    #Read the echo pin signal and then calculate the distance
    while GPIO.input(ECHO) == 0:
        a = 0               #dummy                           
    time1 = time.time()         #capture time 1               
    while GPIO.input(ECHO) == 1:
        a = 0                                                  
    time2 = time.time()         #capture time 2              
    duration = time2 - time1
    return duration*1000000/58 #sensor equation


GPIO.add_event_detect(button,GPIO.FALLING,callback=action,bouncetime=4000) #button is the GPIO Input, edge is falling, callback is the name of the ISR function, x is bounctime in msec
    
        
unlocked=False #flag to enable program features
welcomeflag=True
passcount=0 #count attempts of failed logins
heater=False
ac=False
humidifier=True
flag=0 #flag to record only once at the start of the program

ask=input(str("Do you want to enter flask mode to control the house remotely?: (Y/N)"))  #Gives user option to control the house remotely through flask 
if(ask=="Y"):
    if __name__ == "__main__":
        project.run(host='0.0.0.0',port=5020)

while True:

            
    if(unlocked==False):
        if(flag==0):
            recvideo()
            snap()
            flag+=1
        entry=input("Press R for RFID access, or press P for password entry if RFID key is lost: ")
        if (entry=="R"):
        
            ser.flushInput()
            ser.flushOutput()
            data=ser.read(12)
            code = validate_rfid(data)
            time.sleep(5)
            if (code=="5300C82FB3"):
                print ("RFID tag: {}".format(code))
                ask=input(str("Visitor image captured; Do you want to see it?: (Y/N)")) #Ask the user to view the visitor's image on flask
                if(ask=="Y"):
                    send()
                    if __name__ == "__main__":
                        project.run(host='0.0.0.0',port=5020)
                unlocked=True
            else:
                print("Invalid tag") #if RFID tag doesnt match with the correct access code it will print this message
                play_alarm_sound(300,0.5) #It will play an alarm if invalid RFID tag is read
                snap()
                ask=input(str("Intruder image captured; Do you want to see it?: (Y/N)")) #Ask the user to view the intruder's image on flask
                if(ask=="Y"):
                    send()
                    if __name__ == "__main__":
                        project.run(host='0.0.0.0',port=5020)
                 
         #Password scenario    
        elif (entry=="P"):
            accPass="99"
            print("Enter password: ")
            key1=shiftKey()
            time.sleep(0.5)
            key2=shiftKey()
            time.sleep(0.5)
            password=str(key1)+str(key2)
            LCD1602.write(0,0,password) #displays the typed password on the first line of the LCD
            if(password==accPass and passcount<2):
                print("Correct password; Access granted!\n") 
                unlocked=True
            elif(passcount==2): 
                print("Exceeded login attempts!") #3 attempts after which it detects failed login attempt
                
                snap()
                send()
                play_alarm_sound(300,0.5) #Failed login then plays an alarm sound
                if __name__ == "__main__":
                        project.run(host='0.0.0.0',port=5020)
                
                
                              
                
                exit()
            passcount+=1
            
    if(distance()<10):#Ultrasonic sensor   
            photo_path="/home/pi/Desktop/F23/Project/Flaskpic1.jpeg"#set photo path where photo should be saved after capturing
            
            print("Visitor Detected!")
            snap()
            send()
            flaskmode=input(str(" Do you want to enter Flask mode (Y/N) to view the picture"))
            if(flaskmode=="Y"):
                if __name__ == "__main__":
                        project.run(host='0.0.0.0',port=5020) #To run the flask 
            
  
    if(unlocked):
        if(welcomeflag):
            LCD1602.write(0,0,"Welcome") #prints a Welcome message on the first line of the LCD
            print("Welcome/Marhaban Bikom/Khush Aaamdeed to our Smart Home!") #prints a Welcome message on the terminal
            flash(RLED) #Flashing RLED indicates that we have entered the house
            
            
            welcomeflag=False
         #Uploading temperature and humidity values to Thingspeak   
        result=""
        while (not result):
            result = DHT.readDht11(18) #DHT11->GPIO 18 ; 
            if result:
                Humidity, Temperature = result
                x = urllib.request.urlopen("https://api.thingspeak.com/update?api_key={}&field1={}&field2={}".format(API_KEY, Humidity,Temperature))
                temphumMessage = "{}%, {}C".format(Humidity, Temperature)
                time.sleep(1)
                            
#threshold for activating heater and ACs
            time.sleep(1)
        LCD1602.write(0,1,temphumMessage)
        if(Temperature<15 and heater==False): #Provided that the heater is OFF if temp less than 15 degrees
            heater=True #Turn on heater
            ac=False #turn OFF AC
            print("Heater activated") #Print the message on the terminal
        elif (Temperature>28 and ac==False): #Provided that the AC is OFF if temp less than 28 degrees
            ac=True #AC turns ON 
            heater=False #Heater turns OFF
            print("AC activated")
        elif(ac and Temperature>15): 
            ac=False #AC turns OFF
            print("AC deactivated")
        elif(heater and Temperature<30):
            heater=False #Heater turns OFF
            print("Heater deactivated")
        
        if(Humidity<50 and humidifer==False): #Provided that the humidifier is OFF ; if humidity less than 50 degrees
            humidifier=True #Humidifier turns ON
            print("Humidifier activated")
        elif (Humidity>50 and humidifier): #Humidity greater than 50%
            humidifier=False #Turn OFF the humidifer
            print("Humidifier deactivated")
        
        time.sleep(1)

