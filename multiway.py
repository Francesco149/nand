#!/bin/env python

from nand import Chip, s
from basics import Or
from basics16 import Mux16, DMux16

Or8Way = Chip("Or8Way")
Or8Way.inputs = s("a b c d e f g h")
Or8Way.outputs = s("out")
Or8Way.add(Or, a="a", b="b", out="ab")
Or8Way.add(Or, a="ab", b="c", out="abc")
Or8Way.add(Or, a="abc", b="d", out="abcd")
Or8Way.add(Or, a="abcd", b="e", out="abcde")
Or8Way.add(Or, a="abcde", b="f", out="abcdef")
Or8Way.add(Or, a="abcdef", b="g", out="abcdefg")
Or8Way.add(Or, a="abcdefg", b="h", out="out")

Mux4Way16 = Chip("Mux4Way16")
Mux4Way16.inputs = s("a:16 b:16 c:16 d:16 sel:2")
Mux4Way16.outputs = s("out:16")
Mux4Way16.add(Mux16, a="a", b="b", sel="sel_1", out="muxAB_0_15")
Mux4Way16.add(Mux16, a="c", b="d", sel="sel_1", out="muxCD_0_15")
Mux4Way16.add(Mux16, a="muxAB", b="muxCD", sel="sel_0", out="out")

DMux4Way16 = Chip("DMux4Way16")
DMux4Way16.inputs = s("x:16 sel:2")
DMux4Way16.outputs = s("a:16 b:16 c:16 d:16")
DMux4Way16.add(DMux16, x="x", a="dmuxAB_0_15", b="dmuxCD_0_15", sel="sel_0")
DMux4Way16.add(DMux16, x="dmuxAB", a="a", b="b", sel="sel_1")
DMux4Way16.add(DMux16, x="dmuxCD", a="c", b="d", sel="sel_1")

Mux8Way16 = Chip("Mux8Way16")
Mux8Way16.inputs = s("a:16 b:16 c:16 d:16 e:16 f:16 g:16 h:16 sel:3")
Mux8Way16.outputs = ["out:16"]
Mux8Way16.add(Mux4Way16, a="a", b="b", c="c", d="d",
              sel="sel_1_2", out="muxABCD_0_15")
Mux8Way16.add(Mux4Way16, a="e", b="f", c="g", d="h",
              sel="sel_1_2", out="muxEFGH_0_15")
Mux8Way16.add(Mux16, a="muxABCD", b="muxEFGH", sel="sel_0", out="out")

DMux8Way16 = Chip("DMux8Way16")
DMux8Way16.inputs = s("x:16 sel:3")
DMux8Way16.outputs = s("a:16 b:16 c:16 d:16 e:16 f:16 g:16 h:16")
DMux8Way16.add(DMux16, x="x", a="dmuxABCD_0_15",
               b="dmuxEFGH_0_15", sel="sel_0")
DMux8Way16.add(DMux4Way16, x="dmuxABCD", a="a",
               b="b", c="c", d="d", sel="sel_1_2")
DMux8Way16.add(DMux4Way16, x="dmuxEFGH", a="e",
               b="f", c="g", d="h", sel="sel_1_2")

if __name__ == "__main__":
  d = [(0, 0, 0, 0, 0, 0, 0, 0),
       (1, 0, 0, 0, 0, 0, 0, 0),
       (0, 1, 0, 0, 0, 0, 0, 0),
       (0, 0, 1, 0, 0, 0, 0, 0),
       (0, 0, 0, 1, 0, 0, 0, 0),
       (0, 0, 0, 0, 1, 0, 0, 0),
       (0, 0, 0, 0, 0, 1, 0, 0),
       (0, 0, 0, 0, 0, 0, 1, 0),
       (0, 0, 0, 0, 0, 0, 0, 1),
       (1, 1, 1, 1, 1, 1, 1, 1)]
  print(Or8Way.truth(data=d))

  d = [(99, 0, 0, 0, 0),
       (0, 88, 0, 0, 1),
       (0, 0, 77, 0, 2),
       (0, 0, 0, 66, 3)
       ] + [(0, 0, 0, 0, x) for x in range(4)]
  print(Mux4Way16.truth(data=d))

  d = [(420, x) for x in range(4)] + [(0, x) for x in range(4)]
  print(DMux4Way16.truth(data=d))

  d = [(99, 0, 0, 0, 0, 0, 0, 0, 0),
       (0, 88, 0, 0, 0, 0, 0, 0, 1),
       (0, 0, 77, 0, 0, 0, 0, 0, 2),
       (0, 0, 0, 66, 0, 0, 0, 0, 3),
       (0, 0, 0, 0, 55, 0, 0, 0, 4),
       (0, 0, 0, 0, 0, 44, 0, 0, 5),
       (0, 0, 0, 0, 0, 0, 33, 0, 6),
       (0, 0, 0, 0, 0, 0, 0, 22, 7)
       ] + [(0, 0, 0, 0, 0, 0, 0, 0, x) for x in range(8)]
  print(Mux8Way16.truth(data=d))

  d = [(420, x) for x in range(8)] + [(0, x) for x in range(8)]
  print(DMux8Way16.truth(data=d))
