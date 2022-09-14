#-------------------------------------------------------------------------------
# Name: Expansion Period Analysis
# Purpose:  Determine periods of BTPD colony expansion or stability, finds the maximum
# distance from the center of merged E/S period to furthest perimeter verticie, buffer
# centroid using maximum distance as radius, asign 0 and 1 coding to on-and-off colony points,
# use points to sample all 13 layers of raster data to output table
#
# Author:      Billy.Armstrong
#
# Created:     20/04/2012
# Copyright:   (c) Billy.Armstrong 2012
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python

def main():
    pass

if __name__ == '__main__':
    main()

import os,sys,arcpy,fnmatch,shutil,csv,math

from random import choice
from arcpy.sa import*
from arcpy import env
gp = arcpy.gp

################################################################################
""" Functions """

def greatest(num_list): # Finds the largest number in a number list
    dist_count = 0
    greatest = 0
    for val in num_list:
        if dist_count == 0:
            greatest = val
            dist_count += 1
        if dist_count == 1:
            if val > greatest:
                greatest = val
    return greatest

# Distance function calculates the distances from a center point to each verticie
# in a polygon, input is a center point xy string and polygon xy coord list

def distance(center_point_str,vert_list):
    dist_list = []
    print "vert list: ",vert_list
    for xy in vert_list:

        print "center point: ",center_point_str
        print "xy verts ",xy
        # Split input center point string into x and y components as float type
        c_xy = center_point_str.split()
        cx = float(c_xy[0])
        cy = float(c_xy[1])
        # Split input xy string into x and y components as float type
        xy_str = xy.split()
        print xy_str
        x = float(xy_str[0])
        y = float(xy_str[1])

        # pathagorian theorm to calculate distance

        x_dif = cx - x
        y_dif = cy - y
        x2 = x_dif*x_dif
        y2 = y_dif*y_dif
        sqrt_val = x2+y2
        buff_dist = math.sqrt(sqrt_val)

        dist_list.append(buff_dist)
    return dist_list

################################################################################
""" Inputs """

# txt of input file paths
fin = []
filein = open(r'D:\Expansion_Analysis\test\paths.txt',"r")
for line in filein:
    fin.append(line)


in_raster = fin[0]
unclipped_raster = fin[1]
in_expansion = fin[2]
in_table_geo = fin[3]
in_raster_geo = fin[4]
study_site_ID = fin[5]
#study_site_ID:  Pawnee East = 1, Pawnee West = 2, Carrizo = 3, Timpas = 4, Rita Blanca = 5, Cimarron = 6, Kiowa = 7")

# Setup working folders
temp_dirs = ["shp","table","expansion","pre_expansion","rasters"]
temp_path = r'c:\temp\Random_Sampling'
temp_shp_dir = os.path.join(temp_path,temp_dirs[0])
temp_table_dir = os.path.join(temp_path,temp_dirs[1])
temp_raster_dir = os.path.join(temp_path,temp_dirs[4])


# Check to see if working folders already exist, if they do then delete

if os.path.isdir(temp_shp_dir):
    shutil.rmtree(temp_shp_dir)

if os.path.isdir(temp_table_dir):
    os.rmdir(temp_table_dir)

if os.path.isdir(temp_path):
    os.rmdir(temp_path)

if os.path.isdir(temp_raster_dir):
    shutil.rmtree(temp_raster_dir)

# Create working folders

os.mkdir(temp_path)
os.mkdir(temp_shp_dir)
os.mkdir(temp_table_dir)
os.mkdir(temp_raster_dir)
pre_expansion_dir = os.path.join(temp_shp_dir,temp_dirs[3])
expansion_dir = os.path.join(temp_shp_dir,temp_dirs[2])
os.mkdir(pre_expansion_dir)
os.mkdir(expansion_dir)

# Arcpy temp workspace
env.workspace = temp_shp_dir

#############################################################################
""" Loop through all colonys, check colony for expansion/stability periods, if periods
exist record them to a dictionary, loop through the related colony E/S periods in the dictionary,
determine the largest distance between pre-expansion centroid and dissolved expansion period,
use greatest distance for the colony expansion distance. """


