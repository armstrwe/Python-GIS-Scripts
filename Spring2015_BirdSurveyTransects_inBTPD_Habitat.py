#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Billy.Armstrong
#
# Created:     15/04/2015
# Copyright:   (c) Billy.Armstrong 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------

def main():
    pass

if __name__ == '__main__':
    main()
import os,sys,arcpy,math,random,string,csv
from arcpy import env
from random import choice

                        # Temp environments

temp_dir =  r'D:\temp'
env.workspace = temp_dir
arcpy.env.overwriteOutput = True

in_coords = r'D:\Thunder_Basin\Spring_2015_Bird_Survey_Transects\GIS\All_FocalAreaVerts_wID_v2.shp'




# make layer of input coords
arcpy.MakeFeatureLayer_management(in_coords,"input_coordinates","")


# Go through all verts and do math for start and end coordinates, add to a list which also contains VertID, pID,add the randomly selected number
# based on the object's order in the random selection list
all_verts_list = []
xy_count = 0
field = "VertID"
randCoord_search = arcpy.SearchCursor("input_coordinates")
for row in randCoord_search:
    vert_list = []
    xy_count +=1

    # get vert ID
    vert = row.getValue("VertID")
    vert_list.append(vert)

    # get pID
    pID = row.getValue("pdogID")
    vert_list.append(pID)

    # get vertX, vertY
    vX = row.getValue("POINT_X")
    vert_list.append(vX)

    vY = row.getValue("POINT_Y")
    vert_list.append(vY)

    # get Centroid X,Y
    cX = row.getValue("Cent_X")
    vert_list.append(cX)

    cY = row.getValue("Cent_Y")
    vert_list.append(cY)

    # Add list to list of all verts
    all_verts_list.append(vert_list)






point = arcpy.Point()
array = arcpy.Array()
featurelist = []

##Out_Tshp = "Transect_vID"+str(vert)+"_pDogID"+str(pID)+".shp"
Out_Tshp = "TB_Transects2.shp"
Out_Transects = arcpy.CreateFeatureclass_management(temp_dir, Out_Tshp,"Polyline","","","",r'D:\Thunder_Basin\Spring_2015_Bird_Survey_Transects\GIS\All_FocalAreaVerts_wID_v2.shp')

arcpy.AddField_management(Out_Transects, "vID", "TEXT", "", "", 15, "", "", "")
arcpy.AddField_management(Out_Transects, "pID", "TEXT", "", "", 15, "", "", "")
arcpy.AddField_management(Out_Transects, "cenX", "TEXT", "", "", 15, "", "", "")
arcpy.AddField_management(Out_Transects, "cenY", "TEXT", "", "", 15, "", "", "")
arcpy.AddField_management(Out_Transects, "RandNum", "TEXT", "", "", 5, "", "", "")
arcpy.AddField_management(Out_Transects, "vertX", "TEXT", "", "", 15, "", "", "")
arcpy.AddField_management(Out_Transects, "vertY", "TEXT", "", "", 15, "", "", "")


# OUTPUT TRANSECTS insert cursor
insert = arcpy.InsertCursor(Out_Transects)



# Randomly select 500 verts from list
Random_verts = random.sample(all_verts_list,100)

# keep track of order of random vert selected, add to field in output
random_order = 0

for item in Random_verts:
    vert = item[0]
    pID = item[1]
    vX = item[2]
    vY = item[3]
    cX = item[4]
    cY = item[5]

##    print vert,pID,vX,vY,cX,cY
##    sys.exit()

# Do the math for start and end trans coordinates

    x_dist_raw = int(vX) - int(cX)
    y_dist_raw = int(vY) - int(cY)

    y_dist_raw_str = str(y_dist_raw)
    x_dist_raw_str = str(x_dist_raw)


