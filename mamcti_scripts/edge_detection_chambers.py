# -*- coding: utf-8 -*-
"""
Created on Wed Nov  2 11:58:36 2022

@author: Aurelia Leona
"""
import numpy as np
import matplotlib.pyplot as plt
import cv2
import pathlib 
import skimage.exposure as exposure
import math


#Input the reference chamber details 
class ref_chamber:

    def __init__(self, image, index_height):
        self.input_image = image
        self.ref_height= index_height
      
    def ori_image_data(self):
        sobel_image= sobel_operations(self.input_image)
        ori_area= sobel_image.shape[0]*sobel_image.shape[1]
        ori_edge = []
        ref_edge =[]
        ori_midpoint =[]
        list_mlg = []
        listof_t =[]
        minarea= 0.53*ori_area
        maxarea= 0.60*ori_area

        for t in np.arange(60,80,1): 
            for mlg in [5,10]: 
                edge, midpt,_,_ = findedges(sobel_image,t,mlg)
                if chamber_size(edge) > minarea and chamber_size(edge) <maxarea:
                    if min(edge)[0] != 0 or min(edge)[1] != 0: 
                         ori_edge.append(edge)
                         ori_midpoint.append(midpt)
                         list_mlg.append(mlg)
                         listof_t.append(t)
                         
        area = ori_area
        for i, edge in enumerate(ori_edge):
            calc_area = chamber_size(edge)
            if calc_area < area :
                ref_edge = edge
                ref_mlg = list_mlg[i]
                ref_t = listof_t[i]
                ref_area = calc_area
                ref_midpt= ori_midpoint[i]
                area= calc_area

        return ref_edge, ref_midpt, ref_mlg, ref_t, listof_t, ref_area, ori_area
        
  
    
    
def sobel_operations(inp_img): 
    img = cv2.GaussianBlur(inp_img,(0,0),1.3,1.3)
    
    sobelx = cv2.Sobel(src=img, ddepth=cv2.CV_64F, dx=1, dy=0, ksize=3) 
    sobely = cv2.Sobel(src=img, ddepth=cv2.CV_64F, dx=0, dy=1, ksize=3)
    
    #Improving on Sobel 
    # square 
    sobelx2 = cv2.multiply(sobelx,sobelx)
    sobely2 = cv2.multiply(sobely,sobely)
    
    # add together and take square root
    sobel_magnitude = cv2.sqrt(sobelx2 + sobely2)
    
    # normalize to range 0 to 255 and clip negatives
    sobel_magnitude = exposure.rescale_intensity(sobel_magnitude, in_range='image', out_range=(0,255)).clip(0,255).astype(np.uint8)


    return sobel_magnitude


def findedges(img_matrix, t, mlg): 
    img2= img_matrix.copy() 
    
    # https://www.geeksforgeeks.org/line-detection-python-opencv-houghline-method/

    lines_list =[]
    lines = cv2.HoughLinesP(
                img2, # Input edge image
                1, # Distance resolution in pixels
                np.pi/180, # Angle resolution in radians
                threshold=t, # Min number of votes for valid line
                minLineLength=550, # Min allowed length of line
                maxLineGap= mlg # Max allowed gap between line for joining them
                )
     
    # Iterate over points
    for points in lines:
        # Extracted points nested in the list
        x1,y1,x2,y2=points[0]
        # Draw the lines joing the points
        # On the original image
        # Maintain a simples lookup list for points
        lines_list.append([(x1,y1),(x2,y2)])

    smallest_diff= 50 #in terms of pixels or micrometer 
    vert_lines= []
    hor_lines = []
    for i, lines_coor in enumerate(lines_list): 
        
        if ( abs(lines_coor[0][0]-lines_coor[1][0]) <= smallest_diff ): 
            vert_lines.append(lines_coor)

        if (abs(lines_coor[0][1]-lines_coor[1][1]) <= smallest_diff ): 
            hor_lines.append(lines_coor)
             
    minv= img2.shape[1]
    maxv= 0
    for i, lines in enumerate(vert_lines):
        if min(lines)[0] < minv:
            # vleft= lines
            minv= min(lines)[0]
        
        if max(lines)[0]> maxv:
            # vright = lines
            maxv= max(lines)[0]
  
    minh= img2.shape[0]
    maxh= 0
    for i, lines in enumerate(hor_lines):
        if min(lines)[1] < minh:
            # htop= lines
            minh= min(lines)[1]
        
        if max(lines)[1]> maxh:
            # hbottom = lines
            maxh= max(lines)[1]
          
    # LL.append(vleft)
    # LL.append(vright)       
    # LL.append(htop)
    # LL.append(hbottom)   
 
    boxcoor=[(minv,minh), (minv,maxh), (maxv,minh), (maxv,maxh)]
    # top_left, bottom_left, top_right, bottom_right
    midpoint = ((minv+maxv)/2 ,(minh+maxh)/2  )
    return boxcoor, midpoint

