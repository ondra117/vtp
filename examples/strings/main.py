import sys

sys.path.append('../../')

from vtp import wrapper as wp
from vtp import compile

lib = compile("./lib.v")

lib.my_fn = wp(lib.my_fn, [wp.str, wp.i32], wp.str)

out = lib.my_fn("abcd", 5)

print(out)