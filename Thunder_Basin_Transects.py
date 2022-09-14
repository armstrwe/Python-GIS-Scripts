#-------------------------------------------------------------------------------
# Name:        module1
# Purpose: Finds suitable area for 30m transects inside and outside of fire perimeter,
# Randomly selects transect begining and orientation from within suitable area, outputs
# a shapefile of transect pairs for all ecological sites

# Author:      Billy.Armstrong
#
# Created:     05/11/2013
# Copyright:   (c) Billy.Armstrong 2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python

def main():
    pass

if __name__ == '__main__':
    main()

import os,sys,arcpy,math,random,string
from arcpy import env
from random import choice

##############################################################################################################################
                    # Input features
table_shp = r'D:\Thunder_Basin\Transects\table_xy_rows\11_18_Sandy1014.shp'
inshp = r'D:\Thunder_Basin\GIS\Sampling\Sample_Points_400k.shp'
Fires = r'D:\Thunder_Basin\GIS\FireHistory\All_Years_Shapefiles\Fires_All_V1.shp'
PerimBuff = r'D:\Thunder_Basin\GIS\FireHistory\All_Years_Shapefiles\Fires_All_V1_1kmBuff.shp'
allotment_shp = r'D:\Thunder_Basin\GIS\Allotments_All.shp'
fireHistoryPoint = r'D:\Thunder_Basin\GIS\FireHistoryPoints2xBuff.shp'

# Clipped ecosites (w/50m from fire perimeter, 30m from edge of eco site, Intersected with ownership)
loamyPb = r'D:\Thunder_Basin\GIS\EcoSites\Loamy_10_14_NF_Final.shp'
loamyPvt = r'D:\Thunder_Basin\GIS\EcoSites\Loamy_10_14_pvt_Final.shp'

SandyPub = r'D:\Thunder_Basin\GIS\EcoSites\Sandy_NF_final.shp'
SandyPvt = r'D:\Thunder_Basin\GIS\EcoSites\Sandy_pvt_Final.shp'

###############################################################################################################################

                        # Temp environments

temp_shp_dir =  r'D:\temp'
env.workspace = temp_shp_dir
arcpy.env.overwriteOutput = True

                         # Output Transects Shapefile

out_folder = r'D:\Thunder_Basin\Transects'
Out_Tshp = "transects_11_18_Sandy1014.shp"
try:
    Out_Transects = arcpy.CreateFeatureclass_management(out_folder, Out_Tshp,"Polyline")
except Exception as e:
    print "problem creating output transects shapefile"



                        # Input lists of features and layers

# Public Eco shapefiles list
eco_shps_pub = [SandyPub]        #loamyPb,S_loamyPb,ClayeyPb,S_ClayeyPb,SaUpPub,,S_SandyPub]

# Private Eco shapefiles list
eco_shps_pvt = [SandyPvt]#,loamyPvtS_loamyPvt,Clayeypvt,S_Clayeypvt,SaUpPvt,,S_SandyPvt]

# Public eco layers list
eco_lyrs_pub = ["SandyPub_lyr"]#,"S_loamyPb_lyr","loamyPb_lyr","ClayeyPb_lyr","S_ClayeyPb_lyr","SaUpPub_lyr",,"S_SandyPub_lyr"]

# Private eco layers list
eco_lyrs_pvt = ["SandyPvt_lyr"]#,"loamyPvt_lyr","S_loamyPvt_lyr","Clayeypvt_lyr","S_Clayeypvt_lyr","SaUpPvt_lyr",,"S_SandyPvt_lyr"]

                    # Create working selection layers

# Create public feature layers
eco_len_pub = len(eco_shps_pub)
count1 = 0
while count1 < eco_len_pub:
    arcpy.MakeFeatureLayer_management(eco_shps_pub[count1],eco_lyrs_pub[count1],"")
    count1 += 1
count1 = 0

# Create Private feature layers
while count1 < eco_len_pub:
    arcpy.MakeFeatureLayer_management(eco_shps_pvt[count1],eco_lyrs_pvt[count1],"")
    count1 += 1

# Create sample points feature layer
arcpy.MakeFeatureLayer_management(inshp,"Sample_Points_lyr","")
# Create fire perimeter buffer feature layer
arcpy.MakeFeatureLayer_management(PerimBuff,"Fire_perimBuff_lyr","")
# Create allotments feature layer
arcpy.MakeFeatureLayer_management(allotment_shp,"Allotments_lyr","")
# Create fire feature layer
arcpy.MakeFeatureLayer_management(Fires,"Fires_lyr","")

test_search = arcpy.SearchCursor("Fires_lyr")
# Make fire history points(2x radius)layer
arcpy.MakeFeatureLayer_management(fireHistoryPoint,"Fire_history_points","")



                    # cursors and geometry objects

# INPUT ANALYSIS search cursor
rows_search = arcpy.SearchCursor(table_shp)

# OUTPUT TRANSECTS insert cursor
insert = arcpy.InsertCursor(Out_Transects)
lineArray = arcpy.Array()
line_pnt = arcpy.Point()

