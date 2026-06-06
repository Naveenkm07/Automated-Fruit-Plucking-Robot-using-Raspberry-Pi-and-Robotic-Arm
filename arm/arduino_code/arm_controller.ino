/*
 * =============================================================
 * ARM CONTROLLER — Arduino UNO + PCA9685 Servo Driver
 * =============================================================
 * Receives commands from Raspberry Pi via USB Serial.
 * Controls 6 servo motors through PCA9685 (I2C).
 *
 * Wiring:
 *   Arduino A4 (SDA) → PCA9685 SDA
 *   Arduino A5 (SCL) → PCA9685 SCL
 *   Arduino 5V       → PCA9685 VCC (logic power)
 *   Arduino GND      → PCA9685 GND
 *   External 5V-6V   → PCA9685 V+ (servo power — NOT from Arduino!)
 *
 * Upload this to Arduino UNO using Arduino IDE.
 * 
 * Required Library:
 *   Adafruit PWM Servo Driver Library
 *   Install: Sketch → Include Library → Manage Libraries
 *   Search: "Adafruit PWM Servo Driver" → Install
 * =============================================================
 */

#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

// --- PCA9685 Setup ---
Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();

// --- Servo Channel Definitions ---
#define SERVO_BASE         0   // Base rotation (MG996R)
#define SERVO_SHOULDER     1   // Shoulder lift (MG996R)
#define SERVO_ELBOW        2   // Elbow extend (MG996R)
#define SERVO_WRIST        3   // Wrist rotate (SG90)
#define SERVO_GRIPPER      4   // Gripper open/close (SG90)
#define SERVO_GRIPPER_TILT 5   // Gripper tilt (SG90)

#define NUM_SERVOS 6

// --- PWM Pulse Limits ---
// PCA9685 uses 12-bit resolution (0-4095)
// Standard servos: ~150 (0°) to ~600 (180°)
// CALIBRATE THESE VALUES for your specific servos!
#define SERVO_MIN  150   // Pulse length for 0 degrees
#define SERVO_MAX  600   // Pulse length for 180 degrees

// --- MG996R specific limits (slightly different from SG90) ---
#define MG996R_MIN 150
#define MG996R_MAX 600
#define SG90_MIN   150
#define SG90_MAX   550

// --- Current servo positions (in degrees) ---
int currentAngles[NUM_SERVOS] = {90, 90, 90, 90, 30, 90};

// --- Home position (safe resting position) ---
const int homeAngles[NUM_SERVOS] = {90, 90, 90, 90, 30, 90};

// --- Servo angle limits (min, max) for safety ---
const int servoMinAngle[NUM_SERVOS] = {0, 30, 30, 0, 30, 45};
const int servoMaxAngle[NUM_SERVOS] = {180, 150, 150, 180, 120, 135};

// --- Movement speed (delay between degrees in ms) ---
int moveDelay = 15;  // Lower = faster, Higher = smoother

// --- Serial communication ---
String inputBuffer = "";
bool commandReady = false;


// =============================================================
// SETUP
// =============================================================
void setup() {
    Serial.begin(115200);
    Serial.setTimeout(100);
    
    // Initialize PCA9685
    pwm.begin();
    pwm.setPWMFreq(50);  // 50Hz for standard servos
    
    delay(500);  // Let servos settle
    
    // Move all servos to home position
    goHome();
    
    Serial.println("READY:ARM_CONTROLLER");
    Serial.println("OK:INIT");
}


// =============================================================
// MAIN LOOP
// =============================================================
void loop() {
    // Read serial commands
    while (Serial.available() > 0) {
        char c = Serial.read();
        if (c == '\n' || c == '\r') {
            if (inputBuffer.length() > 0) {
                commandReady = true;
            }
        } else {
            inputBuffer += c;
        }
    }
    
    // Process command when complete
    if (commandReady) {
        inputBuffer.trim();
        processCommand(inputBuffer);
        inputBuffer = "";
        commandReady = false;
    }
}


