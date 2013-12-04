####################################################################################################
#
# PyOpenGLV4 - An OpenGL V4 layer on top of PyOpengl.
# Copyright (C) 2013 Salvaire Fabrice
#
####################################################################################################

####################################################################################################

import ctypes
import logging

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class GlEnums(object):
    pass

####################################################################################################

class ParameterWrapper(object):

    ##############################################

    def __init__(self, location, type_):

        self.location = location
        self.type = type_

    ##############################################

    def from_parameter(self, parameter, c_parameters):

        c_parameters[self.location] = self.type(parameter)

####################################################################################################

class OutputArrayWrapper(ParameterWrapper):

    ##############################################

    def __init__(self, size_location, size_type, pointer_location, pointer_type):

        self.size_location = size_location
        self.size_type = size_type
        self.pointer_location = pointer_location
        self.pointer_type = pointer_type

    ##############################################

    def from_parameter(self, size_parameter, c_parameters):

        c_parameters[self.size_location] = self.size_type(size_parameter)
        array_type = self.pointer_type * size_parameter
        array = array_type(*range(100, 100 + size_parameter))
        print ' ', array_type, list(array)
        c_parameters[self.pointer_location] = ctypes.cast(array, ctypes.POINTER(self.pointer_type))

        return self, array

    ##############################################

    def from_c(self, array):

        return list(array)

####################################################################################################

class GlCommandWrapper(object):

    # Fixme: unsigned comes from typedef
    __gl_to_ctypes_type__ = {
        'char':ctypes.c_char,
        'int8_t':ctypes.c_byte, # c_int8
        'uint8_t':ctypes.c_ubyte, # c_uint8
        'unsigned char':ctypes.c_ubyte,
        'short':ctypes.c_short,
        'unsigned short':ctypes.c_ushort,
        'int32_t':ctypes.c_int32,
        'int':ctypes.c_int32, # not 64-bit integer!
        'unsigned int':ctypes.c_uint32,
        'int64_t':ctypes.c_int64,
        'uint64_t':ctypes.c_uint64,
        'float':ctypes.c_float,
        'float_t':ctypes.c_float,
        'double':ctypes.c_double,
        'intptr_t':ctypes.c_void_p, # ?
        'ptrdiff_t':ctypes.c_void_p, # ?
        'ssize_t':ctypes.c_uint64, # ?
        'void': None, # ?
        }

    ##############################################

    def __init__(self, wrapper, command):

        self._wrapper = wrapper
        self._command = command
        self._number_of_parameters = command.number_of_parameters

        gl_spec_types = wrapper._gl_spec.types

        try:
            self._function = getattr(self._wrapper._libGL, str(command))
        except AttributeError:
            raise NameError("OpenGL function %s was no found in libGL" % (str(command)))

        # argument_types = []
        self._parameter_wrappers = []
        for parameter in command.parameters:
            if parameter.pointer:
                pass
            elif parameter.back_ref is not None:
                pointer_parameter = parameter.back_ref
                if not pointer_parameter.const: # input parameter
                    # size parameter
                    c_type = parameter.translate_gl_type(gl_spec_types)
                    size_ctypes_type = self.__gl_to_ctypes_type__[str(c_type)]
                    # pointer parameter
                    c_type = pointer_parameter.translate_gl_type(gl_spec_types)
                    pointer_ctypes_type = self.__gl_to_ctypes_type__[str(c_type)]
                    # parameter wrapper
                    parameter_wrapper = OutputArrayWrapper(parameter.location, size_ctypes_type,
                                                           pointer_parameter.location, pointer_ctypes_type)
                    self._parameter_wrappers.append(parameter_wrapper)
                else:
                    pass
            else:
                c_type = parameter.translate_gl_type(gl_spec_types)
                ctypes_type = self.__gl_to_ctypes_type__[str(c_type)]
                self._parameter_wrappers.append(ParameterWrapper(parameter.location, ctypes_type))
        # if not has_output_parameter and argument_types:
        #     self._function.argtypes = argument_types

        return_type = command.return_type
        if return_type.type != 'void':
            c_type = return_type.translate_gl_type(gl_spec_types)
            ctypes_type = self.__gl_to_ctypes_type__[str(c_type)]
            # print str(command), c_type, ctypes_type, return_type.pointer
            if return_type.pointer:
                if ctypes_type == ctypes.c_ubyte: # return type is char *
                    ctypes_type = ctypes.c_char_p
                else:
                    raise NotImplementedError
            self._function.restype = ctypes_type
            self._return_void = False
        else:
            self._return_void = True

    ##############################################

    def __call__(self, *args, **kwargs):

        print 'Call', repr(self)
        gl_spec_types = self._wrapper._gl_spec.types
        print self._command.prototype(gl_spec_types)

        c_parameters = [None]*self._number_of_parameters
        output_parameters = []
        for parameter_wrapper, parameter in zip(self._parameter_wrappers, args):
            # print parameter_wrapper, parameter
            output_parameter = parameter_wrapper.from_parameter(parameter, c_parameters)
            if isinstance(parameter_wrapper, OutputArrayWrapper):
                output_parameters.append(output_parameter)

        print ' ', c_parameters
        result = self._function(*c_parameters)

        if 'check_error' in kwargs and kwargs['check_error']:
            error_code = self._wrapper.glGetError()
            if error_code:
                pythonic_wrapper = self._wrapper._pythonic_wrapper
                error_message = pythonic_wrapper.error_code_message(error_code)
                raise NameError(error_message)
        
        if output_parameters:
            output_parameters = [parameter_wrapper.from_c(output_parameter)
                                 for parameter_wrapper, output_parameter in output_parameters]
            if self._return_void:
                if len(output_parameters) == 1:
                    return output_parameters[0]
                else:
                    return output_parameters
            else:
                return [result] + output_parameters
        else:
            if not self._return_void:
                return result

    ##############################################

    def __repr__(self):

        return str(self._command.name) + ' ' + str(self._function.argtypes) + ' -> ' + str(self._function.restype)

