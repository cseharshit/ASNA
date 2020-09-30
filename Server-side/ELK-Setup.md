# ELK (Introduction and Setup Guide)
***Notice: This complete guide is taken from [DigitalOcean page](https://www.digitalocean.com/community/tutorials/how-to-install-elasticsearch-logstash-and-kibana-elastic-stack-on-ubuntu-18-04 "ELK Installation in Ubuntu 18.04").***
## Introduction
The *Elastic Stack* — formerly known as the *ELK Stack* — is a collection of open-source software produced by Elastic which allows you to search, analyze, and visualize logs generated from any source in any format, a practice known as *centralized logging*. Centralized logging can be very useful when attempting to identify problems with your servers or applications, as it allows you to search through all of your logs in a single place. It’s also useful because it allows you to identify issues that span multiple servers by correlating their logs during a specific time frame.
<br>The Elastic Stack has four main components:
* **Elasticsearch**: a distributed RESTful search engine which stores all of the collected data.
* **Logstash**: the data processing component of the Elastic Stack which sends incoming data to Elasticsearch.
* **Kibana**: a web interface for searching and visualizing logs.
* **Beats**: lightweight, single-purpose data shippers that can send data from hundreds or thousands of machines to either Logstash or Elasticsearch.

## Prerequisites
To complete this tutorial, you will need the following:
* An Ubuntu 18.04 server set up by following the [Initial Server Setup Guide for Ubuntu 18.04](https://www.digitalocean.com/community/tutorials/initial-server-setup-with-ubuntu-18-04 "Server Setup Guide"), including a non-root user with sudo privileges and a firewall configured with ufw. The amount of CPU, RAM, and storage that your Elastic Stack server will require depends on the volume of logs that you intend to gather. For this tutorial, we will be using a VPS with the following specifications for our Elastic Stack server:
    * OS: Ubuntu 18.04
    * RAM: 4GB
    * CPU: 2
* **Java 8** — which is required by Elasticsearch and Logstash — installed on your server. *Note that Java 9 is not supported.* To install this, follow the [Installing the Oracle JDK](https://www.digitalocean.com/community/tutorials/how-to-install-java-with-apt-on-ubuntu-18-04#installing-the-oracle-jdk "Installing the Oracle JDK") section of our guide on how to install Java 8 on Ubuntu 18.04.
* **Nginx** installed on your server, which we will configure later in this guide as a reverse proxy for Kibana. Follow the guide on [How to Install Nginx on Ubuntu 18.04](https://www.digitalocean.com/community/tutorials/how-to-install-nginx-on-ubuntu-18-04 "How to install Nginx on Ubuntu 18.04") to set this up.
<br>
Additionally, because the Elastic Stack is used to access valuable information about your server that you would not want unauthorized users to access, it’s important that you keep your server secure by installing a TLS/SSL certificate. This is optional but **strongly encouraged**.

## Step 1: Installing and Configuring Elasticsearch
Follow the commands below:
```
$ wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -
$ echo "deb https://artifacts.elastic.co/packages/7.x/apt stable main" | sudo tee -a /etc/apt/sources.list.d/elastic-7.x.list
$ sudo apt update && sudo apt install elasticsearch
```
Once installed, use your preferred text editor to edit Elasticsearch's main configuration file, *elasticsearch.yml*, like this:<br>
`nano /etc/elasticsearch/elasticsearch.yml`
Elasticsearch listens for traffic from everywhere on port `9200`. You will want to restrict outside access to your Elasticsearch instance to prevent outsiders from reading your data or shutting down your Elasticsearch cluster through the REST API. Find the line that specifies `network.host`, uncomment it, and replace its value with `localhost` so it looks like this:
``` /etc/elasticsearch/elasticsearch.yml
. . .
network.host: localhost
. . .
```
Save and close the *elasticsearch.yml* file.<br>
Start the elastic search service with `systemctl` using the following command:
```
$ sudo systemctl start elasticsearch
$ sudo systemctl enable elasticsearch
```
You can test whether your Elasticsearch service is running by sending an HTTP request:
`$ curl -X GET "localhost:9200"`
You will see a response showing some basic information about your local node, similar to this:
``` Output
{
  "name" : "ElasticSearch",
  "cluster_name" : "elasticsearch",
  "cluster_uuid" : "SMYhVWRiTwS1dF0pQ-h7SQ",
  "version" : {
    "number" : "7.6.1",
    "build_flavor" : "default",
    "build_type" : "deb",
    "build_hash" : "aa751e09be0a5072e8570670309b1f12348f023b",
    "build_date" : "2020-02-29T00:15:25.529771Z",
    "build_snapshot" : false,
    "lucene_version" : "8.4.0",
    "minimum_wire_compatibility_version" : "6.8.0",
    "minimum_index_compatibility_version" : "6.0.0-beta1"
  },
  "tagline" : "You Know, for Search"
}
```

## Step 2: Installing and Configuring Kibana Dashboard
Follow the commands below:
``` bash
$ sudo apt install kibana
$ sudo systemctl enable kibana
$ sudo systemctl start kibana
```
Because Kibana is configured to only listen on `localhost`, we must set up a reverse proxy to allow external access to it. We will use Nginx for this purpose, which should already be installed on your server.<br>
First, use the `openssl` command to create an administrative Kibana user which you’ll use to access the Kibana web interface. As an example we will name this account `kibanaadmin`, but to ensure greater security we recommend that you choose a non-standard name for your user that would be difficult to guess.<br>
The following command will create the administrative Kibana user and password, and store them in the `htpasswd.users` file. You will configure Nginx to require this username and password and read this file momentarily:<br>
`$ echo "kibanaadmin:'openssl passwd -apr1'" | sudo tee -a /etc/nginx/htpasswd.users`<br>
Enter and confirm a password at the prompt. Remember or take note of this login, as you will need it to access the Kibana web interface.
Then, type the following commands:
``` bash
$ sudo systemctl restart nginx
$ sudo ufw allow 'Nginx Full'
```
Kibana is now accessible via your FQDN or the public IP address of your Elastic Stack server. You can check the Kibana server’s status page by navigating to the following address and entering your login credentials when prompted:
```
http://your_server_ip/status
```
This status page displays information about the server’s resource usage and lists the installed plugins.
![Kibana Dashboard](http://assets.digitalocean.com/articles/elastic_1804/KibanaDashboard.png "Kibana Dashboard")

## Step 3: Installing and configuring Logstash
Follow the command below:
```bash
$ sudo apt install logstash
```
After installing Logstash, you can move on to configuring it. Logstash’s configuration files are written in the JSON format and reside in the `/etc/logstash/conf.d` directory. As you configure it, it’s helpful to think of Logstash as a pipeline which takes in data at one end, processes it in one way or another, and sends it out to its destination (in this case, the destination being Elasticsearch). A Logstash pipeline has two required elements, `input` and `output`, and one optional element, `filter`. The input plugins consume data from a source, the filter plugins process the data, and the output plugins write the data to a destination.
![Logstash pipeline](https://assets.digitalocean.com/articles/elastic_1804/logstash_pipeline_updated.png "Logstash Pipeline")
Create a configuration file called `02-beats-input.conf` where you will set up your Filebeat input:
```bash
$ sudo nano /etc/logstash/conf.d/02-beats-input.conf
```
Insert the following `input` configuration. This specifies a `beats` input that will listen on TCP port `5044`.<br>
``` "02-beats-input.conf"
input {
  beats {
    port => 5044
  }
}
```
Save and close the file. Next, create a configuration file called `10-logs-filter.conf`, where we will add a filter for logs, also known as *logs*:
```bash
$ sudo nano /etc/logstash/conf.d/10-logs-filter.conf
```
```/etc/logstash/conf.d/10-logs-filter.conf
filter {
    grok {
        match => {["%{IPV4:IP_Address}:%{DATA:LAB_Name}:%{DATA:Date_Of_Audit}:%{DATA:Employee_Name}:%{DATA:System_Name}:%{DATA:System_Version}:%{DATA:Product_ID}:%{DATA:Last_Update_Date}:%{INT:Password_Strength}:%{INT:Number_of_User_Accounts}:%{DATA:Extra_Programs}:%{DATA:Internet_Connectivity}:%{DATA:NIC_List}:%{DATA:Open_Ports}:%{DATA:Established_Connections}:%{DATA:UDP_Ports}:%{DATA:USB_Plugged}:%{INT:Number_of_USBs}:%{DATA:Startup_Apps}:%{DATA:Shared_Folders}:%{INT:Number_of_Shared_Folders}:%{DATA:RDP_Port}:%{DATA:Firewall}:%{DATA:Antivirus}:%{DATA:Unwanted_Programs}:%{INT:Number_of_unwanted_Programs}:%{INT:Final_Score}:%{DATA:Final_Status}:"]}
    }
}
```
Save and close the file when finished.<br>
Lastly, create a configuration file called `30-elasticsearch-output.conf`:
```bash
$ sudo nano /etc/logstash/conf.d/30-elasticsearch-output.conf
```
Insert the following `output` configuration. Essentially, this output configures Logstash to store the Beats data in Elasticsearch, which is running at `localhost:9200`, in an index named after the Beat used. The Beat used in this tutorial is Filebeat:
``` /etc/logstash/conf.d/30-elasticsearch-output.conf
output {
  elasticsearch {
    hosts => ["localhost:9200"]
    manage_template => false
    index => "%{[@metadata][beat]}-%{[@metadata][version]}-%{+YYYY.MM.dd}"
  }
}
```
Save and close the file.<br>
If you want to add filters for other applications that use the Filebeat input, be sure to name the files so they’re sorted between the input and the output configuration, meaning that the file names should begin with a two-digit number between `02` and `30`.<br>
Test your Logstash configuration with this command:
```bash
$ sudo -u logstash /usr/share/logstash/bin/logstash --path.settings /etc/logstash -t
```
If there are no syntax errors, your output will display `Configuration OK` after a few seconds. If you don’t see this in your output, check for any errors that appear in your output and update your configuration to correct them.<br>
If your configuration test is successful, start and enable Logstash to put the configuration changes into effect:
```bash
$ sudo systemctl start logstash
$ sudo systemctl enable logstash
```

## Step 4: Installing and Configuring Filebeat
Follow the command below:
```bash
$ sudo apt install filebeat
```
Next, configure Filebeat to connect to Logstash. Here, we will modify the example configuration file that comes with Filebeat.<br>
Open the Filebeat configuration file:
```bash
$ sudo nano /etc/filebeat/filebeat.yml
```
Change the following:
``` /etc/filebeat/filebeat.yml
...
#input
   - /home/youruser/filebeat_source_location.txt
...
...
#output.elasticsearch:
  # Array of hosts to connect to.
  #hosts: ["localhost:9200"]
...
...
output.logstash:
  # The Logstash hosts
  hosts: ["localhost:5044"]
...
```
Save and close the file.

## You are all set for starting your audits :metal:



