import numpy as np
import os
import sys
import argparse
from tqdm import tqdm
from src.readers.reader_support_functions import *
from src.readers.reader import *
from .get_field_avg import *

def main():
    parser = argparse.ArgumentParser(description='calculate field \
    average at specific streamwise locations')

    parser.add_argument('-config',
                        type=str,
                        help='file with essential inputs',
                        required=True)

    args = parser.parse_args()

    # parse the config:
    configFile = open(args.config, mode='r')
    configDict = config_to_dict(configFile)

    # read data from configFile
    filePath = os.getcwd()
    planeDir = configDict['planeDirName']
    filePath = filePath + '/postProcessing/'+planeDir
    tDir     = get_time_dir(filePath, configDict)
    filePath = filePath + '/' + tDir

    # list of qauntities to average
    qty = list( )
    for key in configDict.keys():
        if key.startswith('qty'):
            qty.append(configDict[key])
        else:
            continue

    # check if UMean is present in the list:
    checkUMean = False
    if 'UMean' in qty:
        checkUMean = True

    # other parameters:
    h         = float( configDict['h'] )
    nu        = float( configDict['nu'] )
    patchName = configDict['patchName']
    nPlanes   = int( configDict['nPlanes'] )
    direction = configDict['avg-direction']
    caseDir = os.getcwd()

    if direction == 'y':
        axis = 0
        print('\n Avergaing in y-dir...\n')
        caseDir = caseDir + '/postProcessing/my-postprocess/fieldAveraging/y-dir/' + \
                  str(tDir)
        if not os.path.exists(caseDir):
            os.makedirs(caseDir)
    elif direction == 'z':
        axis = 1
        print('\n Avergaing in z-dir...\n')
        caseDir = caseDir + '/postProcessing/my-postprocess/fieldAveraging/z-dir/' + \
                  str(tDir)
        if not os.path.exists(caseDir):
            os.makedirs(caseDir)
    else:
        print('\n The field averaging works in y or z-dir for a given y-z plane.')
        print(' Please select either y or z direction... \n')
        sys.exit()

    ycoord, zcoord, yplus, yGrid, zGrid = dict(), dict(), dict(), dict(), dict()

    for i in tqdm(range(nPlanes), ncols=90):
        pName = patchName + str(i+1)
        fpath = filePath + '/UMean_' + pName + '.raw'
        try:
            umean = get_data(fpath, skiprows=2)
        except:
            raise IOError('UMean file not found ...')

        if direction == 'z':
            print('\n calculating y+ ...')
            if checkUMean == True:
                UMean, ycoord[pName], yplus[pName], yGrid[pName], zGrid[pName] = \
                get_coords(umean, h, nu, direction)
                #
                solution = np.append([ycoord[pName]], [yplus[pName]], axis=0)
                solution = np.append(solution, UMean.T, axis=0)
                solution = solution.T
                #
                fname = caseDir + '/UMean_' + pName + '.csv'
                hLine = 'y/h, y+, UMean_avg_x, UMean_avg_y, UMean_avg_z'
                np.savetxt(fname, solution, fmt='%1.4e', delimiter=', ',
                           newline='\n', header=hLine)
            else:
                _, ycoord[pName], yplus[pName], yGrid[pName], zGrid[pName] = \
                get_coords(umean, h, nu, direction)
        else:
            _, ycoord[pName], zcoord[pName], yGrid[pName], zGrid[pName] = \
            get_coords(umean, h, nu, direction)
            #
    if checkUMean == True:
        qty.remove('UMean')
        #
    print('\nBegin averaging ...\n')
    for i in range( len(qty) ):
        #print('     averaging ' + qty[i] + ' ...')
        desc = qty[i] + ' '
        for j in tqdm( range(nPlanes),desc=desc, ncols=85 ):
            pName = patchName + str(j+1)
            fpath = filePath + '/' + qty[i] + '_' + pName + '.raw'

            data = get_data(fpath, skiprows=2)
            data[:, :3] /= h
            avg  = get_field_avg(data, yGrid[pName], zGrid[pName], h, axis)
            if direction == 'z':
                solution = ycoord[pName]
                solution = np.append([solution], [ yplus[pName] ], axis=0)
            else:
                solution = zcoord[pName]

            fname = caseDir + '/' + qty[i] + '_' + patchName + \
                    str(j+1) + '.csv'
            if avg.ndim == 1:
                if direction == 'z':
                    hLine = 'y/h, y+, ' + qty[i] + '_avg'
                    solution = np.append(solution, [avg], axis=0)
                else:
                    hLine = 'z/h, ' + qty[i] + '_avg'
                    solution = np.append([solution], [avg], axis=0)

            elif avg.ndim == 2 and avg.shape[1] == 3:
                solution = np.append(solution, avg.T, axis=0)
                if direction == 'z':
                    hLine = 'y/h, y+, ' + qty[i] + '_avg_x, ' + \
                            qty[i] + '_avg_y, ' + qty[i] + '_avg_z'
                else:
                    hLine = 'z/h, ' + qty[i] + '_avg_x, ' + \
                            qty[i] + '_avg_y, ' + qty[i] + '_avg_z'

            elif avg.ndim == 2 and avg.shape[1] == 6:
                solution = np.append(solution, avg.T, axis=0)
                if direction == 'z':
                    hLine = 'y/h, y+, ' + qty[i] + '_avg_xx, ' + \
                            qty[i] + '_avg_xy, ' + qty[i] + '_avg_xz, ' + \
                            qty[i] + '_avg_yy, ' + qty[i] + '_avg_yz, ' + \
                            qty[i] + '_avg_zz'
                else:
                    hLine = 'z/h, ' + qty[i] + '_avg_xx, ' + \
                            qty[i] + '_avg_xy, ' + qty[i] + '_avg_xz, ' + \
                            qty[i] + '_avg_yy, ' + qty[i] + '_avg_yz, ' + \
                            qty[i] + '_avg_zz'
            else:
                raise ValueError('Oops! Something went wrong in averaging ...')

            solution = solution.T
            np.savetxt(fname, solution, fmt='%1.4e', delimiter=', ',
                       newline='\n', header=hLine)

if __name__=='__main__':
    main()
