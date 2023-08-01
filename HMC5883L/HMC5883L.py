import smbus
from enum import Enum

bus = smbus.SMBus(1)

# Default I2C address. Modify as needed.
I2C_ADDRESS = 0x1e


# Configuration and ID registers
class Register(Enum):
    CONTROL_1 = 0x00
    CONTROL_2 = 0x01
    MODE = 0x02
    ID_1 = 0x0A
    ID_2 = 0x0B
    ID_3 = 0x0C
    ID_4 = 0x0D

# Output registers
class OutputRegister(Enum):
    X_MSB = 0x03
    X_LSB = 0x04
    Y_MSB = 0x05
    Y_LSB = 0x06
    Z_MSB = 0x07
    Z_LSB = 0x08

# Configuration flags
class ConfigFlags(Enum):
    SAMPLES_PER_MEASUREMENT_1 = 0b00000000  # Samples per measurement = 1
    SAMPLES_PER_MEASUREMENT_2 = 0b00100000  # Samples per measurement = 2
    SAMPLES_PER_MEASUREMENT_4 = 0b01000000  # Samples per measurement = 4
    SAMPLES_PER_MEASUREMENT_8 = 0b01100000  # Samples per measurement = 8
    MEASUREMENT_FREQ_0_75 = 0b00000000  # Output Data Rate = 0.75Hz
    MEASUREMENT_FREQ_1_5 = 0b00000100  # Output Data Rate = 1.5Hz
    MEASUREMENT_FREQ_3 = 0b00001000  # Output Data Rate = 3Hz
    MEASUREMENT_FREQ_7_5 = 0b00001100  # Output Data Rate = 7.5Hz
    MEASUREMENT_FREQ_15 = 0b00010000  # Output Data Rate = 15Hz
    MEASUREMENT_FREQ_30 = 0b00010100  # Output Data Rate = 30Hz
    MEASUREMENT_FREQ_75 = 0b00011000  # Output Data Rate = 75Hz
    MEASUREMENT_NORM = 0b00000000  # Normal Measurement Configuration
    MEASUREMENT_POSITIVE_BIAS = 0b00000001  # Positive bias configuration for X, Y, and Z-axes
    MEASUREMENT_NEGATIVE_BIAS = 0b00000010  # Negative bias configuration for X, Y, and Z-axes
    GAIN_0_88 = 0b00000000  # Gain = +/- 0.88
    GAIN_1_3 = 0b00100000  # Gain = +/- 1.3
    GAIN_1_9 = 0b01000000  # Gain = +/- 1.9
    GAIN_2_5 = 0b01100000  # Gain = +/- 2.5
    GAIN_4_0 = 0b10000000  # Gain = +/- 4.0
    GAIN_4_7 = 0b10100000  # Gain = +/- 4.7
    GAIN_5_6 = 0b11000000  # Gain = +/- 5.6
    GAIN_8_1 = 0b11100000  # Gain = +/- 8.1
    CONTROL_CONTINUOUS = 0b00000000  # Continuous
    CONTROL_SINGLE = 0b00000001  # Single
    CONTROL_OFF = 0b00000010  # Off


class HMC5883L:
    def __init__(self,
                 address=I2C_ADDRESS,
                 samples_per_measurement=ConfigFlags.SAMPLES_PER_MEASUREMENT_8,
                 measurement_frequency=ConfigFlags.MEASUREMENT_FREQ_0_75,
                 measurement_bias=ConfigFlags.MEASUREMENT_NORM,
                 gain_factor=ConfigFlags.GAIN_0_88,
                 i2c_bus=bus):
        self.address = address
        self.bus = i2c_bus
        self.check_chip_id()

        # The startup configuration for resuming startup calibration after modifying results
        self.startup_configuration = (
            samples_per_measurement,
            measurement_frequency,
            measurement_bias,
            gain_factor
        )
        self.current_configuration = self.startup_configuration
        self.set_continuous_config(*self.current_configuration)
        self.set_continuous_mode()

    def __del__(self):
        self.set_off_mode()

    def get_magnetic_raw_data(self):
        mag_xyz = self.bus.read_i2c_block_data(self.address, OutputRegister.X_MSB, 6)
        return mag_xyz

    def get_magnetic_data(self):
        data = self.get_magnetic_raw_data()
        x_mag = data[0] * 256 + data[1]
        if x_mag > 32767:
            x_mag -= 65536

        y_mag = data[2] * 256 + data[3]
        if y_mag > 32767:
            y_mag -= 65536

        z_mag = data[4] * 256 + data[5]
        if z_mag > 32767:
            z_mag -= 65536
        return x_mag, y_mag, z_mag

    def set_startup_configuration(self):
        self.set_continuous_config(*self.startup_configuration)

    def set_continuous_config(self,
                              samples_per_measurement=None,
                              measurement_frequency=None,
                              measurement_bias=None,
                              gain_factor=None):
        samples_per_measurement = (
            self.current_configuration[0]
            if samples_per_measurement is None
            else samples_per_measurement
        )
        measurement_frequency = (
            self.current_configuration[1]
            if measurement_frequency is None
            else measurement_frequency
        )
        measurement_bias = (
            self.current_configuration[2]
            if measurement_bias is None
            else measurement_bias
        )
        gain_factor = (
            self.current_configuration[3]
            if gain_factor is None
            else gain_factor
        )
        self.current_configuration = [
            samples_per_measurement,
            measurement_frequency,
            measurement_bias,
            gain_factor
        ]
        control1_bool = (
            samples_per_measurement
            | measurement_frequency
            | measurement_bias
        )
        bus.write_byte_data(self.address, Register.CONTROL_1, control1_bool)
        bus.write_byte_data(self.address, Register.CONTROL_2, gain_factor)

    def set_continuous_mode(self):
        bus.write_byte_data(self.address, Register.MODE, ConfigFlags.CONTROL_CONTINUOUS)

    def set_single_mode(self):
        bus.write_byte_data(self.address, Register.MODE, ConfigFlags.CONTROL_SINGLE)

    def set_off_mode(self):
        bus.write_byte_data(self.address, Register.MODE, ConfigFlags.CONTROL_OFF)

    def check_chip_id(self):
        id_reg_ascii = ""
        id_reg = self.bus.read_i2c_block_data(self.address, Register.ID_1, 3)
        for i in id_reg:
            id_reg_ascii += chr(i)

        if id_reg_ascii != "H43":
            id_reg_alt = self.bus.read_byte_data(self.address, Register.ID_4)
            if id_reg_alt == 0xff:
                print("Chip ID {} instead of H43. Chip is a V2/V3 variant of "
                      "alternative magnetometer QMC5883L, not supported by the library.".format(id_reg_alt))
            else:
                print("Returned ID {} in ID registers of HMC5883L. Chip not registering correctly.".format(id_reg_ascii))
        else:
            print("Returned chip ID identifies as HMC5883L")
