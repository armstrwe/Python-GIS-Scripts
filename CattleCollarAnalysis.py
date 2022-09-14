#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Billy.Armstrong
#
# Created:     21/07/2014
# Copyright:   (c) Billy.Armstrong 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python

def main():
    pass

if __name__ == '__main__':
    main()

import os
import sys
import arcpy
import fnmatch
import shutil

from arcpy.sa import *
from arcpy import env

# temp workspace
env.workspace = r'D:\temp'

# Input pasture raster layers in order; For all except pDogs, order is 22W, CN, 5W
# For pDogs, there is just one raster, for multi-years, look for multi-year raster

    # dist to fence
fence_dist = [r'D:\CPER\Collar_Data\pDog\rasters\22W\FenceDist22W.tif', r'D:\CPER\Collar_Data\pDog\rasters\CN\FenceDistCN.tif', r'D:\CPER\Collar_Data\pDog\rasters\5W\FenceDist5W.tif']
    # dist to H20
H20_dist = [r'D:\CPER\Collar_Data\pDog\rasters\22W\WaterDist22W.tif', r'D:\CPER\Collar_Data\pDog\rasters\CN\WaterDistCN.tif', r'D:\CPER\Collar_Data\pDog\rasters\5W\WaterDist5W.tif']
    # TWI
twi = [r'D:\CPER\Collar_Data\pDog\rasters\TWI\TWI_Neon.tif']
    # Yearly pDog colonies
pdogs = [r'D:\CPER\Collar_Data\pDog\rasters\08_pDog.tif']
    # Multiyear intersect pDog colonies
pdogs_multi = [r'D:\CPER\Collar_Data\pDog\rasters\pDog_multi_year\07_08_pDog.tif']
    # list or master pasture rasters
past_rasters = [r'D:\CPER\Collar_Data\pDog\rasters\pasture_Extent_rasters\22w_15mBuff.tif', r'D:\CPER\Collar_Data\pDog\rasters\pasture_Extent_rasters\CN_15mBuff.tif', r'D:\CPER\Collar_Data\pDog\rasters\pasture_Extent_rasters\5w_15mBuff.tif']
    # List of pasture master point grids
point_grids = [r'D:\CPER\Collar_Data\pDog\shp\22W\Analysis_shps\22W_Master_Grid.shp', r'D:\CPER\Collar_Data\pDog\shp\CN\Analysis_shps\CN_Master_Grid.shp', r'D:\CPER\Collar_Data\pDog\shp\5W\Analysis_shps\5W_Master_Points.shp']

# Folder names
active_name = "Activity"
merge_name = "Merge"
sample_name = "Sample"

# Create analysis lists

    # List of all paths for all yearly deployment activity shps
activity_paths = []

    # List of all sample data for each steer; [[name,folder[raster 1,2,3...]]]
sample_list = []

# Root folder for deployment shapefiles
active_shp_root = r'D:\CPER\Collar_Data\pDog\shp\Cattle_Activity\2008'


# Loop through all years and all deployments, create folders ("Merged" and "Sample")
# Record shp path, merged path, and sample path, add to a sub list [0,1,2 order...]


