import PySimpleGUI as sg
import collections
import socket
import pathlib
import hashlib
import datetime
import sys
import time
import platform
import subprocess
import os
import csv
import uuid
import getpass
import urllib.request as req
from fpdf import FPDF
import re

"""
Please edit the logo file in the 'bin' directory
"""

# PDF class
class PDF (FPDF):
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial','I',8)
        self.cell(0,10,'Page '+str(self.page_no())+'/{nb}',0,0,'C')

    def chapterTitle(self,num,label):
        self.set_font('Times','',16)
        self.cell(0,6,'Chapter %d : %s'%(num,label),0,1,'L',0)
        self.ln(4)

    def chapterBody(self,text):
        self.set_font('Times','',12)
        self.multi_cell(0,5,text)
        self.ln()

    def print_chapter(self,num,title,text):
        self.add_page()
        self.chapterTitle(num,title)
        self.chapterBody(text)
        

# Windows Class
class Windows:
    logo = 'bin\\logo.png'
# __init__ function, or also called a "constructor" function for the class "Windows"
    def __init__(self, proxy="", window=None, password='', user_name = "", labName = "",simplegui=sg):
        try:
            with open("bin\\serverIP.csv",'r') as csv_file: # this file contains the ip address of the server so as to send the data
                data = csv.reader(csv_file, delimiter=",")
                for row in data:
                    self.serverIP = row[0]
            self.gui = simplegui
            self.password = password
            self.logo = logo
            self.strength=0
            self.user_name = user_name
            self.labName = labName
            self.progbar = window.FindElement('progress')
            self.window = window
            self.proxy = proxy
            self.progBar(2)
            self.dev_basics = self.win_basic_info()
            self.dev = platform.uname()
            data,_ = subprocess.Popen("echo %USERPROFILE%", stdout=subprocess.PIPE, shell=True).communicate()
            data = data.decode("utf-8").strip()
            self.location = data+"\\AppData\\Local\\"
            dat = datetime.datetime.now()
            to = str(dat)
            date = to[:10]
            full_name,_ = subprocess.Popen('echo %username%', stdout=subprocess.PIPE, shell=True).communicate()
            full_name = full_name.decode('utf-8').strip()
            report_dir = ""
            if os.path.isdir("C:\\Users\\"+full_name): # searching for C:\Users\amit or C:\Users\amit shah
                report_dir = "C:\\Users\\"+full_name+"\\Desktop\\"
            elif os.path.isdir("C:\\Users\\"+full_name.capitalize()): # searching for C:\Users\Amit or C:\Users\Amit Shah
                report_dir = "C:\\Users\\"+fullname+"\\Desktop\\"
            else:
                report_dir = simplegui.PopupGetFolder('No folder such as '+full_name+' found. Please select a directory to save Audit Report to.',title="Error",default_path="",default_extension="",save_as=False,multiple_files=False,keep_on_top=True,initial_folder=None)
            self.data_dic = {}
            sysname = self.dev[1]
            self.progBar(5)
            cmd="bin\\ip.bat" # this bat file recovers IP address of the windows device
            ip, err = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()
            #err = err.decode("utf-8")
            if err != b'':
                ip = "IP_NOT_FOUND"
            self.ip = ip.decode("utf-8").strip().replace('\r\n','')
            self.progBar(7)
            if os.path.isdir(self.location+"ASNAData\\"):
                self.logfile = self.location+"ASNAData\\"+sysname.strip()+"_"+self.ip.strip()+".dat"
            else:
                os.system("mkdir "+self.location+"ASNAData")
                self.logfile = self.location+"ASNAData\\"+sysname.strip()+"_"+self.ip.strip()+".dat"
            self.progBar(10)
            self.file = self.location+"Scores_"+sysname.strip()+"_"+self.ip.strip()+date.strip()+".csv"
            self.pfile = report_dir+"Audit_Report_"+sysname.strip()+"_"+self.ip.strip().replace(" ","")+date.strip()+".pdf"
            self.summaryReport = report_dir+"Summary_Audit_"+sysname.strip()+"_"+self.ip.strip().replace(" ","")+date.strip()+".pdf"
            self.score_sheet = "bin\\Scores.csv"
            frontPageData = f"""Audit Report for {sysname.strip()} on {date.strip()}"""
            text2 = f"User: {self.user_name}"
            text3 = f"Lab: {self.labName}"
            text4 = f"Proxy: {self.proxy}"
            self.pdf = PDF()
            self.pdf.alias_nb_pages()
            self.pdf.add_page()
            #self.pdf.set_title(frontPageData)
            self.front_page(frontPageData,text2,text3,text4)
            self.meaning = {}
            self.data = []
            self.audit_summary = {"IP Address": self.ip,"System Name":sysname,"OS Version": self.dev_basics['osversion'],"Product ID":self.dev_basics['productid'],
                                  "Employee Name": self.user_name,"Lab Name":self.labName, "File":self.summaryReport}
            self.progBar(11)
        except Exception as msg:
            self.gui.Popup("Error occured! Please note the error code and contact your system administrator.\nError Code: GWIN_INIT", keep_on_top=True, title="Error")
            #print(str(msg))
            window.close()

# creates front page of the PDF
    def front_page(self,text1,text2,text3,text4):
        try:
            self.pdf.set_font('Arial', 'B', 20)
            self.pdf.cell(0, 15, text1,0,0,'C')
            self.pdf.ln()
            self.pdf.image(self.logo, 90, 80, 33)
            self.pdf.cell(0, 15, text2, 0, 0,'C')
            self.pdf.ln()
            self.pdf.cell(0, 15, text3, 0, 0,'C')
            self.pdf.ln()
            self.pdf.cell(0, 15, text4, 0, 0,'C')
            self.pdf.ln()
        except Exception as msg:
            self.gui.Popup("Error occured! Please note the error code and contact your system administrator.\nError Code: GWIN_FrPg", keep_on_top=True, title="Error")
            #print(msg)
            window.close()

# Animates the progress bar
    def progBar(self, progress=0):
        try:
            self.progbar.UpdateBar(progress, 100)
        except:
            self.gui.Popup("Error occured! Please note the error code and contact your system administrator.\nError Code: GWIN_PB", keep_on_top=True, title="Error")

# Enters scores in the scores file
    def write(self, text, mode="a"):
        try:
            with open(self.file, mode) as file:
                file.write(text)
        except Exception as msg:
            self.gui.Popup("Error occured! Please note the error code and contact your system administrator.\nError Code: GWIN_WRITE", keep_on_top=True, title="Error")
            #print(str(msg))

# logs of audit for record maintenance
    def logger(self,topic,text=''):
        try:
            with open(self.logfile,'a+') as fobj:
                while '\n' in text:
                    text = text.replace('\n',',').replace(' ','')
                self.data.append(text.replace(':','=').replace('Name','').replace('\r\n','').replace('UDP','').replace('N/A','').replace('  ','').replace('"',''))
                fobj.write(f"{topic}::"+text.replace(':','=').replace('Name','').replace('UDP','').replace('N/A','').replace('  ','').replace('\r\n','').replace('"',''))
            #print(text)
        except Exception as msg:
            self.gui.Popup("Error occured! Please note the error code and contact your system administrator.\nError Code: GWIN_LOG", keep_on_top=True, title="Error")
            #print(str(msg))
            sys.exit()
    
# Combines chapter title and body to create a new page in the PDF file
    def print_chapter(self,num=0,title="",name=""):
        try:
            self.pdf.print_chapter(num,title,name)
        except Exception as msg:
            self.gui.Popup("Error occured! Please note the error code and contact your system administrator.\nError Code: GWIN_PRNTCH", keep_on_top=True, title="Error")
            #print(str(msg))

