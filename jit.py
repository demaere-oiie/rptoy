import sys
from rpython import conftest




class o:
    view = False
    viewloops = True
conftest.option = o

from rptoy import main
from rpython.rlib.nonconst import NonConstant
from rpython.rlib import jit
from rpython.jit.metainterp.test.test_ajit import LLJitMixin

class TestLLtype(LLJitMixin):
    def run(self, what):
        def interp_w():
            main(["x", what, "function_threshold=10","10"])
        self.meta_interp(interp_w, [], listcomp=True, listops=True, backendopt=True, inline=True)

    def test_loop(self):
        self.run("hgcd")
