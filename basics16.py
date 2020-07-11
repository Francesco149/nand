#!/bin/env python

from nand import Chip
from basics import Not, And, Or, Mux, DMux

ab = ["a:16", "b:16"]
out = ["out:16"]
x = ["x:16"]
sel = ["sel"]

Not16 = Chip("Not16")
Not16.inputs = x
Not16.outputs = out
for i in range(16):
  Not16.add(Not, x="x_%d" % i, out="out_%d" % i)

And16 = Chip("And16")
And16.inputs = ab
And16.outputs = out
for i in range(16):
  And16.add(And, a="a_%d" % i, b="b_%d" % i, out="out_%d" % i)

Or16 = Chip("Or16")
Or16.inputs = ab
Or16.outputs = out
for i in range(16):
  Or16.add(Or, a="a_%d" % i, b="b_%d" % i, out="out_%d" % i)

Mux16 = Chip("Mux16")
Mux16.inputs = ab + sel
Mux16.outputs = out
for i in range(16):
  Mux16.add(Mux, a="a_%d" % i, b="b_%d" % i, sel="sel", out="out_%d" % i)

DMux16 = Chip("DMux16")
DMux16.inputs = x + sel
DMux16.outputs = ab
for i in range(16):
  DMux16.add(DMux, x="x_%d" % i, sel="sel", a="a_%d" % i, b="b_%d" % i)

if __name__ == "__main__":
  def b16(ks):
    return {k.strip(): "0b{:016b}" for k in ks.split(",")}

  print(Not16.truth(fmt=b16("x, out"),
                    data=[0b0000000000000000, 0b1010101010101010,
                          0b1111111100000000, 0b1111111111111111]))

  print(And16.truth(fmt=b16("a, b, out"),
                    data=[(0b0000000000000000, 0b1111111111111111),
                          (0b0101010101010101, 0b1111111111111111),
                          (0b0101010101010101, 0b1111111100000000),
                          (0b1111111111111111, 0b1111111111111111)]))

  print(Or16.truth(fmt=b16("a, b, out"),
                   data=[(0b0000000000000000, 0b1111111111111111),
                         (0b0101010101010101, 0b1111111111111111),
                         (0b0101010101010101, 0b1111111100000000),
                         (0b1111111111111111, 0b1111111111111111)]))

  print(Mux16.truth(data=[(420, 69, 0), (420, 69, 1), (0, 0, 0), (0, 0, 1)]))
  print(DMux16.truth(data=[(420, 0), (420, 1), (0, 0), (0, 1)]))
