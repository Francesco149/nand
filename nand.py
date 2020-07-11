#!/bin/env python

# this grew into a mess. I will eventually rewrite it into a proper HDL when I know exactly how
# I want it to be structured
# TODO: add time-based simulation and flipflop bultin

from tabulate import tabulate
import itertools


def s(string):
  return [x.strip() for x in string.split(" ")]


class Val:
  def __init__(self, bits=1, signed=False):
    self.val = None
    self.signed = signed
    if bits is not None:
      if bits < 1:
        raise ValueError("need 1+ bits")
      if bits == 1:
        self.bits = [self]
      else:
        self.bits = [Val() for _ in range(bits)]

  def mask(self):
    return (1 << len(self.bits)) - 1

  def __validate_range(self, start, end):
    if end is None:
      end = start
    if start < 0 or start > len(self.bits):
      raise IndexError("slice start %d is out of range" % start)
    if end < 0 or end > len(self.bits):
      raise IndexError("slice end %d is out of range" % end)
    return start, end

  def slice(self, start, end=None):
    """returns a reference to the given range of bits"""
    start, end = self.__validate_range(start, end)
    if start == end:
      return self.bits[start]
    res = Val(None)
    res.bits = [self.bits[i] for i in range(start, end + 1)]
    return res

  def slice_mask(self, start, end=None):
    """returns the bitmask for the given bit range"""
    start, end = self.__validate_range(start, end)
    mask = 0
    for i in range(start, end + 1):
      mask |= 1 << (len(self.bits) - i - 1)
    return mask

  def set(self, val):
    if len(self.bits) == 1:
      self.val = val & 1
    else:
      for i, v in enumerate(self.bits[::-1]):
        v.set((val & (1 << i)) >> i)
    return self

  def get(self):
    return int(self)

  def __int__(self):
    if len(self.bits) == 1:
      return self.val
    res = 0
    for val in self.bits:
      res = (res << 1) | val.get()
    if self.signed and self.bits[0].get():
      res = res - self.mask() - 1
    return res

  def __str__(self):
    return str(int(self))

  def combinations(self):
    """returns all possible values as integers"""
    return [x for x in range(1 << len(self.bits))]

  def assign(self, other, selfdesc="?", otherdesc="?"):
    if len(self.bits) != len(other.bits):
      raise ValueError(
          "%d -> %d: bit count mismatch for %s -> %s" % (
              len(self.bits), len(other.bits), selfdesc, otherdesc))
    self.set(int(other))

  def find_none_bit(self):
    for i, bit in enumerate(self.bits):
      if bit.val is None:
        return i
    return -1

  def fit(self, newbits):
    """resize to fit at least newbits bits"""
    while len(self.bits) < newbits:
      self.bits += [Val()]
    if len(self.bits) > 1 and self.bits[0] is self:
      self.bits[0] = Val()
      if self.val is not None:
        self.bits[0].set(self.val)


class Wiring:
  """
  syntax: "name(_start(_end))" start defaults to 0, end defaults to 0. range is inclusive
  examples: "x" "x_4" "x_4_8"
  """

  def __init__(self, text):
    if isinstance(text, int):
      self.value = text
      return
    self.value = None
    self.infer_width = False
    s = text.split("_")
    self.name = s[0]
    s = s[1:]
    if len(s) == 1:
      self.start = self.end = int(s[0])
    elif len(s) == 2:
      self.start = int(s[0])
      self.end = int(s[1])
    elif len(s) > 2:
      raise SyntaxError("'%s': invalid syntax for bit range" % text +
                        "(should be name_bitnum or name_start_end, inclusive)")
    else:
      self.start = self.end = 0
      self.infer_width = True

  def slice(self, val):
    if self.infer_width:
      return val
    return val.slice(self.start, self.end)

  def slice_mask(self, val):
    return val.slice_mask(self.start, self.end)

  def __str__(self):
    if self.infer_width:
      return self.name
    return "%s[%d:%d]" % (self.name, self.start, self.end)


