####################################################################################################
#
# PyOpenGLng - An OpenGL Python Wrapper with a High Level API.
# Copyright (C) 2013 Salvaire Fabrice
#
####################################################################################################

####################################################################################################

import os

####################################################################################################

def parent_directory_of(file_name, step=1):
    
    directory = os.path.realpath(file_name)
    for i in xrange(step):
        directory = os.path.dirname(directory)
    return directory

####################################################################################################

class Path(object):

    ##############################################

    @staticmethod
    def manual_path(api_number):

        return os.path.join(parent_directory_of(__file__, step=2),
                            'doc', 'man%u' % api_number.major, 'xhtml')

####################################################################################################
# 
# End
# 
####################################################################################################
