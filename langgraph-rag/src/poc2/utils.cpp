#include "utils.h"

float convertRPMToThrust(float rpm) {
    return rpm * 0.75f;
}

float calculateBatteryDrain(float current, float time) {
    return current * time;
}

float getEfficiency(float thrust, float power) {
    if (power == 0)
        return 0.0f;
    return thrust / power;
}