deps = os.listdir(active_shp_root)
for dep in deps:
        dep_path = os.path.join(active_shp_root,dep)

        print "path to deployment activity folder of shps: ",dep_path

        # Create Activity rasters folder
        active_folder = os.path.join(dep_path, active_name)
        os.mkdir(active_folder)

        # Create Merged activity points folder
        merge_dir = os.path.join(dep_path, merge_name)
        os.mkdir(merge_dir)

        # Create Sample tables folder
        sample_dir = os.path.join(dep_path, sample_name)
        os.mkdir(sample_dir)

        dir_files = os.listdir(dep_path)
        dep_shp_names = []
        for d in dir_files:
            if d.endswith('.shp'):
                dep_shp_names.append(d)

        for shp in dep_shp_names:
            # Shp list to add to master
            shp_list = [] # shp path = 0, merge dir = 1, sample dir = 2, pasture raster = 3, pdogs yearly = 4, point grid = 5, active raster folder = 6, twi = 7, water dist = 8,
            # fence dist = 9, combined years pdogs = 10, pasture name = 11

            dep_shp_path = os.path.join(dep_path,shp)
            shp_list.append(dep_shp_path)
            shp_list.append(merge_dir)
            shp_list.append(sample_dir)
            print "working with SHP, ", shp

            if "22W" in shp:
                shp_list.append(past_rasters[0])
                shp_list.append(pdogs[0])
                shp_list.append(point_grids[0])
                shp_list.append(active_folder)
                shp_list.append(twi[0])
                shp_list.append(H20_dist[0])
                shp_list.append(fence_dist[0])
                shp_list.append(pdogs_multi[0])
                shp_list.append("22W")

            if "CN" in shp:
                shp_list.append(past_rasters[1])
                shp_list.append(pdogs[0])
                shp_list.append(point_grids[1])
                shp_list.append(active_folder)
                shp_list.append(twi[0])
                shp_list.append(H20_dist[1])
                shp_list.append(fence_dist[1])
                shp_list.append(pdogs_multi[0])
                shp_list.append("CN")

            if "5W" in shp:
                shp_list.append(past_rasters[2])
                shp_list.append(pdogs[0])
                shp_list.append(point_grids[2])
                shp_list.append(active_folder)
                shp_list.append(twi[0])
                shp_list.append(H20_dist[2])
                shp_list.append(fence_dist[2])
                shp_list.append(pdogs_multi[0])
                shp_list.append("5W")

            activity_paths.append(shp_list)

# Begin work on each shapefile
for shp_list in activity_paths:
    shp = shp_list[0]

    # Reset all environmental settings
    arcpy.ResetEnvironments()


    # Create list of all paths to rasters to be sampled
    sample_list = []
    shp_folder = os.path.dirname(shp)
    shp_fileName = os.path.basename(shp)[:-4]

    # Add fields
    # Add non-active fixes
    arcpy.AddField_management(shp,"nonActv","SHORT","","","","","","","")

    # Add all fixes
    arcpy.AddField_management(shp,"allFixes","SHORT","","","","","","","")

    # Create activity selection layer
    # Activity layer name
    lyr_name = shp_fileName +".lyr"

    # Create layer
    actv_lyr = arcpy.MakeFeatureLayer_management(shp,lyr_name,"","","")

    # List all fields in activity shapefile
    fields = arcpy.ListFields(shp)
    for f in fields:
        fname = f.name
        fnameUp = fname.upper()

        # Find activity field
        if fnmatch.fnmatch(fnameUp,'*ACTIV*'):
            # Calculate fields
            # Active 1 where clause
            Active_str = "1"
            wc = fname + "= "+Active_str+""
            arcpy.SelectLayerByAttribute_management(actv_lyr,"NEW_SELECTION",wc)

# Merge active 1 points

            Active_points = shp_fileName+"Active1.shp"
            active_folderpath = shp_list[1]

            Active_points_path = os.path.join(active_folderpath, Active_points)


            # Create merge of active 1 points and master points grid
            arcpy.Merge_management([shp_list[5],actv_lyr], Active_points_path)

# Set non-active points to 1, Merge

            arcpy.SelectLayerByAttribute_management(actv_lyr,"SWITCH_SELECTION")
            arcpy.CalculateField_management(actv_lyr,"nonActv",1)

            # Create merge of non-active and master points grid
            nonActive_points = shp_fileName+"nonActive1.shp"
            nonActive_points_path = os.path.join(shp_list[1],nonActive_points)


            # Create merge of non-active 1 points and master points grid
            arcpy.Merge_management([shp_list[5],actv_lyr], nonActive_points_path)

