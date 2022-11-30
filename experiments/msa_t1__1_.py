# -*- coding: utf-8 -*-
"""
Created on Thu Sep 22 16:38:45 2022

@author: Aurelia Leona
"""
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
    path = file_path + '\\' + filename
    return  path

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
exp_length = 'test102'

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
        img_phc= capture_and_save(path, channel_name, 1,1)
    f= capture_and_save(path, channel_name, 1,1)
    
    
#%%
## Get original image data as reference 
path = json.dumps(img_phc)
img_input= cv2.imread(img_phc,0)
ref_img = edc.ref_chamber(img_input,100)
ref_edge, ref_midpt, ref_mlg, ref_t, listof_t, ref_area, ori_area = ref_img.ori_image_data()
## Set a basic shape of the matrix of locations based on the drawing by Sam 
matrix = []

edc.draw_box(ref_edge, img_input, 'trial1')

#%% Going through each chambers 
# for i, positions in enumerate(matrix): 
core.set_config('Channels', 'PHC')
input_img= capture_only()
sobel_img= edc.sobel_operations(input_img)
#%% 

edges, mid, LL = edc.findedges(sobel_img, ref_t ,ref_mlg)

#%%
move_on= edc.check_edges(edges, ori_area)
XY_coord= core.get_xy_stage_position()
x= XY_coord.get_x()
y= XY_coord.get_y()
while move_on== False:
    move_x , move_y , _ = edc.reform_edge(move_on, ref_midpt, midpoint2, ref_edge, edges_t2, LL, sobel_t2.shape)
    core.set_xy_position(x + move_x, y + move_y)
    #Recapture the image to see if the movement fixed the position 
    new_img= capture_only()
    sobel_img= edc.sobel_operations(new_img)
    edges, mid, LL = edc.findedges(sobel_img, ref_t ,ref_mlg)
    move_on= edc.check_edges(edges, ori_area)

    # for channel_name in list_of_channel_names:
    #     #change the configuration
    #     core.set_config('Channels', channel_name)
    #     directory = channel_name + '_' + exp_length + '_XY' + str(1)
    #     path = os.path.join(parent_dir, directory)
    #     os.mkdir(path)
    #     pix= capture_and_save(path, channel_name, 1,1)
    #     #Get the x, y coordinates of the stage 
    #     XY_coord= core.get_xy_stage_position()
    #     x= XY_coord.get_x()
    #     y= XY_coord.get_y()
    #     X_data.append(x)
    #     Y_data.append(y)
    #     print(x,y)

#%% 
#Try moving the stage in which 1 unit is 1 micrometer
core.set_xy_position(x + 500, y + 500)
XY_coord= core.get_xy_stage_position()
x_new= XY_coord.get_x()
y_new= XY_coord.get_y()
X_data.append(x_new)
Y_data.append(y_new)
print(x_new,y_new)

#%%
#try returning it back to the original x,y from the list we obtained
core.set_xy_position(X_data[0],Y_data[0])
x= X_data[0]
y= Y_data[0]
print(x,y)

#%%
#### Calling core functions ###
exposure = core.get_exposure()

#### Setting and getting properties ####
#Here we set a property of the core itself, but same code works for device properties
auto_shutter = core.get_property('Core', 'AutoShutter')
core.set_property('Core', 'AutoShutter', 0)

#%% 
#Showing the images 
#pixels by default come out as a 1D array. We can reshape them into an image
#plot it
plt.imshow(pixels, cmap='gray')
plt.show()



#%% 
#12 AM run 

#Get the x, y coordinates of the stage 
XY_coord= core.get_xy_stage_position()
x_error= XY_coord.get_x()
y_error= XY_coord.get_y()

# currently its 1st chamber 
directory ='PHC' + '_' + exp_length + '_XY_error'+ str(1)

path = os.path.join(parent_dir, directory)
os.mkdir(path)
capture_and_save(path, 'PHC', 1,1)







