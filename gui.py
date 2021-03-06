#imports
import RPi.GPIO as GPIO
from tkinter import *
import os
import MySQLdb
import subprocess
from tkinter import ttk
from tkinter import font
import digitalio
import board
from datetime import date,datetime,timedelta
import serial
from PIL import Image,ImageTk
from pydub import AudioSegment
from pydub.playback import play
import time
import os
import pygame

global NAME
global DOB
global GENDER
global CARE


#setup mysql
db = MySQLdb.connect(host="localhost",  # your host 
                     user="cory",       # username
                     passwd="ipothecary",     # password
                     db="pills")   # name of the database
cur = db.cursor()

#shit for the arduino
port1 = "/dev/ttyACM0"
s1 = serial.Serial(port1,9600)
s1.flushInput()

#port2 = "/dev/ttyACM0"
#s2 = serial.Serial(port2,9600)
#s2.flushInput()

i = 9
mapping = []
for y in range(1,4):
    for x in range(-3,0):
        mapping.append((-x,y,i))
        i=i-1

global MAPPING
MAPPING = mapping

#all commands go here
def raise_frame(f):
    f.tkraise()
    pygame.mixer.init()
    pygame.mixer.music.load('jump.wav')
    pygame.mixer.music.play(1)
def playSound(event):
    #print(vol)
    song = AudioSegment.from_wav("jump.wav")
    #song = song+vol 
    play(song)

def addUser(name,rfid,age):
    if name and rfid and age:
        cur.execute("INSERT INTO users (name,RFID,age) VALUES (%s,%s,%s)",
            (name,rfid,age)) #DayOfWeekHourMinute
        db.commit()
               
def rfidScan(widget,eWidget,scanOn,usName,butt):
    global RFID
    rfidValue = input("RFIDNOW")
    rfidE.insert(END,rfidValue)
    rows = cur.execute("SELECT RFID FROM users where name='"+usName+"';")
    result = cur.fetchall()
    
    rows1 = cur.execute("SELECT RFID FROM users where RFID='"+str(rfidValue)+"';")
    rResult = cur.fetchall()
    print("Hi")
    if scanOn and result and rfidValue == result[0][0]:
        print("1")
        widget.configure(text="Success!")
        butt.place(relx= 0.8, y=550,anchor=CENTER)
    elif scanOn:
        print("2")
        widget.configure(text="Failed. Try again")
        eWidget.delete(0,'end')
    elif not scanOn and rResult and rfidValue == rResult[0][0]:
        print("3")
        widget.configure(text="RFID already in use.")
        eWidget.delete(0,'end')
    elif len(str(rfidValue))>10:
        print("5")
        widget.configure(text="Failed. Try again")
        eWidget.delete(0,'end')
    else:
        print("4")
        widget.configure(text="Success!")
        #eWidget.delete(0,'end')
        finButton.place(relx= 0.5, y=550,anchor=CENTER)
        RFID = rfidE
    
def keyboard(frame,widget):
    keys = ["q","w","e","r","t","y","u","i","o","p",
            "a","s","d","f","g","h","j","k","l",":",
            "z","x","c","v","b","n","m",",",".","Back"]
    k=0
    kbtn = [[0 for x in range(10)] for x in range(10)]
    for y in range(0,3):
        for x in range(0,10):
            kbtn[x][y] = ttk.Button(frame, text=keys[k],compound="top",command=lambda k=k:insertText(keys[k],widget),width=4,style='TButton')
            kbtn[x][y].grid(row=y+2,column=x,pady=15)
            if k!=29:
                k=k+1


def keypad(frame,widget):
    keys = ["1","2","3","4","5","6","7","8","9","","0","Back"]
    k=0
    kbtn = [[0 for x in range(4)] for x in range(4)]
    for y in range(0,4):
        for x in range(0,3):
            kbtn[x][y] = ttk.Button(frame, text=keys[k],compound="top",command=lambda k=k:insertText(keys[k],widget),width=7,style='TButton')
            kbtn[x][y].grid(row=y+2,column=x+1,pady=20)
            print(k)
            if k!=11:
                k=k+1
                
                
def insertText(key,widget):
    prevText = widget.get()
    if key == "Back" and prevText:
        widget.delete(len(prevText)-1,len(prevText))
    elif key != "Back"and len(prevText) != 10:
        widget.insert(END,key.upper())          
    
        
        
def cText(size):
    ft = "helvetica " + str(size)
    s = ttk.Style()
    s.configure('TButton',font=ft)
    d = ttk.Style()
    d.configure('TLabel', font=ft)

def dispense(pillList,dButton):
            
    for pill in pillList:
        pName = pill[0]
        pNum = pill[1]
        rows = cur.execute("SELECT containerx,containery,amount FROM pills where name='"+pName+"';")
        pillLoc = cur.fetchall()
        pillXY = (pillLoc[0][0],pillLoc[0][1])
        for M in MAPPING:
            if (M[0],M[1]) == pillXY:
                container = M[2]
        for am in range(0,pNum):
            print("Motor "+str(container)+" run")
            n = str(container)

            n = n.encode()
            if n==1 or n==2 or n==3:
                s2.write(n)
            else:
                s1.write(n)
            time.sleep(1)   
        #dButton.place(relx= 0.5, y=300,anchor=CENTER)
        cur.execute("UPDATE pills SET amount ='"+str(pillLoc[0][2]-pNum)+"' WHERE name = '"+pName+"'")
    db.commit()
    
def removeU(name,bU):
    cur.execute("DELETE FROM users WHERE name='"+name+"';")
    db.commit()
    bU.place_forget()
    remove(fremove)
    

def selectAR(name):
    raise_frame(fSRTimes)
    ART = ttk.Label(fSRTimes,text="Add or Remove Times",style='TLabel')
    ART.place(relx=0.5, y=50,anchor=CENTER)

    AButton = ttk.Button(fSRTimes,text="Add",style='TButton',command=lambda:selectPill(name))
    AButton.place(relx=0.5, y=150,anchor=CENTER)
    RButton = ttk.Button(fSRTimes,text="Remove",style='TButton',command=lambda:removeTime(name))
    RButton.place(relx=0.5, y=250,anchor=CENTER)

    
    ARBButton = ttk.Button(fSRTimes,text="Return",style='TButton',command=lambda:raise_frame(fsettings))
    ARBButton.place(relx=0.5, y=500,anchor=CENTER)

def removeTime(name):
    raise_frame(fRTimes)

    completeButton = ttk.Button(fSRTimes,text="Return",style='TButton',command=lambda:raise_frame(fpComplete))
    completeButton.place(relx=0.5, y=500,anchor=CENTER)
    
def selectPill(name):
    cur.execute("SELECT * FROM pills;")
    result = cur.fetchall()
    raise_frame(fSetTimes4)
    selectPT = ttk.Label(fSetTimes4,text="Select Pill to Give "+name,style='TLabel')
    selectPT.place(relx=0.5, y=50,anchor=CENTER)
    yl=150
    i=0
    for row in result:
        pillTxt = row[0]
        bU = ttk.Button(fSetTimes4, text=pillTxt, style='TButton',command=lambda row=row:selectP(row[0],name))
        bU.place(relx= 0.5, y=yl,anchor=CENTER)
        yl=yl+70
        i=i+1