def chamber_size(boxcoor): 
    area = abs(boxcoor[0][1]-boxcoor[1][1])* abs(boxcoor[0][0]-boxcoor[2][0])
    return area 

def check_edges(boxcoor, ori_area): 
    # Debug to see if we get a good box 
    area= chamber_size(boxcoor)
    if  0.50*ori_area < area and area < 0.70*ori_area:
        move_on = True
    else :
        move_on = False
    return  move_on

def fix_edge_position(ref_midpt, ref_edge, ref_t, ref_mlg, ori_area, sobel_image,  errorimg_size):
   
   edges,new_midpt, vert_lines, hor_lines = findedges(img_matrix, ref_t,  ref_mlg)
   move_on= check_edges(edges, ori_area)
   if move_on:
       x= ref_midpt[0]-ref_midpt[1]
       y= new_midpt[1]-ref_midpt[1]
       boxcoor_new= edges
   else: 
       if chamber_size(edges) < chamber_size(ref_edge):
           rightdiff=500 #100 pixels
           
           if abs(edges[0][0]-edges[2][0])<rightdiff:
               if edges[2][0] <  img_size[0]/2:
                   #maximum vertical point is less than the half point
                   #box is in the 1st or 2nd quadrant 
                   minv=0
                   maxv=edges[2][0]
                   x = ref_edge[2][0] - maxv 
                   
               elif edges[0][0] >  img_size[0]/2:
                   #minimum vertical point is more than the half point
                   #box is in the 3rd or 4th quadrant 
                   minv= edges[2][0]
                   maxv=  img_size[0]
                   x= ref_edge[0][0] - minv
     
                  
           if abs(edges[0][1]-edges[1][1])<rightdiff:
               if edges[1][1] <img_size[1]/2:
                   #maximum horizontal point is less than the half point
                   #move the box to the right
                   minh=0
                   maxh=edges[1][1]
                   y = maxh - ref_edge[1][1]
               elif edges[0][1] > img_size[1]/2 : 
                   #minimum horizontal point is more than the half point
                   #move the box to the left
                   minh= edges[1][1]
                   maxh= img_size[1]
                   y = minh - ref_edge[0][1]
  
#        else:
#            #the horizontal line is way too long!!!! 
#            if edges[2][0]-edges[0][0] > ref_edge[2][0]-ref_edge[0][0]:
               
#                for i, lines in enumerate(vert_lines):
                  
#                    if maxv-minv > ref_edge[2][0]-ref_edge[1][0]:
#                       if min(lines)[0] < minv:
#                        # vleft= lines

#                       if max(lines)[0]> maxv:
#                        # vright = lines
                         
#                     else: 
# =
#             else: 
#               minv= edges[0][0]
#               maxv= edges[2][0]
             
#                minh= img2.shape[0]
#                maxh= 0
#                for i, lines in enumerate(hor_lines):
#                    if min(lines)[1] < minh:
#                        # htop= lines
#                        minh= min(lines)[1]
                   
                   if max(lines)[1]> maxh:
                       # hbottom = lines
                       maxh= max(lines)[1]
                       
                       
                       
       boxcoor_new=[(minv,minh), (minv,maxh), (maxv,minh), (maxv,maxh)]
       #Find location of the edges that is detected!!
       # Figure out where it is in the quadrants and assume it will go to the ref_edge
       
   return x*0.0625 , y*0.0625 , boxcoor_new


def draw_box(boxcoor, img, nama):
    img_use= img.copy()
    cv2.line(img_use,boxcoor[0],boxcoor[1],(255,0,0),5)
    cv2.line(img_use,boxcoor[0],boxcoor[2],(255,0,0),5)
    cv2.line(img_use,boxcoor[1],boxcoor[3],(255,0,0),5)
    cv2.line(img_use,boxcoor[2],boxcoor[3],(255,0,0),5)
    plt.imshow(img_use)
    plt.title(nama)
    plt.show()
    return 


        
        
       
    
    
    
    
    