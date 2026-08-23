% Qfóton - MATLAB / Simulink Photonic Quantum Co-Simulation Script
% Auto-generated for Silicon Photonic Thermal Phase Shifter DACs
clear; clc;
V_pi = 3.2; % Pi-voltage for thermo-optic phase shifters (V)
R_heater = 120.0; % Heater resistance (Ohms)
DAC_bits = 16; % Digital-to-Analog Converter resolution

% MZI Channel Control Table [MZI_ID, Mode_A, Mode_B, V_theta (V), V_phi (V), Power (mW)]
MZI_Control_Table = [
    1, 0, 1, 2.2627, 0.0, 0.0;
    2, 5, 6, 2.2627, 0.0, 0.0;
    3, 6, 7, 2.2627, 3.2, 85.33;
    4, 2, 3, 0.0, 0.0, 0.0;
    5, 1, 2, 2.2627, 3.2, 85.33;
    6, 0, 1, 2.2627, 0.0, 0.0;
    7, 3, 4, 1.6, 3.2, 85.33;
    8, 4, 5, 2.2627, 2.6804, 59.87;
    9, 5, 6, 2.2627, 3.2, 85.33;
    10, 6, 7, 2.2627, 3.2, 85.33;
    11, 4, 5, 0.0, 0.0, 0.0;
    12, 3, 4, 2.2627, 0.0, 0.0;
    13, 2, 3, 1.6, 3.2, 85.33;
    14, 1, 2, 2.2627, 3.2, 85.33;
    15, 0, 1, 2.2627, 0.0, 0.0;
    16, 1, 2, 0.0, 0.0, 0.0;
    17, 2, 3, 2.2627, 0.0, 0.0;
    18, 3, 4, 2.2627, 0.0, 0.0;
    19, 4, 5, 2.2627, 3.2, 85.33;
    20, 5, 6, 1.6, 0.0, 0.0;
    21, 6, 7, 0.0, 0.0, 0.0;
    22, 6, 7, 2.2627, 4.1743, 145.21;
    23, 5, 6, 0.0, 0.0, 0.0;
    24, 4, 5, 2.2627, 3.2, 85.33;
    25, 3, 4, 2.2627, 0.0, 0.0;
    26, 2, 3, 1.6, 3.2, 85.33;
    27, 1, 2, 2.2627, 3.2, 85.33;
    28, 0, 1, 0.0, 0.0, 0.0;
];

% Plot Thermal Dissipation per Channel
figure('Name', 'Qfoton Silicon Photonic DAC Control Voltages', 'Color', 'w');
bar(MZI_Control_Table(:, 1), MZI_Control_Table(:, 5), 'FaceColor', [0.02 0.71 0.83]);
xlabel('Mach-Zehnder Interferometer (MZI) Index');
ylabel('Phase Shifter DAC Voltage (V)');
title('Qfóton: Silicon Photonic Thermo-Optic Phase Shifter Control Voltages');
grid on;
disp('Qfóton MATLAB / Simulink Control Vector Loaded Successfully.');