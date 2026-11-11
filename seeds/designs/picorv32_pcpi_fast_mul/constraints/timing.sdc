# picorv32_pcpi_fast_mul: upstream-referenced clock + explicit evaluation assumptions.
# Upstream commit: ef203c2b0a3fb793280f5114941416c425c5b461
# Clock reference (area evaluation, originally picorv32_axi):
# https://github.com/YosysHQ/picorv32/blob/ef203c2b0a3fb793280f5114941416c425c5b461/scripts/vivado/synth_area.xdc
# The 20 ns reference is reused for this standalone block; it is not an ASIC fmax claim.
# All other numeric values below are benchmark assumptions, not measured specifications.
# OpenSTA command units are explicit: 0.010 pF = 10 fF for every Liberty.
set_cmd_units -time ns -capacitance pF

create_clock -name core_clk -period 20.000 -waveform {0.000 10.000} [get_ports clk]

# Assumed ideal-clock slew and residual jitter/skew budget; no propagated clock tree.
set_clock_transition 0.100 [get_clocks core_clk]
set_clock_uncertainty -setup 0.200 [get_clocks core_clk]
set_clock_uncertainty -hold 0.050 [get_clocks core_clk]

# Assumed same-domain registered environment; 20% of period reserved at each boundary.
# Zero minimum external delay is an explicit evaluation assumption.
# Clock is excluded; synchronous reset and control inputs remain timed normally.
set data_inputs [lsearch -all -inline -not -exact [all_inputs] [get_ports clk]]
set_input_delay -clock core_clk -max 4.000 $data_inputs
set_input_delay -clock core_clk -min 0.000 $data_inputs
set_input_transition 0.100 $data_inputs

set_output_delay -clock core_clk -max 4.000 [all_outputs]
set_output_delay -clock core_clk -min 0.000 [all_outputs]
set_load 0.010 [all_outputs]

# No reset/IRQ false paths, multicycle paths, case analysis, or RTL parameter overrides.
# Real asynchronous interfaces require a separate CDC/integration constraint review.