# Set all points to 1, Merge

            arcpy.SelectLayerByAttribute_management(actv_lyr,"CLEAR_SELECTION")
            arcpy.CalculateField_management(actv_lyr,"allFixes",1)

            # Create merge of all points and master points grid
            all_points = shp_fileName+"Allpoints.shp"
            all_points_path = os.path.join(shp_list[1],all_points)

            # Create merge of all points and master points grid`1
            arcpy.Merge_management([shp_list[5],actv_lyr], all_points_path)


# Create activity 1 raster

                # Set environmental variables
            env.extent = shp_list[3]
            env.snapRaster = shp_list[3]

            # Activity 1 raster path
            Active1_Raster = os.path.join(shp_list[6],"Actv1_"+shp_fileName+".tif")

            # Create Active 1 raster
            arcpy.PointToRaster_conversion(Active_points_path, f.name, Active1_Raster, "SUM","",10.0)

# Create non-active raster

            # Set environmental variables
            env.extent = shp_list[3]
            env.snapRaster = shp_list[3]

            # non-Activ 1 raster path
            nonActive_Raster = os.path.join(shp_list[6],"nonActv1_"+shp_fileName+".tif")

            # Create non-Active 1 raster
            arcpy.PointToRaster_conversion(nonActive_points_path, "nonActv", nonActive_Raster, "SUM","",10.0)

# Create combined active and non-active raster

            # Set environmental variables
            env.extent = shp_list[3]
            env.snapRaster = shp_list[3]

            # combined activity raster path
            Combined_actv_Raster = os.path.join(shp_list[6],"All_activity_"+shp_fileName+".tif")
            # Create combined activity raster
            arcpy.PointToRaster_conversion(all_points_path, "allFixes", Combined_actv_Raster, "SUM","",10.0)

# Set all rasters into a sample list

    Individual_sample = [] # filename [0],output sample folder [1], list of all raster layers [2], pasture name [3]
    raster_layers = []

    # Add the file name
    Individual_sample.append(shp_fileName)
    # Add the sample folder
    Individual_sample.append(shp_list[2])
    # Add all raster layers to raster layers list
        #0 = dist to fence, 1 = dist to water, 2 = twi, 3 =  pdog yearly, 4  = active 1, 5 = non-active, 6 = combined activity 7 = Multi year p-Dog

    raster_layers.append(shp_list[9]) # Dist to fence
    raster_layers.append(shp_list[8]) # Dist to water
    raster_layers.append(shp_list[7]) # twi
    raster_layers.append(shp_list[4]) # pdog yearly

    raster_layers.append(Active1_Raster) # Active 1
    raster_layers.append(nonActive_Raster) # non active
    raster_layers.append(Combined_actv_Raster) # Combined activity and non-activity

    raster_layers.append(shp_list[10]) # pdog combined

    Individual_sample.append(raster_layers)
    Individual_sample.append(shp_list[11])

    # Create output sample table
    sample_name = os.path.join(Individual_sample[1],Individual_sample[0]+"_Sample.dbf")

    # Check out the ArcGIS Spatial Analyst extension license
    arcpy.CheckOutExtension("Spatial")

    for item in Individual_sample[2]:
        print item
    print Individual_sample[3]


    if Individual_sample[3] == "22W":
        Sample([Individual_sample[2][0],Individual_sample[2][1],Individual_sample[2][2],Individual_sample[2][3],Individual_sample[2][4],Individual_sample[2][5],Individual_sample[2][6],Individual_sample[2][7]],point_grids[0],sample_name, "NEAREST")


    if Individual_sample[3] == "CN":
        Sample([Individual_sample[2][0],Individual_sample[2][1],Individual_sample[2][2],Individual_sample[2][3],Individual_sample[2][4],Individual_sample[2][5],Individual_sample[2][6],Individual_sample[2][7]],point_grids[1],sample_name, "NEAREST")

    if Individual_sample[3] == "5W":
        Sample([Individual_sample[2][0],Individual_sample[2][1],Individual_sample[2][2],Individual_sample[2][3],Individual_sample[2][4],Individual_sample[2][5],Individual_sample[2][6],Individual_sample[2][7]],point_grids[2],sample_name, "NEAREST")




























































