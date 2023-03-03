module test

[export: 'my_fn']
fn my_fn(a string, b int) string{
	mut c := a
	for _ in 0..b{
		c += a
	}
	return c
}