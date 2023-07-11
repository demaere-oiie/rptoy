# rptoy
playing with rpython: build via `rpython -O jit rptoy.py`

## goals
this is an attempt to (a) learn how to structure an [rpython](https://rpython.readthedocs.io/en/latest/) bytecode interpreter, and (b) check that we can get the JIT to optimise in cases we hope it will

## preliminary results
promising! *gcd* shows that multiway loop nests are JIT'ed as well as plain loops; that *cfac* is JIT'ed to similar performance as *fac* shows that the JIT successfully elides
the gratuitous closure call that occurs in the former and not in the latter. *csum* and *sum* put a much cheaper op in the closure, and the JIT still performs admirably. Finally *tare*
(400x the null program) shows that we don't have an onerous startup overhead.

| test  | w/ JIT | no JIT |
| ------------- | ------------- | -------- |
| tare | 0m0.009s | 0m0.011s |
| fac  | 0m0.138s | 0m0.168s |
| cfac | 0m0.144s | 0m0.174s |
| gcd | 0m0.079s | 0m0.119s |
| sum | 0m0.114s | 0m0.185s |
| csum | 0m0.112s | 0m0.242s |

<dl>
  <dt>fac</dt>
  <dd>Tail recursive factorial with an accumulator</dd>
  <dt>cfac</dt>
  <dd>Same as <em>fac</em> but with a gratuitous closure call enclosing the multiplication</dd>
  <dt>gcd</dt>
  <dd>Dijkstra's symmetric two-branched subtractive gcd; tests bridge generation</dd>
  <dt>sum</dt>
  <dd>Like <em>fac</em> but adds instead of multiplies to increase the relative cost of control flow</dd>
  <dt>csum</dt>
  <dd>Like <em>cfac</em>, it wraps the addition in a gratuitous closure call</dd>
</dl>

## things learned so far
- *rpython* does a much better job with class-structured internals
- to make things easy on the typer, use *assert* and bind directly to variables
- can_enter_jit and jit_merge_point must have no ops in between
- the "virtualizables" argument is plural but can only take a single argument
- interpreter locals that aren't live between calls don't need to be listed in *reds*

## future work
- continue testing/integrating CF Bolz-Tereick's other recommendations
- try out machine ints (esp. w/ bigint interop) and floats
- maybe move beyond hand-assembled tests?