// =============================================================
// COMMAND PROCESSOR
// =============================================================
void processCommand(String cmd) {
    cmd.toUpperCase();
    
    // --- HOME: Move all servos to resting position ---
    if (cmd == "HOME") {
        goHome();
        Serial.println("OK:HOME");
    }
    // --- PICK: Execute full pick sequence ---
    else if (cmd == "PICK") {
        pickSequence();
        Serial.println("OK:PICK");
    }
    // --- OPEN: Open gripper ---
    else if (cmd == "OPEN") {
        smoothMove(SERVO_GRIPPER, 30);  // Open position
        Serial.println("OK:OPEN");
    }
    // --- CLOSE: Close gripper ---
    else if (cmd == "CLOSE") {
        smoothMove(SERVO_GRIPPER, 110);  // Closed position
        Serial.println("OK:CLOSE");
    }
    // --- MOVE:channel,angle — Move specific servo ---
    else if (cmd.startsWith("MOVE:")) {
        String params = cmd.substring(5);
        int commaIndex = params.indexOf(',');
        if (commaIndex > 0) {
            int channel = params.substring(0, commaIndex).toInt();
            int angle = params.substring(commaIndex + 1).toInt();
            
            if (channel >= 0 && channel < NUM_SERVOS) {
                // Clamp angle to safe limits
                angle = constrain(angle, servoMinAngle[channel], servoMaxAngle[channel]);
                smoothMove(channel, angle);
                Serial.println("OK:MOVE:" + String(channel) + "," + String(angle));
            } else {
                Serial.println("ERR:INVALID_CHANNEL");
            }
        } else {
            Serial.println("ERR:BAD_FORMAT");
        }
    }
    // --- REACH:x,y — Move arm to approximate position ---
    else if (cmd.startsWith("REACH:")) {
        String params = cmd.substring(6);
        int commaIndex = params.indexOf(',');
        if (commaIndex > 0) {
            int x = params.substring(0, commaIndex).toInt();
            int y = params.substring(commaIndex + 1).toInt();
            reachPosition(x, y);
            Serial.println("OK:REACH:" + String(x) + "," + String(y));
        } else {
            Serial.println("ERR:BAD_FORMAT");
        }
    }
    // --- STATUS: Report current positions ---
    else if (cmd == "STATUS") {
        String status = "STATUS:";
        for (int i = 0; i < NUM_SERVOS; i++) {
            status += String(currentAngles[i]);
            if (i < NUM_SERVOS - 1) status += ",";
        }
        Serial.println(status);
    }
    // --- SPEED:value — Set movement speed ---
    else if (cmd.startsWith("SPEED:")) {
        moveDelay = cmd.substring(6).toInt();
        moveDelay = constrain(moveDelay, 1, 50);
        Serial.println("OK:SPEED:" + String(moveDelay));
    }
    // --- PING: Connection test ---
    else if (cmd == "PING") {
        Serial.println("PONG");
    }
    // --- Unknown command ---
    else {
        Serial.println("ERR:UNKNOWN_CMD:" + cmd);
    }
}


// =============================================================
// SMOOTH SERVO MOVEMENT
// =============================================================
void smoothMove(int channel, int targetAngle) {
    /*
     * Moves a servo smoothly from current position to target.
     * Prevents jerky movements that could damage the arm
     * or drop a picked fruit.
     */
    targetAngle = constrain(targetAngle, servoMinAngle[channel], servoMaxAngle[channel]);
    
    int current = currentAngles[channel];
    int step = (targetAngle > current) ? 1 : -1;
    
    while (current != targetAngle) {
        current += step;
        setServoAngle(channel, current);
        delay(moveDelay);
    }
    
    currentAngles[channel] = targetAngle;
}


// =============================================================
// SET SERVO ANGLE (Low-level)
// =============================================================
void setServoAngle(int channel, int angle) {
    /*
     * Convert angle (0-180) to PCA9685 pulse width.
     * Different servo types have slightly different ranges.
     */
    int pulseMin, pulseMax;
    
    // Use different limits for MG996R vs SG90
    if (channel <= SERVO_ELBOW) {
        // MG996R servos (high torque)
        pulseMin = MG996R_MIN;
        pulseMax = MG996R_MAX;
    } else {
        // SG90 servos (micro)
        pulseMin = SG90_MIN;
        pulseMax = SG90_MAX;
    }
    
    int pulse = map(angle, 0, 180, pulseMin, pulseMax);
    pwm.setPWM(channel, 0, pulse);
}