class InOut:
  """
  syntax: "name(:numbits)". numbits defaults to 1. underscores not allowed in the name
  examples: "x:16" "x"
  """

  def __init__(self, text):
    s = text.split(":")
    self.name = s[0]
    self.signed = False
    if self.name[0] == '+':
      self.signed = True
      self.name = self.name[1:]
    if "_" in self.name:
      raise SyntaxError("'%s': input name cannot contain underscore" % text)
    s = s[1:]
    if len(s) == 0:
      self.bits = 1
    elif len(s) == 1:
      self.bits = int(s[0])
    else:
      raise SyntaxError("'%s': invalid syntax for input size" % text)


class Vals:
  def __init__(self, vals_by_name):
    self.vals = vals_by_name
    self.resolved_bits = {k: 0 for k in self.vals}

  def resolved(self, k, s=None):
    bits = self.resolved_bits[k]
    if s is None:
      s = self.vals[k]
    mask = s.mask()
    return (bits & mask) == mask and s.find_none_bit() < 0

  def set(self, dst, v, vdesc="?"):
    dstval = dst.slice(self.vals[dst.name])
    dstval.assign(v, dst.name, vdesc)
    mask = dst.slice_mask(self.vals[dst.name])
    bits = self.resolved_bits[dst.name]
    if bits & mask != 0:
      raise ValueError(
          "'%s' -> '%s': destination bits already wired" % (k, dst))
    self.resolved_bits[dst.name] |= mask


