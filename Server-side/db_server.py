import socket
from datetime import datetime
import csv
import subprocess
import sys
import os
import sqlite3
from sqlite3 import Error

# Edit these variables
#------------------------------------#
#ELK_SERVER_IP ='10.0.2.72'
#ELK_SERVER_PORT=5020
#------------------------------------#

# Do not touch the code from here, unless you are a developer or unsure of how to handle
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 50000
BUFFER_SIZE = 8192
SEPARATOR = "<SEPARATOR>"
case=True

codeName = input("code Name: ")
date = str(datetime.now())[:10]
database = f"AuditData_{codeName}_{date}.db"
sql_create_table = """ CREATE TABLE IF NOT EXISTS Audit_Data (
							IPaddr text,
							EmployeeCode text,
							DateOfAudit text,
							EmployeeName text,
							SystemName text,
							WindowsVersion text,
							ProductID text,
							LastUpdate text,
							PasswordStrength text,
							NumberofAccounts integer,
							ExtraPrograms text,
							InternetConnectivity text,
							NICList text,
							OpenPorts text,
							EstablishedConnections text,
							UDPports text,
							USBPlugged text,
							NumberofUSB integer,
							StartupApps text,
							SharedFolders text,
							NumberofSharedFolders integer,
							RDPport text,
							Firewall text,
							Antivirus text,
							UnwantedPrograms text,
							NumberofUnwantedPrograms integer,
							FinalScore integer,
							FinalStatus text,
							PRIMARY KEY (IPaddr,codeName,DateOfAudit,EmployeeName)
								); """
try:
	conn = sqlite3.connect(database)
	print ("[+] Database Created: "+database)
	crt = conn.cursor()
	crt.execute(sql_create_table)
	print ("[+] Table Created: Audit_Data")
	conn.close()
except Error as e:
    print(e)
    sys.exit(1)

SQL_DB = database

while case:
	score = 0
	s = socket.socket()
	s.bind((SERVER_HOST,SERVER_PORT))
	s.listen(10)
	try:
		print("""
+-----------------------------------------+
| [!] Listening for incoming connections. |
+-----------------------------------------+

""")
		client_socket, address = s.accept()
		received = client_socket.recv(BUFFER_SIZE).decode()
		employee,code,filename, filesize, systemType, data_hash, columns, column_data, data = received.split(SEPARATOR)
		filename = os.path.basename(filename)
		#print(type(column_data))
		systemname = filename.split('_')[1]
		filesize = int(filesize)
		data = data.replace("{",'').replace("}",'').replace(" ",'').replace("'",'')
		data_dict = {}
		data = data.split(',')
		for x in data:
			data_dict[x.split(':')[0]] = x.split(':')[1]
		SystemIP, Port = address
		date = datetime.today().strftime('%d-%m-%Y')
		print(f"""
[+] New Connection Established:
	[*] System Name:{systemname}
	[*] IP Address: {SystemIP}
	[*] FileSize: {filesize} bytes
	[*] Hash: {data_hash}
""")
		text = ""
		for x in data_dict:
			text += '"'+x+'",'+data_dict[x]+'\n'
		with open(filename,'wb') as f:
			#print(text.strip())
			f.write(text.strip().encode())
		client_socket.close()
		s.close()
		print("""
	[*] Scores Received
	[*] Connection Terminated
""")
		cmd = "nmap -sV -A "+SystemIP+"> Nmap/"+code+"_"+SystemIP+"_nmap_scan.txt"
		subprocess.Popen(cmd,stdout=subprocess.PIPE,shell=True).communicate()
		print("[+] NMap Scan Complete")
		try:
			score_dic = {}
			score = 0
			with open(filename,'r') as fobj:
				data = csv.reader(fobj)
				for row in data:
					score += int(row[1])
					score_dic[row[0]] = int(row[1])
			query = """INSERT INTO Audit_Data (IPaddr,EmployeeCode,DateOfAudit,EmployeeName,SystemName,WindowsVersion,ProductID,LastUpdate,PasswordStrength,NumberOfAccounts,ExtraPrograms,InternetConnectivity,NICList,OpenPorts,EstablishedConnections,UDPports,USBPlugged,NumberofUSB,StartupApps,SharedFolders,NumberofSharedFolders,RDPport,Firewall,Antivirus,UnwantedPrograms,NumberofUnwantedPrograms,FinalScore,FinalStatus)
					   values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);"""
			cdata = column_data.split('<<<>>>')
			share = cdata[14]
			shared = ''.join(share.split('\n'))
			data = [SystemIP,code,date,employee,systemname, cdata[3],cdata[0],cdata[4],cdata[5],len(cdata[6].split(',')),cdata[8],cdata[2],cdata[1],cdata[13],cdata[10],cdata[11],cdata[7],len(cdata[7].split(',')),cdata[9],shared,len(shared),cdata[12],cdata[15],cdata[16],cdata[17],len(cdata[17].split(',')),score,cdata[18]]
			#print("First Query:\n"+query+"\n\n")
			conn = sqlite3.connect(SQL_DB)
			cur = conn.cursor()
			cur.execute(query,data)
			conn.commit()
			conn.close()
		except Exception as msg:
			print ("[-] Data not saved in database...\n\t Error message: "+str(msg))
		print("1 record inserted successfully!")
	except Exception as msg:
		print("Error: "+str(msg))
		caseValue = input("Do you want to stop receiving data?(y/n): ")
		if caseValue.lower() == 'y':
			sys.exit(0)
