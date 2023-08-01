# HMC5883L_Raspberry_Pi_Python_library
This repository provides a Python library and code examples to interface with the HMC5883L magnetometer sensor on a Raspberry Pi. The HMC5883L is a three-axis magnetometer that measures magnetic fields in the X, Y, and Z directions. 
It is capable of providing accurate and reliable magnetic field data, making it ideal for various applications such as navigation, orientation detection, and more.

# Requirements
- Raspberry Pi (tested on Raspberry Pi 3 and above)
- HMC5883L Magnetometer sensor
- Python 3.x
- smbus library (already included in most Raspbian distributions)

# Configuration and settings

Startup loads the default starting settings, as recommend by the manual on the HMC5883L.

- Samples per measurement: Takes multiple samples and averages for the result.
- Measurement Frequency: How often a measurement occurs.
- Measurement bias: Modifies bias conditions, useful if operating around electromagnets(Eg, Motors/Servos)
- GAIN: Allows for calibration of bias.
 
# Example

Here's a simple example to get started:

>
> from hmc5883l import HMC5883L
> 
> Create an instance of the HMC5883L class
> 
> sensor = HMC5883L()
>
> try:
>     while True:
>         # Get the magnetic field data
>         x, y, z = sensor.get_magnetic_data()
>         print(f"Magnetic Field (X, Y, Z): ({x}, {y}, {z}) uT")
> except KeyboardInterrupt:
>     print("Measurement stopped by the user.")

# Modify the settings:
The following methods are available:
- set_continuous_config(samples_per_measurement, measurement_frequency, measurement_bias, gain_factor): Sets the continuous measurement configuration. Pass None for any setting you want to keep unchanged.
- set_continuous_mode(): Puts the sensor in continuous measurement mode.
- set_single_mode(): Puts the sensor in single measurement mode.
- set_off_mode(): Puts the sensor in off mode (low power mode).