#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Billy.Armstrong
#
# Created:     12/03/2012
# Copyright:   (c) Billy.Armstrong 2012
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
import glob
import shutil
import csv

from random import choice
from arcpy.sa import*
from arcpy import env
gp = arcpy.gp


in_rasters = raw_input("Enter folder containing all 10m rasters for 1 Study Site: ")
in_groupID = raw_input("Enter full path to GroupID shapefile: ")
in_groupId_avail = raw_input("Enter path to GroupID Buffer shapefile: ")
#out_text = raw_input("Enter path to output text file")
out_log = raw_input("Enter path to output log file")
avail_dist = input("Enter 0 for 500m available, 1 for 2km available: ")
f = raw_input("Enter path to output .csv spreadsheet")

# f_out = open(sys.argv[4],"w")
log = open(out_log,"w")

raster_paths = ["","","","","","","","","","","","","","","","",]
raster_names = os.listdir(in_rasters)

# Check rasters for name patterns, when found append full file names to raster_paths
for name in raster_names:
    if fnmatch.fnmatch(name,'*DEM*.tif'):
            full_path = os.path.join(in_rasters,name)
            raster_paths[0] = full_path
    if fnmatch.fnmatch(name,'*TWI*.tif') and "si" not in name:
            full_path = os.path.join(in_rasters,name)
            raster_paths[1] = full_path
    if fnmatch.fnmatch(name,'*TWIsi*.tif'):
            full_path = os.path.join(in_rasters,name)
            raster_paths[2] = full_path
    if fnmatch.fnmatch(name,'*Clay*.tif'):
            full_path = os.path.join(in_rasters,name)
            raster_paths[3] = full_path
    if fnmatch.fnmatch(name,'*DPTH*.tif'):
            full_path = os.path.join(in_rasters,name)
            raster_paths[4] = full_path
    if fnmatch.fnmatch(name,'*Eco*.tif'):
            full_path = os.path.join(in_rasters,name)
            raster_paths[5] = full_path
    if fnmatch.fnmatch(name,'*Organic*.tif'):
            full_path = os.path.join(in_rasters,name)
            raster_paths[6] = full_path
    if fnmatch.fnmatch(name,'*pH*.tif'):
            full_path = os.path.join(in_rasters,name)
            raster_paths[7] = full_path
    if fnmatch.fnmatch(name,'*Range*.tif'):
            full_path = os.path.join(in_rasters,name)
            raster_paths[8] = full_path
    if fnmatch.fnmatch(name,'*SAND*.tif'):
            full_path = os.path.join(in_rasters,name)
            raster_paths[9] = full_path
    if fnmatch.fnmatch(name,'*TEMPMAX*.tif'):
            full_path = os.path.join(in_rasters,name)
            raster_paths[10] = full_path
    if fnmatch.fnmatch(name,'*PRECIP*.tif'):
            full_path = os.path.join(in_rasters,name)
            raster_paths[11] = full_path


# Working folder names
temp_dirs = ["shp","table"]
temp_path = r'c:\temp\Random_Sampling'
temp_shp_dir = os.path.join(temp_path,temp_dirs[0])
temp_table_dir = os.path.join(temp_path,temp_dirs[1])

# Check to see if working folders already exist, if they do then delete them
if os.path.isdir(temp_shp_dir):
    shutil.rmtree(temp_shp_dir)
if os.path.isdir(temp_table_dir):
    os.rmdir(temp_table_dir)
if os.path.isdir(temp_path):
    os.rmdir(temp_path)

# Create working folders
os.mkdir(temp_path)
os.mkdir(temp_shp_dir)
os.mkdir(temp_table_dir)

# Arcpy temp workspace
env.workspace = temp_shp_dir

# GroupID to line
groupIdsplit = os.path.split(in_groupID)
groupIdline_name = groupIdsplit[1][:-4]+"_line.shp"
groupIdline = os.path.join(temp_shp_dir,groupIdline_name)
print groupIdline
arcpy.FeatureToLine_management(in_groupID,groupIdline,"","")

