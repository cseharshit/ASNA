import sqlite3
import socket
import os
import subprocess

#-----EDIT-THESE-VARIABLES-----#
location = 'DatabaseFiles'
completedFolder = "Completed"
filbeatSource = "Filebeat\\AuditData.txt"
#------------------------------#
f, err = subprocess.Popen("ls *.db",stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True).communicate()
files = f.decode('utf-8').split('\n')
files = [x.strip() for x in files if x]

print(f"[+] {len(files)} databases found...")

for database in files:
    print(f'[+] Sending data from "{database}" database')
    error = 0
    with sqlite3.connect(database) as conn:
        for row in conn.execute('SELECT * FROM Audit_Data;').fetchall():
            data = ':'.join([str(f) for f in row]).replace('\n','')
            data += ":\n"
            try:
                with open(filebeatSource,'a+') as f:
                    f.write(data)
                f.close()
            except Exception as msg:
                error = 1
                print(f"[-] Error occured in writing data in {filbeatSource}...\n\tError Message: {str(msg)}")
                print(f"\tDatabase:{database}\n\tRow:{data}")
        s.close()
    if not error:
        command = "mv .\\"+database+" .\\"+completedFolder+"\\"
        os.system(command)

print("[+] Task Completed Successfully...")


"""
  Grok Filter
---------------
%{IPV4:IP_Address}:%{DATA:Employee_Code}:%{DATA:Date_Of_Audit}:%{DATA:Employee_Name}:%{DATA:System_Name}:%{DATA:System_Version}:%{DATA:Product_ID}:%{DATA:Last_Update_Date}:%{INT:Password_Strength}:%{INT:Number_of_User_Accounts}:%{DATA:Extra_Programs}:%{DATA:Internet_Connectivity}:%{DATA:NIC_List}:%{DATA:Open_Ports}:%{DATA:Established_Connections}:%{DATA:UDP_Ports}:%{DATA:USB_Plugged}:%{INT:Number_of_USBs}:%{DATA:Startup_Apps}:%{DATA:Shared_Folders}:%{INT:Number_of_Shared_Folders}:%{DATA:RDP_Port}:%{DATA:Firewall}:%{DATA:Antivirus}:%{DATA:Unwanted_Programs}:%{INT:Number_of_unwanted_Programs}:%{INT:Final_Score}:%{DATA:Final_Status}:
"""