# Scores and Summary, the last page of the PDF contains the complete summary of the audit
    def comp(self,num): # confusing name to avoid malicious manipulation
        try:
            title = "Score & Summary"
            f_ans = "Description: Your scores according to the audit are as follows:\n\n"
            sheetDict = {}
            mock = ""
            max_score = 0
            total = 0
            with open(self.score_sheet,'r') as sobj:
                data = csv.reader(sobj)
                for row in data:
                    if ("#" in row[0]):
                        max_score = int(row[3])
                        continue
                    if (mock == row[0]):
                        continue
                    else:
                        mock = row[0]
                        sheetDict[mock] = row[4]
            with open(self.file,'r') as fobj:
                data = csv.reader(fobj)
                for row in data:
                    f_ans += "[+] "+sheetDict[row[0]]+" (Score): "+row[1]+"\n    Reason: "+self.meaning[row[0]]+"\n\n"
                    if not(row[1] == "None"):
                        total += int(row[1])
                f_ans += "Total Score: "+str(total)+" out of "+str(max_score)+"\n"
            pcent = (total/25)*100
            anlys = ""
            if pcent >= 1 and pcent <= 33:
                anlys = "Low Security"
            elif pcent > 33 and pcent <= 66:
                anlys = "Medium Security"
            elif pcent > 66 and pcent <= 99:
                anlys = "High Security"
            elif pcent > 99 and pcent <= 100:
                anlys = "Perfect Security"
            f_ans += "Percentage: "+str(pcent)+"%\nAnalysis: "+anlys
            self.print_chapter(num,title,f_ans)
        except Exception as msg:
            self.gui.Popup("Error occured! Please note the error code and contact your system administrator.\nError Code: GWIN_SNS\nError: "+str(msg), keep_on_top=True, title="Error")

# Introduction chapter of the PDF.
    def results(self,num): # confusing name to avoid malicious manipulation
        try:
            title = "Introduction"
            topic = ""
            max_score = 0
            f_ans = ""
            with open("bin\\description.txt",'r') as file:
                data = file.read()
                f_ans = data.strip()
            f_ans += "\n\nMarking Scheme:"
            with open(self.score_sheet,'r') as file:
                sheet = csv.reader(file, delimiter = ",")
                for row in sheet:
                    if row[0] == '#"Topic"':
                        max_score = int(row[3])
                        continue
                    if row[4] != topic:
                        gth = 4
                        f_ans += "\n\n"+row[4]+"\n"+" "*gth+"[*] "+row[5]+": "+row[3]+" points"
                        topic = row[4]
                    else:
                        f_ans += "\n"+" "*gth+"[*] "+row[5]+": "+row[3]+" points"
            f_ans += "\n\n Maximum Possible Score: "+str(max_score)+" points"
            self.print_chapter(num,title,f_ans)
        except:
            f_ans += "[!] An error has occured while Auditing the system, please note the error code and contact your system administrator.\nError Code: GWIN_INTRO"
            self.print_chapter(num,title,f_ans)

# determines the scores that has to be given to a topic.
    def invigilator(self,topic,value): # confusing name to avoid malicious manipulation
        try:
            topics = []
            minParameters = []
            maxParameters = []
            scores = []
            meaning = []
            #print(topic+": "+str(value))
            with open (self.score_sheet,'r') as csv_file:
                data = csv.reader(csv_file,delimiter=',')
                for row in data:
                    if row[0] != '#"Topic"':
                        topics.append(row[0])
                        minParameters.append(row[1])
                        maxParameters.append(row[2])
                        scores.append(row[3])
                        meaning.append(row[6])
                    else:
                        continue
            for x in range(len(topics)):
                if topic in topics[x]:
                    if value != "N/A":
                        if (int(value) >= int(minParameters[x]) and int(value) <= int(maxParameters[x])) or int(value) == int(minParameters[x]):
                            self.meaning[topic] = meaning[x]
                            self.data_dic[topic] = scores[x]
                            return str(scores[x])
                    else:
                        if (value >= int(minParameters[x]) and value <= int(maxParameters[x])) or value == int(minParameters[x]):
                            self.meaning[topic] = meaning[x]
                            self.data_dic[topic] = scores[x]
                            return str(scores[x])                        
        except Exception as msg:
            self.gui.Popup("Error occured! Please note the error code and contact your system administrator.\nError Code: GWIN_INVG\nError: "+str(msg), keep_on_top=True, title="Error")
            
# calculates the strength of the password if supplied
    def password_strength(self):
        try:
            pwd = self.password
            n = len(pwd)
            L,U=0,0
            count1=0
            count2=0
            for i in pwd:
                  if(i.islower()):
                        count1=count1+1
                  elif(i.isupper()):
                        count2=count2+1
            L = count1
            U = count2
            N = 0
            for x in pwd:
                if x.isnumeric():
                    N+=1
            S = len(pwd) - (L+U+N)
            CU=0
            CL=0
            CD=0
            count=0
            Strength = (n*4) + ((n-U)*2) + ((n-L)*2) + (N*4) + (S*6) - (L+U)
            for p in range(len(pwd)-1):
                if pwd[p].isupper() and pwd[p+1].isupper():
                    CU += 1
                elif pwd[p].islower() and pwd[p+1].islower():
                    CL += 1
                elif pwd[p].isnumeric() and pwd[p+1].isnumeric():
                    CD += 1
            Strength -= ((CU*2)+(CL*2)+(CD*2))
            d = collections.defaultdict(int)
            for c in pwd:
                d[c] += 1
            for c in sorted(d, key=d.get, reverse=True):
              if d[c] > 1:
                  count += 1
            Strength -= count
            count = 0
            neg = 0
            for char in range(len(pwd)-1):
                if chr(ord(pwd[char])+1) == pwd[char+1]:
                    count += 1
                if count >= 2:
                    neg -= 1
            Strength += neg
            count = 0
            with open ('bin\\rockyou.txt','r',encoding='ansi') as file:
                data = file.readlines()
                for line in data:
                    if pwd == line.strip():
                        Strength = 0
                        break
                    else:
                        count += 1
            self.strength = Strength
            self.audit_summary["Password Strength"]=self.strength
            return Strength
        except:
            self.gui.Popup("Error occured! Please note the error code and contact your system administrator.\nError Code: GWIN_PWDSTR", keep_on_top=True, title="Error")