# Make lyr of expansion shapefile
arcpy.MakeFeatureLayer_management(in_expansion,"expansion_lyr","")
col_id_rows = arcpy.SearchCursor(in_expansion,"","","")
GroupIDs = []
for row in col_id_rows:
    Colony = row.getValue("Group_ID")   # Make sure that all expansion shapefiles have a colony ID ("col_ID") field
    Colony_str = str(Colony)
    Colony_int = int(Colony)


    if Colony_int not in GroupIDs:
        # Udate colony tracking list with colony number
        GroupIDs.append(Colony_int)

        expansion_dict = {}
        beggining = 0
        expansion_set = 0
        expansion_count = 0
        expansion_years = ""

    # Begin expansion period search

        year = row.getValue("Cng_2002")

        if year == "Increasing" or year == "Stable":

            beggining += 1
            expansion_years = "2002 "
            expansion_count += 1
            print expansion_years

        year = row.getValue("Cng_2003")
        if year == "Increasing" or year == "Stable":

            if beggining == 1:
                new_year = "2003 "
                expansion_years= expansion_years + new_year
                expansion_count += 1
                print expansion_years

            if beggining == 0:
                beggining += 1
                expansion_years = "2003 "
                expansion_count += 1
                print expansion_years
        else:
            beggining = 0
            expansion_count = 0
            expansion_years = ""

        year = row.getValue("Cng_2004")
        if year == "Increasing" or year == "Stable":

            if beggining == 1:
                    new_year = "2004 "
                    expansion_years = expansion_years + new_year
                    print "2004_expansion_years: ",expansion_years
                    expansion_count += 1
                    if expansion_count == 3:
                        expansion_set += 1

            if beggining == 0:
                    beggining += 1
                    expansion_years = "2004 "
                    expansion_count += 1
        else:
            beggining = 0
            expansion_count = 0
            expansion_years = ""

        year = row.getValue("Cng_2005")
        if year == "Increasing" or year == "Stable":

            if beggining == 1:
                    new_year = "2005 "
                    expansion_years = expansion_years + new_year
                    expansion_count += 1
                    if expansion_count == 3:
                        expansion_set += 1

            if beggining == 0:
                    beggining += 1
                    expansion_years = "2005 "
                    expansion_count += 1

        if expansion_count >= 3:
            expansion_dict[expansion_set] = expansion_years
            print expansion_dict
            beggining = 0
            expansion_count = 0
            expansion_years = ""
        else:
            beggining = 0
            expansion_count = 0
            expansion_years = ""

        year = row.getValue("Cng_2006")
        if year == "Increasing" or year == "Stable":

            if beggining == 1:
                    new_year = "2006 "
                    expansion_years = expansion_years + new_year
                    print "2006_expansion_years: ",expansion_years
                    expansion_count += 1
                    print "2006 Expansion Count :",expansion_count
                    if expansion_count == 3:
                        expansion_set += 1

            if beggining == 0:
                    beggining += 1
                    expansion_years = "Cng_2006"
                    expansion_count += 1


        if expansion_count >= 3:
            expansion_dict[expansion_set] = expansion_years
            beggining = 0
            expansion_count = 0
            expansion_years = ""
        else:
            beggining = 0
            expansion_count = 0
            expansion_years = ""


        year = row.getValue("Cng_2007")
        if year == "Increasing" or year == "Stable":

            if beggining == 1:
                    new_year = "2007 "
                    expansion_years = expansion_years + new_year
                    expansion_count += 1
                    if expansion_count == 3:
                        expansion_set += 1

            if beggining == 0:
                    beggining += 1
                    expansion_years = "2007 "
                    expansion_count += 1


        if expansion_count >= 3:
            expansion_dict[expansion_set] = expansion_years
            print "expansion_count", expansion_count,expansion_dict
            beggining = 0
            expansion_count = 0
            expansion_years = ""
        else:
            beggining = 0
            expansion_count = 0
            expansion_years = ""

        year = row.getValue("Cng_2008")
        if year == "Increasing" or year == "Stable":

            if beggining == 1:
                    new_year = "2008 "
                    expansion_years = expansion_years + new_year
                    expansion_count += 1
                    if expansion_count == 3:
                        expansion_set += 1
            if beggining == 0:
                    beggining += 1
                    expansion_years = "2008 "
                    expansion_count += 1

        if expansion_count >= 3:
            expansion_dict[expansion_set] = expansion_years
            beggining = 0
            expansion_count = 0
            expansion_years = ""
        else:
            beggining = 0
            expansion_count = 0
            expansion_years = ""

        year = row.getValue("Cng_2009")
        if year == "Increasing" or year == "Stable":

            if beggining == 1:
                    new_year = "2009 "
                    expansion_years = expansion_years + new_year
                    expansion_count += 1
                    if expansion_count == 3:
                        expansion_set += 1


        if expansion_count >= 3:
            expansion_dict[expansion_set] = expansion_years
            beggining = 0
            expansion_count = 0
            expansion_years = ""
        else:
            beggining = 0
            expansion_count = 0
            expansion_years = ""

        year = row.getValue("Cng_2010")
        if year == "Increasing" or year == "Stable":

            if beggining == 1:
                    new_year = "2010"
                    expansion_years = expansion_years + new_year
                    expansion_count += 1
                    if expansion_count == 3:
                        expansion_set += 1

        else:
            if expansion_count >= 3:
                expansion_dict[expansion_set] = expansion_years


