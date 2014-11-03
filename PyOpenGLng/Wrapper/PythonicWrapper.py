####################################################################################################
# 
# PyOpenGLng - An OpenGL Python Wrapper with a High Level API.
# Copyright (C) 2014 Fabrice Salvaire
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

import numpy as np

####################################################################################################

# Fixme: purpose?
# def glGetActiveUniformBlockiv(program, pname):
#     data = np.zeros(1, dtype=np.int32)
#     GL.glGetActiveUniformBlockiv(program, pname, data)
#     return data[0]

####################################################################################################

class PythonicWrapper(object):

    ##############################################

    def glGetActiveUniformBlockiv(self, program, index, pname):
    
        """ Query information about an active uniform block. """
    
        # Check index
        number_of_uniform_blocks = self.glGetProgramiv(program, self.GL_ACTIVE_UNIFORM_BLOCKS)
        # if not(0 <= index < number_of_uniform_blocks):
        if index < 0 or index >= number_of_uniform_blocks:
            raise IndexError('Index %s out of range 0 to %i' % (index, number_of_uniform_blocks -1))

        if pname != self.GL_UNIFORM_BLOCK_ACTIVE_UNIFORM_INDICES:
            array_size = 1
        else:
            array_size = self.glGetActiveUniformBlockiv(program, index, self.GL_UNIFORM_BLOCK_ACTIVE_UNIFORMS)
        params = np.zeros(array_size, dtype=np.int32)

        self.commands.glGetActiveUniformBlockiv(program, index, pname, params)

        if array_size > 1: 
            return list(params)
        else:
            return params[0]

    ##############################################

    def glGetActiveUniformBlockName(self, program, index):
    
        """ Retrieve the name of an active uniform block. """
    
        number_of_uniform_blocks = self.glGetProgramiv(program, self.GL_ACTIVE_UNIFORM_BLOCKS)
        if index < 0 or index >= number_of_uniform_blocks:
            raise IndexError("Index %s out of range 0 to %i" % (index, number_of_uniform_blocks -1))

        max_name_length = self.glGetProgramiv(program, self.GL_ACTIVE_UNIFORM_BLOCK_MAX_NAME_LENGTH)
        name, name_length = self.commands.glGetActiveUniformBlockName(program, index, max_name_length)
        return name
    
    ##############################################    

    def glGetActiveUniformsiv(self, program, indices, pname):
    
        """ Returns information about several active uniform variables for the specified program
        object.
        """
    
        try:
            indices = list(indices)
        except TypeError:
            indices = (indices,)

        number_of_uniform_blocks = self.glGetProgramiv(program, self.GL_ACTIVE_UNIFORMS)
        for index in indices:
            if index < 0 or index >= number_of_uniform_blocks:
                raise IndexError('Index %s out of range 0 to %i' % (index, number_of_uniform_blocks -1))

        gl_indices = np.array(indices, dtype=np.uint32)
        params = np.zeros(len(indices), dtype=np.int32)

        self.commands.glGetActiveUniformsiv(program, len(indices), gl_indices, pname, params)

        if len(indices) > 1:
            return list(params)
        else:
            return params[0]

    ##############################################    
    
    def glGetProgramiv(self, program, pname):

        # Fixme: pname => size and type
        # Fixme: overhead versus ctype pointer, -> func
        data = np.zeros(1, dtype=np.int32)
        self.commands.glGetProgramiv(program, pname, data)
        return int(data[0])

    ##############################################    

    def glGetShaderiv(self, program, pname):

        # Fixme: cf. infra
        data = np.zeros(1, dtype=np.int32)
        self.commands.glGetShaderiv(program, pname, data)
        return int(data[0])

####################################################################################################
# 
# End
# 
####################################################################################################