#########################################################################################################################################################################
            # Begin selection criteria for analysis rows - For each fire nickname, all rows with that nickname will be added to dictionary for selection analysis

# list of nicknames, each fire nickname added to list once
nicknames = []

# Output transect ID variable
tran_ID = -1

# Begin looping through rows
for row in rows_search:
    # Nickname
    nickname = row.getValue("nickname")

    # Create FIRST DICTIONARY of data for all rows of fire
    FireD = {}

    print "Line 146, found fire name: ",nickname

    if nickname not in nicknames:
        nicknames.append(nickname)
        print nicknames[0]

        # list of all unique IDs for fire
        fire_IDs = []

        # Create FIRST DICTIONARY of data for all rows of fire
        FireD = {}

        # Fire ID value
        fireID = row.getValue("JoinID")
        fire_IDs.append(fireID)

        # Create dictionary value list for fire ID
        FireRowList = []
        print "fire ID,",fireID

        # D[0] Get Eco Site value
        Eco = row.getValue("ES")
        FireRowList.append(Eco)
        print "eco site = ",Eco

        # D[1] Get Ownership
        ownership = row.getValue("Ownership")
        FireRowList.append(ownership)
        print "ownership = ",ownership

        # D[2] Get allotments
        allotments = row.getValue("allotment")
        FireRowList.append(allotments)
        print "allotments = ",allotments

        # Dictionary Item with ID as key and list as value
        FireD[fireID] = FireRowList


        # Create second search cursor of sample points
        rows_search2 = arcpy.SearchCursor(table_shp)

        # Search through shapefile and find all rows with common nickname
        for N_rows in rows_search2:


            N_name = N_rows.getValue("nickname")

            if N_name == nickname:

                # Fire ID value
                fireID = N_rows.getValue("JoinID")
                # IF fire row ID is not found in list than add to it
                if fireID not in fire_IDs:

                    # Create dictionary value list for fire ID
                    FireRowList = []
                    print "fire ID,",fireID

                    fire_IDs.append(fireID)
                    # Create dictionary value list for fire ID
                    FireRowList = []
                    print "fire ID,",fireID

                    # D[0] Get Eco Site value
                    Eco = N_rows.getValue("ES")
                    FireRowList.append(Eco)
                    print "eco site = ",Eco

                    # D[1] Get Ownership
                    ownership = N_rows.getValue("Ownership")
                    FireRowList.append(ownership)
                    print "ownership = ",ownership

                    # D[2] Get allotments
                    allotments = N_rows.getValue("allotment")
                    FireRowList.append(allotments)
                    print "allotments = ",allotments

########################################################################################################
                    # If Sandy 10-14 or Loamy 10-14 add 50x50 and r100 values to dictionary                 for now don't perform 50x50 and r100 analysis
                    if Eco == "Loamy 10-14" or Eco == "Sandy 10-14":

                        # D[3] Get 50x50
                        CSUplot = N_rows.getValue("50x50")
                        FireRowList.append(CSUplot)

                        # D[4] Radial plot
                        rplot = N_rows.getValue('r100')
                        FireRowList.append(rplot)
#########################################################################################################
                    # Dictionary Item with ID as key and list as value
                    FireD[fireID] = FireRowList
