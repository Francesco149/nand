#!/bin/env python

from nand import Chip, s
from basics import Xor, And, Or

HalfAdder = Chip("HalfAdder")
HalfAdder.inputs = s("a b")
HalfAdder.outputs = s("out carry")
HalfAdder.add(Xor, a="a", b="b", out="out")
HalfAdder.add(And, a="a", b="b", out="carry")

FullAdder = Chip("FullAdder")
FullAdder.inputs = s("a b c")
FullAdder.outputs = s("out carry")
FullAdder.add(HalfAdder, a="b", b="c", out="bc", carry="carryBC")
FullAdder.add(HalfAdder, a="a", b="bc", out="out", carry="carryABC")
FullAdder.add(Or, a="carryBC", b="carryABC", out="carry")
# even with 3 bits the maximum carry we can have is 1 bit so we can safely OR the carries since
# they will never both be 1

Add16 = Chip("Add16")
Add16.inputs = s("+a:16 +b:16")
Add16.outputs = s("+out:16")
for i in range(15):
  Add16.add(FullAdder, a="a_%d" % i, b="b_%d" % i, c="carry_%d" % (i + 1),
            out="out_%d" % i, carry="carry_%d" % i)
Add16.add(HalfAdder, a="a_15", b="b_15", out="out_15", carry="carry_15")

Inc16 = Chip("Inc16")
Inc16.inputs = s("x:16")
Inc16.outputs = s("out:16")
Inc16.add(Add16, a="x", b=1, out="out")

if __name__ == "__main__":
  print(HalfAdder.truth())
  print(FullAdder.truth())
  print(Add16.truth(fmt={"carry": "{:016b}"}, data=[
      (69, 420),
      (1234, 4321),
      (10, -5),
      (-20, -30),
      (-1, 1),
  ]))
  print(Inc16.truth(data=[(419,), (68,)]))
