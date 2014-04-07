#configuration.py
from datetime import datetime
from dsmart import engine, version
import logging
import os

if __name__ == "__main__":
    start = datetime.now()
    
    # Configure variables

    # Set the project filestem
    filestem = "region"

    # Set the project workspace
    workspace = "root_directory"

    # Set the number of iterations (integer)
    iterations = 3

    # Set the number of samples per polygon (integer)
    samplesPerPolygon = 1

    # Identify the map unit composition text file
    mapunitFilename = "formatted_attribute_table.txt"#"example_attribute_table.txt"

    # Identify the map unit polygon shapefile
    shapefileFilename = "MUPOLYGON.shp"#"dlr_polys_alb_7km.shp"#"example_shapefile.shp"

    # Westernmost raster column of block (zero-based index)
    # Do not modify this value.
    x = 0

    # Uncertainty factor for soil class allocation
    T = 10000

    # Number of most probable soil class rasters
    # e.g. if nMostProbable = 3, DSMART will create rasters depicting the most
    # probable, second-most-probable and third-most-probable soil classes, their
    # probabilities, and the confusion index for most- and second-most-probable, and
    # second-most- and third-most-probable soil classes. Confusion index is
    # calculated as 1 - (a - b) where a and b are the probabilities of the higher-
    # and next-highly-probable soil classes, respectively, after Burrough et al.
    # (1997).
    nMostProbable = 3

    # Minimum number of sampling points per classification tree leaf
    # (must be greater than or equal to 2)
    min_objs = 100#2

    # If there are sample point files in the profiles subfolder, the value of
    # this variable determines whether the samples supplement or replace the
    # random sampling within polygons.
    # Takes either 'supplement' or 'replacement', or None if not in use. Default
    # is None.
    auxiliarySampleType = None

    # If there are sample point files in the profiles subfolder, the value of
    # this variable determines whether each file is used only once (i.e. ignores
    # the value set in iterations) or whether DSMART loops over each file until
    # iterations is fulfilled.
    # Takes either 'once' or 'loop', or None if not in use. Default is None.
    sampleReuseType = None  

    ######################################################
    ######################################################

    try:
        print "DSMART version", version.__version__
        print "Started at", start
        # Make sure workspace folder exists
        if workspace[-1] != '\\':
            workspace = workspace + '/'
        if not os.path.isdir(workspace):
            raise IOError('\nWorkspace folder {} does not exist.\n'.format(workspace))
    except IOError as e:
        print e

        finish = datetime.now()
        print "Finished WITH ERRORS at", finish
        print (finish - start), "elapsed"
    else:
        try:           
            
            # Configure logger
            logger = logging.getLogger('dsmart')
            logger.setLevel(logging.DEBUG)

            # Identify the log's filename
            fp = workspace + start.strftime('%Y%m%d_%H%M%S') + '_' + filestem + '.log'
            fh = logging.FileHandler(workspace + start.strftime('%Y%m%d_%H%M%S') + '_' + filestem + '.log')

            print "Log file is at", fp

            # Create a formatter for the log
            formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
            fh.setFormatter(formatter)

            # Add the file handler to the logger
            logger.addHandler(fh)
            logger.info('Running DSMART version %s', version.__version__)
            logger.info('Commenced at %s', start)


            # Configure DSMART
            e = engine.Engine(filestem, workspace, iterations,
                              samplesPerPolygon, mapunitFilename,
                              shapefileFilename, x, T, nMostProbable, min_objs,
                              auxiliarySampleType, sampleReuseType)

        except ValueError as e:
            print e
            
            finish = datetime.now()
            logger.info('Finished WITH ERRORS at %s', finish)
            logger.info('%s elapsed', finish - start)
            print "Finished WITH ERRORS at", finish
            print (finish - start), "elapsed"

        except IOError as e:
            print e

            finish = datetime.now()
            logger.info('Finished WITH ERRORS at %s', finish)
            logger.info('%s elapsed', finish - start)
            print "Finished WITH ERRORS at", finish
            print (finish - start), "elapsed"

        else:
            # Run DSMART
            e.run()

            finish = datetime.now()
            logger.info('Finished successfully at %s', finish)
            logger.info('%s elapsed', finish - start)
            print "Finished successfully at", finish
            print (finish - start), "elapsed"
