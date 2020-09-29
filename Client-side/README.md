# Client-Side Software
## What is it?
'ASNA.py' is the main client-side software that has to run in order to audit the system and generate the report.
It is supported on the files that are in the 'bin' directory.

## Where do I start?
First, make sure that all the python requirements are fulfilled. Then, run the following command: <br>
```
> python setup.py build
```
This will generate the binary executable for ASNA inside build folder. <br/>
> **Important Notice:** Due to build errors of *cx-freeze* module, you have to manually make some changes in the build directory


Make the following changes:
* Go to *build* directory, and then the directory within it. You will find some *.dll* files and a *lib* directory within it along with the binary executable.
* Inside *lib* directory, rename the directory named **Tkinter** to **tkinter** (with a smaller case 't').
* Also, copy all the *.dll* files from the *lib* directory in the main directory, where the binary executable presides.
* Copy the *bin* directory to this location.
* Download and copy [rockyou.txt](https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=&ved=2ahUKEwic2oPi1I3sAhW-xzgGHVuzBRsQFjAAegQIBBAB&url=https%3A%2F%2Fgithub.com%2Fbrannondorsey%2Fnaive-hashcat%2Freleases%2Fdownload%2Fdata%2Frockyou.txt&usg=AOvVaw3snAERl1mU6Ccr4WFEazBd) in *bin* directory
* Now, the entire directory that contains the *exe* file, along with our 2 directories and all the *dll* files are to be sent to the user of the *exe* file to work.
