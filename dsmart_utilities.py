import os
import numpy as np
import shapefile

def prepare_input(dims,dir,home_dir):

 #Create directories
 if os.path.exists(dir) == False:
  os.mkdir(dir)
 os.system('rm -rf %s/*' % dir)
 os.mkdir('%s/workspace' % dir)
 os.mkdir('%s/covariates' % dir)
 os.mkdir('%s/polygons' % dir)

 shp_in = '%s/MUPOLYGON.shp' % home_dir
 shp_out = '%s/polygons' % dir
 res = dims['res']#1*0.0002777777777780
 nx = dims['nx']#1000
 ny = dims['ny']#1000
 ncores = 6
 zone='16N'
 res_utm = 30.
 
 #Prepare dem
 dem_in = '%s/NED/*.tif' % home_dir
 dem_out = '%s/workspace/dem.tif' % dir
 dem_utm_out = '%s/workspace/dem_utm.tif' % dir
 os.system("gdalwarp -t_srs 'EPSG:4326' -dstnodata -9.99e+08 -ts %d %d -te %.16f %.16f %.16f %.16f --config GDAL_CACHEMAX 3000 -wm 3000 -overwrite -r near -ot Float64 -overwrite %s %s" % (nx,ny,dims['minlon'],dims['minlat'],dims['maxlon'],dims['maxlat'],dem_in,dem_out))
 os.system("gdalwarp -t_srs '+proj=utm +zone=16N +datum=WGS84' -dstnodata -99999 -overwrite -tr %.16f %.16f %s %s" % (res_utm,res_utm,dem_out,dem_utm_out))

 #Compute derived products
 #Convert to SAGA format
 dem_in = dem_utm_out
 dem_out = '%s/workspace/dem.sdat' % dir
 os.system('gdal_translate -of SAGA %s %s' % (dem_in,dem_out))

 #Produce sink filled dem
 dem_in = '%s/workspace/dem.sgrd' % dir
 dem_out = '%s/workspace/dem_nosinks.sgrd' % dir
 os.system('saga_cmd -c=%d ta_preprocessor 4 -ELEV %s -FILLED %s -MINSLOPE 0.0001' % (ncores,dem_in,dem_out))
 dem_in = dem_out #The dem is now the sink filled one

 #Produce flow accumulation, slope,and flow length
 area_out = '%s/workspace/area.sgrd' % dir
 slope_out = '%s/workspace/slope.sgrd' % dir
 flwpath_out = '%s/workspace/flwpath.sgrd' % dir
 os.system("saga_cmd -c=%d ta_hydrology 'Catchment Area (Parallel)' -ELEVATION %s -CAREA %s -CSLOPE %s -FLWPATH %s" % (ncores,dem_in,area_out,slope_out,flwpath_out))

 #Produce topographic index
 ti_out = '%s/workspace/ti.sgrd' % dir
 os.system("saga_cmd -c=%d ta_hydrology 'Topographic Wetness Index (TWI)' -SLOPE %s -AREA %s -TWI %s -CONV 1" % (ncores,slope_out,area_out,ti_out))  

 #Produce aspect and curvature
 aspect_out = '%s/workspace/aspect.sgrd' % dir
 curvature_out = '%s/workspace/curvature.sgrd' % dir
 os.system("saga_cmd -c=%d ta_morphometry 'Slope, Aspect, Curvature' -ELEVATION %s -SLOPE %s -ASPECT %s -CURV %s" % (ncores,dem_in,slope_out,aspect_out,curvature_out))

 #Produce MRVBF and MRRTF
 mrvbf_out = '%s/workspace/mrvbg.sgrd' % dir
 mrrtf_out = '%s/workspace/mrrtf.sgrd' % dir
 os.system("saga_cmd -c=%d ta_morphometry 'Multiresolution Index of Valley Bottom Flatness (MRVBF)' -DEM %s -MRVBF %s -MRRTF %s" % (ncores,dem_in,mrvbf_out,mrrtf_out))

 #Prepare for dsmart
 vars = ['mrvbg','mrrtf','aspect','ti','curvature','flwpath','slope','dem_nosinks','area']
 for var in vars:
  file_in = '%s/workspace/%s.sdat' % (dir,var)
  file_out = '%s/covariates/%s.tif' % (dir,var)
  #Convert to lat/lon
  os.system("gdalwarp -t_srs EPSG:4326 -dstnodata -99999 -overwrite -tr %.16f %.16f -te %.16f %.16f %.16f %.16f %s %s" % (res,res,dims['minlon'],dims['minlat'],dims['maxlon'],dims['maxlat'],file_in,file_out))
  #Calculate statistiscs
  os.system('gdalinfo -stats %s' % file_out)

 #Prepare nlcd
 nlcd_in = '%s/NLCD/nlcd2006_landcover_4-20-11_se5.img' % home_dir
 nlcd_out = '%s/covariates/nlcd.tif' % dir
 os.system('gdalwarp -dstnodata -99999 -tr %.16f %.16f -t_srs EPSG:4326 -te %.16f %.16f %.16f %.16f -overwrite %s %s' % (res,res,dims['minlon'],dims['minlat'],dims['maxlon'],dims['maxlat'],nlcd_in,nlcd_out))
 os.system('gdalinfo -stats %s' % nlcd_out)

 #Prepare K,U, and Th radiometric
 vars = ['K','U','Th']
 for var in vars:
  file_in = '%s/Radiometric/NArad_%s_geog83.tif' % (home_dir,var)
  file_out = '%s/covariates/rad%s.tif' % (dir,var)
  os.system('gdalwarp -r bilinear -ot Float64 -dstnodata -99999 -tr %.16f %.16f -t_srs EPSG:4326 -te %.16f %.16f %.16f %.16f -overwrite %s %s' % (res,res,dims['minlon'],dims['minlat'],dims['maxlon'],dims['maxlat'],file_in,file_out))
  os.system('gdalinfo -stats %s' % file_out)

 #Extract desired polygons
 os.system('ogr2ogr -spat %.16f %.16f %.16f %.16f -overwrite -select CELLVALUE,MUKEY %s %s' % (dims['minlon'],dims['minlat'],dims['maxlon'],dims['maxlat'],shp_out,shp_in))

 #Rasterize the polygons
 tiff_out = '%s/workspace/mupolygon.tiff' % dir
 os.system('gdal_rasterize -init -9999 -te %f %f %f %f -tr %.16f %.16f -a MUKEY -ot Float32 -a_srs EPSG:4326 -l MUPOLYGON %s %s' % (dims['minlon'],dims['minlat'],dims['maxlon'],dims['maxlat'],res,res,shp_out,tiff_out))

 #Create attribute list
 sf = shapefile.Reader("%s/polygons/MUPOLYGON.shp" % dir)

 #Extract records
 cellvalue = []
 muid = []
 for record in sf.records():
  cellvalue.append(record[0])
  muid.append(record[1])
 muid = np.array(muid)
 cellvalue = np.array(cellvalue)
 
 #Extract the unique muids
 muid, idx = np.unique(muid, return_index=True)
 cellvalue = cellvalue[idx]
 print cellvalue

 #Extract the component ids and percentage coverage
 from rpy2.robjects import r
 import rpy2.robjects.numpy2ri
 rpy2.robjects.numpy2ri.activate()
 r.assign("muids",muid)

 #Prepare SQL request
 #chorizon ON component.cokey = chorizon.cokey AND
 r('library(soilDB)')
 r('in.statement <- format_SQL_in_statement(muids)')
 r('q <- paste("SELECT component.mukey, component.cokey, comppct_r FROM component JOIN chorizon ON component.cokey = chorizon.cokey AND mukey IN ", in.statement, "ORDER BY mukey",sep="")')

 #Request Data
 r('res <- SDA_query(q)')

 #Pass data back to a python dictionary
 output = {}
 output['mukey'] = np.array((r('res$mukey')))
 output['cokey'] = np.array((r('res$cokey')))
 output['comppct_r'] = np.array((r('res$comppct_r')))

 #Create table
 table_out = '%s/polygons/formatted_attribute_table.txt' % dir
 fp = open(table_out,'w')
 for i in xrange(len(cellvalue)):
  mukey = muid[i]
  cl = cellvalue[i]
  idx = np.where(output['mukey'] == np.int(mukey))[0]
  cokeys = output['cokey'][idx]
  pct = output['comppct_r'][idx]
  cokeys, idx = np.unique(cokeys,return_index=True)
  pct = pct[idx]
  ##Make sure it adds up too 100%
  if len(pct) > 0:
   for j in xrange(len(cokeys)):
    fp.write('%d,%s,%s,%f\n' % (cl,mukey,str(cokeys[j]),pct[j]))
 fp.close()

 #Prepare the configuration file
 os.system('cp configuration_template.py %s/configuration.py' % dir)
 import fileinput
 for line in fileinput.input('%s/configuration.py' % dir, inplace = 1): # Does a list of files, and writes redirects STDOUT to the file in question
  print line.replace("root_directory", "%s" % dir),

 return
