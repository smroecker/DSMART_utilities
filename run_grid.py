import numpy as np
import dsmart_utilities
import os
import gdal

def Run_DSMART(region_dir):

 owd = os.getcwd()
 os.chdir(region_dir)
 os.system('python2.7 configuration.py')
 os.chdir(owd)
 
 return

def Region_Cutout(region_dir,id):

 vars = ['maxcl1_class',]
 for var in vars:
  file_in = '%s/output/probabilities/%s.img' % (region_dir,var)
  if os.path.exists('%s/%s' % (output_dir,var)) == False:
   os.mkdir('%s/%s' % (output_dir,var))
  file_out = '%s/%s/%s_%d.tif' % (output_dir,var,var,id)
  #Extract the cutout
  os.system("gdalwarp -te %.16f %.16f %.16f %.16f -overwrite %s %s" % (dims['minlon_c'],dims['minlat_c'],dims['maxlon_c'],dims['maxlat_c'],file_in,file_out))
  #Use the lookup table to assign component ids
  lookup = np.loadtxt('%s/lookup.txt' % region_dir,delimiter=',')
  #Read in the raster
  dataset = gdal.Open(file_out)
  #Get dimensons
  nx = dataset.RasterXSize
  ny = dataset.RasterYSize
  #Retrieve band
  band = dataset.GetRasterBand(1)
  #Convert to numpy array
  data = band.ReadAsArray(0,0,nx,ny).astype(np.float32)
  #Map the component ids
  for id in lookup[:,1]:
   data[data == id]  = lookup[lookup[:,1] == id,0]
  #Place the data back in the raster 
  #file_out = '%s/%s/%s_%d_mapped.tif' % (output_dir,var,var,id)
  dataset_out = dataset.GetDriver().Create(file_out,nx,ny,1,gdal.GDT_Float32)
  dataset_out.GetRasterBand(1).WriteArray(data)
  dataset_out.FlushCache()
  dataset_out.GetRasterBand(1).SetNoDataValue(dataset.GetRasterBand(1).GetNoDataValue())
  dataset_out.SetGeoTransform(dataset.GetGeoTransform())
  dataset_out.SetProjection(dataset.GetProjection())
  
  

 return

#Iterate through the region with overlapping grids
res = 0.0002777777777780
x_overlap = 1000
y_overlap = 1000
nx = 1500
ny = 1500
x_overlap = 2*nx/3
y_overlap = 2*ny/3
minlat = 38.75
minlon = -89.0
n = 1#3

#Prepare directories
dir = '/scratch/sciteam/nchaney/data/gSSURGO/illinois'
home_dir = '/u/sciteam/nchaney/data/gSSURGO/illinois'
#dir = '/home/ice/nchaney/PROJECTS/SYDNEY2014/HOMOGENIZATION/dsmart_example/illinois'
output_dir = '%s/output' % dir
if os.path.exists(output_dir) == False:
 os.mkdir(output_dir)
os.system('rm -rf %s/*' % output_dir)

#Run algorithm on chunks
for i in xrange(n):
 for j in xrange(n):
  print i,j
  #Construct the window
  xmin = i*nx - i*x_overlap
  xmax = (i+1)*nx - i*x_overlap
  ymin = j*ny - j*y_overlap
  ymax = (j+1)*ny - j*y_overlap
  dims = {}
  dims['minlat'] = minlat + ymin*res
  dims['maxlat'] = minlat + ymax*res
  dims['minlon'] = minlon + xmin*res
  dims['maxlon'] = minlon + xmax*res
  dims['minlat_c'] = minlat + (ymin+ny-y_overlap)*res
  dims['minlon_c'] = minlon + (xmin+nx-x_overlap)*res
  dims['maxlat_c'] = minlat + (ymin+y_overlap)*res
  dims['maxlon_c'] = minlon + (xmin+x_overlap)*res
  dims['res'] = res
  dims['nx'] = nx
  dims['ny'] = ny
  dims['id'] = i*n + j

  #Prepare the data
  region_dir = '%s/region_%d' % (dir,dims['id'])
  #dsmart_utilities.prepare_input(dims,region_dir,home_dir)

  #Run dsmart (Change to directory first)
  Run_DSMART(region_dir)

  #Cut out the region of interst
  #Region_Cutout(region_dir,dims['id'])

#Merge each variables files
vars = ['maxcl1_class',]
for var in vars:
 os.system('gdalwarp %s/%s/*.tif %s/%s.tif' % (output_dir,var,output_dir,var))