# powershell code to find anti virus status - by Misha
    def win_antivirus_info(self,num):
        try:
            f_ans=""
            title="Antivirus Status"
            topic="Antivirus"
            cmd = "bin\\antivirus.bat" # batch file that contains the code to find the antivirus
            ans, err = subprocess.Popen(cmd,stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
            value = 0
            ans = ans.decode("utf-8").strip()
            if err != b'':
                ans = "Error: Running of scripts is disabled on the system"
                value = -10
            f_ans = """Description: Antivirus is a application software that avoids virus infection of the system and quarantines the file that may contain it.
Security Tip: Make sure that your antivirus is licensed and has its virus definitions up-to-date.
    ____________________\n\n"""
            ans = ans.replace("Windows Defender","")
            if (len(ans.strip()) != 0):
                self.logger(topic,ans.strip())
                value=1
            else:
                value=0
                self.logger(topic,"N/A")
            score = self.invigilator(topic,value)
            value2text={0:"Not Installed",1:"Installed"}
            self.audit_summary["Antivirus Status"]=value2text[value]
            self.write("\""+topic+"\","+score+"\n")
            f_ans += ans.strip().replace("\n","\n\t[*] ")
            f_ans += "\n___________\nScore: "+score+"\n___________\n"
            f_ans += "\nScheme:"
            with open(self.score_sheet,'r') as fobj:
                data = csv.reader(fobj)
                for row in data:
                    if row[0] == topic:
                        f_ans += "\n    [*] "+row[5]+": "+row[3]+" points"
            self.print_chapter(num,title,f_ans)
        except:
            f_ans += "[!] An error has occured while Auditing the system, please note the error code and contact your system administrator.\nError Code: GWIN_ANTV"
            self.print_chapter(num,title,f_ans)
            
# Blacklisted softwares and their location has to be supplied in the dictionary named 'location'
    def win_check_remote_softwares(self,num):
        try:
            topic="UnwantedProgs"
            title = "Unwanted Softwares"
            ans = []
            f_ans = """Description: Certain softwares are not needed in the system and may cause security to lack if installed.
Security Tip: If you find any such software, or one that you did not installed, report it to your system administrator immediately.
    ____________________\n\n"""
# Dictionary name 'location' for the possible locations of the unwanted softwares
# format: 'Location of installation':'Software Name'
            locations = {'C:\\Program Files (x86)\\TeamViewer':'TeamViewer',
                         'C:\\Program Files (x86)\\AnyDesk':'AnyDesk',
                         'C:\\Program Files (x86)\\RegistryCleaner':'Registry Cleaner',
                         'C:\\Program Files\\TeamViewer':'TeamViewer',
                         'C:\\Program Files\\AnyDesk':'AnyDesk',
                         'C:\\Program Files\\RegistryCleaner':'Registry Cleaner',
                         'C:\\Program Files\\CCleaner':'CCleaner',
                         'C:\\Program Files\\Oracle\\VirtualBox':'VirtualBox',
                         'C:\\Program Files\\VMWare':'VMWare'}
            for loc in locations:
                if pathlib.Path(loc).is_dir():
                    ans.append(locations[loc])
            if len(ans) == 0:
                self.logger(topic,"N/A")
            else:
                self.logger(topic,','.join(ans))
            score = self.invigilator(topic,len(ans))
            self.audit_summary["Number of Unwanted Softwares"]=len(ans)
            self.write("\""+topic+"\","+score+"\n")
            f_ans += "\n".join(ans)
            f_ans += "\n___________\nScore: "+score+"\n___________\n"
            f_ans += "\nScheme:"
            with open(self.score_sheet,'r') as fobj:
                data = csv.reader(fobj)
                for row in data:
                    if row[0] == topic:
                        f_ans += "\n    [*] "+row[5]+": "+row[3]+" points"
            self.print_chapter(num,title,f_ans)
        except Exception as msg:
            f_ans += "[!] An error has occured while Auditing the system, please note the error code and contact your system administrator.\nError Code: GWIN_BLKSFT"
            #print(str(msg))
            self.print_chapter(num,title,f_ans)
            
# enters firewall rules of the system in a file called firewall-rules.txt located with the scores file.
    def win_firewall_rules(self):
        try:
            #urllib.request.urlretrieve(self.URL+"fw-rules.bat", "fw-rules.bat") # To download the file "fw-rules.bat" for ip address
            os.system("bin\\fw-rules.bat") # batch file that returns the list of firewall rules
            file = "fw-rules.csv"
            rules_file = self.location+"firewall-rules.txt"
            make = open(rules_file,'w')
            make.write("**** Rules Start ****\n")
            count=0
            with open(file,'r') as cfile:
                read = csv.reader(cfile, delimiter=',')
                for row in read:
                    action = ""
                    if(row[17] == "1"):
                        action = "Allow"
                    elif (row[17] == "0"):
                        action = "Block"
                    count += 1
                    make.write("Rule Number: "+str(count)+"\n")
                    make.write("Name: "+row[0]+"\n")
                    make.write("Description: "+row[1]+"\n")
                    make.write("Application: "+row[2]+"\n")
                    make.write("Service: "+row[3]+"\n")
                    make.write("Protocol: "+row[4]+"\n")
                    make.write("LocalPort: "+row[5]+"\n")
                    make.write("RemotePort: "+row[6]+"\n")
                    make.write("LocalAddress: "+row[7]+"\n")
                    make.write("RemoteAddress: "+row[8]+"\n")
                    make.write("Direction: "+row[10]+"\n")
                    make.write("Enabled: "+row[13]+"\n")
                    make.write("Action: "+action+"\n")
                    make.write("SecureFlags: "+row[24]+"\n")
                    make.write("----------------------------------------------------------\n")
            make.write("**** Rules End ****")
            make.close()
            make=None
            os.system("del fw-rules.csv")
        except:
            self.gui.Popup("Error occured! Please note the error code and contact your system administrator.\nError Code: GWIN_FWRLZ", keep_on_top=True, title="Error")

# Check for established connections other than those of set proxy.
    def win_connections(self,num):
        try:
            topic="Estb"
            title = "Established Connections"
            value = 0
            final_ans = """Description: List of connections that were established without going through proxy.
Security Tip: Connections that bypass proxy may lead to an insecure system as unfiltered commands or tasks may easily be performed by malicious user
    ____________________\n\n"""
            cmd = "netstat -ano | find \"ESTABLISHED\" | find /V \"127.0.0.1\" | find /V \""+proxy+"\""
            ans, err = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell = True).communicate()
            ans = ans.decode("utf-8")
            #err = err.decode("utf-8")
            if err != b'':
                ans = "Error: Running of scripts is disabled on the system"
                value = -10
                final_ans += ans
                self.logger(topic,"N/A")
                score = self.invigilator(topic,value)
                self.write("\""+topic+"\","+str(score)+"\n")
                final_ans += "\n___________\nScore: "+str(score)+"\n___________\n"
                f_ans = final_ans
                f_ans += "\nScheme:"
                with open(self.score_sheet,'r') as fobj:
                    data = csv.reader(fobj)
                    for row in data:
                        if row[0] == topic:
                            f_ans += "\n[*] "+row[5]+": "+row[3]+" points"
                self.print_chapter(num,title,f_ans)
                return "None"
            final_ans += "Proxy: "+proxy
            #ans = ans.replace("\r\n","")
            if (len(ans.replace("\r\n","")) == 0):
                value = 0
                final_ans = final_ans + "\nNo unusual connections"
                self.logger(topic,"No connections bypassing proxy ("+proxy+")")
            else:
                value = len(ans.strip().split("\n"))
                self.logger(topic,"Proxy: "+proxy+"\n"+ans.strip().replace('TCP','[+]').replace('\r\n','\n'))
                final_ans = final_ans+"\n "+ans.strip()
            score = self.invigilator(topic,value)
            self.write("\""+topic+"\","+str(score)+"\n")
            final_ans += "\n___________\nScore: "+str(score)+"\n___________\n"
            f_ans = final_ans
            f_ans += "\nScheme:"
            with open(self.score_sheet,'r') as fobj:
                data = csv.reader(fobj)
                for row in data:
                    if row[0] == topic:
                        f_ans += "\n    [*] "+row[5]+": "+row[3]+" points"
            self.print_chapter(num,title,f_ans)
        except:
            f_ans += "[!] An error has occured while Auditing the system, please note the error code and contact your system administrator.\nError Code: GWIN_ESTBC"
            self.print_chapter(num,title,f_ans)
            
