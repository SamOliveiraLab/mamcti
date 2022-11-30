# -*- coding: utf-8 -*-
"""
Created on Wed Nov 16 11:15:51 2022

@author: Aurelia Leona
"""

#%% 
import os 
# import pathlib 
import time 
import cv2
from pycromanager import Core
import numpy as np
import matplotlib.pyplot as plt
import edge_detection_chambers as edc

#Setup
# get object representing MMCore to bridge between MM and Pycromanager
core = Core()
print(core)


## Acquiring images and Saving them####
# Make sure MM program is not capturing images LIVE for the function to work 
def capture_and_save(file_path, channel_name, iter_time, chamber_num ):
    #The micro-manager core exposes several mechanisms for acquiring images. In order to
    #not interfere with other pycromanager functionality, this is the one that should be used
    #can only run when live function is off
    #Add 0.5 milliseconds delay before capture so that we give the microscope time to move and PFS to adjust 
    core.set_config('Channels', channel_name)
    time.sleep(0.5)
    core.set_exposure(10)
    core.snap_image()
    tagged_image = core.get_tagged_image()
    pixels = np.reshape(tagged_image.pix,
                            newshape=[tagged_image.tags['Height'], tagged_image.tags['Width']])
    
    #Create a filename
    if iter_time < 10:
        str_time = '00'+str(iter_time)
    elif iter_time < 100:
        str_time = '0'+str(iter_time)
    else: 
        str_time = str(iter_time)
    
    filename = 'img_'+ channel_name + '_XY' + str(chamber_num) + '_T' + str_time + '.tif'
    os.chdir(file_path)
    cv2.imwrite(filename,pixels)
    return  

## Only Acquire the image and not save ## 
def capture_only ():
    time.sleep(0.5)
    core.set_exposure(10)
    core.snap_image()
    tagged_image = core.get_tagged_image()
    pixels = np.reshape(tagged_image.pix,
                            newshape=[tagged_image.tags['Height'], tagged_image.tags['Width']])
    return pixels

#%%
### Initialization ###

#initialize your folder here 
parent_dir = "D:\CIDAR\Sam\Aurelia\image_111622"
# indicate the length of your experiment
exp_length = 'test101'

## Collecting Coordinates of the chamber while snapping the images ##
#Initialize data that will keep a record of the chambers we want to see. 
X_data=[]
Y_data=[]


#%%
# Capturing the first chamber
# Setting the microscope to use different lights that is already configured
# in the hardware configuration under 'Groups' and 'Presets'
list_of_channel_names = {'PHC', 'GFP', 'mCherry'}
#change the configuration
#Get the x, y coordinates of the stage for the first chamber 
XY_coord= core.get_xy_stage_position()
x= XY_coord.get_x()
y= XY_coord.get_y()
X_data.append(x)
Y_data.append(y)
print(x,y)

for channel_name in list_of_channel_names:
    # currently its 1st chamber 
    directory = channel_name + '_' + exp_length + '_XY' + str(1)
    path = os.path.join(parent_dir, directory)
    os.mkdir(path)
    if channel_name == 'PHC':
        img_phc= capture_only()
    capture_and_save(path, channel_name, 1,1)
    
    
#%%
## Get original image data as reference ##
ref_img = edc.ref_chamber(img_phc,100)
ref_edge, ref_midpt, ref_mlg, ref_t, listof_t, ref_area, ori_area = ref_img.ori_image_data()
## Set a basic shape of the matrix of locations based on the drawing by Sam 
matrix = []
    
#%% Going through each chambers 
for positions in matrix: 
    core.set_config('Channels', 'PHC')
    move_on= False
    while move_on== False:
        input_img= capture_only()
        sobel_img= edc.sobel_operations(input_img)
        edges, mid, line_list = edc.findedges(sobel_img,ref_t,ref_mlg)
        #Recapture the image to see if the movement fixed the position
        
        #Next_t 
        move_on= edc.check_edges(edges, ori_area)
    
    for channel_name in list_of_channel_names:
        #change the configuration
        core.set_config('Channels', channel_name)
        directory = channel_name + '_' + exp_length + '_XY' + str(1)
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        pix= capture_and_save(path, channel_name, 1,1)
        #Get the x, y coordinates of the stage 
        XY_coord= core.get_xy_stage_position()
        x= XY_coord.get_x()
        y= XY_coord.get_y()
        X_data.append(x)
        Y_data.append(y)
        print(x,y)



#%%













