% Qfóton - MATLAB / Simulink Photonic Quantum Co-Simulation Script
% Auto-generated for Silicon Photonic Thermal Phase Shifter DACs
clear; clc;
V_pi = 3.2; % Pi-voltage for thermo-optic phase shifters (V)
R_heater = 120.0; % Heater resistance (Ohms)
DAC_bits = 16; % Digital-to-Analog Converter resolution

% MZI Channel Control Table [MZI_ID, Mode_A, Mode_B, V_theta (V), V_phi (V), Power (mW)]
MZI_Control_Table = [
    1, 0, 1, 1.8475, 3.2, 85.33;
    2, 5, 6, 1.6, 3.2, 85.33;
    3, 6, 7, 2.2627, 3.9984, 133.23;
    4, 2, 3, 1.3064, 0.0, 0.0;
    5, 1, 2, 1.8997, 0.0, 0.0;
    6, 0, 1, 1.7239, 3.2, 85.33;
    7, 3, 4, 2.2627, 3.9839, 132.26;
    8, 4, 5, 1.4939, 2.1467, 38.4;
    9, 5, 6, 1.4766, 0.0, 0.0;
    10, 6, 7, 1.9132, 3.9984, 133.23;
    11, 4, 5, 1.3064, 0.0, 0.0;
    12, 3, 4, 2.2627, 4.493, 168.22;
    13, 2, 3, 2.2627, 1.8558, 28.7;
    14, 1, 2, 1.7145, 3.2, 85.33;
    15, 0, 1, 1.9132, 0.0, 0.0;
    16, 1, 2, 1.6, 3.2, 85.33;
    17, 2, 3, 1.4939, 4.5255, 170.67;
    18, 3, 4, 2.2627, 3.8852, 125.79;
    19, 4, 5, 1.9132, 2.3206, 44.88;
    20, 5, 6, 1.7145, 3.9984, 133.23;
    21, 6, 7, 1.7239, 3.2, 85.33;
    22, 6, 7, 1.8475, 3.2, 85.33;
    23, 5, 6, 1.8997, 3.2, 85.33;
    24, 4, 5, 2.2627, 3.5511, 105.08;
    25, 3, 4, 2.2627, 3.5353, 104.16;
    26, 2, 3, 1.9132, 3.2, 85.33;
    27, 1, 2, 1.4766, 3.2, 85.33;
    28, 0, 1, 2.2627, 4.4327, 163.74;
];

% Plot Thermal Dissipation per Channel
figure('Name', 'Qfoton Silicon Photonic DAC Control Voltages', 'Color', 'w');
bar(MZI_Control_Table(:, 1), MZI_Control_Table(:, 5), 'FaceColor', [0.02 0.71 0.83]);
xlabel('Mach-Zehnder Interferometer (MZI) Index');
ylabel('Phase Shifter DAC Voltage (V)');
title('Qfóton: Silicon Photonic Thermo-Optic Phase Shifter Control Voltages');
grid on;
disp('Qfóton MATLAB / Simulink Control Vector Loaded Successfully.');