####################################################################################################################################################################

                                    # Go through fire dictionary, perform selection one eco site at a time
        for fire_ID,fire_data in FireD.iteritems():


            # Create dictionary to store same eco site rows - key == sequence of eco rows - Value = row ID
            eco_dict = {}

            eco_count = 0
            eco_type = fire_data[0]

                        # Create code to represent eco types 10 = private 20 = public/private 30 = public

            eco_code = 0
            print "line 185, Found eco type: ",eco_type

            eco_count +=1
            eco_dict[eco_count] = int(fire_ID)

            # Create final Eco ID to determine allotments
            Eco_ID_Final = 0
            # If fire dictionary has more than one record, search through for same eco sites
            if len(FireD) > 1:
                for fire_ID2,fire_data2 in FireD.iteritems():
                    # If other eco sites of the same type are found add to eco count, add count and ID to eco dictionary
                    if fire_data2[0] == eco_type:
                        eco_count += 1
                        eco_dict[eco_count] = fire_ID2


                # List of IDs for eco sites
            Final_ecoID_list = []

                # List of ownership types to search for
            Ownership_type = ["PRIVATE","PUBLIC/PRIVATE","PUBLIC"]



                                         # Check count to see if more than one of the same eco type
            if eco_count > 1:

                print "line 289, ",str(eco_count), " rows of eco site ",str(eco_type)," found"

                # Check ownership types, choose public first, then pub/private, then private -- Select one row to represent each eco site of a fire
                #######################################################################################################################################################
                # Add code to perform 50x50 and r100 analysis
                #######################################################################################################################################################


                # Loop through eco ID dictionary, access ownership from Fire dictionary

                # ownership counts
                pvt_count, pvt_pub_count, pub_count = 0,0,0

                for eID,origID in eco_dict.iteritems():
                    eco_owner = FireD[origID][1]
                    eco_owner_CAP = eco_owner.upper()

                    # check for private, if private add to list first
                    if eco_owner_CAP == Ownership_type[0]:
                        if pvt_count == 0:
                            origID_owner = str(origID)+","+Ownership_type[0]
                            Final_ecoID_list.append(origID_owner)
                            pvt_count += 1

                    # check for public/private, if exists add to list second
                    if eco_owner_CAP == Ownership_type[1]:
                        if pvt_pub_count == 0:
                            origID_owner = str(origID)+","+Ownership_type[1]
                            Final_ecoID_list.append(origID_owner)
                            pvt_pub_count += 1

                    # check for public if exists add to list third
                    if eco_owner_CAP == Ownership_type[1]:
                        if pub_count == 0:
                            origID_owner = str(origID)+","+Ownership_type[2]
                            Final_ecoID_list.append(origID_owner)
                            pub_count += 1

                                    # Check length of eco ID list to determine which ownership selection to perform
                                                        # Create Ownership selection string


                # Check for public first
                for item in Final_ecoID_list:
                    id_owner = item.split(",")
                    if id_owner[1] == Ownership_type[2]:
                        Eco_ID_Final = id_owner[0]
                        eco_code = 30
                        print "Ownership ",Ownership_type[2]," to be used for selection"

                # Check for public/private second
                if eco_code == 0:
                    for item in Final_ecoID_list:
                        id_owner = item.split(",")
                        if id_owner[1] == Ownership_type[1]:
                            Eco_ID_Final = id_owner[0]
                            eco_code = 20
                            print "Ownership ",Ownership_type[1]," to be used for selection"

                # Check for private third
                if eco_code == 0:
                    for item in Final_ecoID_list:
                        id_owner = item.split(",")
                        if id_owner[1] == Ownership_type[0]:
                            Eco_ID_Final = id_owner[0]
                            eco_code = 10
                            print "Ownership ",Ownership_type[0]," to be used for selection"


                                        # Create ownerhip selection type if there is just one row for eco type
        print "only one eco class found for fire ",nickname

        if eco_count == 1:
            Eco_ID_Final = eco_dict[1]
            eco_owner = FireD[Eco_ID_Final][1]

            if eco_owner.upper() == Ownership_type[2]:
                eco_code = 30
            if eco_owner.upper() == Ownership_type[1]:
                eco_code = 20
            if eco_owner.upper() == Ownership_type[0]:
                eco_code = 10
        print "eco code: ",eco_code


        # Get list of allotment(s)
        allotments_raw = FireD[Eco_ID_Final][2]
        allotment_count = 1
        allotment_SELECT = allotments_raw.upper()

                                        # create list of multiple allotments
        if "," in allotments_raw:
            allotments_list = allotments_raw.split(",")
            allotment_count = len(allotments_list)

                    # If no sample points are found in an allotment, and there are multiple allotments, try next allotment
                                             # If multiple allotments randomly select one

        if allotment_count > 1:
            ran_allotment = random.choice(allotments_list)
            allotment_SELECT = ran_allotment.upper()

        print "Allotment ",allotment_SELECT," to be selected for eco site ",eco_type

###############################################################################################################################
                # Link eco type and ownership type with eco layers, for pub/pvt ownership, retrieve both layers

# Public ownership layers
        if eco_code == 30:
            if eco_type == "Loamy 10-14":
                eco_SELECT_pub = eco_lyrs_pub[0]

            if eco_type == "Shallow Loamy 10-14":
                eco_SELECT_pub = eco_lyrs_pub[1]
            if eco_type == "Clayey 10-14":
                eco_SELECT_pub = eco_lyrs_pub[2]
            if eco_type == "Shallow Clayey 10-14":
                eco_SELECT_pub = eco_lyrs_pub[3]
            if eco_type == "Saline Upland 10-14":
                eco_SELECT_pub = eco_lyrs_pub[4]
            if eco_type == "Sandy 10-14":
                eco_SELECT_pub = eco_lyrs_pub[0]    # Change back to [5]
            if eco_type == "Shallow Sandy 10-14":
                eco_SELECT_pub = eco_lyrs_pub[6]

# Private ownership layers
        if eco_code == 10:
            if eco_type == "Loamy 10-14":
                eco_SELECT_pvt = eco_lyrs_pvt[0]
            if eco_type == "Shallow Loamy 10-14":
                eco_SELECT_pvt = eco_lyrs_pvt[1]
            if eco_type == "Clayey 10-14":
                eco_SELECT_pvt = eco_lyrs_pvt[2]
            if eco_type == "Shallow Clayey 10-14":
                eco_SELECT_pvt = eco_lyrs_pvt[3]
            if eco_type == "Saline Upland 10-14":
                eco_SELECT_pvt = eco_lyrs_pvt[4]
            if eco_type == "Sandy 10-14":       # Change back to [5]
                eco_SELECT_pvt = eco_lyrs_pvt[0]
            if eco_type == "Shallow Sandy 10-14":
                eco_SELECT_pvt = eco_lyrs_pvt[6]

