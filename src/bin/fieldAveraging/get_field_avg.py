import numpy as np
import os
from tqdm import tqdm
from scipy.interpolate import griddata
from scipy.interpolate import InterpolatedUnivariateSpline

__all__ = ['get_coords', 'get_field_avg']

def complete_array(data, ycoord):
    try:
        nCols = data.shape[1]
        data = np.insert(data, 0, 0, axis=0)
        data = np.vstack((data, np.zeros(nCols)))

        for i in range(nCols):
            # fit first element
            spline = InterpolatedUnivariateSpline(ycoord[1:5], data[1:5, i])
            data[0, i] = spline(ycoord[0])

            # fit last element
            spline = InterpolatedUnivariateSpline(ycoord[-5:-1], data[-5:-1, i])
            data[-1, i] = spline(ycoord[-1])

    except:
        nCols = 1
        data = np.insert(data, 0, 0)
        data = np.append(data, 0)

        spline = InterpolatedUnivariateSpline(ycoord[1:5], data[1:5])
        data[0] = spline( ycoord[0] )

        spline = InterpolatedUnivariateSpline(ycoord[-5:-1], data[-5:-1])
        data[-1] = spline( ycoord[-1] )

    return data

def get_coords(data, h, nu, dir):
    # normalize lengths:
    data[:, :3] /= h

    ycoord = np.unique( data[:, 1] )

    zcoord = np.unique( data[:, 2] )
    zcoord[0]  = (zcoord[0] + zcoord[1])/2
    zcoord[-1] = (zcoord[-1] + zcoord[-2])/2

    zGrid, yGrid = np.meshgrid( zcoord, ycoord )

    tempUMean = griddata( (data[:, 2], data[:, 1]), data[:, 3],
                (zGrid[1:-1, :], yGrid[1:-1, :]), method='cubic')
    umean = np.mean(tempUMean, axis=1)

    tempUMean = griddata( (data[:, 2], data[:, 1]), data[:, 4],
                (zGrid[1:-1, :], yGrid[1:-1, :]), method='cubic')
    umean = np.append([umean], [np.mean( tempUMean, axis=1 )], axis=0)

    tempUMean = griddata( (data[:, 2], data[:, 1]), data[:, 5],
                (zGrid[1:-1, :], yGrid[1:-1, :]), method='cubic')
    umean = np.append(umean, [np.mean( tempUMean, axis=1 )], axis=0)

    # fit spline in the first and last ycoord:
    umean = complete_array(umean.T, ycoord)
    if dir == 'z':
        UMean = np.sqrt( np.sum( np.square(umean), axis=1 ) )
        du_dy = UMean[0]/(ycoord[0]*h)
        utau  = np.sqrt( nu*du_dy )

        yplus = ycoord*(h*utau/nu)

        return umean, ycoord, yplus, yGrid, zGrid
    else:
        return umean, ycoord, zcoord, yGrid, zGrid

def get_field_avg(data, yGrid, zGrid, h, axis):

    # number of columns in the file
    nCols = data.shape[1]

    # scalar data:
    if nCols == 4:
        qty = griddata( (data[:, 2], data[:, 1]), data[:, 3],
              (zGrid[1:-1, :], yGrid[1:-1, :]), method='cubic')
        avg = np.mean( qty, axis=axis )
        if axis:
            avg = complete_array(avg.T, yGrid[:, 0])
        else:
            avg = complete_array(avg.T, zGrid[0, :])
            avg = avg[1:-1]
    # vector data:
    elif nCols == 6:
        qtyX = griddata( (data[:, 2], data[:, 1]), data[:, 3],
               (zGrid[1:-1, :], yGrid[1:-1, :]), method='cubic')
        avg = np.mean( qtyX, axis=axis )

        qtyY = griddata( (data[:, 2], data[:, 1]), data[:, 4],
               (zGrid[1:-1, :], yGrid[1:-1, :]), method='cubic')
        avg = np.append([avg], [np.mean( qtyY, axis=axis )], axis=0)

        qtyZ = griddata( (data[:, 2], data[:, 1]), data[:, 5],
               (zGrid[1:-1, :], yGrid[1:-1, :]), method='cubic')
        avg = np.append(avg, [np.mean( qtyZ, axis=axis )], axis=0)

        if axis:
            avg = complete_array(avg.T, yGrid[:, 0])
        else:
            avg = complete_array(avg.T, zGrid[0, :])
    # tensor data:
    elif nCols == 9:
        qtyXX = griddata( (data[:, 2], data[:, 1]), data[:, 3],
                (zGrid[1:-1, :], yGrid[1:-1, :]), method='cubic')
        avg = np.mean( qtyXX, axis=axis )

        qtyXY = griddata( (data[:, 2], data[:, 1]), data[:, 4],
                (zGrid[1:-1, :], yGrid[1:-1, :]), method='cubic')
        avg = np.append([avg], [np.mean( qtyXY, axis=axis )], axis=0)

        qtyXZ = griddata( (data[:, 2], data[:, 1]), data[:, 5],
                (zGrid[1:-1, :], yGrid[1:-1, :]), method='cubic')
        avg = np.append(avg, [np.mean( qtyXZ, axis=axis )], axis=0)

        qtyYY = griddata( (data[:, 2], data[:, 1]), data[:, 6],
                (zGrid[1:-1, :], yGrid[1:-1, :]), method='cubic')
        avg = np.append(avg, [np.mean( qtyYY, axis=axis )], axis=0)

        qtyYZ = griddata( (data[:, 2], data[:, 1]), data[:, 7],
                (zGrid[1:-1, :], yGrid[1:-1, :]), method='cubic')
        avg = np.append(avg, [np.mean( qtyYZ, axis=axis )], axis=0)

        qtyZZ = griddata( (data[:, 2], data[:, 1]), data[:, 8],
                (zGrid[1:-1, :], yGrid[1:-1, :]), method='cubic')
        avg = np.append(avg, [np.mean( qtyZZ, axis=axis )], axis=0)

        if axis:
            avg = complete_array(avg.T, yGrid[:, 0])
        else:
            avg = complete_array(avg.T, zGrid[0, :])

    return avg
