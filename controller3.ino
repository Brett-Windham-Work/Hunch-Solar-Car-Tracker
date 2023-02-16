#include <Servo.h> 
Servo servo_yaw;  // create servo object to control a servo
int yaw = 90;
int y_avg_int = 0;

const byte numChars = 32;
char receivedChars[numChars];
boolean newData = false;
boolean move_servo = false;

void setup() {
    Serial.begin(9600);
    servo_yaw.writeMicroseconds(1500); //set initial servo position if desired
    servo_yaw.attach(9);  //the pin for the servo control
    servo_yaw.write(90);
    Serial.println("<Arduino is ready>");
}

void loop() {
    recvWithStartEndMarkers();
    showNewData();
    move_yaw_servo();
}

void recvWithStartEndMarkers() {
    static boolean recvInProgress = false;
    static byte ndx = 0;
    char startMarker = '<';
    char endMarker = '>';
    char rc;
 
    while (Serial.available() > 0 && newData == false) {
        rc = Serial.read();

        if (recvInProgress == true) {
            if (rc != endMarker) {
                receivedChars[ndx] = rc;
                ndx++;
              
                if (ndx >= numChars) {
                    ndx = numChars - 1;
                }
            }
            else {
                receivedChars[ndx] = '\0'; // terminate the string
                recvInProgress = false;
                ndx = 0;
                newData = true;
            }
        }

        else if (rc == startMarker) {
            recvInProgress = true;
        }
    }
}

void showNewData() {
    if (newData == true) {
        Serial.print("avg y: ");
        
        String y_avg_string = String(receivedChars);
        int y_avg_int = (y_avg_string.toInt());
        yaw = round( atan2 (500,  (y_avg_int-500)) * 180/3.14159265 ); // radians to degrees and rounding
        Serial.println(y_avg_int);
        
        move_servo = true;
        newData = false;
    }
}

void move_yaw_servo() {
  if (move_servo == true) {
          Serial.print("yaw: ");
          servo_yaw.write(yaw);
          Serial.println(yaw); 
        }        
  move_servo = false;
  }
