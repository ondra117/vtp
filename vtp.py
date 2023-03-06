import ctypes
import os
import numpy as np

"""
this is a library to easily run vlang functions from python,
supports basic types including (int8-64, float32, float64, bool, string, arrays)
"""

#compile V file and load dll file
def compile(v_path: str):
    os.system(f"v -d no_backtrace -shared {v_path}")
    return load(v_path.replace(".v", ".dll"))

#load dll file
def load(dll_pah: str):
    lib = ctypes.CDLL(dll_pah)
    lib._initialise()
    return lib

#structure represent V arrays
class ArrayV(ctypes.Structure):
    _fields_ = [
                ('element_size', ctypes.c_int32),
                ('data', ctypes.POINTER(ctypes.c_void_p)),
                ('offset', ctypes.c_int32),
                ('len', ctypes.c_int32),
                ('cap', ctypes.c_int32),
                ('flags', ctypes.c_int32),
               ]

#structure represent V strings
class StringV(ctypes.Structure):
    _fields_ = [
                ('str', ctypes.POINTER(ctypes.c_uint8)),
                ('len', ctypes.c_int32),
                ('is_lit', ctypes.c_int32),
               ]

#class witch wrap V function
class wrapper:
    #define types
    i8 = ctypes.c_int8
    i16 = ctypes.c_int16
    i32 = ctypes.c_int32
    i64 = ctypes.c_int64
    f32 = ctypes.c_float
    f64 = ctypes.c_double
    bool = ctypes.c_bool
    str = ...
    retyp = {ctypes.c_int8: np.int8, ctypes.c_int16: np.int16, ctypes.c_int32: np.int32,
              ctypes.c_int64: np.int64, ctypes.c_float: np.float32, ctypes.c_double: np.float64,
              ctypes.c_bool: np.bool8}
    
    #class stranslate np.ndarray to ArrayV structure and transpate ArrayV structure to np.ndarray
    class Array:
        def __init__(self, type):
            self.type = type #type of array elements (it can also be an Array again)

        #translate np.ndarray to ArrayV
        def __call__(self, arg):
            arrv = ArrayV()
            arrv.element_size = ctypes.sizeof(self.type) if not isinstance(self.type, wrapper.Array) else (ctypes.c_int32)(32)
            arrv.offset = (ctypes.c_int32)(0)
            arrv.len = (ctypes.c_int32)(len(arg))
            arrv.cap = arrv.len
            arrv.flags = (ctypes.c_int32)(0)

            data = (self.type * len(arg))(*arg)
            data = ctypes.cast(data, ctypes.POINTER(ctypes.c_void_p))
            arrv.data = data

            return arrv

        #ensures function for array of arrays ...
        def __mul__(self, y):
            def multiply(*arg):
                data = [None] * y
                for idx in range(y):
                    data[idx] = self(arg[idx])
                return (ArrayV * y)(*data)
            return multiply
        
        #translate ArrayV to np.ndarray
        def out(self, res, shape=[None, [], True], idxs=[]):
            if shape[2]:
                shape[1].append(res.len)
            if isinstance(self.type, wrapper.Array):
                nparr_data = ctypes.cast(res.data, ctypes.POINTER(ArrayV * res.len))[0]
                for idx, subarr in enumerate(nparr_data):
                    self.type.out(subarr, shape=shape, idxs=[*idxs, idx])
                return shape[0]
            else:
                if shape[2]:
                    shape[2] = False
                    shape[0] = np.zeros(shape[1], dtype=wrapper.retyp[self.type])
                data = ctypes.cast(res.data, ctypes.POINTER(self.type * res.len))
                if idxs != []:
                    shape[0][idxs] = np.ctypeslib.as_array(data.contents)
                else:
                    shape[0] = np.ctypeslib.as_array(data.contents)
                return shape[0]

    #class stranslate python string to StringV structure and transpate StringV structure to python string
    class _string:
            def __init__(self):
                ...
            
            #trnsalate python string to StringV
            def __call__(self, str):
                strv = StringV()
                strv.len = (ctypes.c_int32)(len(str))
                strv.is_lit = (ctypes.c_int32)(0)

                data = (ctypes.c_uint8 * len(str))(*str.encode())
                strv.str = ctypes.cast(data, ctypes.POINTER(ctypes.c_uint8))

                return strv
            
            #ensures function for array of strings
            def __mul__(self, y):
                def multiply(*arg):
                    data = [None] * y
                    for idx in range(y):
                        data[idx] = wrapper._string(arg[idx])
                    return (StringV * y)(*data)
                return multiply
            
            #translate StringV to python string
            def out(self, res):
                data = ctypes.cast(res.str, ctypes.POINTER(ctypes.c_uint8 * res.len))[0]
                return "".join(map(chr, [*data]))
            
    str = _string()

    #define V function, argument types and result types 
    def __init__(self, fn, argtypes, restype):
        self.fn = fn
        self.argslen = len(argtypes)
        self.argtypes = [(arg) for arg in argtypes]
        self.restype = restype
        self.fn.argtypes = [self._filter(argtype) for argtype in argtypes]
        self.fn.restype = self._filter(self.restype)

    #translate inputs to V format
    def __call__(self, *args):
        if self.argslen != len(args):
            ...
        args = [argtype(arg) for arg, argtype in zip(args, self.argtypes)]

        out = self.fn(*args)

        out = self._unzip(out)

        return out
    
    #ensure correct set for argtypes/restype
    def _filter(self, type):
        if isinstance(type, wrapper.Array): return ArrayV
        if isinstance(type, wrapper._string): return StringV
        return type

    #ensure translate structures to python form
    def _unzip(self, out):
        if isinstance(self.restype, wrapper.Array) or isinstance(self.restype, wrapper._string):
           return self.restype.out(out)
        return out