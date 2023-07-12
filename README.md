# HMC5883L_Raspberry_Pi_Python_library
HMC5883L code for Raspberry Pi.

# Overview
This is a library for the magnetometer HMC5883L. This does not work a varied form of it, the QMC5883L.

# Configuration and settings

Startup loads the default starting settings, as recommend by the manual on the HMC5883L.

- Samples per measurement: Takes multiple samples and averages for the result.
- Measurement Frequency: How often a measurement occurs.
- Measurement bias: Modifies bias conditions, useful if operating around electromagnets(Eg, Motors/Servos)
- GAIN: Allows for calibration of bias.
