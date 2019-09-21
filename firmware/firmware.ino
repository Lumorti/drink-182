#include <Wire.h>

const int MIN_PULSE_WIDTH = 500;
const int MAX_PULSE_WIDTH = 2000;
const int FREQUENCY = 50;

char inByte = ' ';
String recievedString = "";

void setup(){

  // Start comms with the pi
  Serial.begin(9600);

  // Clear the buffer 
  while (Serial.available() > 0){inByte = Serial.read();}

	// Set all the output pins for the optocoupler
	for (int i = 2; i < 10; i++){
		pinMode(i, OUTPUT);	
		digitalWrite(i, HIGH);
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

	Serial.print("com: ");
	Serial.println(command);

  // If the command doesn't start and end with '-' then return
  if (command.charAt(0) != endChar || command.charAt(command.length()-1) != endChar){
		Serial.println("err");
		return;
  }

  // String is something like "-1200o1=50+2=250+-"
  // (valve should open for 1200 milliseconds per 25 ml)
  // (liquid 1 for 50 ml and liquid 2 for 250 ml)
  for (int i=1; i<recievedString.length()-1; i++){

    if (recievedString.charAt(i) == '='){

      motor = current.toInt();
      current = "";
      
    } else if (recievedString.charAt(i) == '+'){

      amount = current.toInt();
      current = "";
			
			Serial.print("mot: ");
			Serial.println(motor);
			Serial.print("time: ");
			Serial.println(amount);
			Serial.flush();

			digitalWrite(motor+2, LOW);
			delay(amount);
			digitalWrite(motor+2, HIGH);
			delay(200);

		} else {

      current = current + recievedString[i];
      
    }

  }

}

