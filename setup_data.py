####################################################################################################
# 
# PyOpenGLV4 - An OpenGL V4 layer on top of PyOpengl..
# Copyright (C) 2013 Salvaire Fabrice
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>. 
# 
####################################################################################################

####################################################################################################

import os

####################################################################################################


# Utility function to read the README file.
# Used for the long_description.
def read(file_name):

    path = os.path.dirname(__file__)
    if os.path.basename(path) == 'tools':
        path = os.path.dirname(path)
    absolut_file_name = os.path.join(path, file_name)

    return open(absolut_file_name).read()

####################################################################################################

setup_dict = dict(
    name='PyOpenGLV4',
    version='0.1.0',
    author='Fabrice Salvaire',
    author_email='fabrice.salvaire@orange.fr',
    description='An OpenGL V4 layer on top of PyOpengl.',
    license = "GPLv3",
    keywords = "OpenGL",
    url='http://fabrice-salvaire.pagesperso-orange.fr/software/index.html',
    packages=['PyOpenGLV4'],
    data_files = [],
    long_description=read('README.pypi'),
    # cf. http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Topic :: Scientific/Engineering",
        "Intended Audience :: Education",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        ],
    install_requires=[
        'pyqt>=4.9',
        'numpy>=1.4',
        'PyOpenGL>=3.0.2',
        ],
    )

####################################################################################################
#
# End
#
####################################################################################################
