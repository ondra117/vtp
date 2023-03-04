import sys

sys.path.append('../../')

from vtp import wrapper as wp
from vtp import compile

#compile and load V file
lib = compile("./lib.v")

#define arguments types and result type
lib.my_fn = wp(lib.my_fn, [wp.str, wp.i32], wp.str)

out = lib.my_fn("abcd", 5)

print(out)