#include "motor.h"

int motorSpeed = 0;

int setMotorSpeed(int rpm) {
    motorSpeed = rpm;
    return motorSpeed;
}

int getMotorSpeed() {
    return motorSpeed;
}

int increaseSpeed(int step) {
    motorSpeed += step;
    return motorSpeed;
}
