module test

[export: 'my_fn']
pub fn my_fn(a string, b int) string{
	return a.repeat(b)
}