# Mixed ownership layers
        if eco_code == 20:
            if eco_type == "Loamy 10-14":
                eco_SELECT_pub = eco_lyrs_pub[0]
                eco_SELECT_pvt = eco_lyrs_pvt[0]
            if eco_type == "Shallow Loamy 10-14":
                eco_SELECT_pub = eco_lyrs_pub[1]
                eco_SELECT_pvt = eco_lyrs_pvt[1]
            if eco_type == "Clayey 10-14":
                eco_SELECT_pub = eco_lyrs_pub[2]
                eco_SELECT_pvt = eco_lyrs_pvt[2]
            if eco_type == "Shallow Clayey 10-14":
                eco_SELECT_pub = eco_lyrs_pub[3]
                eco_SELECT_pvt = eco_lyrs_pvt[3]
            if eco_type == "Saline Upland 10-14":
                eco_SELECT_pub = eco_lyrs_pub[4]
                eco_SELECT_pvt = eco_lyrs_pvt[4]
            if eco_type == "Sandy 10-14":
                eco_SELECT_pub = eco_lyrs_pub[0]        # Change back to [5]
                eco_SELECT_pvt = eco_lyrs_pvt[0]
            if eco_type == "Shallow Sandy 10-14":
                eco_SELECT_pub = eco_lyrs_pub[6]
                eco_SELECT_pvt = eco_lyrs_pvt[6]