// =============================================================
// GO HOME — Safe resting position
// =============================================================
void goHome() {
    /*
     * Move all servos to their home/resting positions.
     * Moves shoulder and elbow first (to avoid collisions),
     * then base, wrist, and gripper.
     */
    
    // First, lift the arm up (shoulder + elbow)
    smoothMove(SERVO_SHOULDER, homeAngles[SERVO_SHOULDER]);
    smoothMove(SERVO_ELBOW, homeAngles[SERVO_ELBOW]);
    delay(200);
    
    // Then rotate base
    smoothMove(SERVO_BASE, homeAngles[SERVO_BASE]);
    delay(200);
    
    // Set wrist and gripper
    smoothMove(SERVO_WRIST, homeAngles[SERVO_WRIST]);
    smoothMove(SERVO_GRIPPER_TILT, homeAngles[SERVO_GRIPPER_TILT]);
    smoothMove(SERVO_GRIPPER, homeAngles[SERVO_GRIPPER]);  // Open gripper
}


// =============================================================
// PICK SEQUENCE — Full fruit picking operation
// =============================================================
void pickSequence() {
    /*
     * Automated sequence to pick a fruit:
     * 1. Open gripper
     * 2. Extend arm forward (shoulder down, elbow out)
     * 3. Close gripper (grab fruit)
     * 4. Lift arm back up
     * 5. Rotate to collection basket
     * 6. Open gripper (release fruit)
     * 7. Return to home position
     *
     * IMPORTANT: Calibrate angles based on your actual arm geometry!
     */
    
    // Step 1: Open gripper
    smoothMove(SERVO_GRIPPER, 30);
    delay(300);
    
    // Step 2: Extend arm forward
    smoothMove(SERVO_SHOULDER, 60);   // Lower shoulder
    delay(200);
    smoothMove(SERVO_ELBOW, 120);     // Extend elbow
    delay(200);
    smoothMove(SERVO_GRIPPER_TILT, 70);  // Tilt gripper for grabbing
    delay(500);
    
    // Step 3: Close gripper (grab fruit)
    smoothMove(SERVO_GRIPPER, 100);   // Close firmly but gently
    delay(500);
    
    // Step 4: Lift arm with fruit
    smoothMove(SERVO_ELBOW, 60);      // Retract elbow
    delay(200);
    smoothMove(SERVO_SHOULDER, 120);  // Lift shoulder up
    delay(300);
    
    // Step 5: Rotate to collection basket side
    // Adjust base angle based on where your basket is!
    smoothMove(SERVO_BASE, 150);      // Rotate toward basket
    delay(300);
    
    // Step 6: Lower arm slightly and release
    smoothMove(SERVO_SHOULDER, 80);
    delay(200);
    smoothMove(SERVO_GRIPPER, 30);    // Open gripper — drop fruit
    delay(500);
    
    // Step 7: Return to home
    goHome();
}


// =============================================================
// REACH POSITION — Move to approximate X,Y coordinates
// =============================================================
void reachPosition(int x, int y) {
    /*
     * Move the arm to reach a position defined by:
     *   x = horizontal offset from center (-100 to +100)
     *   y = vertical position (0 = ground level, 100 = max height)
     *
     * This is a simplified mapping. For precise control,
     * you'd need inverse kinematics based on arm dimensions.
     */
    
    // Map x to base rotation angle
    // x: -100 (full left) → 180°, 0 (center) → 90°, +100 (full right) → 0°
    int baseAngle = map(x, -100, 100, 180, 0);
    baseAngle = constrain(baseAngle, 0, 180);
    
    // Map y to shoulder angle
    // y: 0 (reach down) → 45°, 100 (reach up) → 135°
    int shoulderAngle = map(y, 0, 100, 45, 135);
    shoulderAngle = constrain(shoulderAngle, 30, 150);
    
    // Calculate elbow based on extension needed
    int elbowAngle = map(y, 0, 100, 130, 50);
    elbowAngle = constrain(elbowAngle, 30, 150);
    
    // Execute movement
    smoothMove(SERVO_BASE, baseAngle);
    smoothMove(SERVO_SHOULDER, shoulderAngle);
    smoothMove(SERVO_ELBOW, elbowAngle);
}