class Chip:
  def __init__(self, name):
    self.name = name
    self.inputs = []
    self.outputs = []
    self.internals = []
    self.builtin = None
    self.parts = []
    self.__cache_map = {}

  def __cache(self, k, f):
    if k not in self.__cache_map:
      self.__cache_map[k] = f()
    return self.__cache_map[k]

  def run(self, **kwargs):
    inputs = kwargs
    if self.builtin:
      return self.builtin(**inputs), {}

    def parse_outputs():
      outputs = [InOut(x) for x in self.outputs]
      return {x.name: Val(x.bits, x.signed) for x in outputs}

    outputs = self.__cache("run_outputs", parse_outputs)

    # automatically figure out number of bits for internal buses
    # shit, this still requires you to specify width at least once
    def eval_internals():
      internals = {}
      for chip, wiring in self.parts:
        for k, v in wiring:
          if v.value is not None:
            continue
          if v.name not in self.internals:
            continue
          if v.name not in internals:
            internals[v.name] = Val()
          val = internals[v.name]
          bits = len(val.bits)
          low = min(v.start, v.end)
          hi = max(v.start, v.end)
          newbits = max(hi + 1, bits)
          internals[v.name].fit(newbits)

      return {k: len(v.bits) for k, v in internals.items()}

    internals = {k: Val(v) for k, v in self.__cache(
        "run_internals", eval_internals).items()}
    internals = Vals(internals)

    # there's probably a good way to do this, but i just loop over all the parts multiple times
    # until everything is resolved
    done = {}
    last_unresolved = 0
    while True:
      num_unresolved = 0
      unresolved_items = []
      for i, (chip, wiring) in enumerate(self.parts):
        chip_inputs = [InOut(x) for x in chip.inputs]
        chip_inputs = {x.name: Val(x.bits, x.signed) for x in chip_inputs}
        unresolved = False

        for k, v in wiring:
          if k.name not in chip_inputs:
            continue

          dst = k.slice(chip_inputs[k.name])

          def assignment(src):
            try:
              dst.assign(v.slice(src[v.name]), k.name, v.name)
            except TypeError:
              print("!!! assignment failed! (%s.%s) %s -> %s. is this disconnected?\n" %
                    (self.name, chip.name, k, v))
              raise

          if v.value is not None:
            dst.set(v.value)
          elif v.name in inputs:
            assignment(inputs)

          elif v.name in internals.vals:
            s = v.slice(internals.vals[v.name])
            if not internals.resolved(v.name, s):
              unresolved = True
              break
            assignment(internals.vals)

        if unresolved:
          num_unresolved += 1
          unresolved_items += [(chip, wiring)]
          continue

        if i in done:
          continue

        res, _ = chip.run(**chip_inputs)
        for k, v in res.items():
          dsts = [(wk, wv) for wk, wv in wiring if wk.name == k]
          for src, dst in dsts:
            if dst.name in internals.vals:
              internals.vals[dst.name].fit(len(v.bits))
              internals.set(dst, v)
            else:
              dst.slice(outputs[dst.name]).assign(src.slice(v), dst, src)

        done[i] = True

      if num_unresolved == 0:
        break
      if num_unresolved == last_unresolved:
        for chip, wiring in unresolved_items:
          print(self.name + "." + chip.name)
          for k, v in wiring:
            print("  unresolved: %s %s" % (k, v))
        print("")
        raise ValueError("unresolvable circuit, check your wirings")
      last_unresolved = num_unresolved

    for k, val in outputs.items():
      while True:
        bit = val.find_none_bit()
        if bit < 0:
          break
        print("W: bit %d of %s was never set, defaulting to zero" % (bit, k))
        val.slice(bit).set(0, "(zero)")

    return outputs, internals.vals

  def add(self, chip, **kwargs):
    # this is absolute garbage
    inputs = self.__cache("add_inputs", lambda: [
        InOut(x).name for x in self.inputs])
    outputs = self.__cache("add_outputs", lambda: [
        InOut(x).name for x in self.outputs])
    parsed = [(Wiring(k), Wiring(v)) for k, v in kwargs.items()]
    for k, v in parsed:
      chipinputs = [InOut(x).name for x in chip.inputs]
      chipoutputs = [InOut(x).name for x in chip.outputs]
      if k.name not in chipinputs and k.name not in chipoutputs:
        raise ValueError("%s is not an input or output of %s" % (k, chip))
      if v.value is not None:
        continue
      if v.name not in outputs and v.name not in inputs and v.name not in self.internals:
        self.internals += [v.name]
    self.parts += [(chip, parsed)]

  def __fmt(self, fmt, k, v):
    if k in fmt:
      return fmt[k].format(int(v))
    return int(v)

  def truth(self, fmt={}, data=[]):
    spacer = [" " * 10] if self.internals else []
    results = []
    parsed_inputs = [InOut(k) for k in self.inputs]
    outputnames = [InOut(k).name for k in self.outputs]
    inputs = {k.name: Val(bits=k.bits) for k in parsed_inputs}
    inputnames = [x.name for x in parsed_inputs]
    inputvals = [inputs[x] for x in inputnames]
    data = data or itertools.product(
        *[x.combinations() for x in inputvals])
    for values in data:
      def setinputs():
        for i, x in enumerate(values):
          inputvals[i].set(x)
      try:
        setinputs()
      except TypeError:
        values = (values,)
        setinputs()
      outputs, internals = self.run(**inputs)
      item = ['']
      item += [self.__fmt(fmt, inputnames[i], x) for i, x in enumerate(values)]
      item += [self.__fmt(fmt, k, outputs[k]) for k in outputnames]
      item += spacer
      item += [self.__fmt(fmt, k, internals[k]) for k in self.internals]
      results += [item]
    return tabulate(results, headers=[self.name] + inputnames +
                    outputnames + spacer + self.internals) + "\n"

  def __str__(self):
    return "%s(in: %s, out: %s)" % (self.name, self.inputs, self.outputs)


Nand = Chip("Nand")
Nand.inputs = ["a", "b"]
Nand.outputs = ["out"]
Nand.builtin = lambda a, b: {"out": Val().set(~(a.get() & b.get()))}

if __name__ == "__main__":
  print(Nand.truth())
