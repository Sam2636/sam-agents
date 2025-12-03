#include "safety.h"

bool emergencyStopFlag = false;

void triggerEmergencyStop() {
    emergencyStopFlag = true;
}

void resetEmergencyStop() {
    emergencyStopFlag = false;
}

bool isEmergencyActive() {
    return emergencyStopFlag;
}