###########################################################################################################################################################################################
# Available selection layers            "Sample_Points_lyr"   "Fire Perimeter"  "Fire_perimBuff_lyr"        "Allotments_lyr"
    # Interior/Exterior Count

        Perim_Count = 0
        try:
            if Perim_Count == 0:
                                            # Begin selection
                                # 1. Select sample points within fire perimeter

                fire_wc = "FIRE_NAME" +"= '"+nickname+"'"
                arcpy.SelectLayerByAttribute_management ("Fires_lyr", "NEW_SELECTION", fire_wc)
                try:
                                            # 2. Select sample points within fire

                    arcpy.SelectLayerByLocation_management("Sample_Points_lyr","INTERSECT","Fires_lyr","","NEW_SELECTION")
                    sample_select = int(arcpy.GetCount_management("Sample_Points_lyr").getOutput(0))
                    print "Selecting sample points that are inside the fire perimeter, ",str(sample_select)," points found"
                except Exception as e:
                    print e.message
                                            # 2a. Select fire history 2x radius buffers
                sel_val = "1"
                fireHistoryWC = "Sel_str" +"= '"+sel_val+"'"
                arcpy.SelectLayerByAttribute_management ("Fire_history_points", "NEW_SELECTION", fireHistoryWC)



                                            # 2b. Remove fire nickname history from fire history point buffers
                nickname_str =nickname
                nickname_CAP = nickname_str.upper()
                fireP_wc = "FIRE_NAME" +"= '"+nickname_CAP+"'"

                try:
                    arcpy.SelectLayerByAttribute_management ("Fire_history_points", "REMOVE_FROM_SELECTION", fireP_wc)
                    sample_select = int(arcpy.GetCount_management("Fire_history_points").getOutput(0))
                    print "fire history buffers selected after removal ",sample_select
                except Exception as e:
                    print e.message + " line 504"
                    print "fire history not found in fire history buffers"

                                            # Remove sample points within fire history buffers (non working fire)

                try:
                    arcpy.SelectLayerByLocation_management("Sample_Points_lyr","INTERSECT","Fire_history_points","","REMOVE_FROM_SELECTION")

                except Exception as e:
                    print e.message + " line 510"

                                            # 3. Select allotment

                WC_allot = "UNIT_NAME" + "= '"+allotment_SELECT+"'"
                arcpy.SelectLayerByAttribute_management ("Allotments_lyr","NEW_SELECTION",WC_allot)

                                    # 5. Select sample points within allotment
                try:
                    arcpy.SelectLayerByLocation_management("Sample_Points_lyr","INTERSECT","Allotments_lyr","","SUBSET_SELECTION")
                    sample_select = int(arcpy.GetCount_management("Sample_Points_lyr").getOutput(0))
                    print "Selecting fire sample points that are inside allotment and fire, ",str(sample_select)," points found"

                    if sample_select == 0:
                        if allotment_count > 1:
                            attempt_count = 0
                            while attempt_count < allotment_count:
                                if sample_select == 0:
                                    try:
                                            # 2. Select sample points within fire
                                        arcpy.SelectLayerByLocation_management("Sample_Points_lyr","INTERSECT","Fires_lyr","","NEW_SELECTION")
                                    except Exception as e:
                                        print e.message

                                    allotment_SELECT = allotments_list[attempt_count]
                                    print "line 502 - allotment select = ",allotment_SELECT
                                    attempt_count += 1
                                    WC_allot = "UNIT_NAME" + "= '"+allotment_SELECT+"'"
                                    arcpy.SelectLayerByAttribute_management ("Allotments_lyr","NEW_SELECTION",WC_allot)
                                    arcpy.SelectLayerByLocation_management("Sample_Points_lyr","INTERSECT","Allotments_lyr","","SUBSET_SELECTION")
                                    sample_select = int(arcpy.GetCount_management("Sample_Points_lyr").getOutput(0))
                                    print "Selecting fire sample points that are inside allotment and fire, ",str(sample_select)," points found"
                                attempt_count += 1
                except Exception as e:
                    print e.message + " line 548"



                                    # 5. Select sample points in clipped Eco Site
                try:
                    # Public First
                    if eco_code == 30:
                        arcpy.SelectLayerByLocation_management("Sample_Points_lyr","INTERSECT",eco_SELECT_pub,"","SUBSET_SELECTION")            # Add count check to make sure sample points
                        sample_select = int(arcpy.GetCount_management("Sample_Points_lyr").getOutput(0))
                        print "line 497 - Working on Public selection of ",allotment_SELECT," Allotment for ",eco_type," Number of points found :",str(sample_select)
        ##            sys.exit()
                except Exception as e:
                    print e.message

                try:
                    # Public/Private Second
                    if eco_code == 20:
                        arcpy.SelectLayerByLocation_management("Sample_Points_lyr","INTERSECT",eco_SELECT_pub,"","SUBSET_SELECTION")

                        # count of selected points, if 0 try private else pass
                        sample_select = int(arcpy.GetCount_management("Sample_Points_lyr").getOutput(0))
                        if sample_select < 1:
                            arcpy.SelectLayerByLocation_management("Sample_Points_lyr","INTERSECT",eco_SELECT_pvt,"","SUBSET_SELECTION")
                            sample_select = int(arcpy.GetCount_management("Sample_Points_lyr").getOutput(0))
                        print "line 440 - Working on Public/Private selection of ",allotment_SELECT," Allotment for ",eco_type," Number of points found :",str(sample_select)
                except Exception as e:
                    print e.message

                try:
                    # Private Third
                    if eco_code == 10:
                        sample_select = o
                        arcpy.SelectLayerByLocation_management("Sample_Points_lyr","INTERSECT",eco_SELECT_pvt,"","SUBSET_SELECTION")
                        sample_select += int(arcpy.GetCount_management("Sample_Points_lyr").getOutput(0))
                        print "line 448 - Working on Private selection of ",allotment_SELECT," Allotment for ",eco_type," Number of points found :",str(sample_select)
                except Exception as e:
                    print e.message

                                    # Create list of all available XY string pairs

                input_search = arcpy.SearchCursor("Sample_Points_lyr")
                point_describe = arcpy.Describe(inshp)

                # SAMPLE POINTS geometry object
                point_shp = point_describe.ShapeFieldName


                count_3 = 0
                selection_points_XY = []        # Create list of all available selected sample points
                for row in input_search:            # Original search cursor of sample points
                    if count_3 < 100:
                        p_feat = row.getValue(point_shp)
                        xy_orig = p_feat.getPart()
                        origX = str(xy_orig.X)            # X coord
                        origY = str(xy_orig.Y)            # Y coord
                        print "Found coordinates X:",origX,", Y",origY
                        origXYstring = origX+","+origY      # String of comma deliminated XY
                        selection_points_XY.append(origXYstring)
                        count_3 += 1


                try:
                                        # Randomly select XY coordinates from list                          # Coordinate of start point of interior 30m transect

                    rnd_intr_xy_str = random.choice(selection_points_XY)
                    print "first random point :",rnd_intr_xy_str
                    interior_xy_list =rnd_intr_xy_str.split(",")
                    interior_X = float(interior_xy_list[0])
                    interior_Y = float(interior_xy_list[1])

                                        # Add first point to output transect file
                    if tran_ID == -1:
                        print "Line 554: Adding FIRST vertice to transect for ID ",str(Eco_ID_Final)
                        line_pnt.ID = int(Eco_ID_Final)         #Add final eco Id to line Id


                        line_pnt.X = interior_X             # Add X to transect
                        line_pnt.Y = interior_Y             # Add Y to transect
                        lineArray.add(line_pnt)

                    if tran_ID != -1:
                        print "Line 455: Adding FIRST vertice to transect for ID ",str(Eco_ID_Final)
                        line_pnt.ID = int(Eco_ID_Final)         #Add final eco Id to line Id

                        line_pnt.X = interior_X             # Add X to transect
                        line_pnt.Y = interior_Y             # Add Y to transect

                                        # Create new line feature to add points to
                        feat = insert.newRow()
                        feat.shape = lineArray
                        insert.insertRow(feat)
                        lineArray.removeAll()
                        lineArray.add(line_pnt)




                                        # Create layer of xy point
                    temp_point_list = []
                    pnt = arcpy.Point()
                    pnt.X = interior_X
                    pnt.Y = interior_Y
                    pointGeometry = arcpy.PointGeometry(pnt)
                    temp_point_list.append(pointGeometry)

                                        # Create temp shapefile of point, for naming convention use row ID and Interior or Exterior
                    shp_name = str(Eco_ID_Final)+"InsideP.shp"
                    temp_point_inside_path = os.path.join(temp_shp_dir,shp_name)
                    arcpy.CopyFeatures_management(temp_point_list, temp_point_inside_path)

                                        # 30m buffer of interior temp point

                    buff_name = str(Eco_ID_Final)+"InsideP_30mBuff.shp"
                    temp_point_Buff_path = os.path.join(temp_shp_dir,buff_name)

                    try:
                        arcpy.Buffer_analysis (temp_point_inside_path,  temp_point_Buff_path, "30 Meters", "FULL", "ROUND", "", "")
                    except Exception as e:
                        print "30m Buffer failed!"

                                        # Create points from Buffer
                    buff_points_name = str(Eco_ID_Final)+"InsideP_30mBuff_Points.shp"
                    temp_buffpoints_path = os.path.join(temp_shp_dir,buff_points_name)
                    try:
                        arcpy.FeatureVerticesToPoints_management (temp_point_Buff_path, temp_buffpoints_path, "ALL")
                    except:
                        print "Buffer to points conversion failed! "

                                        # Randomly select one point from available points

                        # Buffer pointss search cursor
                    BuffPoints_search = arcpy.SearchCursor(temp_buffpoints_path)
                    Buff_points_describe = arcpy.Describe(temp_buffpoints_path)

                        # SAMPLE POINTS geometry object
                    Buff_points_shp = Buff_points_describe.ShapeFieldName

                        # List of all XY string pairs of buffer points
                    Buff_points_All = []

                        # Go through points and add to list
                    for bp in BuffPoints_search:
                        bp_feat = bp.getValue( Buff_points_shp)
                        bp_xy_orig = bp_feat.getPart()
                        bp_origX = str(bp_xy_orig.X)            # X coord
                        bp_origY = str(bp_xy_orig.Y)            # Y coord
                        bp_xy_str = bp_origX+","+bp_origY
                        Buff_points_All.append(bp_xy_str)

                    # Randomly select XY coordinates from list                                  # Coordinates for end point of 30m Internal transect

                    rnd_BP_intr_xy_str = random.choice(Buff_points_All)
                    interior_BPxy_list =rnd_BP_intr_xy_str.split(",")
                    interior_BP_X = float(interior_BPxy_list[0])
                    interior_BP_Y = float(interior_BPxy_list[1])
                    print "randomly selected coordinate for second transect point :",str(interior_BP_X)," ",str(interior_BP_Y)


                                    # Add BP transect coordinate to Transect shapefile
                    if tran_ID == -1:
                        print "Line 526: Adding second vertice to transect for ID ",str(Eco_ID_Final)
                        line_pnt.ID = int(Eco_ID_Final)         #Add final eco Id to line Id
                        line_pnt.X = interior_BP_X             # Add X to transect
                        line_pnt.Y = interior_BP_Y             # Add Y to transect
                        lineArray.add(line_pnt)


                    if tran_ID != -1:
                        print "Line 534: Adding second vertice to transect for ID ",str(Eco_ID_Final)
                        line_pnt.ID = int(Eco_ID_Final)         #Add final eco Id to line Id

                        line_pnt.X = interior_BP_X            # Add X to transect
                        line_pnt.Y = interior_BP_Y             # Add Y to transect
                        lineArray.add(line_pnt)

                    if tran_ID == -1:
                        tran_ID = line_pnt.ID                   # set transect ID to final eco ID

                    # Delete search cursor of selected sample points
                    del row

                    # Update perimeter count - Always one for inside, 0 for outside
                    Perim_Count += 1
                except Exception as e:
                    print e.message
                    # Attempt to add last feature
        except Exception as e:
            print e.message

