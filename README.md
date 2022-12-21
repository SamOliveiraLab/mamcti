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
    The code detects the images captured and outputs the edges in terms of pixel coordinates. The pixels of the images taken are 2048 by 2048. 
    For example, this image below has edges located in '[(289, 330), (289, 1874), (1888, 330), (1888, 1874)]' (top_left, bottom_left, top_right, bottom_right):  
    
    ![Figure 2022-12-21 131637](https://user-images.githubusercontent.com/98775102/208978521-504a5386-2245-491c-8186-3b8c76d107e6.png)
    
    Furthermore, the class 'ref_chamber' in the code enables the first image taken, that is manually positioned, to be used as a reference for the position and           orientation of subsequent chambers. The other functions in this library includes drawing the edges, detecting the chamber size and fixing the errors in terms of       both edge recognition and the stage position to capture the chamber in the same position and orientation as the reference. 
    
    However, there is a need to improve the error recognition and adjustment as the algorithm can take the wrong set of edges as shown below: 
    
    ![Figure 2022-12-21 131447](https://user-images.githubusercontent.com/98775102/208979235-3e13b80a-bf23-44c8-b0a5-079a80759dfb.png)

2. In the experiments folder, the codes updated there can be used for different types of experiments according to the design of the microfluidic chamber. For now, it     can only take 1 run through of the experiment. It still needs to be changed to fit the current 'edge_detection_chambers.py' library.
    
 
    
    
