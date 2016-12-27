
"""
Output

Total per day per city vs max per day?

Time slot average line chart (0 means canceled)

When people 'book'

What if people register but don't show?

Classes by trainer / by day

--

Database  - so just grab the latest always and overwrite unless it's canceled or newfield is ""
Date - stamp - data...
Date - stamp2 - data...

date | timestamp | time | trainer | spots | status |  location | weather? | 

"""

#=====================
#SQL Connection
#=====================

#CREATE TABLE "Pure" (
#	`Date`	TEXT,
#	`Time`	TEXT,
#	`Date_Time_Key`	INTEGER UNIQUE,
#	`Num_Spots`	TEXT,
#	`Total_Spots`	TEXT,
#	`Class_Name`	TEXT,
#	`Teacher`	TEXT,
#	`Location`	TEXT,
#	`Status`	TEXT,
#	`Weather`	TEXT,
#	PRIMARY KEY(Date_Time_Key)
#)


#=====================
#SQL
#=====================
import sqlite3
sqlite_file = 'puredb.sqlite3'
conn = sqlite3.connect(sqlite_file)
c = conn.cursor()

log=open("log.txt",'a')

def insertNewSQL(data):
    #INSERT INTO table_name (column1,column2,column3,...)
    #VALUES (value1,value2,value3,...);
  
    # A) Inserts an ID with a specific value in a second column
    try:
        query="INSERT INTO Pure (Date,Time,Date_Time_Key,Num_Spots,Total_Spots,Class_Name,Teacher,Location,Status) VALUES ({joinedList})".\
            format(joinedList=",".join(data))
        c.execute(query)
    
    except sqlite3.IntegrityError:
        print "SQL Insert Error"
        log.write("SQL Insert Error - "+query)

def updateSQL(data,id):
    try:
        # C) Updates the newly inserted or pre-existing entry      
        query="UPDATE pure SET Num_Spots={sp},Total_Spots={tot},Status={stat} WHERE Date_Time_Key={did}".\
                format(sp=data[0],tot=data[1],stat=data[2],did=id)      
        c.execute(query)
    except:
        print "SQL Update Error"
        log.write("SQL Update Error - "+query)

def checkIDExists(id):
    # 1) Contents of all columns for row that match a certain value in 1 column
    query='SELECT * FROM pure WHERE Date_Time_Key={did}'.format(did=id)
    c.execute(query)
    row = c.fetchall()
    return row

def validateAndInsert(list):
    if len(list) == 9:
        
        id=list[2]
        #check if ID exists
        row = checkIDExists(id) 

        if row is None or row==[]: #doesnt exist
            insertNewSQL(list)  #appending weather

        else:

            if list[3]=="": #spots gone, time passed or canceled, need to keep old ones
                #Num_Spots,Total_Spots,Status
                data=[row[3],row[4],list[-1]]
            else: #insert new spots
                data=[list[3],list[4],list[-1]]

            updateSQL(data,id)

        #if #see if num spot blank

            
    else:   
        print "List invalid"
        

from selenium import webdriver
import time
import string, sys
import csv
from datetime import datetime

#wr=open('output.csv','w')
timestamp=datetime.now()
path_to_chromedriver = r"chromedriver.exe"


#====================================

def createDateID(list):
    #date_object = datetime.strptime('Jun 1 2005  1:33PM', '%b %d %Y %I:%M%p')
    
    datestring = list[0]
    timestring = list[1][1:-1]
    date_object = datetime.strptime(datestring, "%B %d, %Y")  #should be -d
    formateddate = date_object.strftime('%Y%m%d')
    starttime = timestring.split("-")[0]

    if "pm" in starttime:
        starttime=starttime.split(":")
        hour=int(starttime[0])+12
        starttime=str(hour)+":"+starttime[1]
    
    starttime=starttime.replace(":","")

       
    starttime = starttime.split(' ',1)[0]
    if len(starttime)==3:
        starttime="0"+starttime
    newlist=[formateddate,starttime,formateddate.replace("-","")+starttime]
    return newlist


#============================
# Main Extraction
#============================

def mainExtract(url):

    browser = webdriver.Chrome(executable_path = path_to_chromedriver)
    browser.get(url)
    time.sleep(4)         
    daterow=False
    skiplast=True

    try:
        table = browser.find_element_by_class_name('schedule')
        trs = table.find_elements_by_tag_name("tr")
    except:
        print "\nCant Access Site\n"
        log.write("Cant Access Site - "+str(datetime.now()))
        browser.close()
        raise


    for i in range(len(trs)):  
        trClass=''
        try:
            trClass=trs[i].get_attribute("class")
        except:
            pass

        if "schedule_header" in trClass:
            #header - get date
            daterow=True
            data = trs[i].find_elements_by_tag_name("span")
            date = data[1].text
            print "\n===========\n"
            print date

        else:
            if "canceled" in trClass:
                status="canceled"
            else:
                status="open"

            daterow=False
            tds = trs[i].find_elements_by_tag_name("td") 

            list=[]
            list.append(date)

            rowtext=tds[0].text

            if rowtext!="":
                print rowtext

                for id,td in enumerate(tds):
                    #DB
                    #Date,Time,Date_Time_Key,Num_Spots,Total_Spots,Class,Teacher,Location,Status,Weather
                    #Site Table
                    #Time    Availability 	CLASS	INSTRUCTOR	LOCATION
                    line=td.text
                    print line
                
                    if id==1:
                        if "SIGN" in line:
                            #sign up 6 of 25
                            if "aitlist" in line:
                                list.append("'full'")
                                list.append("''")                    
                            else:
                                try:
                                    line = line.split(" ")
                                    list.append(line[2])
                                    list.append(line[-2])
                                except:
                                    print "Number of spots not printed \n"
                                    log.write("Number of spots not printed - "+ url)
                                    raise
                        else:
                            #check if canceled
                            list.append("''")
                            list.append("''")
                
                    else:
                        list.append("'"+line+"'")

                    if id==0: #second colum
                        list=createDateID(list)

                if id==3: #no Location:
                    list.append("''")

                list.append("'"+status+"'")
                #list.append(timestamp.strftime('%b %d %Y %I:%M'))
        
                validateAndInsert(list)
                        
                #wr.write(",".join(list))
                #wr.write("\n
            else:
                print "SkipRow"

        #except:
        #    pass
            #fri november 25, 2016 	CLASS	INSTRUCTOR	LOCATION
            #<span class="hc_date">November 25, 2016</span>
    browser.close()

#==================================


#urlreader

#url="http://purebarre.com/in-carmel/#healcode"
#url2="http://purebarre.com/in-fishers/"

urlfile=open("pureurls.csv",'r')
urlfile.next() #header

for l in urlfile:
    l=l.split(",")
    url=l[0]
    print "\n=================\n"
    print l[1]
    print "\n=================\n"
    mainExtract(url)

conn.commit()
conn.close()
log.write("Success - "+str(datetime.now()))
log.close()
time.sleep(1)
#wr.close()