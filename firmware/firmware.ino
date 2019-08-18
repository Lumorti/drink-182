#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

char inByte = ' ';
String recievedString = "";
int milliPer25 = 500;
int openAngle = 10;
int closedAngle = 20;

Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver(0x40);

void setup(){

  pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(9600);
  while (Serial.available() > 0){inByte = Serial.read();}
  //pwm.begin();
  //pwm.setPWMFreq(50);
  
}

void loop(){
  
  if (Serial.available() > 0){

    inByte = Serial.read();
    recievedString = recievedString + inByte;
    if (inByte == '\n'){
      processCommand(recievedString);
      recievedString = "";
    }
    
  }
  
}

void processCommand(String command){

  Serial.print(recievedString);

  int motor = -1;
  int amount = 0;
  String current = "";

  for (int i=1; i<recievedString.length()-2; i++){

    if (recievedString[i] == '='){

      motor = current.toInt();
      current = "";
      
    } else if (recievedString[i] == '+'){

      amount = current.toInt();
      current = "";

      Serial.print("motor = ");
      Serial.println(motor);
  
      Serial.print("amount = ");
      Serial.println(amount);

      setMotorAngle(motor, openAngle);
      delay(int((amount / 25.0) * milliPer25));
      setMotorAngle(motor, closedAngle);
      
    } else {

      current = current + recievedString[i];
      
    }

  }

}

void setMotorAngle(int motor, int angle){

  //pwm.setPin(motor, 1024)

}