# checks for firewall status of windows firewall for 3 profiles - Domain, Public, and Private profile
    def win_firewall_info(self, num):
        try:
            title="Firewall Status"
            des = ""
            #self.write("Title: Firewall Status\n")
            topic = "Firewall"
            f_ans = """Description: Windows Defender Firewall status.
Security Tip: Ensure that all 3 profiles (Domain, Public, and Private) have firewall configured and their state on.
    ____________________\n\n"""
            self.win_firewall_rules()
            value = 0
            profiles = ['Public','Private','Domain']
            for x in profiles:
                ans,err = subprocess.Popen("netsh advfirewall show " + x +" state | find /v \"Profile\" | find /v \"---\" | find /v \"Ok.\"", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()
                ans = ans.decode("utf-8")
                #err = err.decode("utf-8")
                if err != b'':
                    ans = "Error: Running of scripts is disabled on the system"
                    value = -10
                    f_ans += ans
                    self.logger(topic,"N/A")
                    score = self.invigilator(topic,value)
                    self.write("\""+topic+"\","+str(score)+"\n")
                    f_ans += "\n___________\nScore: "+str(score)+"\n___________\n"
                    f_ans += "\nScheme:"
                    with open(self.score_sheet,'r') as fobj:
                        data = csv.reader(fobj)
                        for row in data:
                            if row[0] == topic:
                                f_ans += "\n    [*] "+row[5]+": "+row[3]+" points"
                    self.print_chapter(num,title,f_ans)
                    return "None"
                loc = ans.find("Ok.")
                ans = ans[:loc]
                des += x+" "+ans.strip()+"\n"
                if "ON" in ans:
                    value += 1
                    f_ans += x + " State: ON\n"
                else:
                    f_ans += x + " State: OFF\n"
            score = self.invigilator(topic,value)
            self.logger(topic,des.strip())
            self.write("\""+topic+"\","+score+"\n")
            f_ans += "\n___________\nScore: "+score+"\n___________\n"
            f_ans += "\nScheme:"
            with open(self.score_sheet,'r') as fobj:
                data = csv.reader(fobj)
                for row in data:
                    if row[0] == topic:
                        f_ans += "\n    [*] "+row[5]+": "+row[3]+" points"
            self.print_chapter(num,title, f_ans)
        except:
            f_ans += "[!] An error has occured while Auditing the system, please note the error code and contact your system administrator.\nError Code: GWIN_FWNFO"
            self.print_chapter(num,title,f_ans)
            
# lists the users in the system
    def users_list(self,num):
        try:
            title = "Users"
            final_ans = "Description: List of all the users in the system\n____________________\n\n"
            process = subprocess.Popen("echo %username%", stdout=subprocess.PIPE,stderr=subprocess.PIPE, shell=True)
            user, err = process.communicate()
            user = user.decode("utf-8").strip()
            #err = err.decode("utf-8")
            if err != b'':
                user = "Error: Running of scripts is disabled on the system"
                #value = -10
                final_ans += user
                self.print_chapter(num,title,final_ans)
                return
            cmd = "net user | find /V \"User accounts for\" | find /v \"------\" | find /v \"The command completed\""
            users,_ = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True).communicate()
            users = users.decode("utf-8").strip()
            usrlt = users.split('  ')
            current_user = getpass.getuser()
            chk = True
            while chk:
                if "" in usrlt:
                    usrlt.remove('')
                else:
                    chk=False
            final_ans += "List of users:\n"
            des = ""
            for x in usrlt:
                des += x.strip()+"\n"
                final_ans += "    * "+x.strip()+"\n"
            final_ans += "\nCurrent Username:\n*"+current_user
            self.print_chapter(num,title,final_ans)            
        except:
            final_ans += "[!] An error has occured while Auditing the system, please note the error code and contact your system administrator.\nError Code: GWIN_USRLT"
            self.print_chapter(num,title,final_ans)
            
# Lists the UDP connections to and from the system.
    def udp_connections(self,num):
        try:
            total = 0
            topic = "UDP"
            title = "UDP Services"
            cmd = "netstat -a -p \"UDP\" | find \"UDP\""
            ans, err = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()
            value = 0
            ans = ans.decode("utf-8")
            f_ans = """Description: List of connections that use UDP (User Datagram Protocol). 
   ____________________\n
    """
            #err = err.decode("utf-8")
            if err != b'':
                ans = "Error: Running of scripts is disabled on the system"
                value = -10
                f_ans += ans
                self.logger(topic,"N/A")
                score = self.invigilator(topic,value)
                self.write("\""+topic+"\","+str(score)+"\n")
                f_ans += "\n___________\nScore: "+str(score)+"\n___________\n"
                f_ans += "\nScheme:"
                with open(self.score_sheet,'r') as fobj:
                    data = csv.reader(fobj)
                    for row in data:
                        if row[0] == topic:
                            f_ans += "\n[*] "+row[5]+": "+row[3]+" points"
                self.print_chapter(num,title,f_ans)
                return
            if (len(ans.replace("\r\n", "")) == 0):
                value = 0
                f_ans += "No UDP Connections"
                self.logger(topic,"No UDP Connections")
            else:
                total = ans.count("UDP",0,len(ans))
                value = total
                f_ans += ans.strip()
                f_ans = f_ans+"\nTotal connections: "+str(total)
                self.logger(topic,ans.strip().replace('UDP','[+]').replace('\r\n','\n'))
            score = self.invigilator(topic,value)
            self.write("\""+topic+"\","+score+"\n")
            f_ans += "\n___________\nScore: "+score+"\n___________\n"
            f_ans += "\nScheme:"
            with open(self.score_sheet,'r') as fobj:
                data = csv.reader(fobj)
                for row in data:
                    if row[0] == topic:
                        f_ans += "\n    [*] "+row[5]+": "+row[3]+" points"
            self.print_chapter(num,title,f_ans)
        except:
            f_ans += "[!] An error has occured while Auditing the system, please note the error code and contact your system administrator.\nError Code: GWIN_UDPC"
            self.print_chapter(num,title,f_ans)

# Checks the status of last update date and subtracts with today's date to determine the number of days it has been since.
    def win_last_update(self,num):
        try:
            os.system("wmic qfe list full /format:csv > hotfixes.csv")
            _,err = subprocess.Popen("bin\\osworker.bat",stderr=subprocess.PIPE,shell=True).communicate()
            file = "newfile.txt"
            topic = "LastUpdateDiff"
            title = "Last Update"
            f_ans = "Description: The date when the system was last updated, and number of days since the last update.\n____________________\n\n"
            value = -1
            #err = err.decode("utf-8")
            if err != b'':
                ans = "Error: Running of scripts is disabled on the system"
                self.logger(topic,ans)
                value = -10
                f_ans += ans
                score = self.invigilator(topic,"N/A")
                self.write("\""+topic+"\","+str(score)+"\n")
                f_ans += "\n___________\nScore: "+str(score)+"\n___________\n"
                f_ans += "\nScheme:"
                with open(self.score_sheet,'r') as fobj:
                    data = csv.reader(fobj)
                    for row in data:
                        if row[0] == topic:
                            f_ans += "\n[*] "+row[5]+": "+row[3]+" points"
                self.print_chapter(num,title,f_ans)
                return
            with open(file, 'r') as fobj:
                data = csv.reader(fobj, delimiter=',')
                for line in data:
                    if line != '':
                        date = line[8]
                    else:
                        date = ''
                    if len(date.strip()) != 0:
                        #self.print_chapter(num,title,date)
                        loc = date.find("/")
                        dam = date[loc+1:]
                        loc1 = dam.find("/")
                        year = int(date[-4:])
                        month = int(date[:loc])
                        day = int(dam[:loc1])
                        din = datetime.date(year, month, day)
                        difference = self.date_diff(din)
                        value = difference
                        f_ans += "Last Update Date: "+str(date)+"\nDays since last update: "+str(difference)
                        self.audit_summary["Last Update Date"] = str(date)
                        self.logger(topic,str(date))
                    else:
                        value = -1
                        f_ans += "Never Updated..."
                        self.audit_summary["Last Update Date"] = "Never Updated"
                        self.logger(topic,"N/A")
                    break
            cmd = "del "+file
            os.system(cmd)
            score = self.invigilator(topic,value)
            self.write("\""+topic+"\","+score+"\n")
            f_ans += "\n___________\nScore: "+score+"\n___________\n"
            f_ans += "\nScheme:"
            with open(self.score_sheet,'r') as fobj:
                data = csv.reader(fobj)
                for row in data:
                    if row[0] == topic:
                        f_ans += "\n    [*] "+row[5]+": "+row[3]+" points"
            self.print_chapter(num,title,f_ans)
        except Exception as msg:
            f_ans += "[!] An error has occured while Auditing the system, please note the error code and contact your system administrator.\nError Code: GWIN_LSTUP\nError Message: "+str(msg)
            self.print_chapter(num,title,f_ans)