####################################################################################################

class CtypeWrapper(object):

   ##############################################

    def __init__(self, gl_spec, api, api_number, profile=None):

        self._gl_spec = gl_spec

        api_enums, api_commands = self._gl_spec.generate_api(api, api_number, profile)

        self._libGL = ctypes.cdll.LoadLibrary('libGL.so')
        self._init_enums(api_enums)
        self._init_commands(api_commands)

        self._pythonic_wrapper = PythonicWrapper(self)

    ##############################################

    def _init_enums(self, api_enums):

        gl_enums = GlEnums()
        for enum in api_enums:
            setattr(gl_enums, str(enum), int(enum))
        # self._gl_enums = gl_enums
        self.GL = gl_enums # Fixme: namespace?

    ##############################################

    def _init_commands(self, api_commands):

        for command in api_commands.itervalues():
            setattr(self, str(command), GlCommandWrapper(self, command))

####################################################################################################

class PythonicWrapper(object):

    ##############################################

    def __init__(self, wrapper):

        self._wrapper = wrapper

    ##############################################

    def error_code_message(self, error_code):

        # glGetError

        if not error_code:
            # GL_NO_ERROR: The value of this symbolic constant is guaranteed to be 0.
            return 'No error has been recorded.'
        else:
            GL = self._wrapper.GL
            if error_code == GL.GL_INVALID_ENUM:
                return 'An unacceptable value is specified for an enumerated argument.'
            elif error_code == GL.GL_INVALID_VALUE:
                return 'A numeric argument is out of range.'
            elif error_code == GL.GL_INVALID_OPERATION:
                return 'The specified operation is not allowed in the current state.'
            elif error_code == GL.GL_INVALID_FRAMEBUFFER_OPERATION:
                return 'The framebuffer object is not complete.'
            elif error_code == GL.GL_OUT_OF_MEMORY:
                return 'There is not enough memory left to execute the command.'
            elif error_code == GL.GL_STACK_UNDERFLOW:
                return 'An attempt has been made to perform an operation that would cause an internal stack to underflow.'
            elif error_code == GL.GL_STACK_OVERFLOW:
                return 'An attempt has been made to perform an operation that would cause an internal stack to overflow.'
            else:
                raise NotImplementedError

####################################################################################################
#
# End
#
####################################################################################################