############################################################################################################################################################################
        try:                                                        # Create Transects OUTSIDE of fire perimeter
            if Perim_Count == 1:
                                            # Select points in perimeter buffer(1km)

                fire_wc = "FIRE_NAME" +"= '"+nickname+"'"
                arcpy.SelectLayerByAttribute_management ("Fire_perimBuff_lyr", "NEW_SELECTION", fire_wc)
                try:
                                            # 2. Select sample points within fire

                    arcpy.SelectLayerByLocation_management("Sample_Points_lyr","INTERSECT","Fire_perimBuff_lyr","","NEW_SELECTION")
                    sample_select = int(arcpy.GetCount_management("Sample_Points_lyr").getOutput(0))
                    print "Selecting sample points that are inside the fire perimeter, ",str(sample_select)," points found"

                except Exception as e:
                    print e.message

                                           # 2a. Select fire history 2x radius buffers
                sel_val = "1"
                fireHistoryWC = "Sel_str" +"= '"+sel_val+"'"
                arcpy.SelectLayerByAttribute_management ("Fire_history_points", "NEW_SELECTION", fireHistoryWC)


                                            # 2b. Remove fire nickname history from fire history point buffers
                nickname_str =nickname
                nickname_CAP = nickname_str.upper()
                fireP_wc = "FIRE_NAME" +"= '"+nickname_CAP+"'"

                try:
                    arcpy.SelectLayerByAttribute_management ("Fire_history_points", "REMOVE_FROM_SELECTION", fireP_wc)
                    sample_select = int(arcpy.GetCount_management("Fire_history_points").getOutput(0))
                    print "fire history buffers selected after removal ",sample_select
                except Exception as e:
                    print e.message + " line 758"
                    print "fire history not found in fire history buffers"

                                            # 2c. Remove sample points within fire history buffers (non working fire)

                try:
                    arcpy.SelectLayerByLocation_management("Sample_Points_lyr","INTERSECT","Fire_history_points","","REMOVE_FROM_SELECTION")

                except Exception as e:
                    print e.message + " line 768"


                                            # 2d.   Remove points within fire perimeter
                    # Select Fire
                fire_wc = "FIRE_NAME" +"= '"+nickname+"'"
                arcpy.SelectLayerByAttribute_management ("Fires_lyr", "NEW_SELECTION", fire_wc)

                    # Intersect selected points with fire and remove points from selection
                arcpy.SelectLayerByLocation_management("Sample_Points_lyr","INTERSECT","Fires_lyr","","REMOVE_FROM_SELECTION")



                                            # 3. Select allotment

                WC_allot = "UNIT_NAME" + "= '"+allotment_SELECT+"'"
                arcpy.SelectLayerByAttribute_management ("Allotments_lyr","NEW_SELECTION",WC_allot)

                                    # 5. Select sample points within allotment
                try:
                    arcpy.SelectLayerByLocation_management("Sample_Points_lyr","INTERSECT","Allotments_lyr","","SUBSET_SELECTION")
                    sample_select = int(arcpy.GetCount_management("Sample_Points_lyr").getOutput(0))
                    print "Selecting fire sample points that are inside allotment and fire, ",str(sample_select)," points found"

                except Exception as e:
                    print e.message

                                    # 5. Select sample points in clipped Eco Site
                try:
                    # Public First
                    if eco_code == 30:
                        arcpy.SelectLayerByLocation_management("Sample_Points_lyr","INTERSECT",eco_SELECT_pub,"","SUBSET_SELECTION")            # Add count check to make sure sample points
                        sample_select = int(arcpy.GetCount_management("Sample_Points_lyr").getOutput(0))
                        print "line 801 - Working on Public selection of ",allotment_SELECT," Allotment for ",eco_type," Number of points found :",str(sample_select)
                except Exception as e:
                    print e.message

                try:
                    # Public/Private Second
                    if eco_code == 20:
                        arcpy.SelectLayerByLocation_management("Sample_Points_lyr","INTERSECT",eco_SELECT_pub,"","SUBSET_SELECTION")

                        # count of selected points, if 0 try private else pass
                        sample_select = int(arcpy.GetCount_management("Sample_Points_lyr").getOutput(0))
                        if sample_select < 1:
                            arcpy.SelectLayerByLocation_management("Sample_Points_lyr","INTERSECT",eco_SELECT_pvt,"","SUBSET_SELECTION")
                            sample_select = int(arcpy.GetCount_management("Sample_Points_lyr").getOutput(0))
                        print "line 815 - Working on Public/Private selection of ",allotment_SELECT," Allotment for ",eco_type," Number of points found :",str(sample_select)
                except Exception as e:
                    print e.message

                try:
                    # Private Third
                    if eco_code == 10:
                        sample_select = o
                        arcpy.SelectLayerByLocation_management("Sample_Points_lyr","INTERSECT",eco_SELECT_pvt,"","SUBSET_SELECTION")
                        sample_select += int(arcpy.GetCount_management("Sample_Points_lyr").getOutput(0))
                        print "line 825 - Working on Private selection of ",allotment_SELECT," Allotment for ",eco_type," Number of points found :",str(sample_select)
                except Exception as e:
                    print e.message

                                    # Create list of all available XY string pairs

                input_search = arcpy.SearchCursor("Sample_Points_lyr")
                point_describe = arcpy.Describe(inshp)

                # SAMPLE POINTS geometry object
                point_shp = point_describe.ShapeFieldName


                count_3 = 0
                selection_points_XY = []        # Create list of all available selected sample points
                for row in input_search:            # Original search cursor of sample points
                    if count_3 < 100:
                        p_feat = row.getValue(point_shp)
                        xy_orig = p_feat.getPart()
                        origX = str(xy_orig.X)            # X coord
                        origY = str(xy_orig.Y)            # Y coord
                        print "Found coordinates X:",origX,", Y",origY
                        origXYstring = origX+","+origY      # String of comma deliminated XY
                        selection_points_XY.append(origXYstring)
                        count_3 += 1


                try:
                                        # Randomly select XY coordinates from list                          # Coordinate of start point of interior 30m transect

                    rnd_intr_xy_str = random.choice(selection_points_XY)
                    print "first random point :",rnd_intr_xy_str
                    interior_xy_list =rnd_intr_xy_str.split(",")
                    interior_X = float(interior_xy_list[0])
                    interior_Y = float(interior_xy_list[1])

                                        # Add first point to output transect file
