import numpy as np
import dsmart_utilities
import os

def Run_DSMART(region_dir):

 owd = os.getcwd()
 os.chdir(region_dir)
 os.system('python configuration.py')
 os.chdir(owd)
 
 return

def Region_Cutout(region_dir,id):

 vars = ['maxcl1_class',]
 for var in vars:
  file_in = '%s/output/probabilities/%s.img' % (region_dir,var)
  if os.path.exists('%s/%s' % (output_dir,var)) == False:
   os.mkdir('%s/%s' % (output_dir,var))
  file_out = '%s/%s/%s_%d.tif' % (output_dir,var,var,id)
  os.system("gdalwarp -te %.16f %.16f %.16f %.16f -overwrite %s %s" % (dims['minlon_c'],dims['minlat_c'],dims['maxlon_c'],dims['maxlat_c'],file_in,file_out))

 return

#Iterate through the region with overlapping grids
res = 0.0002777777777780
x_overlap = 600
y_overlap = 600
nx = 900
ny = 900
minlat = 38.75
minlon = -89.0
n = 3

#Prepare directories
dir = '/home/ice/nchaney/PROJECTS/SYDNEY2014/HOMOGENIZATION/dsmart_example/illinois'
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
  dims['minlat_c'] = minlat + (ymin+300)*res
  dims['minlon_c'] = minlon + (xmin+300)*res
  dims['maxlat_c'] = minlat + (ymin+600)*res
  dims['maxlon_c'] = minlon + (xmin+600)*res
  dims['res'] = res
  dims['nx'] = nx
  dims['ny'] = ny
  dims['id'] = i*n + j

  #Prepare the data
  region_dir = '%s/region_%d' % (dir,dims['id'])
  #dsmart_utilities.prepare_input(dims,region_dir)

  #Run dsmart (Change to directory first)
  #Run_DSMART(region_dir)

  #Cut out the region of interst
  Region_Cutout(region_dir,dims['id'])

#Merge each variables files
vars = ['maxcl1_class',]
for var in vars:
 os.system('gdalwarp %s/%s/*.tif %s/%s.tif' % (output_dir,var,output_dir,var))