def selectP(pName,uName):
    raise_frame(fSetTimes5)
    PTT = ttk.Label(fSetTimes5,text="Select Number of "+pName+" to Perscribe.",style='TLabel')
    PTT.place(relx=0.5, y=50,anchor=CENTER)
    yl=150
    i=0
    for num in range(1,8):
        numTxt = str(num)
        bU = ttk.Button(fSetTimes5, text=numTxt, style='TButton',command=lambda num=num:getPTime(num,pName,uName))
        bU.place(relx= 0.5, y=yl,anchor=CENTER)
        yl=yl+70
        i=i+1

def getPTime(num,pName,uName):
    raise_frame(fSetTimes6)
    gPTT = ttk.Label(fSetTimes6,text="Select Time to Perscribe.",style='TLabel')
    gPTT.place(relx=0.5, y=50,anchor=CENTER)

    
    comboHour = ttk.Combobox(fSetTimes6, values = ["0","1","2","3","4","5","6","7","8","9","10","11"],font=('Helvetica',70),width=3)
    comboHour.place(relx=0.3, y=120,anchor=CENTER)
    comboHour.current(0)
    gPTT = ttk.Label(fSetTimes6,text=":",style='TLabel')
    gPTT.place(relx=0.4, y=120,anchor=CENTER)
    comboMin = ttk.Combobox(fSetTimes6, values = ["00","15","30","45"],font=('Helvetica',70),width=3)
    comboMin.place(relx=0.5, y=120,anchor=CENTER)
    comboMin.current(0)
    comboAP = ttk.Combobox(fSetTimes6, values = ["AM","PM"],font=('Helvetica',70),width=3)
    comboAP.place(relx=0.7, y=120,anchor=CENTER)
    comboAP.current(0)
    fPTButton = ttk.Button(fSetTimes6,text = "Next",style='TButton',command=lambda:getFP(comboHour,comboMin,comboAP,num,pName,uName))
    fPTButton.place(relx=0.5, y=300,anchor=CENTER)
    

def getFP(comboHour,comboMin,comboAP,num,pName,uName):
    
    if comboAP.get()=="PM":
        inputHour=int(comboHour.get())+12
    else:
        inputHour = int(comboHour.get())
     
    year = str(date.today().year)
    month = str(date.today().month)
    day = str(date.today().day)
    hour = datetime.now().strftime('%H')
    minN = datetime.now().strftime('%M')        
    x = month+"/"+day+"/"+year[-2:]+" "+str(inputHour)+":"+str(comboMin.get())
    d = datetime.strptime(x,"%m/%d/%y %H:%M")

    if inputHour - int(hour)<0:
        d = d + timedelta(days=1)
    elif inputHour-int(hour)==0 and int(comboMin.get())-int(minN)<=0:
        d=d+timedelta(days=1)

    pTimes = d.strftime("%m/%d/%y %H:%M")
    
    raise_frame(fSetTimes7)
    setT = ttk.Label(fSetTimes7,text="Input hour frequency of perscription",style='TLabel')
    setT.grid(row=0,column=2,pady=5)
    FreqText = Entry(fSetTimes7,width=10, font=('Helvetica', 30))
    FreqText.grid(row=1,column=2)

    keypad(fSetTimes7,FreqText)

    fPTButton = ttk.Button(fSetTimes7,text = "Finish",style='TButton',command=lambda:finalPillTime(FreqText.get(),pTimes,num,pName,uName))
    fPTButton.grid(row=6,column=3,pady=30)
    
