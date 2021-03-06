import numpy as np
import os
import argparse
from src.readers.reader_support_functions import *
from src.readers.reader import *
from .track_vorticity import *

def main():
    parser = argparse.ArgumentParser(description='calculate the turbulent KE \
    per unit area in the separation region')

    parser.add_argument('-config',
                        type=str,
                        help='file with the essential inputs',
                        required=True)

    args = parser.parse_args()

    # parse the config:
    configFile = open(args.config, mode='r')

    coordPlane, vorCenter, vorCenterDist = track_vorticity_center(configFile)
    solution = np.vstack((coordPlane, vorCenter.T, vorCenterDist))

    caseDir = os.getcwd()
    caseDir = caseDir + '/postProcessing/my-postprocess'
    if not os.path.exists(caseDir):
        os.mkdir(caseDir)

    fname = caseDir + '/vorticity_center.csv'
    np.savetxt(fname, solution.T, fmt='%.4f',
               delimiter=', ', newline='\n',
               header='x/h, vortex-center (y/h), vortex-center (z/h), distance-from-1st-center/h')


if __name__=='__main__':
    main()
