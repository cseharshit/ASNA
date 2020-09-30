# Server-Side Code
## How to start?
* Make sure you get the correct internal IP address of your server and save it to *serverIP.csv* in client-side code inside *bin* directory.
* Install the requirements using the following command:
  > $pip install -r requirements.txt
* Download and Install ELK stack, and filebeat with *grok filter* as specified below:
```
%{IPV4:IP_Address}:%{DATA:Employee_Code}:%{DATA:Date_Of_Audit}:%{DATA:Employee_Name}:%{DATA:System_Name}:%{DATA:System_Version}:%{DATA:Product_ID}:%{DATA:Last_Update_Date}:%{INT:Password_Strength}:%{INT:Number_of_User_Accounts}:%{DATA:Extra_Programs}:%{DATA:Internet_Connectivity}:%{DATA:NIC_List}:%{DATA:Open_Ports}:%{DATA:Established_Connections}:%{DATA:UDP_Ports}:%{DATA:USB_Plugged}:%{INT:Number_of_USBs}:%{DATA:Startup_Apps}:%{DATA:Shared_Folders}:%{INT:Number_of_Shared_Folders}:%{DATA:RDP_Port}:%{DATA:Firewall}:%{DATA:Antivirus}:%{DATA:Unwanted_Programs}:%{INT:Number_of_unwanted_Programs}:%{INT:Final_Score}:%{DATA:Final_Status}:
```
* If you don't need ELK stack for visualization or prefer another then you can easily extract data from databases and use them for it.
