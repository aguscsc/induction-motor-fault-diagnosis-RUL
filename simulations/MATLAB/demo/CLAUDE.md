# DC Motor Fault Diagnosis — Model-Based FDI

## Goal
Build a proof-of-concept demo (for a professor pitch) implementing the classical
model-based Fault Detection and Isolation (FDI) pipeline on a DC motor:

  motor plant model -> fault injection -> state observer -> residual generation -> threshold decision

Primary deliverable is a working simulation, not a full research contribution.
Keep scope tight; propose extensions rather than building them all up front.

## Tooling
- MATLAB / Simulink (chosen over Python for this project — visual block diagram
  is easier to present, faculty are MATLAB-fluent, Control System Toolbox has
  built-in `place()` / `kalman()` for observer design).

## Plant Model
DC motor, linear state-space, armature voltage control. Chosen over induction
motor / PMSM specifically because it's linear — enables clean Luenberger/Kalman
observer design without nonlinear dynamics, which matters for a first
proof-of-concept.

States: x = [omega; i]   (angular velocity, armature current)
Input:  u = armature voltage V_a
Output: y = omega (speed is measured; current is not)

    xdot = A x + B u
    y    = C x = [1 0] x

    A = [ -B/J      Kt/J ]        B = [   0   ]        C = [1 0]
        [ -Kb/La   -Ra/La]            [ 1/La  ]

Reference numeric values (YA-070 motor, from anchor paper below — exact match
NOT required, motor parameters vary by source):
- Ra = 7 Ohm, La = 0.008436 H
- J = 2.2097e-4 kg.m^2, B (friction) = 1.65e-4 N.m/rad/s
- Kb = 0.094 V/rad/s, Kt = 0.094 N.m/A
- Resulting A = [-0.7467, 425.4; -11.14, -829.8], B = [0; 118.5], C = [1 0]

## Reference Paper (anchor)
Almobaied, M. & Al-Mutayeb, Y. "Luenberger Observer-Based Speed Sensor Fault
Detection: real time implementation to DC Motors." JERT, Vol 10, Issue 1, 2023.

Use this paper for structure and fault-type inspiration, not for exact numeric
matching. Known gap in the paper (explicitly call this out in the pitch): it
does DETECTION only (single residual, single fixed threshold), no fault
ISOLATION/classification — that's the natural "next step" to propose.

## Fault Taxonomy
From the paper (sensor faults, speed sensor only):
- Sensor fault: measured speed drops to constant zero (sensor disconnect)
- Abrupt fault: step change added to sensor output (hardware damage)
- Intermittent fault: repeated pulses added to sensor output (partial wiring damage)
- Incipient fault: ramp/gradual drift in sensor output (aging, multiplicative)

Additional categories already scoped for this project (beyond the paper):
- Actuator fault: partial voltage loss to the motor
- Parametric fault: increased Ra (winding degradation), increased friction B
  (bearing wear) — these change the A matrix itself, not just the measurement

## Observer Design Notes
- Standard Luenberger form: xhat_dot = A xhat + B u + L(y - C xhat)
- Error dynamics: edot = (A - LC) e, where e = x - xhat (state error, used for
  the stability proof — NOT directly computable at runtime)
- Runtime-usable signal is the OUTPUT error / residual: r(t) = y(t) - yhat(t) = C*e(t)
- Observer poles (eigenvalues of A-LC) must be placed faster (more negative)
  than the plant's own dominant pole, or the estimate lags real transients and
  the residual can't distinguish "still converging" from "actual fault."
  Rule of thumb starting point: ~3-5x faster than the plant's slowest pole.
- Faster poles = larger L = more measurement noise injected into xhat. This is
  the same speed-vs-noise trade-off a Kalman filter resolves automatically via
  Q/R; with plain pole placement it's tuned by hand — worth showing a
  pole-speed-vs-residual-noise sweep as a figure in the pitch.
- Threshold: paper uses a FIXED threshold, calibrated empirically from
  fault-free residual noise (upper/lower bounds). Adaptive thresholding is a
  known alternative, out of scope for v1.

## Planned Extensions (in order of increasing effort, for the "next steps" slide)
1. Residual-shape classification: fault types already produce visibly
   different residual shapes (step / ramp / pulse-train / collapse) — add
   post-threshold logic to classify based on slope/persistence/sign.
2. Bank of observers (dedicated/generalized observer scheme) for real fault
   isolation — standard classical FDI approach.
3. RLS parameter tracking specifically for the parametric fault case (Ra, B
   drift) — isolates *which* parameter changed, rather than just flagging
   a residual anomaly.

## Status
- [ ] State-space model in MATLAB
- [ ] Simulink block diagram (plant + fault injection)
- [ ] Observer design (pole placement, gain L)
- [ ] Residual generation + threshold logic
- [ ] Fault sweep test (all fault types, log residual behavior)
- [ ] Pitch figures / slides