# GroupId line to buffer
intersect_buff = groupIdline[:-4]+"_buff.shp"
arcpy.Buffer_analysis(groupIdline,intersect_buff,1,"FULL","ROUND","","")

# Create a point shapefile of a raster
point_raster = raster_paths[0]
point_shp_name = "raster_points.shp"
point_shp_path = os.path.join(temp_shp_dir,point_shp_name)
arcpy.RasterToPoint_conversion(point_raster,point_shp_name,"")

# Add a delete field, delete intersecting pixels, save to new shp
gp.MakeFeatureLayer(point_shp_path, "non_int_points_temp", "")
new_field_1 = "status"
arcpy.AddField_management("non_int_points_temp",new_field_1,"SHORT","","","10","","","","")

# Initialize points "status" values to 0
arcpy.CalculateField_management("non_int_points_temp",new_field_1,0)

# All intersecting points "status" to 1
# arcpy.SelectLayerByLocation_management("non_int_points_temp","INTERSECT",intersect_buff,"","NEW_SELECTION")
# arcpy.CalculateField_management("non_int_points_temp","status",1)
arcpy.SelectLayerByAttribute_management("non_int_points_temp","CLEAR_SELECTION","")

# Create new shapefile of non-intersecting points

arcpy.SelectLayerByLocation_management("non_int_points_temp","INTERSECT",in_groupId_avail,"","NEW_SELECTION")
arcpy.SelectLayerByLocation_management("non_int_points_temp","INTERSECT",intersect_buff,"","REMOVE_FROM_SELECTION")
non_int_points = point_shp_path[:-4]+"_nonInt.shp"
gp.CopyFeatures("non_int_points_temp",non_int_points)
arcpy.Delete_management("non_int_points_temp","layer")

# New feature layer of non-intersecting points
gp.MakeFeatureLayer(non_int_points, "non_int_points_lyr", "")

# Add GID field to points layer
arcpy.AddField_management("non_int_points_lyr","point_GID","SHORT","","","10","","","","")

# Determine if working with 500m or 2km available area
GID_avail_field = ""
try:
    if avail_dist == 0:
        GID_avail_field = "GID_500m"
        print "500m GID field found"
    if avail_dist == 1:
        GID_avail_field = "GID_2km"
        print "2km GID field found"
except:
    print "Make sure that 'GID_500m' or 'GID_2km' field exist"
    sys.exit()

""" Loop through all GroupIDs of dissolved available, create layer of each GroupID, select
layer against all available GroupIDs, remove GroupID being checked from the selection, if
any availables remain record the gID number. """

# Create Group ID occupied(merged colonies) and Group ID available(buffered) layer
gp.MakeFeatureLayer(in_groupId_avail,"avail_lyr_all")
gp.MakeFeatureLayer(in_groupID,"GroupID_Occ")

