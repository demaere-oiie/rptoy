# playing with GCD
The `gcd` test, with its execution pattern of (A|B)*, runs afoul of the unpredictable branching mentioned by [Tratt](https://tratt.net/laurie/blog/2012/fast_enough_vms_in_fast_enough_time.html) — not unexpectedly, because unpredictable branches are also a problem for hardware, and like hardware (unlike method JITs), tracing JITs experience code as a stream of ops.
```
gcd := (x@x,x),Rep.(x-y,y @ x,(y<x) :: x,y-x @ (x<y),y)
```

It's not a big deal for me at this point, because the JIT still manages to come in within a factor of 2 of handwritten rpython, but I did learn a few things while playing with it:

## non-meta rpython does well
AOT compilation at the rpython level does well with the following (handwritten) code:
```
def gcd(i):
   m,n = i.head, i.tail
   while not m.eq(n):
       if   m.lt(n): n=n.sub(m)
       elif n.lt(m): m=m.sub(n)
   return m
```
but without a method JIT, it seems ~~we have no hope of generating this from the meta level~~.

Actually, that's not true. The JIT does eventually generate a CFG which includes the effective loop above, but for $REASONS it only gets there after generating several partial approximations. Maybe I can play with some JIT settings to improve this behaviour?

## branchless loops trace well
As with all the other tests, rpython's tracing JIT does an amazing job when given a straight-line loop.
```
gcd := (m@m,m),Rep.(y,max.(m,n)-y @ m,n ~ y:=min.(m,n))
```
gets JIT'ted to something that approaches the handwritten:
```
def gcd(i):
   m,n = i.head, i.tail
   while m.ne(n):
       x = m.max(n)
       y = m.min(n)
       m = y
       n = x.sub(y)
   return m
```
## the tracer is aggressive ... and that's good
My first attempt to produce a branchless loop failed, because I had called `max` and `min` at the rpython level, and the tracer had looked *inside* these functions to find branches and produce the usual nest of guards and bridges.

My next attempt defined `min` as `RegBox((x<=y)*x + (y<x)*y)` and `max` as `RegBox((x>y)*x + (y>=x)*y)`.
Not only did the JIT generate a single tight loop, but even though the calls to these functions were each in distinct opcodes, it was pleasantly surprising that the SSA optimisation is strong enough that, having calculated the value of `x<=y`, it simply reused it for `y>=x` (`y<x`and `x>y`, respectively).
