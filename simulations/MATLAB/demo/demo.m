%parameters for motor YA-070
V = 24;         % nominal drive voltage [V]

Ra = 7;         % armature resistance [Ohm]
Ra_d = 8;         % armature resistance [Ohm]
La = 0.008436;  % armature inductance [H]
J  = 2.2097e-4; % rotor inertia [kg.m^2]
B  = 1.65e-4;   % viscous friction [N.m/(rad/s)]
Kb = 0.094;     % back-EMF constant [V/(rad/s)]
Kt = 0.094;     % torque constant [N.m/A]

% state-space model: x = [omega; i], u = Va, y = omega
A = [-B/J,    Kt/J;
     -Kb/La, -Ra/La];
B_ss = [0; 1/La];
C = [1, 0];

% degraded state-space model
A_d = [-B/J,    Kt/J;
     -Kb/La, -Ra_d/La];
% plant model
sys = ss(A, B_ss, C, 0);

% observer design (Luenberger, pole placement)
p_plant = pole(sys);
p_obs = 4 * p_plant;        % observer poles ~4x faster than plant poles (rule of thumb: 3-5x)
L = place(A', C', p_obs)';  % dual of state-feedback place(): gives L such that eig(A-LC) = p_obs

% observer as one State-Space block with 2 inputs: [u; y_measured]
Ae = A - L*C;               % observer error dynamics matrix
Be = [B_ss, L];       % 2x2: column 1 multiplies u, column 2 multiplies y
Ce = eye(2);          % output the full state estimate xhat = [omega_hat; i_hat]
De = zeros(2,2);
% plant transfer function (for reference)
sys_tf = tf(sys);
num = sys_tf.Numerator{1};
den = sys_tf.Denominator{1};