# Create searchcursor object to iterate through Group ID available layer
rows = gp.Searchcursor(in_groupId_avail,"","",GID_avail_field)
for row in rows:
        # Create Group ID whereclause
    GID = row.getValue(GID_avail_field)
    GID_string = str(GID)
    print "Working on "+GID_avail_field+" GID: "+GID_string
    GID_wc = GID_avail_field +"= "+GID_string+""

    # Initial Group ID Available selection
    arcpy.SelectLayerByAttribute_management("avail_lyr_all","NEW_SELECTION",GID_wc)

    # Create the individual GroupId available layer
    gp.MakeFeatureLayer("avail_lyr_all", "avail_lyr_selection", "")
    arcpy.SelectLayerByAttribute_management("avail_lyr_all","CLEAR_SELECTION","")

    # Check for overlapping available groups
    arcpy.SelectLayerByLocation_management("avail_lyr_all","INTERSECT","avail_lyr_selection","","NEW_SELECTION")
    arcpy.SelectLayerByAttribute_management("avail_lyr_all","REMOVE_FROM_SELECTION",GID_wc)

    # SearchCursor to check for selected overlapping available Group IDs
    rows1 = gp.Searchcursor("avail_lyr_all","","",GID_avail_field)

    # count of overlapping buffers
    selection_count = 0

    # List of overlapping buffer GIDs
    Buff_overlap_GIDs_master = []
    Buff_overlap_GIDs = []

    # If selection count > 0 repeat SearchCursor loop and extract GID values, add to list
    # if selection_count >= 1:
    for selection in rows1:
        GID_val = selection.getValue(GID_avail_field)
        Buff_overlap_GIDs.append(GID_val)
        selection_count += 1

    print "Number of overlapping available areas found: "+str(selection_count)
    for item in Buff_overlap_GIDs:
        print "Overlapping available GID: "+str(item)+" found"

    """ If there are no overlapping available buffers begin occupied assignment and random point sampling assignment,
        occupied = 1, available used = 2, all other points stay at 0 """


    # list of analyzed overlap available buffers


    if selection_count == 0:
            print "beginning non-overlapping random sampling"

            # Select occupied with same GroupID as loop
            arcpy.SelectLayerByAttribute_management("GroupID_Occ","NEW_SELECTION",GID_wc)

            # Select points which intersect occupied
            #arcpy.SelectLayerByLocation_management("non_int_points_lyr","INTERSECT","GroupID_Occ","","NEW_SELECTION")

            arcpy.SelectLayerByLocation_management("non_int_points_lyr","INTERSECT","avail_lyr_selection","","NEW_SELECTION")
            # Assign GID number to points
            arcpy.CalculateField_management("non_int_points_lyr","point_GID",GID)
            # New selection of points which intersect occupied
            arcpy.SelectLayerByLocation_management("non_int_points_lyr","INTERSECT","GroupID_Occ","","NEW_SELECTION")

            # Create a count of occupied points
            occ_points = 0
            # Loop through occupied points
            row_P = gp.Searchcursor("non_int_points_lyr","","","FID")
            for p in row_P:
                occ_points += 1
            print str(occ_points)+" Occupied points found"

            # Calculate all occupied points to 1
            arcpy.CalculateField_management("non_int_points_lyr",new_field_1,1)
            # Select all points which intersect available/occupied selection
            arcpy.SelectLayerByLocation_management("non_int_points_lyr","INTERSECT","avail_lyr_selection","","NEW_SELECTION")
            # Remove from selection those points which intersect occupied
            arcpy.SelectLayerByLocation_management("non_int_points_lyr","INTERSECT","GroupID_Occ","","REMOVE_FROM_SELECTION")

            # Create list of all available point "FID" values
            avail_fids = []
            # Create a searchCursor object of available points
            row_Avail = gp.Searchcursor("non_int_points_lyr","","","FID")

            # loop through available points get all fids
            for r in row_Avail:
                fid_val = r.getValue("FID")
                avail_fids.append(fid_val)
            print str(len(avail_fids))+" Number of available points found"

            """ randomly select number of points = or < occupied points """
            avail_len = len(avail_fids)
            avail_random_select = []

            while len(avail_random_select) < occ_points:

                    # use choice function from module Random to randomly select fids from available fid list
                    random_point = choice(avail_fids)
                    # add random sample point to list of points
                    avail_random_select.append(random_point)
                    # create where clause for randomly selected FID
                    random_point_str = str(random_point)
                    random_point_wc = "FID" + "= "+random_point_str+""

                    # Create a selection of randomly generated FIDs, begin with a new selection then add to it
                    if len(avail_random_select) == 1:
                        arcpy.SelectLayerByAttribute_management("non_int_points_lyr","NEW_SELECTION",random_point_wc)
                    if len(avail_random_select) > 1:
                        arcpy.SelectLayerByAttribute_management("non_int_points_lyr","ADD_TO_SELECTION",random_point_wc)

            # Calculate selection values to 2
            print "Number of randomly selected points: "+str(len(avail_random_select))
            arcpy.CalculateField_management("non_int_points_lyr",new_field_1,2)


    """ If there are overlapping availables the first GID layer will be analyzed first, after 1 and 2 values have been calculated
        all remaining 0 points which intersect the overlapping available will be calculated to 3

        All points which intersect the first GID layer will have their GID field calculated to that GID value """

    if selection_count >= 1:
            # look for 3 vals

            # Select all points which intersect available/occupied selection
            arcpy.SelectLayerByLocation_management("non_int_points_lyr","INTERSECT","avail_lyr_selection","","NEW_SELECTION")

            # Select occupied with same GroupID as loop
            arcpy.SelectLayerByAttribute_management("GroupID_Occ","NEW_SELECTION",GID_wc)

            # Remove from selection  points which intersect occupied
            arcpy.SelectLayerByLocation_management("non_int_points_lyr","INTERSECT","GroupID_Occ","","REMOVE_FROM_SELECTION")


            avail_overlap_analyzed = gp.Searchcursor("non_int_points_lyr","","","status")
            count_3s = 0

            for point in avail_overlap_analyzed:
                if count_3s < 2:
                    pval = point.getValue("status")
                    if pval == 3:
                        count_3s += 1

            if count_3s == 0:

                print "beginning overlapping non_assigned random sampling"
                # Select points which intersect occupied
                arcpy.SelectLayerByLocation_management("non_int_points_lyr","INTERSECT","GroupID_Occ","","NEW_SELECTION")

                # Create a count of occupied points
                occ_points = 0
                # Loop through occupied points
                row_P = gp.Searchcursor("non_int_points_lyr","","","FID")
                for p in row_P:
                    occ_points += 1

                print str(occ_points)+" Occupied points found"

                # Calculate all occupied points to 1
                arcpy.CalculateField_management("non_int_points_lyr",new_field_1,1)
                # Select all points which intersect available/occupied selection
                arcpy.SelectLayerByLocation_management("non_int_points_lyr","INTERSECT","avail_lyr_selection","","ADD_TO_SELECTION")

                # Assign GID number to points
                arcpy.CalculateField_management("non_int_points_lyr","point_GID",GID)

                # Remove from selection those points which intersect occupied
                arcpy.SelectLayerByLocation_management("non_int_points_lyr","INTERSECT","GroupID_Occ","","REMOVE_FROM_SELECTION")

                 # Create list of all available point "FID" values
                avail_fids = []
                # Create a searchCursor object of available points
                row_Avail = gp.Searchcursor("non_int_points_lyr","","","FID")

                # loop through available points get all fids
                for r in row_Avail:
                    fid_val = r.getValue("FID")
                    avail_fids.append(fid_val)

                print str(len(avail_fids))+" Number of available points found"

                """ randomly select number of points = or < occupied points """
                avail_len = len(avail_fids)
                avail_random_select = []

                while len(avail_random_select) < occ_points:
                    # use choice function from module Random to randomly select fids from available fid list
                    random_point = choice(avail_fids)
                    # add random sample point to list of points
                    avail_random_select.append(random_point)
                    # create where clause for randomly selected FID
                    random_point_str = str(random_point)
                    random_point_wc = "FID" + "= "+random_point_str+""

                    # Create a selection of randomly generated FIDs, begin with a new selection then add to it
                    if len(avail_random_select) == 1:
                        arcpy.SelectLayerByAttribute_management("non_int_points_lyr","NEW_SELECTION",random_point_wc)
                    if len(avail_random_select) > 1:
                        arcpy.SelectLayerByAttribute_management("non_int_points_lyr","ADD_TO_SELECTION",random_point_wc)


                # Calculate values to 2
                arcpy.CalculateField_management("non_int_points_lyr",new_field_1,2)
                print "Number of randomly selected points: "+str(len(avail_random_select))

                #Intersect GID available points selection with overlapping available, if any 0 values are present in selection, calculate them to 3

                arcpy.SelectLayerByLocation_management("non_int_points_lyr","INTERSECT","avail_lyr_selection","","NEW_SELECTION")
                arcpy.SelectLayerByLocation_management("non_int_points_lyr","INTERSECT","avail_lyr_all","","SUBSET_SELECTION")

                point = "0"
                wc = new_field_1 + "= "+point+""
                arcpy.SelectLayerByAttribute_management("non_int_points_lyr","SUBSET_SELECTION",wc)
                arcpy.CalculateField_management("non_int_points_lyr",new_field_1,3)

                # Add GID to list of used available overlaps
                Buff_overlap_GIDs_master.append(GID)

            if count_3s > 0:
                print "beginning overlapping assigned random sampling"
                # Select occupied with same GroupID as loop
                arcpy.SelectLayerByAttribute_management("GroupID_Occ","NEW_SELECTION",GID_wc)
                # Select points which intersect occupied
                arcpy.SelectLayerByLocation_management("non_int_points_lyr","INTERSECT","GroupID_Occ","","NEW_SELECTION")

                # Create a count of occupied points
                occ_points = 0
                # Loop through occupied points
                row_N = gp.Searchcursor("non_int_points_lyr","","","FID")
                for p in row_N:
                    occ_points += 1
                print str(occ_points)+ "Occupied points found"
                # Calculate all occupied points to 1
                arcpy.CalculateField_management("non_int_points_lyr",new_field_1,1)
                 # Select all points which intersect available/occupied selection
                arcpy.SelectLayerByLocation_management("non_int_points_lyr","INTERSECT","avail_lyr_selection","","NEW_SELECTION")

                # Remove from selection any points with vals of 2 or 3
                point2 = "2"
                point3 = "3"
                wc2 = new_field_1 + "= "+point2+""
                wc3 = new_field_1 + "= "+point3+""
                arcpy.SelectLayerByAttribute_management("non_int_points_lyr","REMOVE_FROM_SELECTION",wc2)
                arcpy.SelectLayerByAttribute_management("non_int_points_lyr","REMOVE_FROM_SELECTION",wc3)

                # Assign GID number to points
                arcpy.CalculateField_management("non_int_points_lyr","point_GID",GID)

            # Remove from selection those points which intersect occupied
                arcpy.SelectLayerByLocation_management("non_int_points_lyr","INTERSECT","GroupID_Occ","","REMOVE_FROM_SELECTION")

                # Create list of all available point "FID" values
                avail_fids = []
                # Create a searchCursor object of available points
                row_Avail2 = gp.Searchcursor("non_int_points_lyr","","","FID")

                # loop through available points get all fids
                for r in row_Avail2:
                    fid_val = r.getValue("FID")
                    avail_fids.append(fid_val)

                """ randomly select number of points = or < occupied points """
                avail_len = len(avail_fids)
                print str(avail_len)+" Available points found"
                avail_random_select = []

                while len(avail_random_select) < occ_points:
                    # use choice function from module Random to randomly select fids from available fid list
                    random_point = choice(avail_fids)
                    # add random sample point to list of points
                    avail_random_select.append(random_point)
                    # create where clause for randomly selected FID
                    random_point_str = str(random_point)
                    random_point_wc = "FID" + "= "+random_point_str+""

                    # Create a selection of randomly generated FIDs, begin with a new selection then add to it
                    if len(avail_random_select) == 1:
                        arcpy.SelectLayerByAttribute_management("non_int_points_lyr","NEW_SELECTION",random_point_wc)
                    if len(avail_random_select) > 1:
                        arcpy.SelectLayerByAttribute_management("non_int_points_lyr","ADD_TO_SELECTION",random_point_wc)

                # Calculate values to 2
                arcpy.CalculateField_management("non_int_points_lyr",new_field_1,2)
                print str(len(avail_random_select))+ " Randomly selected points found"
                # Check to see if overlapping availables exist that have not been calculated yet
                non_calc_intersects = []
                for item in Buff_overlap_GIDs:
                    if item not in Buff_overlap_GIDs_master:
                        non_calc_intersects.append(item)

                if len(non_calc_intersects) >= 1:

                    arcpy.SelectLayerByLocation_management("non_int_points_lyr","INTERSECT","avail_lyr_selection","","NEW_SELECTION")
                    arcpy.SelectLayerByLocation_management("non_int_points_lyr","INTERSECT","avail_lyr_all","","SUBSET_SELECTION")
                    point2 = "2"
                    point3 = "3"
                    wc2 = new_field_1 + "= "+point2+""
                    wc3 = new_field_1 + "= "+point3+""
                    arcpy.SelectLayerByAttribute_management("non_int_points_lyr","REMOVE_FROM_SELECTION",wc2)
                    arcpy.SelectLayerByAttribute_management("non_int_points_lyr","REMOVE_FROM_SELECTION",wc3)

                    point0 = "0"
                    wc = new_field_1 + "= "+point0+""
                    arcpy.SelectLayerByAttribute_management("non_int_points_lyr","SUBSET_SELECTION",wc)
                    arcpy.CalculateField_management("non_int_points_lyr",new_field_1,3)
                    Buff_overlap_GIDs_master.append(GID)

    # Delete the available layer selection
    arcpy.Delete_management("avail_lyr_selection","layer")


