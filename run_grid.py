import numpy as np
import dsmart_utilities
import os

def Run_DSMART(region_dir):

 owd = os.getcwd()
 os.chdir(region_dir)
 os.system('python configuration.py')
 os.chdir(owd)
 
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
dir = '/home/ice/nchaney/PROJECTS/SYDNEY2014/HOMOGENIZATION/dsmart_example/illinois'
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
  dims['res'] = res
  dims['nx'] = nx
  dims['ny'] = ny
  dims['id'] = i*n + j

  #Prepare the data
  region_dir = '%s/region_%d' % (dir,dims['id'])
  dsmart_utilities.prepare_input(dims,region_dir)

  #Run dsmart (Change to directory first)
  #os.chdir(region_dir)
  #os.system('python configuration.py')
  Run_DSMART(region_dir)
