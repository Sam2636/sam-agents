# Utils Module Documentation

## Summary
This document provides an overview of the functions defined in the `utils.cpp` source file. The functions are designed to perform various calculations related to thrust, battery drain, and efficiency.

## Functions

### `convertRPMToThrust`
- **Signature**: `float convertRPMToThrust(float rpm)`
- **Inputs**:
  - `rpm` (float): The revolutions per minute to be converted to thrust.
- **Outputs**:
  - Returns a float representing the thrust calculated from the given RPM.
- **Description**: Converts a given RPM value into thrust.

---

### `calculateBatteryDrain`
- **Signature**: `float calculateBatteryDrain(float current, float time)`
- **Inputs**:
  - `current` (float): The current in amperes.
  - `time` (float): The time in hours for which the current is drawn.
- **Outputs**:
  - Returns a float representing the battery drain calculated based on the current and time.
- **Description**: Calculates the battery drain based on the current and the duration of usage.

---

### `getEfficiency`
- **Signature**: `float getEfficiency(float thrust, float power)`
- **Inputs**:
  - `thrust` (float): The thrust value to evaluate efficiency.
  - `power` (float): The power input to evaluate efficiency.
- **Outputs**:
  - Returns a float representing the efficiency calculated from thrust and power.
- **Description**: Computes the efficiency based on thrust and power inputs.

## Globals
- **MISSING**: No global variables are defined in this module.

## Notes
- libclang failed: Could not find module 'libclang.dll' (or one of its dependencies). Try using the full path with constructor syntax. To provide a path to libclang use `Config.set_library_path()` or `Config.set_library_file()`. Falling back to regex.

## Source Reference
- **Source File**: `utils.cpp`
- **Workspace**: `workspaces\\b6bf6d9a7042`