""" Begin raster analysis and spreadsheet population """


# Remove 0 vals from points layer
wc1 = '"Status" = 1'
wc2 = '"Status" = 2'
arcpy.SelectLayerByAttribute_management("non_int_points_lyr","NEW_SELECTION",wc1)
arcpy.SelectLayerByAttribute_management("non_int_points_lyr","ADD_TO_SELECTION",wc2)

# copy 1 and 2 values to new shapefile then create a new lyr
analysis_points = point_shp_path[:-4]+"_analysis_points.shp"
gp.CopyFeatures("non_int_points_lyr",analysis_points)
# Add XY coordinates to shapefile
arcpy.AddXY_management(analysis_points)
# Add a field to record 1 to whenever a point has successfully been used to extract raster values
arcpy.AddField_management(analysis_points,"Processed","SHORT","","","10","","","","")
# Create a new layer of 1 and 2 points
gp.MakeFeatureLayer(analysis_points, "analysis_points_lyr", "")

# Create CSV output
f_out = open(f, 'w')

writer = csv.writer(f_out)
# Write CSV header/field names
writer.writerow( ('Group_ID','Status','X_Coord','Y_Coord','TWI', 'TWIsi', 'Clay','Restricted_lyr','Ecological_Sites','Organic_Matter','pH','Range_Production','Sand','Temp_Max','Precip') )

xy_curs = gp.Searchcursor("non_int_points_lyr","","","FID")

# Loop through each 1 or 2 point
for row in xy_curs:
    # Create row list for all values to be written to
    spreadsheet_row = []

    # Get GID, status, X val, Y val from point, write to list
    spreadsheet_row.append(row.getValue(GID_avail_field))
    spreadsheet_row.append(row.getValue("Status"))
    spreadsheet_row.append(row.getValue("POINT_X"))
    spreadsheet_row.append(row.getValue("POINT_Y"))
    # Create xy string for GetCellValue_management
    x_string = str(row.getValue("POINT_X"))
    y_string = str(row.getValue("POINT_Y"))
    xy_string = x_string + " "+y_string

    for r in raster_paths:
        try:
            # Get cell val for XY loc
            r_val = arcpy.GetCellValue_management(r,xy_string,"")
            spreadsheet_row.append(r_val)
        except:
            # If error getting val record it to log so that row can be deleated and reprocessed
            error_string = "problem extracting cell value for GID: "+str(GID_avail_field)+"Point X coord: "+ x_string + "Point Y coord: " + y_string
            print error_string
            log.write(error_string)
            log.flush()
























