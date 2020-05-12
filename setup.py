from setuptools import setup
from setuptools import find_packages

setup(name='OpenFOAM-custom-postProcess',
      description='Package to perform post-porcessing of data from OpenFOAM simulations',
      version='1.0.0',
      author='Suyash Tandon',
      packages=find_packages(),
      entry_points = {
          'console_scripts':[
              'writeVorticityCenter=src.bin.trackVortices.write_vorticity_center:main',
              'plotVorticityCenter=src.bin.trackVortices.plot_vorticity_center:main',
              'writeTkePerArea=src.bin.tkePerUnitArea.write_tke_per_unit_area:main',
              'writeSgsTkePerArea=src.bin.sgsTkePerUnitArea.write_sgs_tke_per_unit_area:main',
              'writeTkeStdDev=src.bin.tkeStdDev.write_tke_std_dev:main',
              'writeSeparationVolume=src.bin.regionOfSeparation.write_separation_volume:main',
              'writeTwoPointCorr=src.bin.twoPointCorr.write_two_point_corr:main',
              'writeFieldAvg=src.bin.fieldAveraging.write_field_avg:main',
              'writeIntLengthScale=src.bin.intLengthScale.write_int_length_scale:main'
              ]
          },
      install_requires=[
          'numpy',
          'scipy',
          'matplotlib',
          'tqdm',
          ],
      zip_safe=False)