##                    if tran_ID == -1:
##                        print "Line 554: Adding FIRST vertice to transect for ID ",str(Eco_ID_Final)
##                        line_pnt.ID = int(Eco_ID_Final)         #Add final eco Id to line Id
##
##
##                        line_pnt.X = interior_X             # Add X to transect
##                        line_pnt.Y = interior_Y             # Add Y to transect
##                        lineArray.add(line_pnt)

                    if tran_ID != -1:
                        print "Line 455: Adding FIRST vertice to transect for ID ",str(Eco_ID_Final)
                        line_pnt.ID = int(Eco_ID_Final)         #Add final eco Id to line Id

                        line_pnt.X = interior_X             # Add X to transect
                        line_pnt.Y = interior_Y             # Add Y to transect

                                        # Create new line feature to add points to
                        feat = insert.newRow()
                        feat.shape = lineArray
                        insert.insertRow(feat)
                        lineArray.removeAll()
                        lineArray.add(line_pnt)




                                        # Create layer of xy point
                    temp_point_list = []
                    pnt = arcpy.Point()
                    pnt.X = interior_X
                    pnt.Y = interior_Y
                    pointGeometry = arcpy.PointGeometry(pnt)
                    temp_point_list.append(pointGeometry)

                                        # Create temp shapefile of point, for naming convention use row ID and Interior or Exterior
                    shp_name = str(Eco_ID_Final)+"InsideP.shp"
                    temp_point_inside_path = os.path.join(temp_shp_dir,shp_name)
                    arcpy.CopyFeatures_management(temp_point_list, temp_point_inside_path)

                                        # 30m buffer of interior temp point

                    buff_name = str(Eco_ID_Final)+"InsideP_30mBuff.shp"
                    temp_point_Buff_path = os.path.join(temp_shp_dir,buff_name)

                    try:
                        arcpy.Buffer_analysis (temp_point_inside_path,  temp_point_Buff_path, "30 Meters", "FULL", "ROUND", "", "")
                    except:
                        print "30m Buffer failed"

                                        # Create points from Buffer
                    buff_points_name = str(Eco_ID_Final)+"InsideP_30mBuff_Points.shp"
                    temp_buffpoints_path = os.path.join(temp_shp_dir,buff_points_name)
                    try:
                        arcpy.FeatureVerticesToPoints_management (temp_point_Buff_path, temp_buffpoints_path, "ALL")
                    except:
                        print "Buffer to points conversion failed "

                                        # Randomly select one point from available points

                        # Buffer pointss search cursor
                    BuffPoints_search = arcpy.SearchCursor(temp_buffpoints_path)
                    Buff_points_describe = arcpy.Describe(temp_buffpoints_path)

                        # SAMPLE POINTS geometry object
                    Buff_points_shp = Buff_points_describe.ShapeFieldName

                        # List of all XY string pairs of buffer points
                    Buff_points_All = []

                        # Go through points and add to list
                    for bp in BuffPoints_search:
                        bp_feat = bp.getValue( Buff_points_shp)
                        bp_xy_orig = bp_feat.getPart()
                        bp_origX = str(bp_xy_orig.X)            # X coord
                        bp_origY = str(bp_xy_orig.Y)            # Y coord
                        bp_xy_str = bp_origX+","+bp_origY
                        Buff_points_All.append(bp_xy_str)

                    # Randomly select XY coordinates from list                                  # Coordinates for end point of 30m Internal transect

                    rnd_BP_intr_xy_str = random.choice(Buff_points_All)
                    interior_BPxy_list =rnd_BP_intr_xy_str.split(",")
                    interior_BP_X = float(interior_BPxy_list[0])
                    interior_BP_Y = float(interior_BPxy_list[1])
                    print "randomly selected coordinate for second transect point :",str(interior_BP_X)," ",str(interior_BP_Y)

                    if tran_ID != -1:
                        print "Line 534: Adding second vertice to transect for ID ",str(Eco_ID_Final)
                        line_pnt.ID = int(Eco_ID_Final)         #Add final eco Id to line Id

                        line_pnt.X = interior_BP_X            # Add X to transect
                        line_pnt.Y = interior_BP_Y             # Add Y to transect
                        lineArray.add(line_pnt)

                    if tran_ID == -1:
                        tran_ID = line_pnt.ID                   # set transect ID to final eco ID

                    # Delete search cursor of selected sample points
                    del row

                    # Update perimeter count - Always one for inside, 0 for outside
                    Perim_Count = 0
                except Exception as e:
                    print e.message
                    # Attempt to add last feature
        except Exception as e:
            print e.message

try:
    feat = insert.newRow()
    feat.shape = lineArray
    insert.insertRow(feat)
    lineArray.removeAll()
except Exception as e:
    print "no last line array row found"

del insert
del rows_search





































