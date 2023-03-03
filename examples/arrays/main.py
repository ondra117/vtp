import sys

sys.path.append('../../')

from vtp import wrapper as wp
from vtp import compile
import numpy as np

lib = compile("./lib.v")

lib.my_fn = wp(lib.my_fn, [wp.Array(wp.Array(wp.i32))], wp.Array(wp.Array(wp.i32)))

inp = np.array([[1, 2], [3, 4], [5, 6]], dtype=np.int32)

out = lib.my_fn(inp)

print(out)