def finalPillTime(freq,pTimes,num,pName,uName):
    cur.execute("SELECT containerx,containery FROM pills where name='"+pName+"';")
    result = cur.fetchall()
    x,y=result[0][0],result[0][1]

    cur.execute("INSERT INTO pilltimes (user,pillName,containerx,containery,number,timeNext,freq,lastMiss,lastRecieve) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (uName,pName,x,y,num,pTimes,freq,0,0)) 
    db.commit()
        
    raise_frame(fpComplete)

def selectU(name):
    raise_frame(fSetTimes3)
    #fSetTimes3 stuff
    selectUT = ttk.Label(fSetTimes3,text="Scan User RFID"+name,style='TLabel')
    selectUT.place(relx=0.5, y=50,anchor=CENTER)
    addI = Image.open("rfidScan.png")
    imageS = addI.resize((150,150),Image.ANTIALIAS)
    rScanImage = ImageTk.PhotoImage(imageS)

    RFIDT = ttk.Label(fSetTimes3,text="Please scan your RFID Chip now!",style='TLabel')
    RFIDT.place(relx=0.5, y=50,anchor=CENTER)

    succT = ttk.Label(fSetTimes3,text="To scan, place your chip on the scanner below.",style='TLabel')
    succT.place(relx=0.5, y=460,anchor=CENTER)

    rfidE = Entry(fSetTimes3,width=15, show="*",font=('Helvetica', 30))
    rfidE.place(relx=0.5, y=400,anchor=CENTER)

    #nextButton = ttk.Button(fSetTimes3,text = "Next",style='TButton',command=lambda:selectPill(usName))
    RbtnBack = ttk.Button(fremove,text="Return",style='TButton',command=lambda:raise_frame(fSetTimes2))
    RbtnBack.place(relx=0.2, y=550,anchor=CENTER)
    nextButton = ttk.Button(fSetTimes3,text = "Next",style='TButton',command=lambda:selectAR(name))
    #nextButton.place(relx= 0.8, y=550,anchor=CENTER)
    nextButton.place_forget()

    scanB = ttk.Button(fSetTimes3,text = "Press to start scan",style='TButton',image=rScanImage,compound="top",command=lambda:rfidScan(succT,rfidE,True,name,nextButton))
    scanB.place(relx=0.5, y=190,anchor=CENTER)
    
def removeConf(frame,name,bU):
    raise_frame(fremoveC)
    CremoveUT = ttk.Label(fremoveC,text="Confirm Remove User: "+name,style='TLabel')
    CremoveUT.place(relx=0.5, y=100,anchor=CENTER)
    
    CbtnNo = ttk.Button(fremoveC,text="Yes",style='TButton',command=lambda:removeU(name,bU))
    CbtnNo.place(relx=0.2, y=400,anchor=CENTER)
    CbtnYes = ttk.Button(fremoveC,text="No",style='TButton',command=lambda:raise_frame(fsettings))
    CbtnYes.place(relx=0.8, y=400,anchor=CENTER)
    
def remove(frame):
    raise_frame(fremove)
    removeUT = ttk.Label(fremove,text="Select User",style='TLabel')
    removeUT.place(relx=0.5, y=50,anchor=CENTER)
    RbtnBack = ttk.Button(fremove,text="Return",style='TButton',command=lambda:raise_frame(fsettings))
    RbtnBack.place(relx=0.8, y=500,anchor=CENTER)
    rows = cur.execute("SELECT name, Gender, DOB FROM users")
    result = cur.fetchall()
    yl=150
    i=0
    for row in result:
        usrTxt = row[0]+", "+row[1]+", "+str(row[2])[:4]
        bU = ttk.Button(fremove, text=usrTxt, style='TButton',command=lambda row=row:removeConf(frame,row[0],bU))
        bU.place(relx= 0.5, y=yl,anchor=CENTER)
        yl=yl+70
        i=i+1

def selectUser(fSetTimes1,pinText,fSetTimes2):
    if pinText.get() == "1234":
        raise_frame(fSetTimes2)
        pinText.delete(0,"end")

    #fSetTimes2 stuff
    removeUT = ttk.Label(fSetTimes2,text="Select User",style='TLabel')
    removeUT.place(relx=0.5, y=50,anchor=CENTER)
    RbtnBack = ttk.Button(fSetTimes2,text="Return",style='TButton',command=lambda:raise_frame(fsettings))
    RbtnBack.place(relx=0.8, y=500,anchor=CENTER)
    rows = cur.execute("SELECT name, Gender, DOB FROM users")
    result = cur.fetchall()
    yl=150
    i=0
    for row in result:
        usrTxt = row[0]+", "+row[1]+", "+str(row[2])[:4]
        bU = ttk.Button(fSetTimes2, text=usrTxt, style='TButton',command=lambda row=row:selectU(row[0]))
        bU.place(relx= 0.5, y=yl,anchor=CENTER)
        yl=yl+70
        i=i+1
        
def getValue(nextFrame,widget,valueSet):
    valueSet = widget.get()
    if widget.get():
        raise_frame(nextFrame)
        
def getValueP(widget,x,y,PN):
    if widget.get():
        raise_pinFrame(x,y,PN)
        pnameText.delete(0,"end")
        #raise_paaframe(x,y,PN)

def raise_pinFrame(x,y,PN):
    raise_frame(fCarePin)
    setT = ttk.Label(fCarePin,text="Input your caretaker pin",style='TLabel')
    setT.grid(row=0,column=2,pady=5)
    pinText = Entry(fCarePin,width=10, show="*",font=('Helvetica', 30))
    pinText.grid(row=1,column=2)

    keypad(fCarePin,pinText)

    Cbtn = ttk.Button(fCarePin, text="Cancel", style='TButton',command=lambda:raise_frame(fmain))
    Cbtn.grid(row=6,column=1,pady=30)
    addButton = ttk.Button(fCarePin,text = "Next",style='TButton',command=lambda:raise_paaframe(x,y,PN,pinText))
    addButton.grid(row=6,column=3,pady=30)
    
def pillFrames(cN,pillFreeD,removePillsButton):
    addPC = Image.open("cont.png")
    imageS = addPC.resize((300,300),Image.ANTIALIAS)
    PCImage = ImageTk.PhotoImage(imageS)
    
    containerT.configure(text="Container " +str(cN))
    pillAdd = ttk.Button(fcont, text="Add", style='TButton',command=lambda:raise_paframe(x,y))
    pillAdd.place(relx= 0.6, y=350,anchor=CENTER)
    
    PCL = Label(fcont,image = PCImage,bg="#595959")
    PCL.image=PCImage
    PCL.place(relx=0.3, y=250,anchor=CENTER)
    for M in MAPPING:
        if M[2]==cN:
            x=M[0]
            y=M[1]
    rows = cur.execute("SELECT name, amount,dateIn,freeDispense FROM pills where containerx="+str(x)+" and containery="+str(y))
    result = cur.fetchall()
    
    
    dContButton = ttk.Button(fcont,text = "Done",style='TButton',command=lambda:raise_frame(fpills))
    dContButton.place_forget()

    
    removePillsButton.place_forget()
    if result:
        pillNameT = result[0][0]
        pillAmountT = str(result[0][1])
        pillDateT = result[0][2]       
        pillNT.configure(text="Pills: " + pillNameT)
        pillAT.configure(text="Amount: "+ pillAmountT)
        pillDT.configure(text="Added on: "+ pillDateT)
        removePillsButton.configure(command=lambda:removePills(pillNameT))
        removePillsButton.place(relx= 0.6, y=400,anchor=CENTER)
    else:
        pillNP.configure(text="No Pills in this Container")
        removePillsButton.place_forget()
    
    if result and result[0][3]==1:
        pillList = []
        pillList.append((pillNameT,1))
        pillFreeD.configure(command=lambda:dispense(pillList,dContButton))
        pillFreeD.place(relx= 0.6, y=450,anchor=CENTER)
    else:
        pillFreeD.place_forget()
    
    raise_frame(fcont)

def removePills(pillName):
    removeUT = ttk.Label(fremoveCP,text="Remove "+pillName+"?",style='TLabel')
    removeUT.place(relx=0.5, y=50,anchor=CENTER)
    RbtnBack = ttk.Button(fremoveCP,text="No",style='TButton',command=lambda:raise_frame(fpills))
    RbtnBack.place(relx=0.3, y=500,anchor=CENTER)
    RbtnBack = ttk.Button(fremoveCP,text="Yes",style='TButton',command=lambda:removeCP(pillName))
    RbtnBack.place(relx=0.3, y=500,anchor=CENTER)

def removeCP(pillName):
    cur.execute("DELETE FROM pills WHERE pillName = '"+pillName+"';")    
    raise_frame(fpills)

def contFrameRaise(pillNT,pillAT,pillDT,pillNP):
    pillNT.configure(text="")
    pillAT.configure(text="")
    pillDT.configure(text="")       
    pillNP.configure(text="")
    raise_frame(fpills)
    
def raise_paframe(x,y):
    THING = ''
    for M in MAPPING:
        if x==M[0] and y==M[1]:
            contNumber = M[2]
    #fpAdd Stuff
    paddT = ttk.Label(fpAdd,text="Pill Name for Container "+ str(contNumber),style='TLabel')
    paddT.grid(row=0,column=4,columnspan=1,pady=5)
    pnameText = Entry(fpAdd,width=15, font=('Helvetica', 30))
    pnameText.grid(row=1,column=4,columnspan=3,sticky=W)
    keyboard(fpAdd,pnameText)
    pCbtn = ttk.Button(fpAdd, text="Cancel", style='TButton',command=lambda:raise_frame(fcont))
    pCbtn.grid(row=5,column=2,pady=5,columnspan=3)
    paddButton = ttk.Button(fpAdd,text = "Next",style='TButton',command=lambda:getValueP(pnameText,x,y,pnameText.get()))
    paddButton.grid(row=5,column=5,pady=5,columnspan=3)
    raise_frame(fpAdd)
    
def raise_paaframe(x,y,PN, pinText):
    #fpAdd1 Stuff
    if pinText.get() =='1234':
        padd1T = ttk.Label(fpAdd1,text="Pill Amount ",style='TLabel')
        padd1T.grid(row=0,column=2,pady=5)
        pAText = Entry(fpAdd1,width=10, font=('Helvetica', 30))
        pAText.grid(row=1,column=2)
        keypad(fpAdd1,pAText)
        Cbtn = ttk.Button(fpAdd1, text="Cancel", style='TButton',command=lambda:raise_frame(fcont))
        Cbtn.grid(row=6,column=1,pady=30)
        addButton = ttk.Button(fpAdd1,text = "Next",style='TButton',command=lambda:freeYN(x,y,PN,pAText.get(),pAText))
        addButton.grid(row=6,column=3,pady=30)
        pinText.delete(0,'end')
        raise_frame(fpAdd1)

def freeYN(x,y,PN,am,pAText):
    raise_frame(ffreeYN)
    fYNText = ttk.Label(ffreeYN,text="Pills to Freely Dispense?",style='TLabel')
    fYNText.place(relx=0.5, y=50,anchor=CENTER)

    yButton = ttk.Button(ffreeYN,text = "Yes",style='TButton',command=lambda:getFinalP(x,y,pn,am,pAText,1))
    yButton.place(relx=0.3, y=300,anchor=CENTER)
    nButton = ttk.Button(ffreeYN,text = "No",style='TButton',command=lambda:getFinalP(x,y,pn,am,pAText,0))
    nButton.place(relx=0.7, y=300,anchor=CENTER)


    
def getFinalP(x,y,pn,pa,pAText,free):
    pAText.delete(0,'end')
    for M in MAPPING:
        if x==M[0] and y==M[1]:
            cNumb = M[2]
    containerT = ttk.Label(fpAddF,text="Please put your "+pn+" into container "+str(cNumb) +".",style='TLabel')
    containerT.place(relx=0.5, y=50,anchor=CENTER)
    Backbtn = ttk.Button(fpAddF, text="Finish", style='TButton',command=lambda:raise_frame(fmain))
    Backbtn.place(relx= 0.5, y=500,anchor=CENTER)
    
    if pa:
        year = str(date.today().year)
        month = str(date.today().month)
        day = str(date.today().day)
        dateN = month+"/"+day+"/"+year
        cur.execute("DELETE FROM pills WHERE containerx="+str(x)+" and containery="+str(y)+";")
        cur.execute("INSERT INTO pills (name,amount,dateIn,containerx,containery,freeDispense) VALUES (%s,%s,%s,%s,%s,%s)",
            (pn,pa,dateN,x,y,free)) 
        db.commit()
        raise_frame(fpAddF)
    
def getFinal(fadd4,nameV,dobV,rfidV,genV,careV,nameText,dobText,rfidE,careText):
    raise_frame(fadd4)
    cText = ttk.Label(fadd4,text="Confirm Information",style='TLabel')
    cText.place(relx=0.5, y=50,anchor=CENTER)

    name = "Name: " + nameV
    dob = "Date of Birth: " +str(dobV)
    gen = "Gender: " +genV
    car = "Caretaker: " + careV

    allI = [amo.get(),amp.get(),asp.get(),che.get(),erb.get(),ibu.get(),ins.get(),pen.get(),teg.get(),oth.get()]

    nT = ttk.Label(fadd4,text=name,style='TLabel')
    nT.place(relx=0.5, y=125,anchor=CENTER)
    dobT = ttk.Label(fadd4,text=dob,style='TLabel')
    dobT.place(relx=0.5, y=175,anchor=CENTER)
    gT = ttk.Label(fadd4,text=gen,style='TLabel')
    gT.place(relx=0.5, y=225,anchor=CENTER)
    cT = ttk.Label(fadd4,text=car,style='TLabel')
    cT.place(relx=0.5, y=275,anchor=CENTER)

    Cbtn1 = ttk.Button(fadd4, text="Cancel", style='TButton',command=lambda:raise_frame(fsettings))
    Cbtn1.place(relx= 0.2, y=400,anchor=CENTER)
    finButton1 = ttk.Button(fadd4,text = "Finish",style='TButton',command=lambda:insertStuff(nameV,dobV,genV,rfidV,careV,allI,
                                                                                             nameText,dobText,rfidE,careText))
    finButton1.place(relx= 0.8, y=400,anchor=CENTER)

    

def insertStuff(nameI,dobI,genI,rfidI,careI,allI,nameText,dobText,rfidE,careText):        
    
    nameText.delete(0,'end')
    dobText.delete(0,'end')
    rfidE.delete(0,'end')
    careText.delete(0,'end')

    
    raise_frame(fChan)
    cText = ttk.Label(fChan,text="Scan",style='TLabel')
    cText.place(relx=0.5, y=50,anchor=CENTER)
    channels = ["Of07kjLIFUO9f2qt","JtaddyKXml0tkMQ2","dfGSAlUt88MzWxxO","L4I3MMiol1cvu42z",
                "Pdmd9g9O3fPHsWCx","qBrkwRvqxwPnZW59"]
    uu = cur.execute("SELECT channel FROM users")
    ad=cur.fetchall()
    usedChannels = []
    for i in ad:
        usedChannels.append(i[0])
    
    scannyT = ttk.Label(fChan,style='TLabel',text= "Please scan the below QR")
    scannyT.place(relx=0.5, y=100,anchor=CENTER)

    availChannels = []
    for c in channels:
        if c not in usedChannels:
            availChannels.append(c)
    if len(availChannels)>0:
        
        addPC = Image.open(availChannels[0]+".jpg")
        imageS = addPC.resize((300,300),Image.ANTIALIAS)
        QRI = ImageTk.PhotoImage(imageS)

        QRB = ttk.Button(fChan, style='TButton',image=QRI)
        QRB.image= QRI
        QRB.place(relx= 0.5,y =125,anchor =CENTER)
        cur.execute("INSERT INTO users (name,RFID,DOB,Gender,caretaker,amoxAll,ampiAll,aspiAll,cheAll,erbAll,ibupAll,insAll,penAll,tegAll,othAll,channel) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (nameI,rfidI,dobI,genI,careI,allI[0],allI[1],allI[2],allI[3],allI[4],allI[5],allI[6],allI[7],allI[8],allI[9],availChannels[0])) #DayOfWeekHourMinute
        db.commit()
        
    else:
        scannyT.configure(text="No more users available")

    Cbtn3 = ttk.Button(fChan, text="Done", style='TButton',command=lambda:raise_frame(fsettings))
    Cbtn3.place(relx= 0.5, y=500,anchor=CENTER)



def pillTime0(user,time,pillGet,bU):
    raise_frame(pillTime0)
    pUserT = ttk.Label(fPillTime0,style='TLabel',text= "Pills for User: "+user)
    bU.place_forget()
    pUserT.place(relx=0.5, y=50,anchor=CENTER)
    rows = cur.execute("SELECT pillName, number,freq FROM pilltimes where user = '"+user+"' and timeNext = '"+time+"'")
    result = cur.fetchall()
    yl=150
    i=0
    pillList = []
    for row in result:
        pillList.append((row[0],row[1],row[2]))
        pillTxt = str(row[1])+"x "+row[0]
        pillL = ttk.Label(fPillTime0,text=pillTxt,style='TLabel')
        pillL.place(relx=0.5, y=yl,anchor=CENTER)
        yl=yl+60
        i=i+1

    CButton = ttk.Button(fPillTime0,text = "Confirm",style='TButton',command=lambda:pillTime1(user,time,pillList,pillGet))
    CButton.place(relx= 0.8, y=500,anchor=CENTER)

def pillTime1(user,time,pillList,pillGet):
    raise_frame(fPillTime1)
    addI = Image.open("rfidScan.png")
    imageS = addI.resize((150,150),Image.ANTIALIAS)
    rScanImage = ImageTk.PhotoImage(imageS)
    #fPillTime1 Stuff
    #rows = cur.execute("SELECT RFID FROM users where user = '"+user+"'")
    #result = cur.fetchall()
    #RFIDValue = result[0][0]
    rfiT = ttk.Label(fPillTime1,text="Scan Your RFID",style='TLabel')
    rfiT.place(relx=0.5, y=50,anchor=CENTER)

    rPText = Entry(fPillTime1,width=10, font=('Helvetica', 30))
    rPText.place(relx=0.5, y=350,anchor=CENTER)
    
    RbtnBack = ttk.Button(fremove,text="Return",style='TButton',command=lambda:raise_frame(fsettings))
    RbtnBack.place(relx=0.2, y=350,anchor=CENTER)
    CPButton1 = ttk.Button(fPillTime1,text = "Next",style='TButton',command=lambda:pillTime2(user,time,pillList,pillGet))
    #CPButton1.place(relx= 0.5, y=350,anchor=CENTER)
    scanPB = ttk.Button(fPillTime1,text = "Press to start scan",style='TButton',image=rScanImage,compound="top",command=lambda:rfidScan(rfiT ,rPText,True,user,CPButton1))
    scanPB.place(relx=0.5, y=190,anchor=CENTER)


def pillTime2(user,time,pillList,pillGet):
    raise_frame(fPillTime2)
    #fPillTime2 Stuff
    d1t = ttk.Label(fPillTime2,text="Dispensing",style='TLabel')
    d1t.place(relx=0.5, y=50,anchor=CENTER)
    motornum=0

    for pill in pillList:
        freq = pill[2]
        pillN = pill[0]
        nextTime = datetime.strptime(time,"%m/%d/%y %H:%M") + timedelta(hours=freq)
        nextTime = nextTime.strftime('%m/%d/%y %H:%M')
        newtime = datetime.strptime(time,"%m/%d/%y %H:%M").strftime('%m/%d/%y %H:%M')
        cur.execute("UPDATE pilltimes SET timeNext ='"+nextTime+"' AND lastMiss=0 AND lastRecieve = 1 WHERE user = '"+user+"' AND pillName = '"+pillN+"' AND timeNext='"+str(newtime)+"';")
        db.commit()
    
    dButton = ttk.Button(fPillTime2,text = "Done",style='TButton',command=lambda:raise_frame(fmain))
    #dButton.place(relx= 0.5, y=300,anchor=CENTER)
    rows = cur.execute("SELECT user FROM pilltimes WHERE timeNext = '"+time+"'")
    rTime = cur.fetchall()
    dButton.place_forget()
    if len(rTime)>0:
        pillGet.place_forget()
    
    Dispbtn = ttk.Button(fPillTime2, text="Press to Dispense!", style='TButton',command=lambda:dispense(pillList,dButton))
    Dispbtn.place(relx= 0.5, y=150,anchor=CENTER)

def removeTime():
    raise_frame(fremove)
    removeUT = ttk.Label(fremove,text="Select Scheduled Time",style='TLabel')
    removeUT.place(relx=0.5, y=50,anchor=CENTER)
    RbtnBack = ttk.Button(fremove,text="Return",style='TButton',command=lambda:raise_frame(fsettings))
    RbtnBack.place(relx=0.8, y=500,anchor=CENTER)
    rows = cur.execute("SELECT name, pillNBam, DOB FROM users")
    result = cur.fetchall()
    yl=100
    i=0
    for row in result:
        usrTxt = row[0]+", "+row[1]+", "+str(row[2])[:4]
        bU = ttk.Button(fremove, text=usrTxt, style='TButton',command=lambda row=row:removeConf(frame,row[0]))
        bU.place(relx= 0.5, y=yl,anchor=CENTER)
        yl=yl+30
        i=i+1



root = Tk()
root.wm_attributes('-type','splash')

mainW=1300
mainH=775
fmain = Frame(root,width=mainW,height=mainH)
fsettings = Frame(root,width=mainW,height=mainH)
fadd = Frame(root,width=mainW,height=mainH)
fadd1 = Frame(root,width=mainW,height=mainH)
fabout = Frame(root,width=mainW,height=mainH)
fadd2 = Frame(root,width=mainW,height=mainH)
fadd3 = Frame(root,width=mainW,height=mainH)
fadd35 = Frame(root,width=mainW,height=mainH)
fadd4 = Frame(root,width=mainW,height=mainH)
ftime = Frame(root,width=mainW,height=mainH)
fusers = Frame(root,width=mainW,height=mainH)
fPillTime = Frame(root,width=mainW,height=mainH)
fPillTime1 = Frame(root,width=mainW,height=mainH)
fPillTime2 = Frame(root,width=mainW,height=mainH)
ftest = Frame(root,width=mainW,height=mainH)
fsound = Frame(root,width=mainW,height=mainH)
ftext = Frame(root,width=mainW,height=mainH)
fCarePin = Frame(root,width=mainW,height=mainH)
flanguage = Frame(root,width=mainW,height=mainH)
fpills = Frame(root,width=mainW,height=mainH)
fcont= Frame(root,width=mainW,height=mainH)
faddg= Frame(root,width=mainW,height=mainH)
fRTimes=Frame(root,width=mainW,height=mainH)
fremove =Frame(root,width=mainW,height=mainH)
fremoveC =Frame(root,width=mainW,height=mainH)
fCare= Frame(root,width=mainW,height=mainH)
fpAdd =Frame(root,width=mainW,height=mainH)
fpAdd1= Frame(root,width=mainW,height=mainH)
faddC = Frame(root,width=mainW,height=mainH)
fpAddF= Frame(root,width=mainW,height=mainH)
fSetTimes= Frame(root,width=mainW,height=mainH)
fSetTimes1= Frame(root,width=mainW,height=mainH)
fSetTimes2= Frame(root,width=mainW,height=mainH)
fSetTimes3= Frame(root,width=mainW,height=mainH)
fSetTimes4= Frame(root,width=mainW,height=mainH)
fSetTimes5= Frame(root,width=mainW,height=mainH)
fSetTimes6= Frame(root,width=mainW,height=mainH)
fSetTimes7= Frame(root,width=mainW,height=mainH)
fpComplete = Frame(root,width=mainW,height=mainH)
fSRTimes = Frame(root,width=mainW,height=mainH)
ffreeYN = Frame(root,width=mainW,height=mainH)
fChan = Frame(root,width=mainW,height=mainH)
fPillTime0= Frame(root,width=mainW,height=mainH)
fremoveCP = Frame(root,width=mainW,height=mainH)

#STYLES
s = ttk.Style()
s.configure('TButton',foreground="white",activebackground="#4286f4",background="#4286f4",font='helvetica 25',relief='flat')
d = ttk.Style()
d.configure('TLabel', background="#595959",foreground="white",font='helvetica 25')


#Create Frames
for frame in (fmain, fsettings, fPillTime1,fadd, faddC, fadd1,fadd2,fadd3, fadd35, fadd4, ftime, ftest,fsound, fPillTime,
              fpills, fpAddF,fCare, fPillTime2,fabout,flanguage,ftext,faddg,fusers,fpAdd,fpAdd1,fcont,fremove,
              fSetTimes,fSetTimes1,fSetTimes2,fSetTimes3,fSetTimes4,fSetTimes5,fSetTimes6,fSetTimes7,
              fSRTimes,fRTimes,fremoveC,fCarePin,fpComplete,fChan,ffreeYN,fPillTime0,fremoveCP):
    frame.grid(row=0,column=0,sticky='news')
    frame.configure(bg="#595959")
    frame.configure(cursor="none")
    #frame.pack_propagate(0)
fsettings.columnconfigure(0,weight=1)
fsettings.columnconfigure(1,weight=1)
fsettings.columnconfigure(2,weight=1)

for col in range(0,10):
    
    fadd1.columnconfigure(col,weight=1)
    fCare.columnconfigure(col,weight=1)
    fpAdd.columnconfigure(col,weight=1)

for col in range(0,5):
    fSetTimes.columnconfigure(col,weight=1)
    fSetTimes5.columnconfigure(col,weight=1)
    fSetTimes7.columnconfigure(col,weight=1)
    fadd2.columnconfigure(col,weight=1)
    fpAdd1.columnconfigure(col,weight=1)
    fCarePin.columnconfigure(col,weight=1)

root.title("Test")
root.geometry('1300x775')
bigfont = font.Font(family="Helvetica",size=20)
root.option_add("*TCombobox*Listbox*Font",bigfont)

#fpills stuff
fpills.columnconfigure(0,weight=1)
fpills.columnconfigure(1,weight=1)
fpills.columnconfigure(2,weight=1)

imW = int(mainW/8)
imH = int(mainH/5)
contI = Image.open("cont.png")
imageA = contI.resize((imW,imH),Image.ANTIALIAS)
contImage = ImageTk.PhotoImage(imageA)

pillT = ttk.Label(fpills,text="All Pills",style='TLabel')
pillT.grid(row=0,column=1)
removePillsButton = ttk.Button(fcont,text = "Remove",style='TButton')

pbtn = [[0 for x in range(5)] for x in range(5)]
pillFreeD = ttk.Button(fcont, text="Free Dispense", style='TButton')
pillFreeD.place_forget()      
for x in range(1,4):
    for y in range(1,4):
        for M in MAPPING:
            if x==M[0] and y==M[1]:
                cN=M[2]
                pbtn[x][y] = ttk.Button(fpills, text="Container "+str(cN),image=contImage,compound="top",
                                        command=lambda cN=cN: pillFrames(cN,pillFreeD,removePillsButton),style='TButton')
                pbtn[x][y].grid(row=y,column=x-1,pady=2)

  
Pbtn = ttk.Button(fpills, text="Cancel", style='TButton',command=lambda:raise_frame(fmain))
Pbtn.grid(row=4,column=1,pady=10)


#fmain stuff

addI = Image.open("settings.png")
imageS = addI.resize((150,150),Image.ANTIALIAS)
addImage = ImageTk.PhotoImage(imageS)

pillsI = Image.open("pills.png")
imageS = pillsI.resize((150,150),Image.ANTIALIAS)
pillsImage = ImageTk.PhotoImage(imageS)

pillI = Image.open("pill.png")
imageS = pillI.resize((150,150),Image.ANTIALIAS)
pillImage = ImageTk.PhotoImage(imageS)

mainT = Label(fmain,text="iPothecary",font=('Helvetica', 60),bg="#595959",fg="white")
mainT.place(relx=0.5, y=75,anchor=CENTER)



time1 = ''
clock = Label(fmain, font=('Helvetica', 50),bg="#595959",fg="white")
clock.place(relx=0.5, y=200,anchor=CENTER)
noticeT = ttk.Label(fmain,style='TLabel')
noticeT.place(relx=0.5, y=150,anchor=CENTER)

pillB = ttk.Button(fmain, style='TButton',text="Pills",image=pillImage,compound="top",command=lambda:raise_frame(fpills))
pillB.place(relx= 0.2,y =400, anchor =CENTER)
newB = ttk.Button(fmain, style='TButton',text="Settings",image=addImage,compound="top",command=lambda:raise_frame(fsettings))
newB.place(relx= 0.8,y =400,anchor =CENTER)

#fSetTimes stuff
#setT = ttk.Label(fSetTimes,text="Set a pill time",style='TLabel')
#setT.place(relx=0.5, y=50,anchor=CENTER)

#pin for caretaker
#fSetTimes stuff
setT = ttk.Label(fSetTimes,text="Input your caretaker pin",style='TLabel')
setT.grid(row=0,column=2,pady=5)
pinText = Entry(fSetTimes,width=10, show="*",font=('Helvetica', 30))
pinText.grid(row=1,column=2)

keypad(fSetTimes,pinText)

Cbtn = ttk.Button(fSetTimes, text="Cancel", style='TButton',command=lambda:raise_frame(fsettings))
Cbtn.grid(row=6,column=1,pady=30)
addButton = ttk.Button(fSetTimes,text = "Next",style='TButton',command=lambda:selectUser(fSetTimes1,pinText,fSetTimes2))
addButton.grid(row=6,column=3,pady=30)

#fSetTimes4 stuff
#pill name
#number of pills 


#time to take


#Frequency

#fpComplete stuff
doneT = ttk.Label(fpComplete,text="Added!",style='TLabel')
doneT.place(relx=0.5, y=50,anchor=CENTER)

FButton = ttk.Button(fpComplete,text = "Finish",style='TButton',command=lambda:raise_frame(fsettings))
FButton.place(relx= 0.5, y=300,anchor=CENTER)

#fcont Stuff
containerT = ttk.Label(fcont,text="Container ",style='TLabel')
containerT.place(relx=0.5, y=50,anchor=CENTER)

pillNT = ttk.Label(fcont,style='TLabel')
pillNT.place(relx=0.6, y=170,anchor=CENTER)
pillAT = ttk.Label(fcont,style='TLabel')
pillAT.place(relx=0.6, y=220,anchor=CENTER)
pillDT = ttk.Label(fcont,style='TLabel')
pillDT.place(relx=0.6, y=270,anchor=CENTER)        

pillNP = ttk.Label(fcont,style='TLabel')
pillNP.place(relx=0.6, y=170,anchor=CENTER)

Backbtn = ttk.Button(fcont, text="Back", style='TButton',command=lambda:contFrameRaise(pillNT,pillAT,pillDT,pillNP))
Backbtn.place(relx= 0.5, y=550,anchor=CENTER)




NAME = ""
DOB = 0
GENDER = ""
CARE = ""
#fusers
la = ttk.Label(fusers, text= "Users",style='TLabel')
la.place(relx=0.5, y=50,anchor=CENTER)

btnAdd = ttk.Button(fusers,text="Add User",style='TButton',command=lambda:raise_frame(fadd1))
btnAdd.place(relx=0.5, y=150,anchor=CENTER)
btnRemove = ttk.Button(fusers,text="Remove User",style='TButton',command=lambda:remove(fremove))
btnRemove.place(relx=0.5, y=250,anchor=CENTER)
btnBack = ttk.Button(fusers,text="Return",style='TButton',command=lambda:raise_frame(fsettings))
btnBack.place(relx=0.8, y=450,anchor=CENTER)

#fadd1 stuff
addT = ttk.Label(fadd1,text="         Name",style='TLabel')
addT.grid(row=0,column=4,columnspan=1,pady=5)

nameText = Entry(fadd1,width=15, font=('Helvetica', 30))
nameText.grid(row=1,column=4,columnspan=3,sticky=W)

keyboard(fadd1,nameText)
Cbtn = ttk.Button(fadd1, text="Cancel", style='TButton',command=lambda:raise_frame(fsettings))
Cbtn.grid(row=5,column=2,pady=5,columnspan=3)
addButton = ttk.Button(fadd1,text = "Next",style='TButton',command=lambda:getValue(fadd2,nameText,NAME))
addButton.grid(row=5,column=5,pady=5,columnspan=3)


#fadd2 stuff
addT = ttk.Label(fadd2,text="Year of Birth",style='TLabel')
addT.grid(row=0,column=2,pady=5)
dobText = Entry(fadd2,width=10, font=('Helvetica', 30))
dobText.grid(row=1,column=2)

keypad(fadd2,dobText)

Cbtn = ttk.Button(fadd2, text="Cancel", style='TButton',command=lambda:raise_frame(fsettings))
Cbtn.grid(row=6,column=1,pady=30)
addButton = ttk.Button(fadd2,text = "Next",style='TButton',command=lambda:getValue(faddg,dobText,DOB))
addButton.grid(row=6,column=3,pady=30)

#fadd35 stuff
addT = ttk.Label(fadd35,text="Allergies?",style='TLabel')
addT.place(relx=0.5, y=50,anchor=CENTER)
amo=IntVar()
amp=IntVar()
asp=IntVar()
che=IntVar()
erb=IntVar()
ibu=IntVar()
ins=IntVar()
pen = IntVar()
teg=IntVar()
oth=IntVar()

Checkbutton(fadd35,text="Amoxicillin",variable=amo,font=('Helvetica', 25)).place(relx=0.2, y=100,anchor=CENTER)
Checkbutton(fadd35,text="Ampicillin",variable=amp,font=('Helvetica', 25)).place(relx=0.2, y=150,anchor=CENTER)
Checkbutton(fadd35,text="Aspirin",variable=asp,font=('Helvetica', 25)).place(relx=0.2, y=200,anchor=CENTER)
Checkbutton(fadd35,text="Chemotherapy",variable=che,font=('Helvetica', 25)).place(relx=0.2, y=250,anchor=CENTER)
Checkbutton(fadd35,text="Erbitux",variable=erb,font=('Helvetica', 25)).place(relx=0.2, y=300,anchor=CENTER)

Checkbutton(fadd35,text="Ibuprofen",variable=ibu,font=('Helvetica', 25)).place(relx=0.8, y=100,anchor=CENTER)
Checkbutton(fadd35,text="Insulin",variable=ins,font=('Helvetica', 25)).place(relx=0.8, y=150,anchor=CENTER)
Checkbutton(fadd35,text="Penicillin",variable=pen,font=('Helvetica', 25)).place(relx=0.8, y=200,anchor=CENTER)
Checkbutton(fadd35,text="Tegretol",variable=teg,font=('Helvetica', 25)).place(relx=0.8, y=250,anchor=CENTER)
Checkbutton(fadd35,text="Other",variable=oth,font=('Helvetica', 25)).place(relx=0.8, y=300,anchor=CENTER)

addButton = ttk.Button(fadd35,text = "Next",style='TButton',command=lambda:raise_frame(fadd3))
addButton.place(relx=0.5, y=400,anchor=CENTER)

#fadd3 stuff
addI = Image.open("rfidScan.png")
imageS = addI.resize((150,150),Image.ANTIALIAS)
rScanImage = ImageTk.PhotoImage(imageS)

addI = Image.open("rfidSucc.png")
imageS = addI.resize((150,150),Image.ANTIALIAS)
rSuccImage = ImageTk.PhotoImage(imageS)


RFIDT = ttk.Label(fadd3,text="Please scan your RFID Chip now!",style='TLabel')
RFIDT.place(relx=0.5, y=50,anchor=CENTER)

succT = ttk.Label(fadd3,text="To scan, place your chip on the scanner below.",style='TLabel')
succT.place(relx=0.5, y=460,anchor=CENTER)

rfidE = Entry(fadd3,width=15, show="*",font=('Helvetica', 30))
rfidE.place(relx=0.5, y=400,anchor=CENTER)


finButton = ttk.Button(fadd3,text = "Finish",style='TButton',command=lambda:getFinal(fadd4,nameText.get(),
                                                                                     dobText.get(),rfidE.get(),
                                                                                     comboG.get(),careText.get(),
                                                                                     nameText,dobText,rfidE,careText))
finButton.place(relx= 0.8, y=550,anchor=CENTER)
finButton.place_forget()

scanB = ttk.Button(fadd3,text = "Press to start scan",style='TButton',image=rScanImage,compound="top",command=lambda:rfidScan(succT,rfidE,False,nameText.get(),None))
scanB.place(relx=0.5, y=190,anchor=CENTER)

#faddg stuff

addT = ttk.Label(faddg,text="Gender",style='TLabel')
addT.place(relx=0.5, y=50,anchor=CENTER)

comboG = ttk.Combobox(faddg, values = ["Male","Female","No Specify"],font=('Helvetica',40),width=10)
comboG.place(relx=0.5, y=150,anchor=CENTER)

addButton3 = ttk.Button(faddg,text = "Next",style='TButton',command=lambda:getValue(fCare,comboG,GENDER))
addButton3.place(relx=0.5, y=400,anchor=CENTER)


#fCare stuff
cText = ttk.Label(fCare,text="   Caretaker",style='TLabel')
cText.grid(row=0,column=4,columnspan=2,pady=5)

careText = Entry(fCare,width=15, font=('Helvetica', 30))
careText.grid(row=1,column=4,columnspan=3,sticky=W)

keyboard(fCare,careText)


addButton4 = ttk.Button(fCare,text = "Next",style='TButton',command=lambda:getValue(fadd35,careText,CARE))
addButton4.grid(row=5,column=7,pady=20,columnspan=3)

#fadd4 stuff

#fsettings stuff
l = ttk.Label(fsettings, text= "Settings",style='TLabel')
l.grid(row=0,column=1,pady=10)

imW = int(mainW/8)
imH = int(mainH/5)

timeI = Image.open("clock.png")
imageT = timeI.resize((imW,imH),Image.ANTIALIAS)
timeImage = ImageTk.PhotoImage(imageT)

aboutI = Image.open("about.png")
imageA = aboutI.resize((imW,imH),Image.ANTIALIAS)
aboutImage = ImageTk.PhotoImage(imageA)

langI = Image.open("changeT.png")
imageL = langI.resize((imW,imH),Image.ANTIALIAS)
langImage = ImageTk.PhotoImage(imageL)

soundI = Image.open("sound.png")
imageS = soundI.resize((imW,imH),Image.ANTIALIAS)
soundImage = ImageTk.PhotoImage(imageS)

usersI = Image.open("users.png")
imageU = usersI.resize((imW,imH),Image.ANTIALIAS)
usersImage = ImageTk.PhotoImage(imageU)

textI = Image.open("text.png")
imageT = textI.resize((imW,imH),Image.ANTIALIAS)
textImage = ImageTk.PhotoImage(imageT)

btn1 = ttk.Button(fsettings, text="Set Time",image=timeImage,compound="top",style='TButton',command=lambda:raise_frame(ftime))
btn1.grid(row=1,column=0,pady=5)
btn2 = ttk.Button(fsettings, text="Sound",image=soundImage,compound="top",style='TButton',command=lambda:raise_frame(fsound))
btn2.grid(row=1,column=1,pady=5)
btn3 = ttk.Button(fsettings, text="Text",image=textImage,compound="top",style='TButton',command=lambda:raise_frame(ftext))
btn3.grid(row=1,column=2,pady=5)
btn4 = ttk.Button(fsettings, text="Pill Times",image=langImage,compound="top",style='TButton',command=lambda:raise_frame(fSetTimes))
btn4.grid(row=2,column=0,pady=5)
btn5 = ttk.Button(fsettings, text="Users", image=usersImage,compound="top",style='TButton',command=lambda:raise_frame(fusers))
btn5.grid(row=2,column=1,pady=5)
btn6 = ttk.Button(fsettings, text="About", image=aboutImage,compound="top",style='TButton',command=lambda:raise_frame(fabout))
btn6.grid(row=2,column=2,pady=5)
btn7 = ttk.Button(fsettings,text="Return", style='TButton',command=lambda:raise_frame(fmain))
btn7.grid(row=3,column=1,pady=30)


#fabout stuff
la = ttk.Label(fabout, text= "About",style='TLabel')
la.place(relx=0.5, y=50,anchor=CENTER)

la = ttk.Label(fabout, text= "iPothecary",style='TLabel')
la.place(relx=0.5, y=100,anchor=CENTER)
la1 = ttk.Label(fabout, text= "Created By:",style='TLabel')
la1.place(relx=0.5, y=200,anchor=CENTER)
la2 = ttk.Label(fabout, text= "Christian Puerta, Cory Ye",style='TLabel')
la2.place(relx=0.5, y=250,anchor=CENTER)
la3 = ttk.Label(fabout, text= "Elijah Shultz and Yeil Choi",style='TLabel')
la3.place(relx=0.5, y=300,anchor=CENTER)
la3 = ttk.Label(fabout, text= "For Senior Design 2018-2019",style='TLabel')
la3.place(relx=0.5, y=350,anchor=CENTER)
btnBack = ttk.Button(fabout,text="Return",style='TButton',command=lambda:raise_frame(fsettings))
btnBack.place(relx=0.8, y=450,anchor=CENTER)


#ftime stuff
comboH = ttk.Combobox(ftime, values = ["Hawaii","Alaska","Pacific","Mountain","Central","Eastern"],font=('Helvetica',40),width=8)
comboH.place(relx=0.5, y=120,anchor=CENTER)
comboH.current(5)
lt = ttk.Label(ftime, text= "Set Time",style='TLabel')
lt.place(relx=0.5, y=50,anchor=CENTER)

btnBack = ttk.Button(ftime,text="Return",style='TButton',command=lambda:raise_frame(fsettings))
btnBack.place(relx=0.5, y=250,anchor=CENTER)
#need an alert for the time being changed

#fsound stuff
ls = ttk.Label(fsound, text= "Sound",style='TLabel')
ls.place(relx= 0.5, y=50,anchor=CENTER)
btnBackS = ttk.Button(fsound,text="Return",style='TButton',command=lambda:raise_frame(fsettings))
btnBackS.place(relx= 0.5, y=250,anchor=CENTER)
sScale = Scale(fsound,from_=0, to=100,orient=HORIZONTAL,width = 30,bg="white")
sScale.place(relx=0.5,y=150,anchor=CENTER)
sScale.bind("<ButtonRelease-1>",playSound)


#ftext stuff
lt = ttk.Label(ftext, text= "Text",style='TLabel')
lt.place(relx= 0.5, y=50,anchor=CENTER)

btnSmall= ttk.Button(ftext,text="Small",style='TButton',command=lambda:cText(18))
btnSmall.place(relx= 0.5, y=150,anchor=CENTER)
btnMed= ttk.Button(ftext,text="Normal",style='TButton',command=lambda:cText(25))
btnMed.place(relx= 0.5, y=225,anchor=CENTER)
btnLarge= ttk.Button(ftext,text="Large",style='TButton',command=lambda:cText(32))
btnLarge.place(relx= 0.5, y=300,anchor=CENTER)

btnBackS = ttk.Button(ftext,text="Return",style='TButton',command=lambda:raise_frame(fsettings))
btnBackS.place(relx= 0.5, y=400,anchor=CENTER)

#flanguage stuff
ll = ttk.Label(flanguage, text= "Language",style='TLabel')
ll.place(relx= 0.5, y=50,anchor=CENTER)
btnBackS = ttk.Button(flanguage,text="return",style='TButton',command=lambda:raise_frame(fsettings))
btnBackS.place(relx= 0.5, y=350,anchor=CENTER)

def func(x):
        d = datetime.strptime(x[1],"%m/%d/%y %H:%M")
        bd = str(time.strftime('%m/%d/%y %H:%M'))
        bdE = datetime.strptime(bd,"%m/%d/%y %H:%M")
        delta = d - bdE if d>bdE else timedelta.max
        return delta

def tick():
    global time1
    # get the current local time from the PC
    os.environ['TZ'] = "US/"+comboH.get()
    time.tzset()
    time2 = time.strftime('%m/%d/%y %H:%M:%S')
    year = str(date.today().year)
    month = str(date.today().month)
    day = str(date.today().day)
    #print (time2)
    
    # if time string has changed, update it
    if time2 != time1:
        time1 = time2
        clock.config(text=time2)
    # calls itself every 200 milliseconds
    # to update the time display as needed
    # could use >200 ms, but display gets jerky
    
    rows = cur.execute("SELECT * FROM pilltimes")
    result = cur.fetchall()
    tList = []

    db.commit()

    #checks which pilltime is closest to now
    if result:
        for r in result:
            tList.append((r[0],r[5],r[6]))
            nextY = sorted(tList,key=func)
            nextPilltime = nextY[0][1]
            nextName = nextY[0][0]
            prevPilltime = nextY[-1][1]
            prevName = nextY[-1][0]
            prevFreq = nextY[-1][2]
        
    else:
        nextPilltime = ""
        nextName = ""

    rows = cur.execute("SELECT user FROM pilltimes WHERE timeNext = '"+nextPilltime+"'")
    usersT = cur.fetchall()
    puList = []
    for user in usersT:
        puList.append(user[0])
    #print(noticeT.get())
    #print("Next Pilltime for "+nextName+" at "+nextPilltime)
    noticeT.configure(text="Next Pilltime for "+str(puList).strip("[]\'")+" at "+nextPilltime)
    nextD = str(time.strftime('%m/%d/%y %H:%M:%S'))
    nextPST = datetime.strptime(nextPilltime,'%m/%d/%y %H:%M')
    userN=nextName
    userPt=nextPilltime
    pillGet = Button(fmain,text="Prescription: "+userN,image=pillsImage,compound="top")
    pillGet.configure(bg = "#d12121",)
    pillGet.place_forget()
    
    missPST = datetime.strptime(prevPilltime,'%m/%d/%y %H:%M')
    
    
    #pillGet.place(relx= 0.5,y=325, anchor =CENTER)

    #print(datetime.strptime(nextPilltime,"%m/%d/%y %H:%M") -timedelta(seconds=1))
    #print(datetime.strptime(nextD,"%m/%d/%y %H:%M:%S"))
    
    if datetime.strptime(nextPilltime,"%m/%d/%y %H:%M") -timedelta(seconds=1)== datetime.strptime(nextD,"%m/%d/%y %H:%M:%S"):
        pillGet.configure(bg = "#d12121",font=('Helvetica',40))
        pillGet.configure(command=lambda:pillTime(puList,userPt,pillGet))
        pillGet.place(relx= 0.5,y=350, anchor =CENTER)
        for ubC in puList:
            rows = cur.execute("SELECT channel FROM users where name='"+ubC+"';")
            channelR = cur.fetchall()
            db.commit()
            if channelR:
                channel = channelR[0][0]
                command = "curl https://notify.run/"+channel+" -d 'iPothecary: Its your Pill Time!'"
                p = subprocess.Popen(command,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                out,err = p.communicate()

        yl=150
        i=0
        for user in userList:
            usrTxt = user
            bU[i] = ttk.Button(fPillTime, text=usrTxt, style='TButton',command=lambda user=user:pillTime0(user,time,pillGet,bU))
            bU[i].place(relx= 0.5, y=yl,anchor=CENTER)
            yl=yl+70
            i=i+1
        
    missTime = missPST + timedelta(minutes=5)
    missTime = missTime.strftime('%m/%d/%y %H:%M')
    nextMissTime = missPST + timedelta(hours=prevFreq)
    nextMissTime = nextMissTime.strftime('%m/%d/%y %H:%M')

    if nextD == missTime:
        miss = 1
        fmain.configure(bg="#595959")
        d.configure('TLabel',background="#595959")
        mainT.configure(bg="#595959")
        clock.configure(bg="#595959")
        noticeT.config(text="")
        pillGet.place_forget()
        cur.execute("UPDATE pilltimes SET lastMiss=1 and lastRecieve = 0 and timeNext='"+nextMissTime+"'WHERE timeNext = '"+prevPilltime+"';")
        db.commit()
        rows = cur.execute("SELECT channel FROM users where name='"+prevName+"';")
        channelR = cur.fetchall()
        db.commit()
        if channelR:
            channel = channelR[0][0]
            command = "curl https://notify.run/"+channel+" -d 'iPothecary: Pill Time missed!'"
            p = subprocess.Popen(command,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            out,err = p.communicate()
        
    clock.after(200, tick)



alarm=0
tick()
raise_frame(fmain)

root.mainloop()
