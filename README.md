# rptoy
playing with rpython: build via `rpython -O jit rptoy.py`

## goals
this is an attempt to (a) learn how to structure an [rpython](https://rpython.readthedocs.io/en/latest/) bytecode interpreter, and (b) check that we can get the JIT to optimise in the cases we hope it will

## preliminary results
very promising! `gcd` shows that multiway loop nests are JIT'ed as well as plain loops; that `cfac` is JIT'ed to similar performance as *fac* shows that the JIT successfully elides
the gratuitous closure call that occurs in the former and not in the latter. `csum` and `sum` put a much cheaper op in the closure, and the JIT still performs admirably.
`hfac` and `hsum` are jitted equivalently to their non-inner-function variants, and `hgcd` comes close.
Finally `tare` (4000x the null program) shows that we don't have an onerous startup overhead.

| test  | w/ JIT | no JIT |
| ------------- | ------------- | -------- |
| tare |        0m0.008s |      0m0.008s|
| fac | 0m0.886s |      0m1.316s|
| cfac |        0m0.883s |      0m1.641s|
| hfac |        0m0.870s |      0m1.382s|
| gcd | 0m0.038s |      0m0.670s|
| hgcd |        0m0.051s |      0m0.756s|
| sum | 0m0.035s |      0m1.085s|
| csum |        0m0.034s |      0m1.884s|
| hsum |        0m0.035s |      0m1.229s|
| odd | 0m0.032s |      0m0.650s|


<dl>
  <dt>fac</dt>
  <dd>Tail recursive factorial with an accumulator</dd>
  <dt>cfac</dt>
  <dd>Same as <em>fac</em> but with a gratuitous closure call enclosing the multiplication</dd>
  <dt>hfac</dt>
  <dd>factorial again, but with a recursive inner helper</dd>
  <dt>gcd</dt>
  <dd>Dijkstra's symmetric two-branched subtractive gcd; tests bridge generation</dd>
  <dt>hgcd</dt>
  <dd>GCD with recursive inner helper</dd>
  <dt>sum</dt>
  <dd>Like <em>fac</em> but adds instead of multiplies to increase the relative cost of control flow</dd>
  <dt>csum</dt>
  <dd>Like <em>cfac</em>, it wraps the addition in a gratuitous closure call</dd>
  <dt>hsum</dt>
  <dd>Like <em>hfac</em></dd>
  <dt>odd</dt>
  <dd>Parity check via mutually recursive inner helpers</dd>
</dl>

## things learned so far
- `rpython` does a much better job with class-structured internals
- to make things easy on the typer, use *assert* and bind directly to variables
- `can_enter_jit` and `jit_merge_point` must not have any ops in between
- the "virtualizables" argument is plural but can only take a single argument
- interpreter locals that aren't live between calls don't need to be listed in *reds*
- machine int/bigint shimmering is very effective
- virtualisation is very sensitive to other changes, but when it works, it's amazing
- "[unpredictable loops](https://github.com/demaere-oiie/rptoy/blob/main/gcdthoughts.md)" have a longer jit warmup time

## future work
- continue testing/integrating CF Bolz-Tereick's other recommendations
- try out floats
- maybe move beyond hand-assembled tests?