###########################################################################
    # Work on creating X coordinates for transect
    # NE quad first

    if x_dist_raw_str[0] != "-" and y_dist_raw_str[0] != "-":                     ########## Positive X difference, use x_dist_raw

        X_dist_scale25 = x_dist_raw * 25

        # Beginning and ending Xcoordinates for transect
        tranStartXpos = vX + X_dist_scale25
        tranEndXpos = vX - X_dist_scale25

        # Beginning and ending Xcoordinates for transect
        Y_dist_scale25 = y_dist_raw*25
        tranStartY = vY + Y_dist_scale25
        tranEndY = vY - Y_dist_scale25

        tranStartXY = str(tranStartXpos)+" "+str(tranStartY)
        tranEndXY = str(tranEndXpos)+" "+str(tranEndY)
        print "transect start XY, ",tranStartXY


    # SW quad second
    if x_dist_raw_str[0] == "-" and y_dist_raw_str[0] == "-":

        x_pow = math.pow(x_dist_raw,2)
        final_X_dist = math.sqrt(x_pow)

        # scale by 25x
        X_dist_scale25 = final_X_dist * 25

        # Beginning and ending X coords for transect
        tranStartXneg = vX + X_dist_scale25
        tranEndXneg = vX - X_dist_scale25

        y_pow = math.pow(y_dist_raw,2)
        final_Y_dist = math.sqrt(y_pow)

        # scale by 25x
        Y_dist_scale25 = final_Y_dist * 25

        # Beginning and ending Y coords for transect
        tranStartY = vY + Y_dist_scale25
        tranEndY = vY - Y_dist_scale25

        tranStartXY = str(tranStartXneg)+" "+str(tranStartY)
        tranEndXY = str(tranEndXneg)+" "+str(tranEndY)
        print "transect start XY, ",tranStartXY

    # NW quad third
    if x_dist_raw_str[0] == "-" and y_dist_raw_str[0] != "-":

        x_pow = math.pow(x_dist_raw,2)
        final_X_dist = math.sqrt(x_pow)

        # scale by 25x
        X_dist_scale25 = final_X_dist * 25

        # Beginning and ending X coordinates for transect
        tranStartXneg = vX - X_dist_scale25
        tranEndXneg = vX + X_dist_scale25

        # Beginning and ending Y coords for transect
        Y_dist_scale25 = y_dist_raw*25
        tranStartY = vY + Y_dist_scale25
        tranEndY = vY - Y_dist_scale25

        tranStartXY = str(tranStartXneg)+" "+str(tranStartY)
        tranEndXY = str(tranEndXneg)+" "+str(tranEndY)
        print "transect start XY, ",tranStartXY

    # SE quad fourth
    if x_dist_raw_str[0] != "-" and y_dist_raw_str[0] == "-":

        X_dist_scale25 = x_dist_raw * 25

        # Beginning and ending X coordinates for transect
        tranStartXpos = vX - X_dist_scale25
        tranEndXpos = vX + X_dist_scale25

        y_pow = math.pow(y_dist_raw,2)
        final_Y_dist = math.sqrt(y_pow)

        # scale by 25x
        Y_dist_scale25 = final_Y_dist * 25

        # Beginning and ending Y coords for transect
        tranStartY = vY + Y_dist_scale25                # start Y coordinate is North
        tranEndY = vY - Y_dist_scale25

        tranStartXY = str(tranStartXpos)+" "+str(tranStartY)
        tranEndXY = str(tranEndXpos)+" "+str(tranEndY)
        print "transect start XY, ",tranStartXY


#####################################################################################################

    # Create Transect for each randomly selected vert






##    # OUTPUT TRANSECTS insert cursor
##    insert = arcpy.InsertCursor(Out_Transects)
##    lineArray = arcpy.Array()
##    line_pnt = arcpy.Point()

    feat = insert.newRow()

         #Add First XY point to Line
    point.X = float(tranStartXY.split()[0])
    point.Y = float(tranStartXY.split()[1])
    array.add(point)
        #Add First XY point to Line
    point.X = float(tranEndXY.split()[0])
    point.Y = float(tranEndXY.split()[1])
    array.add(point)

    polyline = arcpy.Polyline(array)
    array.removeAll()
    featurelist.append(polyline)
    feat.shape = polyline

    # populate fields
    feat.vID = str(vert)
    feat.pID = str(pID)
    feat.cenX = str(cX)
    feat.cenY = str(cY)
    feat.RandNum = str(random_order)
    feat.vertX = str(vX)
    feat.vertY = str(vY)

    insert.insertRow(feat)

    random_order += 1

del feat
del insert




# List for all transect shapefiles
Transect_Verts_All_list = []

# Create lyr from transects
# make layer of input coords
arcpy.MakeFeatureLayer_management(Out_Transects,"outTranlayer","")

tran_search = arcpy.SearchCursor("outTranlayer")

for tran in tran_search:

    transect_list = []          # order = vID,pID,CENX,CENY,RandNum
    tranVID = tran.getValue("vID")
    tranPID = tran.getValue("pID")
    tranCX = tran.getValue("cenX")
    tranCY = tran.getValue("cenY")
    tranRandN = tran.getValue("RandNum")
    tranVertX = tran.getValue('vertX')
    tranVertY = tran.getValue('vertY')


    transect_list.append(tranVID)
    transect_list.append(tranPID)