# returns basic information about the system in the form of a dictionary called, 'dev_basics'
    def win_basic_info(self):
        try:
            _,err = subprocess.Popen("systeminfo /FO:csv > sysinfo.csv",stderr=subprocess.PIPE,shell=True).communicate()
            #err = err.decode("utf-8")
            if err != b'':
                return None
            temp_file = "sysinfo.csv" # input from this file is used for it
            dev_basics = {}
            with open(temp_file, 'r') as csv_file:
                read = csv.reader(csv_file, delimiter=',')
                count = 0
                for row in read:
                    if count == 0:
                        count += 1
                    else:
                        dev_basics = {'osversion': row[2],
                                      'osconfig': row[4],
                                      'productid': row[8],
                                      'installdate': row[9],
                                      'boottime':row[10],
                                      'biosversion':row[15],
                                      'windir': row[16],
                                      'sysdir': row[17],
                                      'domain': row[28],
                                      'hotfixes': row[30]
                                      }
            os.system("del sysinfo.csv")
            return dev_basics
        except:
            self.gui.Popup("Error occured! Please note the error code and contact your system administrator.\nError Code: GWIN_BSNFO", keep_on_top=True, title="Error")

            
# Checks password status, policy, and tests its strength if it is provided
    def password_details(self,num):
        try:
            topic="PassStrength"
            title = "Password Details"
            value = -1
            cmd = "net user %username%| find /I \"Password\" | find /v \"Password last set\""
            ans, err = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()
            ans = ans.decode("utf-8")
            f_ans = "Description: The date when the password of system was last changed and other basic details\n____________________\n\n"
            strg = self.password_strength()
            if err != b'':
                ans = "Error: Running of scripts is disabled on the system"
                self.logger(topic,"N/A")
                score = self.invigilator(topic,strg)
                self.write("\""+topic+"\","+str(score)+"\n")
                f_ans += "\n___________\nStrength Score: "+str(score)+"\n___________\n"
                f_ans += "\nScheme:"
                with open(self.score_sheet,'r') as fobj:
                    data = csv.reader(fobj)
                    for row in data:
                        if row[0] == topic:
                            f_ans += "\n[*] "+row[5]+": "+row[3]+" points"
                self.print_chapter(num,title,f_ans)
                return "0"
            cmd = "net user %username%| find /I \"Password expires\""
            f_ans += ans
            ans, _ = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True).communicate()
            ans = ans.decode("utf-8")
            time = ans.replace("Password expires", "")
            time = time.strip()
            score = self.invigilator(topic,strg)
            self.logger(topic,str(strg))
            self.write("\""+topic+"\","+str(score)+"\n")
            f_ans += "\n___________\nStrength Score: "+str(score)+"\n___________\n"
            f_ans += "\nScheme:"
            with open(self.score_sheet,'r') as fobj:
                data = csv.reader(fobj)
                for row in data:
                    if row[0] == topic:
                        f_ans += "\n    [*] "+row[5]+": "+row[3]+" points"
            self.print_chapter(num,title,f_ans)
        except:
            f_ans += "[!] An error has occured while Auditing the system, please note the error code and contact your system administrator.\nError Code: GWIN_PWDST"
            self.print_chapter(num,title,f_ans)

# checks number of shared folders and its location.
    def win_shared_folders(self,num):
        try:
            topic = "SharedFolders"
            title = "Shared Folders"
            value = 0
            f_ans = "Description: List of folders that are shared with other systems.\n____________________\n\n"
            cmd = "net view "+self.dev[1]+"| find /V \"Share\" | find /V \"------\" | find /V \"command\""
            ans, err = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()
            ans = ans.decode("utf-8").strip()
            if err != b'':
                ans = "Error: Running of scripts is disabled on the system"
                self.logger(topic,'N/A')
                value = -10
                score = self.invigilator(topic,value)
                self.write("\""+topic+"\","+str(score)+"\n")
                f_ans += "\n___________\nScore: "+str(score)+"\n___________\n"
                f_ans += "\nScheme:"
                with open(self.score_sheet,'r') as fobj:
                    data = csv.reader(fobj)
                    for row in data:
                        if row[0] == topic:
                            f_ans += "\n    [*] "+row[5]+": "+row[3]+" points"
                self.print_chapter(num,title,f_ans)
                return
            f_ans += "Folder    Location    Used as     Comment\n" 
            value = len(ans.strip().split("\n"))
            value -= 1
            self.logger(topic,ans.strip())
            score = self.invigilator(topic,value)
            self.audit_summary["Number of Shared Folders"] = value
            self.write("\""+topic+"\","+score+"\n")
            if len(ans.strip()) != 0:
                f_ans += ans.strip()
            else:
                f_ans += "No Shared Folders"
            f_ans += "\n___________\nScore: "+str(score)+"\n___________\n"
            f_ans += "\nScheme:"
            with open(self.score_sheet,'r') as fobj:
                data = csv.reader(fobj)
                for row in data:
                    if row[0] == topic:
                        f_ans += "\n[*] "+row[5]+": "+row[3]+" points"
            self.print_chapter(num,title,f_ans)
        except:
            f_ans += "[!] An error has occured while Auditing the system, please note the error code and contact your system administrator.\nError Code: GWIN_SHRDFD"
            self.print_chapter(num,title,f_ans)

# checks if RDP port of the sysem is open and if open, checks if a connection has been maintained
    def check_win_rdp(self,num):
        try:
            topic = "WinRDPports"
            title = "RDP Connections"
            cmd = "netstat -nao | find '3389'"
            f_ans = """Description: RDP (Remote Desktop Protocol) is a Windows' protocol to remotely access the system.
Security Tip: Ensure that RDP is filtered if not required by the user of the system to prevent its unauthorized access.
    ____________________\n
    """
            sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            value = 0
            if not(sock.connect_ex(('127.0.0.1',3389))):
                f_ans += "RDP Port On"
                value += 1
                ans,err = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()
                ans = ans.decode("utf-8")
                if err != b'':
                    ans = "Error: Running of scripts is disabled on the system"
                    value = -10
                    self.logger(topic,"N/A")
                    score = self.invigilator(topic,value)
                    self.write("\""+topic+"\","+str(score)+"\n")
                    f_ans += "\n___________\nScore: "+str(score)+"\n___________\n"
                    f_ans += "\nScheme:"
                    with open(self.score_sheet,'r') as fobj:
                        data = csv.reader(fobj)
                        for row in data:
                            if row[0] == topic:
                                f_ans += "\n[*] "+row[5]+": "+row[3]+" points"
                    self.print_chapter(num,title,f_ans)
                    return
                if ans == '':
                    f_ans += "No RDP Connections Found\n"
                    self.logger(topic,"ON OFF")
                else:
                    value += 1
                    f_ans += ans
                    self.logger(topic,"ON ON")
            else:
                f_ans += "RDP Port Off\n"
                self.logger(topic,"OFF")
            sock.close()
            score = self.invigilator(topic,value)
            self.write("\""+topic+"\","+score+"\n")
            f_ans += "\n___________\nScore: "+score+"\n___________\n"
            f_ans += "\nScheme:"
            with open(self.score_sheet,'r') as fobj:
                data = csv.reader(fobj)
                for row in data:
                    if row[0] == topic:
                        f_ans += "\n    [*] "+row[5]+": "+row[3]+" points"
            self.print_chapter(num,title,f_ans)
        except:
            f_ans += "[!] An error has occured while Auditing the system, please note the error code and contact your system administrator.\nError Code: GWIN_RDPNF"
            self.print_chapter(num,title,f_ans)

