#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

const int MIN_PULSE_WIDTH = 500;
const int MAX_PULSE_WIDTH = 2000;
const int FREQUENCY = 50;

char inByte = ' ';
String recievedString = "";
int milliPer25 = 500;
int openAngle = 40;
int closedAngle = 150;

// For controlling the motors
Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver(0x41);

void setup(){

  // Start comms with the pi
  Serial.begin(9600);

  // Clear the buffer 
  while (Serial.available() > 0){inByte = Serial.read();}

  // Start the motor
  pwm.begin();
  pwm.setPWMFreq(FREQUENCY);

	for (int i=0;i<8;i++){
		setMotorAngle(i, closedAngle);
	}
  
}

void loop(){
  
  // Keep reading, process command on newline
  if (Serial.available() > 0){

    inByte = Serial.read();
    
    if (inByte == '\n'){
      processCommand(recievedString);
      recievedString = "";
    } else {
      recievedString = recievedString + inByte;
    }
    
  }
  
}

void processCommand(String command){

  int motor = -1;
  int amount = 0;
  String current = "";
  char endChar = '-';

  Serial.print("recieved command: ");
  Serial.println(command);

  // If the command doesn't start and end with '-' then return
  if (command.charAt(0) != endChar || command.charAt(command.length()-1) != endChar){
	  Serial.println("not a valid command");
	  return;
  }

  // String is something like "-90c120o1=50+2=250-"
  // (valve is closed at 90 degrees and open at 120)
  // (liquid 1 for 50 ml and liquid 2 for 250 ml)
  for (int i=1; i<recievedString.length()-1; i++){

    if (recievedString.charAt(i) == '='){

      motor = current.toInt();
      current = "";
      
    } else if (recievedString.charAt(i) == '+'){

      amount = current.toInt();
      current = "";

      setMotorAngle(motor, openAngle);
      delay(int((amount / 25.0) * milliPer25));
      setMotorAngle(motor, closedAngle);

	} else if (recievedString.charAt(i) == 'o'){
      
	  openAngle = current.toInt();
	  Serial.print("open angle is now: ");
	  Serial.println(openAngle);
	  current = "";

	} else if (recievedString.charAt(i) == 'c'){
      
	  closedAngle = current.toInt();
	  Serial.print("closed angle is now: ");
	  Serial.println(closedAngle);
	  current = "";

    } else {

      current = current + recievedString[i];
      
    }

  }

}

// Set the motor to a certain angle
void setMotorAngle(int motor, int angle){

  // Function to convert angle to num of cycles on
  int pulse_wide, analog_value;
  pulse_wide = map(angle, 0, 180, int(MIN_PULSE_WIDTH), int(MAX_PULSE_WIDTH));
  analog_value = int(float(pulse_wide) / 1000000 * FREQUENCY * 4096);

  Serial.print("setting angle of motor ");
  Serial.print(motor);
  Serial.print(" to ");
  Serial.print(angle);
  Serial.print(" (");
  Serial.print(analog_value);
  Serial.println(")");

  // Set the motor to the angle
  pwm.setPin(motor, analog_value);

}
