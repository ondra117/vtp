module test
//functions for initialization and deinitialise of lib, (it's important otherwise some things won't work)
fn C._vinit(argc int, argv &&char)
fn C._vcleanup()
[export: '_initialise']
pub fn initialise() { C._vinit(0, 0) }
[export: 'deinitialise']
pub fn deinitialise() { C._vcleanup() }


[export: 'my_fn']
fn my_fn(a f32, b int) bool{
	return (a * b) == 4.0
}