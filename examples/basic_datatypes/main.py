import sys

sys.path.append('../../')

from vtp import wrapper as wp
from vtp import compile

lib = compile("./lib.v")

lib.my_fn = wp(lib.my_fn, [wp.f32, wp.i32], wp.bool)

out = lib.my_fn(2.0, 2)

print(out)