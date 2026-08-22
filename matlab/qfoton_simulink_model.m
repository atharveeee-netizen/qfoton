% Qfóton - MATLAB / Simulink Photonic Quantum Co-Simulation Script
% Auto-generated for Silicon Photonic Thermal Phase Shifter DACs
clear; clc;
V_pi = 3.2; % Pi-voltage for thermo-optic phase shifters (V)
R_heater = 120.0; % Heater resistance (Ohms)
DAC_bits = 16; % Digital-to-Analog Converter resolution

% MZI Channel Control Table [MZI_ID, Mode_A, Mode_B, V_theta (V), V_phi (V), Power (mW)]
MZI_Control_Table = [
    1, 0, 1, 1.2328, 3.0291, 76.46;
    2, 3, 4, 1.1097, 3.9442, 129.64;
    3, 4, 5, 2.0479, 0.9128, 6.94;
    4, 2, 3, 1.725, 3.148, 82.58;
    5, 1, 2, 1.714, 4.3151, 155.17;
    6, 0, 1, 1.7742, 3.7638, 118.05;
    7, 1, 2, 2.0141, 2.9788, 73.94;
    8, 2, 3, 1.3039, 3.8722, 124.95;
    9, 3, 4, 1.8526, 1.4522, 17.57;
    10, 4, 5, 1.8732, 2.4185, 48.74;
    11, 4, 5, 1.3633, 2.6202, 57.21;
    12, 3, 4, 2.0971, 3.9861, 132.41;
    13, 2, 3, 1.9705, 3.0277, 76.39;
    14, 1, 2, 2.2251, 3.7262, 115.7;
    15, 0, 1, 1.6665, 4.0078, 133.85;
];

% Plot Thermal Dissipation per Channel
figure('Name', 'Qfoton Silicon Photonic DAC Control Voltages', 'Color', 'w');
bar(MZI_Control_Table(:, 1), MZI_Control_Table(:, 5), 'FaceColor', [0.02 0.71 0.83]);
xlabel('Mach-Zehnder Interferometer (MZI) Index');
ylabel('Phase Shifter DAC Voltage (V)');
title('Qfóton: Silicon Photonic Thermo-Optic Phase Shifter Control Voltages');
grid on;
disp('Qfóton MATLAB / Simulink Control Vector Loaded Successfully.');