###############################################################################################################
        """ Begin dictionary check to see if expansion period(s) exist for colony"""

        if len(expansion_dict) == 0:
            print "Expansion dictionary length = ",len(expansion_dict)
            pass
        if len(expansion_dict) >= 1:
                count = 0
                # list containing the yearly greatest distances between centroid and polygon verticies for each year
                yearly_greatest = []
                expansion_shps = {}


                for num,years in expansion_dict.iteritems():

                    count +=1

                    # Greatest distnace between centroid and verticies for the expansion/stability period
                    greatest_distance = 0

                    years_list = years.split()

                    # Print years
                    print "Colony ",Colony_str,"Expansion Period ",num," Expansion Years: ",years_list

                    #for item in years_list:
                    print years_list
                    #first_year_split = item.split("_")

                    first_year_nu = int(years_list[0])
                    print "first expansion year: ",str(first_year_nu)
                    pre_expansion = first_year_nu - 1
                    pre_expansion_str = "y"+str(pre_expansion)
                    print "pre first expansion year: ",pre_expansion_str

                        # Whereclause for Colony ID
                    col_wc = "Group_ID" + "="+Colony_str+""


                    # Loop through all fields in expansion shp, find columns that match pre-expansion and expansion/stability
                    # For each expansion/stability period, merge all years into new shp
                    # Find centroid of pre-expansion, find furthest point of merge shp from centroid
                    # Calc distance, use distance to create expansion analysis buffer

                    year_fields = arcpy.ListFields(in_expansion,"","")
                    for field in year_fields:
                        field_str = str(field.name)
                        if field_str == pre_expansion_str:
                            print str(field_str)+"pre expanssion year field found"
                            pre_expansion_name = "PE_year_"+pre_expansion_str+".shp"
                            pre_expansion_shp = os.path.join(pre_expansion_dir,pre_expansion_name)

                            val = "1"
                            Pre_ex_wc = field_str + "= "+val+""

                                # Select all rows in colony, subset rows from pre-expansion year
                            arcpy.SelectLayerByAttribute_management("expansion_lyr","NEW_SELECTION",col_wc)
                            arcpy.SelectLayerByAttribute_management("expansion_lyr","SUBSET_SELECTION",Pre_ex_wc)
                            result = int(arcpy.GetCount_management("expansion_lyr").getOutput(0))
                            print "the following number or rows were found to be dissolved into pre-expansion shp: ",str(result)
                            if result >= 1:
                                    # Merge rows from pre expansion year
                                arcpy.Dissolve_management("expansion_lyr",pre_expansion_shp,"Group_ID","","")

                                    # Create centroid shapefile of pre-expansion shapefile
                                pre_expansion_point_name = pre_expansion_name[:-4]+"_point.shp"
                                pre_expansion_centroid = os.path.join(pre_expansion_dir,pre_expansion_point_name)
                                arcpy.FeatureToPoint_management(pre_expansion_shp,pre_expansion_centroid,"")  # Make determination of inside or outside poly boundary

                                point_rows = arcpy.SearchCursor(pre_expansion_centroid)
                                point_describe = arcpy.Describe(pre_expansion_centroid)
                                point_shp = point_describe.ShapeFieldName
                                for p in point_rows:
                                    p_feat = p.getValue(point_shp)
                                    pnt = p_feat.getPart()
                                    center_xy_str = str(pnt.X)+" "+ str(pnt.Y)
                                    print "center point coordinates: "+center_xy_str

                        # Select all expansion/stability years, dissolve into new feature
                    years_len = len(years_list)
                    year_fields2 = arcpy.ListFields(in_expansion,"","")

                        # Loop through field list, find fields that match year, select rows that are increasing or stable

                    years_count = 0
                    for field in year_fields2:
                        for year in years_list:
                            fname = "Cng_"+str(year)
                            if field.name == fname:
                                inc = "Increasing"
                                stb = "Stable"
                                wc = fname + "= "+inc+""
                                wc2 = fname + "= "+stb+""
                                if years_count == 0:
                                    arcpy.SelectLayerByAttribute_management("expansion_lyr","NEW_SELECTION",col_wc)
                                    arcpy.SelectLayerByAttribute_management("expansion_lyr","ADD_TO_SELECTION",col_wc)
                                    years_count += 1
                                if years_count > 0:
                                    arcpy.SelectLayerByAttribute_management("expansion_lyr","ADD_TO_SELECTION",col_wc)
                                    arcpy.SelectLayerByAttribute_management("expansion_lyr","ADD_TO_SELECTION",col_wc)

                     # Remove all rows not in colony
                    arcpy.SelectLayerByAttribute_management("expansion_lyr","SUBSET_SELECTION",col_wc)

                    # Create expansion/stability shapefile
                    Col_expansion_period_name = "Expansion_period_"+str(num)+".shp"
                    Col_expansion_shp = os.path.join(expansion_dir,Col_expansion_period_name)
                    arcpy.Dissolve_management("expansion_lyr",Col_expansion_shp,"Group_ID","","")

                    # Get X and Y Coordinates of each polygon vertex
                    xy_list = []

                    v_desc = arcpy.Describe(in_expansion)
                    shapefieldname = v_desc.ShapeFieldName

                    v_rows = arcpy.SearchCursor(in_expansion)

                    for row in v_rows:

                        feat = row.getValue(shapefieldname)
                        partnum = 0

                        partcount = feat.partCount

                        while partnum < partcount:
                            part = feat.getPart(partnum)
                            pnt = part.next()
                            pntcount = 0

                            while pnt:
                                #print pnt.X, pnt.Y
                                point_str = str(pnt.X)+" "+str(pnt.Y)

                                xy_list.append(point_str)

                                pnt = part.next()
                                pntcount +=1

                                # Check for interior rings
                                if not pnt:
                                    pnt = part.next()
                                    if pnt:
                                        print "interior ring"
                            partnum += 1


                    expansion_distance = greatest(distance(center_xy_str,xy_list))
                    yearly_greatest.append(expansion_distance)
                    expansion_shps_list = [Col_expansion_shp,pre_expansion_centroid]
                    expansion_shps[expansion_distance] = expansion_shps_list

            # Find greatest expansion period distance for the colony
                analysis_distance = greatest(yearly_greatest)

                expansion_buff_len = analysis_distance + 60

            # Retreive pre-expansion centroid and expansion shp paths
                pe_Centroid = expansion_shps[analysis_distance][1]
                dissolved_expansion_years = expansion_shps[analysis_distance][0]

            # Create the expansion shp using pre-expansion points and expansion distance
                expansion_shp = pe_Centroid[:-4]+"_expansion_dist.shp"
                arcpy.Buffer_analysis(pe_Centroid,expansion_shp,expansion_buff_len,"","","","")# Change buffer distance as needed

            # Run a second buffer (16m) on the colony expansion shp to make sure that all pixels within the colony get a point created for them

                expansion_buff_shp = expansion_shp[:-4]+"_16m_ext.shp"
                arcpy.Buffer_analysis(expansion_shp,expansion_buff_shp,32,"","","","")

            # Clip the single raster band by the expansion shp w/16m buffer
                r_name = Colony_str + "_clip.tif"
                r_colony_clip = os.path.join(temp_raster_dir,r_name)
                arcpy.Clip_management(unclipped_raster,"#", r_colony_clip,expansion_buff_shp,-9999,"ClippingGeometry")

            # Set environmental variables for new raster
                arcpy.env.extent = r_colony_clip
                arcpy.env.snapRaster = r_colony_clip

            # Clip the multiple band raster by expansion shp w/16m buffer
                path = r'D:\Expansion_Analysis\Cim_raster.gdb'
                r_name_multi =  "MBC_" + Colony_str
                multi_clip = os.path.join(path,r_name_multi)
                arcpy.Clip_management(in_raster,"#",multi_clip,expansion_buff_shp,-9999,"ClippingGeometry")

            # convert clipped colony raster to points
                R_points_shp_name = Colony_str + "_raster_points.shp"
                R_points_shp = os.path.join(temp_shp_dir,R_points_shp_name)
                arcpy.RasterToPoint_conversion(r_colony_clip,R_points_shp,"")

            # Add status,study site ID, col number fields to clipped points
                arcpy.AddField_management(R_points_shp,"Status","SHORT","","","10","","","","")
                arcpy.AddField_management(R_points_shp,"SiteID","SHORT","","","10","","","","")
                arcpy.AddField_management(R_points_shp,"ColonyN","SHORT","","","10","","","","")

            # Create layer of clipped raster points
                arcpy.MakeFeatureLayer_management(R_points_shp,"raster_clip_points","")

            # Calculate Status values, all occupied = 1, Available = 0
            # Select by dissolved expansion years shp to get occupied
                arcpy.SelectLayerByLocation_management("raster_clip_points","INTERSECT",dissolved_expansion_years,"","NEW_SELECTION")
                arcpy.CalculateField_management("raster_clip_points","Status",1)

            # Select by expansion shp to calculate all rows site ID and Colony ID values
                arcpy.SelectLayerByLocation_management("raster_clip_points","INTERSECT",expansion_shp,"","NEW_SELECTION")

                 # Calculate study site ID field
                arcpy.CalculateField_management("raster_clip_points","SiteID",study_site_ID)

                # Calculate study Colony ID field
                arcpy.CalculateField_management("raster_clip_points","ColonyN",Colony_int)


            # Remove all occupied to calculate available
                arcpy.SelectLayerByLocation_management("raster_clip_points","INTERSECT",dissolved_expansion_years,"","REMOVE_FROM_SELECTION")
                arcpy.CalculateField_management("raster_clip_points","Status",0)


