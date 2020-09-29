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
* Finally, copy the *bin* directory to this location.
* Now, the entire directory that contains the *exe* file, along with our 2 directories and all the *dll* files are to be sent to the user of the *exe* file to work.
