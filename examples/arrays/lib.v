module test

[export: 'my_fn']
fn my_fn(mut a [][]int) [][]int{
	a = a.map(it.map(it * 2))
	return a
}