# TinyML RISC CPU

A compact, single-cycle 32-bit RISC core that doubles as a miniature TinyML accelerator. The base datapath remains intentionally simple—no pipeline, no cache—but the ISA now includes MAC4 plus a trio of “Level-3 ML” helpers (CONV3, SIGMOID, and ACC) so you can demonstrate real TinyML behavior in one self-contained Verilog project.

## Highlights
- **Single-cycle core**: PC, instruction ROM, decoder, control unit, parity-protected register file, and ALU wired together in one readable datapath.
- **MAC4 instruction**: Treats each 32-bit operand as four signed int8 lanes and computes `a0*b0 + a1*b1 + a2*b2 + a3*b3` in one cycle.
- **Level-3 ML helpers**  
  - **CONV3 (`1101`)** multiplies three signed 8-bit lanes from each source register—perfect for sliding windows and FIR filters.  
  - **Piecewise SIGMOID (`1110`)** clamps to −128 / +127 outside ±64, otherwise returns `a >>> 1` in the low byte.  
  - **TinyML accumulator (`1111`)** writes to a dedicated `acc` register (independent of the regfile) so MAC/conv results can be chained without shuttling through memory.
- **Parity-protected register file**: Sixteen 32-bit registers with parity stored and checked on every read path.
- **Verbose testbench + plotting flow**: Every cycle is logged (`TRACE …` line) so you can generate plots or inspect the accelerator behavior without waveform viewers.

## Directory Layout
```
tinyml_risc_cpu/
├── rtl/
│   ├── alu.v                # arithmetic/logic + MAC4 unit
│   ├── control_unit.v       # decode-to-control mapping
│   ├── cpu_top.v            # ties everything together
│   ├── decoder.v            # field extractor
│   ├── instruction_memory.v # small demo program ROM
│   ├── pc.v                 # +4 program counter
│   └── regfile.v            # 16x32b regs with parity
├── tb/
│   └── cpu_tb.v             # verbose simulation harness
├── synth/
│   └── synth.ys             # Yosys script
└── sta/
    └── constraints.sdc      # 100 MHz timing constraint
```

## Building and Running the Testbench
1. Install a Verilog simulator (Icarus Verilog works great).
2. From the repo root:
   ```bash
   iverilog -g2012 -o cpu_tb.out rtl/*.v tb/cpu_tb.v
   vvp cpu_tb.out
   ```
3. The console log prints each cycle, showing the current PC, instruction, ALU result, parity status, and the full register file. When the MAC4 instruction issues, it calls out the dot-product result explicitly.

Expected TinyML demo flow:
1. Build MAC4 vectors in R1/R2 and compute `1*5 + 2*6 + 3*7 + 4*8 = 70` into R3.
2. Load three-lane convolution operands into R4/R5; CONV3 writes −3 into R6.
3. Run the piecewise sigmoid twice: a positive input saturates to +127 (R8), a negative input to −128 (R10).
4. Exercise the accumulator three times so `acc` ends at 195 (70 − 3 + 128), proving the dedicated accumulator behavior.

## Plotting the Run
The testbench emits a normalized `TRACE` line every cycle:

1. Capture the log:
   ```bash
   cd tinyml_risc_cpu
   iverilog -g2012 -o cpu_tb.out rtl/*.v tb/cpu_tb.v
   vvp cpu_tb.out | tee assets/cpu.log
   ```
2. Generate SVG visuals (pure Python, no extra dependencies):
   ```bash
   python3 scripts/gen_plots.py
   ```

You’ll get three SVGs in `assets/`:

![Simulation waveforms for PC/ALU/ACC](assets/sim_waveforms.svg)

Multiband waveforms highlight PC, ALU, and accumulator values with vertical “MAC4/CONV3/SIG/ACC” markers so you can see when each ML helper fires.

![Accumulator evolution](assets/accumulator.svg)

Each ACC instruction is annotated (`+= operand`) so you can see exactly how the dedicated accumulator reaches its final value.

![Opcode timeline](assets/opcode_timeline.svg)

Shows the instruction schedule (color legend + per-cycle tick marks) so you can correlate ROM flow with ALU behavior or timing analysis.

## Synthesis
The provided Yosys script targets a generic netlist:
```bash
cd synth
yosys synth.ys
```
That produces `cpu.json` and `cpu_synth.v` for downstream tooling.

## Constraints
`sta/constraints.sdc` defines a single 10 ns clock on `clk`, enough for basic static timing checks or handoff to a backend flow.

## Extending the Core
- Add more TinyML primitives (without breaking single-cycle timing) by extending `alu.v`, `decoder.v`, and `control_unit.v`.
- Expand the instruction memory or hook up a real memory interface.
- Modify the plot generator to overlay custom instrumentation or bring the trace into pandas/jupyter for deeper analysis.

Everything stays small enough to hack quickly, while the advanced ML instructions plus automated plots make it feel like a real TinyML accelerator rather than another toy ALU demo.
