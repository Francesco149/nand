#!/bin/env python

from nand import Chip, Nand

ab = ["a", "b"]
x = ["x"]
out = ["out"]
sel = ["sel"]

Not = Chip("Not")
Not.inputs = x
Not.outputs = out
Not.add(Nand, a="x", b="x", out="out")

And = Chip("And")
And.inputs = ab
And.outputs = out
And.add(Nand, a="a", b="b", out="aNandB")
And.add(Not, x="aNandB", out="out")

Or = Chip("Or")
Or.inputs = ab
Or.outputs = out
Or.add(Not, x="a", out="notA")
Or.add(Not, x="b", out="notB")
Or.add(And, a="notA", b="notB", out="notAAndNotB")
Or.add(Not, x="notAAndNotB", out="out")

Xor = Chip("Xor")
Xor.inputs = ab
Xor.outputs = out
Xor.add(Not, x="a", out="notA")
Xor.add(Not, x="b", out="notB")
Xor.add(And, a="notA", b="b", out="notAAndB")
Xor.add(And, a="a", b="notB", out="aAndNotB")
Xor.add(Or, a="notAAndB", b="aAndNotB", out="out")

Mux = Chip("Mux")
Mux.inputs = ab + sel
Mux.outputs = out
Mux.add(Not, x="sel", out="notSel")
Mux.add(And, a="a", b="notSel", out="aAndNotSel")
Mux.add(And, a="b", b="sel", out="bAndSel")
Mux.add(Or, a="aAndNotSel", b="bAndSel", out="out")

DMux = Chip("DMux")
DMux.inputs = x + sel
DMux.outputs = ab
DMux.add(Not, x="sel", out="notSel")
DMux.add(And, a="notSel", b="x", out="a")
DMux.add(And, a="sel", b="x", out="b")

if __name__ == "__main__":
  print(Not.truth())
  print(And.truth())
  print(Or.truth())
  print(Xor.truth())
  print(Mux.truth())
  print(DMux.truth())