###########################################################################################################################

                """ Convert points, create multi-band variable raster and perform sample  """


                # Set environmental variables for new raster
                arcpy.env.extent = r_colony_clip
                arcpy.env.snapRaster = r_colony_clip

            # Convert points to status raster
                r_status_name = Colony_str+"_status.tif"
                r_status = os.path.join(temp_raster_dir,r_status_name)
                arcpy.PointToRaster_conversion(R_points_shp,"Status",r_status,"","",30)

             # Convert points to Site ID raster
                r_siteID_name = Colony_str+"_site_ID.tif"
                r_siteID = os.path.join(temp_raster_dir,r_siteID_name)
                arcpy.PointToRaster_conversion(R_points_shp,"SiteID",r_siteID,"","",30)

             # Convert points to Colony name raster
                r_Colony_name = Colony_str+"_Colony_name.tif"
                r_Colony = os.path.join(temp_raster_dir,r_Colony_name)
                arcpy.PointToRaster_conversion(R_points_shp,"ColonyN",r_Colony,"","",30)

            # Set Enviro variables to extent and snap of input multiband raster
                arcpy.env.extent = in_raster
                arcpy.env.snapRaster = in_raster

            # Create list of all raster inputs for composite bands tool
                comp_list = [multi_clip,r_status,r_siteID,r_Colony]

            # New composite raster
                comp_raster_name = "FM_"+Colony_str
                comp_raster = os.path.join(path,comp_raster_name)

            # Merge new rasters with existing multiband raster
                arcpy.CompositeBands_management(comp_list,comp_raster)

            # Select all 0 and 1 points from status field of raster points
                wc1 = '"Status" = 1'
                wc2 = '"Status" = 0'
                arcpy.SelectLayerByAttribute_management("raster_clip_points","NEW_SELECTION",wc1)
                arcpy.SelectLayerByAttribute_management("raster_clip_points","ADD_TO_SELECTION",wc2)

            # Sample multi-band raster using selected points

                    # create output table name
                table_n = "Sample_Col_"+Colony_str
                table_path = os.path.join(in_table_geo,table_n)
                    # Check out extension
                arcpy.CheckOutExtension("Spatial")
                arcpy.sa.Sample(comp_raster,"raster_clip_points",table_n,"NEAREST")













