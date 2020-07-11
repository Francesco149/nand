#!/bin/env python

from nand import Chip, s
from adder import Add16
from basics import Not, Or
from basics16 import And16, Not16, Mux16
from multiway import Or8Way

# the ALU used in "From Nand To Tetris"
HackALU = Chip("HackALU")
# zero x, negate x, zero y, negate y, addition/AND, negate out
HackALU.inputs = s("+x:16 +y:16 zx nx zy ny f no")
HackALU.outputs = s("+out:16 zr ng")

for x in "xy":
  HackALU.add(Mux16, sel="z" + x, a=x, b=0, out=x + "PostZ_0_15")
  HackALU.add(Not16, x=x + "PostZ", out=x + "not_0_15")
  HackALU.add(Mux16, sel="n" + x, a=x + "PostZ",
              b=x + "not", out=x + "PostN_0_15")

HackALU.add(Add16, a="xPostN", b="yPostN", out="sumXY_0_15")
HackALU.add(And16, a="xPostN", b="yPostN", out="andXY_0_15")
HackALU.add(Mux16, sel="f", a="andXY", b="sumXY", out="fout_0_15")
HackALU.add(Not16, x="fout", out="notFout_0_15")
HackALU.add(Mux16, sel="no", a="fout", b="notFout",
            out="out", out_0_15="outi_0_15", out_0="ng_0")

HackALU.add(Or8Way, out="orhi",
            **{k: "outi_%d" % i for i, k in enumerate("abcdefgh")})
HackALU.add(Or8Way, out="orlo",
            **{k: "outi_%d" % (i + 8) for i, k in enumerate("abcdefgh")})
HackALU.add(Or, a="orhi", b="orlo", out="notZR")
HackALU.add(Not, x="notZR", out="zr")

if __name__ == "__main__":
  d = [
      # x   y  zx nx zy ny  f no
      (420, 69, 1, 0, 1, 0, 1, 0),  # 0
      (420, 69, 1, 1, 1, 1, 1, 1),  # 1
      (420, 69, 1, 1, 1, 0, 1, 0),  # -1
      (420, 69, 0, 0, 1, 1, 0, 0),  # x
      (420, 69, 1, 1, 0, 0, 0, 0),  # y
      (420, 69, 0, 0, 1, 1, 0, 1),  # !x
      (420, 69, 1, 1, 0, 0, 0, 1),  # !y
      (420, 69, 0, 0, 1, 1, 1, 1),  # -x
      (420, 69, 1, 1, 0, 0, 1, 1),  # -y
      (420, 69, 0, 1, 1, 1, 1, 1),  # x+1
      (420, 69, 1, 1, 0, 1, 1, 1),  # y+1
      (420, 69, 0, 0, 1, 1, 1, 0),  # x-1
      (420, 69, 1, 1, 0, 0, 1, 0),  # y-1
      (420, 69, 0, 0, 0, 0, 1, 0),  # x+y
      (420, 69, 0, 0, 0, 1, 1, 1),  # y-x
      (0xFFF, 0xFF, 0, 0, 0, 0, 0, 0),  # x&y
      (0b01010101, 0b10101010, 0, 1, 0, 1, 0, 1),  # x|y
  ]
  print(HackALU.truth(data=d))