# lists out the applications that are listed to run on system startup
    def win_startup_apps(self, num):
        try:
            title = "Startup Apps"
            ans, err = subprocess.Popen("wmic startup get name", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()
            ans = ans.decode("utf-8")
            f_ans = "Description: List of application softwares that first starts with the system boot\n____________________\n\n"
            #err = err.decode("utf-8")
            if err != b'':
                f_ans += "Error: Running of scripts is disabled on the system"
                self.print_chapter(num,title,f_ans)
                return
            f_ans += ans[5:].strip()
            self.print_chapter(num,title,f_ans)
        except:
            f_ans += "[!] An error has occured while Auditing the system, please note the error code and contact your system administrator.\nError Code: GWIN_STRAPP"
            self.print_chapter(num,title,f_ans)
    
# lists all the programs installed in the system and count the programs that are  not from google, microsoft, hp, lenovo, mozilla, intel, adobe, etc.
    def win_prog_lister(self, num):
        try:
            topic = "ExtraProgs"
            title = "Programs List"
            value = 0
            f_ans = """Description: List of softwares installed in the system classified into 3 categories-
                   1) Microsoft Softwares
                   2) HP Softwares
                   3) Other Softwares
    ____________________\n\n"""
            mic, err = subprocess.Popen(["powershell.exe", "Get-ItemProperty HKLM:\\Software\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\* | Select-Object DisplayName |Format-Table –AutoSize"],stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
            progs = mic.decode("utf-8").strip().split('\n')
            #print(mic)
            for x in range(len(progs)):
                progs[x] = progs[x].strip()
            progs = [x for x in progs if x]
            progs.pop(0)
            progs.pop(0)
            microsoftProgs = []
            hpProgs = []
            otherProgs = []
            allowedProgs = ['Microsoft','HP','Google','Adobe','Intel','Lenovo','Mozilla']
            if err != b'':
                mic = "Error: Running of scripts is disabled on the system"
                self.logger(topic,"N/A")
                value = -10
                score = self.invigilator(topic,value)
                self.write("\""+topic+"\","+str(score)+"\n")
                f_ans += "\n___________\nScore: "+str(score)+"\n___________\n"
                f_ans += "\nScheme:"
                with open(self.score_sheet,'r') as fobj:
                    data = csv.reader(fobj)
                    for row in data:
                        if row[0] == topic:
                            f_ans += "\n[*] "+row[5]+": "+row[3]+" points"
                self.print_chapter(num,title,f_ans)
                return
            for x in progs:
                if 'Microsoft' in x:
                    microsoftProgs.append(x)
                elif 'HP' in x:
                    hpProgs.append(x)
                else:
                    for y in allowedProgs:
                        if y in x:
                            break
                        elif y == 'Mozilla':
                            otherProgs.append(x)
            f_ans += "\t[1] Microsoft Programs:\n"+'\n'.join(microsoftProgs)
            #f_ans += "\n\n\t[2] HP Programs:\n"+'\n'.join(hpProgs)
            f_ans += "\n\n\t[3] Other Program:\n"+'\n'.join(otherProgs)
            value = len(otherProgs)
            self.logger(topic,"Extra Programs: "+str(value))
            f_ans = f_ans+"\n\n\t[*] Total Extra Programs: "+str(value)
            score = self.invigilator(topic,value)
            self.write("\""+topic+"\","+score+"\n")
            f_ans += "\n___________\nScore: "+score+"\n___________"
            f_ans += "\nScheme:"
            with open(self.score_sheet,'r') as fobj:
                data = csv.reader(fobj)
                for row in data:
                    if row[0] == topic:
                        f_ans += "\n    [*] "+row[5]+": "+row[3]+" points"
            self.print_chapter(num,title,f_ans)
        except:
            f_ans += "[!] An error has occured while Auditing the system, please note the error code and contact your system administrator.\nError Code: GWIN_PRGLS"
            self.print_chapter(num,title,f_ans)

# difference between two dates. One date - today's date
    def date_diff(self, that_day):
        try:
            today = datetime.datetime.now()
            delta = datetime.date(today.year,today.month, today.day) - that_day
            return delta.days
        except:
            self.gui.Popup("Error occured! Please note the error code and contact your system administrator.\nError Code: GWIN_DATDI", keep_on_top=True, title="Error")

# looks for open ports from the list of those which can be used for malicious purpose or those which are not needed in a client device
    def win_open_ports(self,num):
        try:
            file = "bin\\protocols_list.csv" # list of possible ports to check and their details. Add more to this list if need be.
            topic = "openPorts"
            title = "Open Ports"
            f_ans = "Description: List of open ports that should not be open for a client device (Standalone Workstation), unless the device acts as a server.\n____________________\n\n"
            value = 0
            des = "N/A"
            with open(file,'r') as fobj:
                data = csv.reader(fobj)
                for row in data:
                    if "#" in row[0]:
                        continue
                    else:
                        sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                        if not(sock.connect_ex(('127.0.0.1',int(row[0])))):
                            f_ans += "[+] Port: "+row[0]+"\n     Service: "+row[1]+"\n     Protocol: "+row[2]+"\n"
                            if des != "N/A":
                                des += row[0]+"\n"
                            else:
                                des = row[0]+"\n"
                            value += 1
                        sock.close()
            score = self.invigilator(topic,value)
            self.logger(topic,des)
            self.write("\""+topic+"\","+score+"\n")
            f_ans += "\n___________\nScore: "+score+"\n___________\n"
            f_ans += "\nScheme:"
            with open(self.score_sheet,'r') as fobj:
                data = csv.reader(fobj)
                for row in data:
                    if row[0] == topic:
                        f_ans += "\n    [*] "+row[5]+": "+row[3]+" points"
            self.print_chapter(num,title,f_ans)
        except:
            f_ans += "[!] An error has occured while Auditing the system, please note the error code and contact your system administrator.\nError Code: GWIN_OPNPT"
            self.print_chapter(num,title,f_ans)

# lists out the details of the usb devices that were plugged in the system long with their date and time.
    def usb_lister(self,num):
        try:
            cmd = "powershell -Command \"& {get-winevent -logname Microsoft-Windows-DriverFrameworks-UserMode/Operational -computername $env:COMPUTERNAME | where {$_.ID -eq 2100} | select timecreated, message | export-csv 'USB_logs.csv' -noType}\""
            topic="USBPlugged"
            value = 0
            title = "USB List"
            f_ans = "Description: Details about the USB that were plugged in the system.\n____________________\n\n"
            _, err = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True).communicate()
            if (len(err.decode("utf-8")) != 0):
                f_ans = f_ans + "Logging is disabled or Logs are cleared"
                self.logger(topic,"N/A")
                value = -1
                pass
            temp_file = "USB_logs.csv"
            des = ""
            try:
                with open(temp_file,'r') as file:
                    data = csv.reader(file)
                    for line in data:
                        date, msg = line[0], line[1]
                        if (msg != "Message"):
                            value += 1
                            loc = msg.find("VEN_")
                            loce = msg.find("PROD")
                            vendor = msg[loc+4:loce-1]
                            loc = loce
                            loce = msg.find("REV_")
                            typ = msg[loc+5:loce-1]
                            typ = typ.replace("_", " ")
                            loc = loce+9
                            loce = msg.find("{")
                            serial = msg[loc:loce-3]
                            loc = loce+1
                            loce = msg.find("}")
                            iden = msg[loc:loce+1]
                            f_ans = f_ans+"Date Time: "+date+"\nType: "+typ+"\nVendor: "+vendor+"\nSerialNumber: "+serial+"\nIdentification: "+iden+"\n*****************\n"
                            des += "Date Time = "+date+"|Vendor = "+vendor+","
                cmd = "del "+temp_file
                os.system(cmd)
                self.logger(topic,des)
                score = self.invigilator(topic,value)
                self.audit_summary["Number of USBs plugged"] = value
                self.write("\""+topic+"\","+score+"\n")
                f_ans += "\n___________\nScore: "+score+"\n___________\n"
                f_ans += "\nScheme:"
                with open(self.score_sheet,'r') as fobj:
                    data = csv.reader(fobj)
                    for row in data:
                        if row[0] == topic:
                            f_ans += "\n    [*] "+row[5]+": "+row[3]+" points"
                    self.print_chapter(num,title,f_ans)
            except Exception:
                _,err = subprocess.Popen("bin\\usb.bat",stderr=subprocess.PIPE,shell=True).communicate()
                #err = err.decode("utf-8")
                if err != b'':
                    ans = "Error: Running of scripts is disabled on the system"
                    value = -1
                    score = self.invigilator(topic,value)
                    self.write("\""+topic+"\","+str(score)+"\n")
                    f_ans += "\n___________\nScore: "+str(score)+"\n___________\n"
                    f_ans += "\nScheme:"
                    with open(self.score_sheet,'r') as fobj:
                        data = csv.reader(fobj)
                        for row in data:
                            if row[0] == topic:
                                f_ans += "\n    [*] "+row[5]+": "+row[3]+" points"
                    self.print_chapter(num,title,f_ans)
                    return
                with open(temp_file, 'r') as file:
                    data = file.read()
                self.usb_lister(num)
        except:
            f_ans += "[!] An error has occured while Auditing the system, please note the error code and contact your system administrator.\nError Code: GWIN_USBLT"
            self.print_chapter(num,title,f_ans)
  
# main function of the class "Windows". Add a new function in this to call.
    def windows_OS(self):
        try:
            self.progBar(15)
            index = """Chapter 1: Introduction
Chapter 2: System Information
Chapter 3: Last Update Status
Chapter 4: Password Status
Chapter 5: Users' List
Chapter 6: USB List
Chapter 7: Programs' List
Chapter 8: Startup Applications
Chapter 9: Established Connections
Chapter 10: UDP Services
Chapter 11: RDP Connections
Chapter 12: Open Ports
Chapter 13: Shared Folders
Chapter 14: Firewall Status
Chapter 15: Antivirus Status
Chapter 16: Blacklisted Softwares
Chapter 17: Score & Summary
"""
# Index List... Edit for furthur changes
            self.print_chapter(0,'Index',index)
            self.results(1)
            num = 2
            title = "System Information"
            if self.dev_basics != None:
                device_info = {'os': "Windows",
                               'release':self.dev[2],
                               'version':self.dev[3],
                               'machine':self.dev[4],
                               'processor':self.dev[5],
                               'sysname':self.dev[1],
                               'ipaddr':self.ip}
                pack = platform.win32_ver()
                service_pack = pack[2]
#For checking MAC Address
                mac = (':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff) for ele in range(0,8*6,8)][::-1]))
#Check for Internet Connectivity
                auth = req.HTTPBasicAuthHandler()
                opener = req.build_opener(None, auth, req.HTTPHandler)
                req.install_opener(opener)
                try:
                    conn = req.urlopen('http://google.com', timeout=3)
                    return_str = conn.read()
                    internet_conn="Internet Connected"
                except Exception as e:
                       internet_conn="Internet Not Connected"
                self.audit_summary["Internet Connection"] = internet_conn
#Information for Newtork Interface in system                       
                nic,err = subprocess.Popen("wmic nic where netenabled=true get netconnectionID",stdout=subprocess.PIPE,stderr=subprocess.PIPE).communicate()
                nic = nic.decode("utf-8")
#Wireless Interfaces Information
                wifi,err = subprocess.Popen("netsh wlan show interfaces",stdout=subprocess.PIPE,stderr=subprocess.PIPE).communicate()
                wifi = wifi.decode("utf-8")
                f_ans = "Description: Basic details about the system such as configuration, version, Install Date, etc.\n____________________\n\n"
                f_ans += "[+] IP Address:\n"+self.ip.replace("_","")+"\n"
                f_ans += "[+] MAC Address:\n"+mac+"\n"
                f_ans = f_ans+"[+] SystemName:\n"+ device_info['sysname']+"\n"
                topic = "WinSystemVersion"
                value = float(device_info['release'])
                f_ans = f_ans + "[+] Operating System:\nWindows "+device_info['release']+"\n"
                f_ans = f_ans + "[+] OS Version:\n"+self.dev_basics['osversion']+"\n"
                f_ans = f_ans + "[+] ServicePack:\n"+service_pack+"\n"
                f_ans = f_ans + "[+] OS Configuration:\n"+self.dev_basics['osconfig']+"\n"
                f_ans = f_ans + "[+] Product ID:\n"+self.dev_basics['productid']+"\n"
                f_ans = f_ans + "[+] BIOS Version:\n"+self.dev_basics['biosversion']+"\n"
                f_ans = f_ans + "[+] Windows Directory:\n"+self.dev_basics['windir']+"\n"
                f_ans = f_ans + "[+] System Directory:\n"+self.dev_basics['sysdir']+"\n"
                f_ans = f_ans + "[+] Processor:\n"+device_info['processor']+"\n"
                f_ans = f_ans + "[+] Machine:\n"+device_info['machine']+"\n"
                f_ans = f_ans + "[+] Internet Connectivity:\n"+internet_conn+"\n"
                f_ans = f_ans + "[+] Network Interface:\n"+nic[15:]+"\n"
                f_ans = f_ans + "[+] WiFi Interface:\n"+wifi+"\n"
                f_ans = f_ans + "[+] OS Install Date:\n"+self.dev_basics['installdate']+"\n"
                f_ans = f_ans + "[+] Domain:\n"+self.dev_basics['domain']+"\n"
                f_ans = f_ans + "[+] Hotfixes:\n"+self.dev_basics['hotfixes']+"\n"
                self.logger(topic,str(value))
                score = self.invigilator(topic,value)
                self.write("\""+topic+"\","+score+"\n",'w')
                f_ans += "\n___________\nScore: "+score+"\n___________\n"
                f_ans += "\nScheme:"
                with open(self.score_sheet,'r') as fobj:
                    data = csv.reader(fobj)
                    for row in data:
                        if row[0] == topic:
                            f_ans += "\n    [*] "+row[5]+": "+row[3]+" points"
                self.print_chapter(num,"System Information",f_ans)
            else:
                device_info = {'os': "Windows",
                               'release':self.dev[2],
                               'version':self.dev[3],
                               'machine':self.dev[4],
                               'processor':self.dev[5],
                               'sysname':self.dev[1],
                               'ipaddr':self.ip}
                pack = platform.win32_ver()
                service_pack = pack[2]
                f_ans = "Description: Basic details about the system such as configuration, version, Install Date, etc.\n____________________\n\n"
                f_ans = f_ans+"[+] SystemName:\n"+ device_info['sysname']+"\n"
                topic = "WinSystemVersion"
                value = int(device_info['release'])
                f_ans = f_ans + "[+] Operating System:\nWindows "+device_info['release']+"\n"
                f_ans = f_ans + "[+] ServicePack:\n"+service_pack+"\n"
                f_ans = f_ans+"[+] Processor:\n"+device_info['processor']+"\n"
                f_ans = f_ans + "[+] Machine:\n"+device_info['machine']+"\n"
                self.logger(topic,str(value))
                score = self.invigilator(topic,value)
                self.write("\""+topic+"\","+score+"\n",'w')
                f_ans += "\n___________\nScore: "+score+"\n___________\n"
                f_ans += "\nScheme:"
                with open(self.score_sheet,'r') as fobj:
                    data = csv.reader(fobj)
                    for row in data:
                        if row[0] == topic:
                            f_ans += "\n    [*] "+row[5]+": "+row[3]+" points"
                self.print_chapter(num,"System Information",f_ans)
            self.progBar(20)
            self.win_last_update(3)
            self.progBar(25)
            self.password_details(4)
            self.progBar(30)
            self.progBar(35)
            self.users_list(5)
            self.progBar(40)
            self.usb_lister(6)
            self.progBar(45)
            self.win_prog_lister(7)
            self.progBar(50)
            self.win_startup_apps(8)
            self.progBar(55)
            self.win_connections(9)
            self.progBar(60)
            self.udp_connections(10)
            self.progBar(65)
            self.check_win_rdp(11)
            self.progBar(70)
            self.win_open_ports(12)
            self.progBar(75)
            self.win_shared_folders(13)
            self.progBar(80)
            self.win_firewall_info(14)
            self.progBar(85)
            self.win_antivirus_info(15)
            self.progBar(90)
            self.win_check_remote_softwares(16)
            self.progBar(95)
            self.comp(17)
            self.progBar(100)
            #os.system("start "+self.file)
            self.pdf.output(self.pfile,'F')
            os.system("start "+self.pfile)
            #print(len(self.data))
            return (self.file, self.serverIP, self.data_dic, self.data, self.audit_summary)
        except Exception as msg:
            self.gui.Popup("Error occured! Please note the error code and contact your system administrator.\nError Code: GWIN_WINOS\n"+str(msg), keep_on_top=True, title="Error")
            #print(str(msg))
            return (self.file, self.serverIP, self.data_dic, self.data, self.audit_summary)

# strength checking module for the second tab to call for
def chk_strength(pwd=''):
    n = len(pwd)
    L,U=0,0
    count1=0
    count2=0
    for i in pwd:
          if(i.islower()):
                count1=count1+1
          elif(i.isupper()):
                count2=count2+1
    L = count1
    U = count2
    N = 0
    for x in pwd:
        if x.isnumeric():
            N+=1
    S = len(pwd) - (L+U+N)
    CU=0
    CL=0
    CD=0
    count=0
    Strength = (n*4) + ((n-L)*2) + ((n-U)*2) + (N*4) + (S*6) - (L+U)
    for p in range(len(pwd)-1):
        if pwd[p].isupper() and pwd[p+1].isupper():
            CU += 1
        elif pwd[p].islower() and pwd[p+1].islower():
            CL += 1
        elif pwd[p].isnumeric() and pwd[p+1].isnumeric():
            CD += 1
    Strength -= ((CU*2)+(CL*2)+(CD*2))
    d = collections.defaultdict(int)
    for c in pwd:
        d[c] += 1
    for c in sorted(d, key=d.get, reverse=True):
      if d[c] > 1:
          count += 1
    Strength -= count
    count = 0
    neg = 0
    for char in range(len(pwd)-1):
        if chr(ord(pwd[char])+1) == pwd[char+1]:
            count += 1
        if count >= 2:
            neg -= 1
    Strength += neg
    count = 0
    with open ('bin\\rockyou.txt','r',encoding='ansi') as file:
        data = file.readlines()
        for line in data:
            if pwd == line.strip():
                Strength = 0
                text = "The password is a common one.\nIt is recommended NOT to use it for security purposes"
                break
            else:
                count += 1
                text = "Password strength calculated successfully!"
    if Strength > 100:
        Strength = 100
    return (text, Strength)

# theme for the program
sg.theme('DarkAmber')
# visual display of tab1 "Run Automated Audit"
tab1 = [[sg.Text("")],
        [sg.T(' ' * 5),sg.Text('Automated System Auditor', size=(50,1),justification='center', font=("Helvetica", 15), relief=sg.RELIEF_RIDGE)],
        [sg.Text("")],
        [sg.Text('Important Notice:\tThe Auditor may become unresponsive several times depending on the system resources.\n\t\tPlease do NOT exit!\n\t\tIt is running in the background and you can continue your work till the auditor runs.', relief = sg.RELIEF_RIDGE)],
        [sg.Text("")],
        [sg.Text('Employee Name *\t', font=("Times New Roman", 12)), sg.InputText(font=("Times New Roman", 15), size=(45,20))],
        [sg.Text('Employee Code *\t', font=("Times New Roman", 12)), sg.InputText(font=("Times New Roman", 15), size=(45,20))],
        [sg.Text("\tEmployee name and code are compulsory fields")],
        [sg.Text('User Password\t', font=("Times New Roman", 12)), sg.InputText('', password_char='*', font=("Times New Roman", 15))],
        [sg.Text('\t\t\t(Leave password blank if not set.)', justification='center')],
        [sg.Text('Note:\tProxy IP and Port are optional if you have proxy settings setup in your oganization\n\tIf unsure about these settings, contact your system administrator', relief = sg.RELIEF_RIDGE)],
        [sg.Text('Proxy IP\t\t', font=("Times New Roman", 12)), sg.InputText(font=("Times New Roman", 15))],
        [sg.Text('Proxy Port\t', font=("Times New Roman", 12)), sg.InputText(font=("Times New Roman", 15))],
        [sg.Text("")],
        [sg.T(' ' * 60),sg.Button('Start', font=("Times New Roman", 15))],
        [sg.Text('Progress '),sg.ProgressBar(1,orientation='h', size=(50,20), key='progress')]]

# visual display of tab2 "Check Password Strength" module
tab2 = [[sg.Text("")],
        [sg.T(' ' * 5),sg.Text('Password Strength Calculator', size=(50,1),justification='center', font=("Helvetica", 15), relief=sg.RELIEF_RIDGE)],
        [sg.Text("")],
        [sg.Text('Password', font=("Times New Roman", 12)), sg.InputText('',password_char='*', font=("Times New Roman", 15))],
        [sg.Text("")],
        [sg.T(' ' * 45),sg.Button("Check Strength", font=("Times New Roman", 15)),sg.T(' ' * 5),sg.Quit(font=("Times New Roman", 15))]]

# layout of overall program
layout = [[sg.TabGroup([[sg.Tab('Run Automated Audit', tab1), sg.Tab('Check Password Strength', tab2)]])],
          [sg.Text("")]]

# window begins here.
window = sg.Window('Automated Systems & Network Auditor (ASNA)', layout)
s=True
while s:
    event, values = window.read()
    if event == "Start":
        if not((values[0] == "")or(values[1] == "")):
            empname = values[0]
            labname = values[1]
            password = values[2]
            if values[3] != "" and values[4] != "":
                proxy = values[3]+":"+values[4]
            else:
                proxy=""
            win = Windows(proxy, window, password, empname, labname,sg)
            
            # Preping to send data
            try:
                columns = ""
                SEPARATOR = "<SEPARATOR>"
                BUFFER_SIZE = 8192
                file, IP, data_dic, karl, summary = win.windows_OS() # data to send is in file and address is the server IP
                #print_summaryFile(summary)
                with open(file, 'r') as fobj:
                    data = fobj.read()
                with open(file,'r') as fobj:
                    cdata = csv.reader(fobj)
                    for row in cdata:
                        columns += row[0]+","
                columns = columns[:len(columns)-1]
                rahul = '<<<>>>'.join(karl)
                data_hash = hashlib.md5(data.encode('utf-8')).hexdigest()
                if True:
                    filesize = os.path.getsize(file)
                    s = socket.socket()
                    s.connect((IP,50000))
                    s.send(f"{empname}{SEPARATOR}{labname}{SEPARATOR}{file}{SEPARATOR}{filesize}{SEPARATOR}Windows{SEPARATOR}{data_hash}{SEPARATOR}{columns}{SEPARATOR}{rahul}{SEPARATOR}{data_dic}".encode())
                    s.close()
                    
                sg.Popup("The Scorer has completed successfully!", keep_on_top=True,title="ASNA")
                window.close()
                s=False
            except Exception as msg:
                sg.Popup("Error in sending scores to server", keep_on_top=True, title="Error")
                #print(str(msg))
                window.close()
                s=False
            break
        else:
            sg.Popup("Please fill Employee Name and Lab Name.", keep_on_top=True, title="ASNA")
    elif event == "Check Strength":
        if values[6] != "":
            sg.PopupAnimated(sg.DEFAULT_BASE64_LOADING_GIF, message='Please wait...', background_color=None, keep_on_top=True, no_titlebar=True)
            password = values[6]
            cmnt, strn = chk_strength(password)
            text = cmnt+"\nPassword Strength: "+str(strn)+"%"
            sg.popup_animated(None)
            sg.Popup("",text, keep_on_top=True)
        else:
            sg.Popup("Fill in the password to check it's strength.", keep_on_top=True,title="Error")
    elif event == "Quit":
        s=False
        window.close()
        break
    #print("Done")
