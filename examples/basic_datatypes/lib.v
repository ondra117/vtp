module test

[export: 'my_fn']
fn my_fn(a f32, b int) bool{
	return (a * b) == 4.0
}