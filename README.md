an exploration of building logic out of NAND gates.

I'm using python as kind of a poor man's HDL just because I like making my own tools. this is by no
means an efficient or elegant simulator, it's just something i hacked together as i explored

see `basics.py` and the other files for usage. if you don't wanna spoil yourself the fun of figuring
out the gates, try not to look past basics

`test.py` runs all the gates and compares output with the `.cmp` files

# requirements
* `pip install --user tabulate`

# basics.py
* 1-bit Not, And, Or, Xor: not much to explain here, basic primitives implemented with NAND
* 1-bit Mux, DMux: multiplexers can be used to interleave data on a shared bus. they're basically
  a switch - the sel determines which input is passed through to the output (0 for a, 1 for b).
  the DMux does the opposite, it takes 1 input and sel decides whether it gets passed through to
  a or b. a Mux/DMux pair with synchronized sel can transfer data for both a and b on a single bus

# basics16.py
* Not16, And16, Or16, Mux16, DMux16: straightforward extensions with 16-bit inputs

# multiway.py
* Or8Way: takes 8 1-bit inputs and ORs them together
* Mux4Way16, DMux4Way16: 4-way de/multiplexer. it takes 4 inputs and has a 2-bit sel (0-3).
  now we're talking. this could be used in an actual computer to transfer 16 bit values between
  components
* Mux8Way16, DMux8Way16: 8-way de/multiplexer. it takes 8 inputs and has a 3-bit sel (0-7)

# adder.py
* HalfAdder: adds 2 bits together and outputs sum and carry
* FullAdder: adds 3 bits together and outputs sum and carry
* Add16: now that we have a FullAdder we can put 15 of them in cascade plus a HalfAdder for the
  least significant bit which doesn't start with a carry. this gives us a 16-bit adder, which we
  could also cascade up to higher word sizes

# HackALU.py
implements the ALU used in "From NAND to Tetris". while this is a very neat design, I plan on coming
up with my own eventually

# References
I picked up the basics from https://www.nand2tetris.org/