##    transect_list.append(tranCX)
##    transect_list.append(tranCY)
    transect_list.append(tranRandN)
    transect_list.append(tranVertX)
    transect_list.append(tranVertY)

    tran_name_raw = "Transect_"+tranVID+"_"+tranPID+"_"



    # Create layer of Verticie XY
    temp_point_list = []
    pnt = arcpy.Point()
    pnt.X = float(tranVertX)
    pnt.Y = float(tranVertY)
    pointGeometry = arcpy.PointGeometry(pnt)
    temp_point_list.append(pointGeometry)

    # Create temp shapefile of point
    shp_name =  tran_name_raw+"VERT.shp"
    Vert_point = os.path.join(temp_dir,shp_name)
    arcpy.CopyFeatures_management(temp_point_list, Vert_point)

    # Create all 250m buffers

    # list of all buffer distances
##    buff_dists = ["125 Meters","375 Meters","625 Meters","875 Meters"] # Naming coding = Index slice []+1
    buff_dists = ["125 Meters","375 Meters","625 Meters","875 Meters","1125 Meters","1375 Meters","1625 Meters"] # Naming coding = Index slice []+1
    buff_path_list = []
    buff_count = 1

    for buff in buff_dists:

        buff_name = tran_name_raw+"Buffer_"+str(buff_count)+".shp"
        buff_count += 1
        buff_path = os.path.join(temp_dir,buff_name)
        buff_path_list.append(buff_path)

        try:
            arcpy.Buffer_analysis (Vert_point,  buff_path, buff, "FULL", "ROUND", "", "")
        except Exception as e:
            print "30m Buffer failed!"

    Intersect_list = []
    Int_count = 1
    for buff in buff_path_list:

        IntName = tran_name_raw+"Intersect"+str(Int_count)+".shp"
        Int_path = os.path.join(temp_dir,IntName)
        Int_count += 1
        Intersect_list.append(Int_path)
        # Select transect to work with
        T_wc = "vID" +"= '"+tranVID+"'"
        arcpy.SelectLayerByAttribute_management ("outTranlayer", "NEW_SELECTION", T_wc)

        # Input intersect files list
        Int_list = [buff,"outTranlayer"]

        # Intersect buffer with transect
        arcpy.Intersect_analysis (Int_list, Int_path, "ALL", "", "LINE")

    # Merge all Intersect segments together

    MergeName = tran_name_raw+"Merge.shp"
    Merge_path = os.path.join(temp_dir,MergeName)
    arcpy.Merge_management (Intersect_list, Merge_path, "")

    # Dissolve output based on VID
    DissName = tran_name_raw+"Dissolve.shp"
    Dissolve_path = os.path.join(temp_dir,DissName)

    arcpy.Dissolve_management (Merge_path, Dissolve_path, "vID", "", "", "")

##    # Add fields back into data (stripped from data by dissolve)
##    SJName = tran_name_raw+"SpatialJoin.shp"
##    SJ_path = os.path.join(temp_dir,SJName)
##
##    # Field mappings
##
##    fieldmappings = arcpy.FieldMappings()
##    fieldmappings.addTable(Merge_path)


    # transect verts to points
    Tverts = tran_name_raw+"Tverts.shp"
    Tverts_path = os.path.join(temp_dir,Tverts)

    arcpy.FeatureVerticesToPoints_management(Dissolve_path, Tverts_path, "ALL")


    # Do a final merge to add edge vert into transect verts


##    arcpy.SpatialJoin_analysis (Dissolve_path, Merge_path, SJ_path, "", "", {field_mapping}, "", ", ")

    TvertsALL = tran_name_raw+"TvertsALL.shp"
    TvertsALL_path = os.path.join(temp_dir,TvertsALL)
    arcpy.Merge_management([Tverts_path, Vert_point], TvertsALL_path, "")

    # Add pID, vID, random number back into points
    arcpy.AddField_management(TvertsALL_path, "pID", "TEXT", "", "", 15, "", "", "")
    arcpy.AddField_management(TvertsALL_path, "RanNum", "TEXT", "", "", 15, "", "", "")

    # pID SQL
    pCF = "pID" +"= '"+tranPID+"'"
    # vID SQL
    vCF = "vID" +"= '"+tranVID+"'"
    # Random Number SQL
    rCF = "RanNum" +"= '"+tranRandN+"'"

    arcpy.CalculateField_management (TvertsALL_path, "pID", tranPID)
    arcpy.CalculateField_management (TvertsALL_path, "vID", tranVID)
    arcpy.CalculateField_management (TvertsALL_path, "RanNum", tranRandN)

    Transect_Verts_All_list.append(TvertsALL_path)


# Merge all files into one output
FinalT_dir = r'D:\Thunder_Basin\Spring_2015_Bird_Survey_Transects\GIS\Output_Transects'
Final_Transects = "Final_Transects_FocalArea1_V2.shp"
Final_Transects_path = os.path.join(FinalT_dir,Final_Transects)
arcpy.Merge_management(Transect_Verts_All_list, Final_Transects_path, "")





