import ctypes
import os
import numpy as np

def compile(v_path: str):
    os.system(f"v -d no_backtrace -shared {v_path}")
    return ctypes.CDLL(v_path.replace(".v", ".dll"))

class ArrayV(ctypes.Structure):
    _fields_ = [
                ('element_size', ctypes.c_int32),
                ('data', ctypes.POINTER(ctypes.c_void_p)),
                ('offset', ctypes.c_int32),
                ('len', ctypes.c_int32),
                ('cap', ctypes.c_int32),
                ('flags', ctypes.c_int32),
               ]

class wrapper:
    i8 = ctypes.c_int8
    i16 = ctypes.c_int16
    i32 = ctypes.c_int32
    i64 = ctypes.c_int64
    f32 = ctypes.c_float
    f64 = ctypes.c_double
    bool = ctypes.c_bool
    retyp = {ctypes.c_int8: np.int8, ctypes.c_int16: np.int16, ctypes.c_int32: np.int32,
              ctypes.c_int64: np.int64, ctypes.c_float: np.float32, ctypes.c_double: np.float64,
              ctypes.c_bool: np.bool8}
    class Array:
        def __init__(self, type):
            self.type = type

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

        def __mul__(self, y):
            def multiply(*arg):
                data = [None] * y
                for idx in range(y):
                    data[idx] = self(arg[idx])
                return (ArrayV * y)(*data)
            return multiply
        
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

            

    def __init__(self, fn, argtypes, restype):
        self.fn = fn
        self.argslen = len(argtypes)
        self.argtypes = [(arg) for arg in argtypes]
        self.restype = restype
        self.fn.argtypes = [ArrayV if isinstance(argtype, wrapper.Array) else argtype for argtype in argtypes]
        self.fn.restype = ArrayV if isinstance(self.restype, wrapper.Array) else self.restype

    def __call__(self, *args):
        if self.argslen != len(args):
            ...
        args = [argtype(arg) for arg, argtype in zip(args, self.argtypes)]

        out = self.fn(*args)

        if isinstance(self.restype, wrapper.Array):
            out = self.restype.out(out)

        return out