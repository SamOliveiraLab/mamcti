# Microscope Stage Automation for Multiple-location Chamber Time-lapse Imaging

This repository, `mamcti`, contains the codes needed to automate the movement of the microscope stage with respect to a matrix of the chamber positions in a microfluidic chip. It is automated to capture a multi-channel time-lapse experiment. It corrects the errors in alignment using a chamber detection algorithm real-time. It also interfaces with `MLIDA` to conduct on the flu image analysis. 

# Setting up your environment
1. Create a new conda environment using
```
conda create --name <NAME>
```
2. Install the following packages using anaconda:

     - Python
     - Spyder
     - pycromanager
     - matplotlib
     - scikit-learn
     - opencv
     - pandas
     - numpy
     - skimage


via:

```
conda install <PACKAGE>
```

# Setting up Micromanager 2.0 in your microscope computer
1. Install [Micromanager 2.0](https://micro-manager.org/Version_2.0) using instructions on the website into the computer that is connected to the microscope.

2. There is a need to do a hardware configuration to connect the microscope to the program. Check out the [Micromanager page](https://micro-manager.org/wiki/Micro-Manager_Configuration_Guide#Hardware_Configuration_Wizad) to walk you through it. 
    a. For our case, we add 'Ti2_Mic_Driver.dll' file into the Micro-Manager program file in the computer because we use a Nikon Ti2 microscope
    b. We also use a PCO camera, so we added 'PCO_CDlg.dll' , 'PCO_Conv.dll', and 'PCO_Kamlib64.dll' files into the same program file.  

# What the current code entails 
1. 'edge_detection_chambers.py' is a function code that helps detect the edges of the chamber present in the images captured under a normal PHC light.
Sample of the image detection using this code is as shown below. 


