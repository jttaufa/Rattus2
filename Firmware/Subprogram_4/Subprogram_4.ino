/*
 * Subprogram_2
 *
 * Jonathon Taufatofua
 * The University of Queensland
 *
 * Motor Command Processing
 * This module contains command processing for the command array
 * for motor control, including PID control for accurate motor
 * output and servo control for rearing mechanism.
 */
#include <Servo.h>


typedef struct {
  char cmdType;
  uint8_t v_A;
  uint8_t v_B;
  uint8_t cmdVal;
} 
Cmd; //Command structure

const Cmd EmptyCmd = {};
Cmd cmdArr[72] = {};    //Create command array
int i_cmd = 0;          //Cmd array active index


Servo myservo;
int pos = 0;  //Variable to store servo position
boolean servoUP = false;
// IO Pins
const int servoPin = 10;

const int PWMB = 3;
const int BIN2 = 4;
const int BIN1 = 5;
const int NSTBY = 6;
const int AIN1 = 7;
const int AIN2 = 8;
const int PWMA = 11;

const int IRA = A1;
const int IRB = A0;

//const int ENCA1 = ;
//const int ENCA2 = ;
//const int ENCB1 = ;
//const int ENCB2 = ;

boolean dirEN;

uint8_t speedA;
uint8_t speedB;
int mode, modeRx;
uint16_t distIRA, distIRB; //Sensor distances in cm

int wfDist = 15; //Distance to keep from wall in cm
char currWFMode = 'R';
char prevWFMode = 'L';
char rxChar;

void setup() { 
  myservo.attach(servoPin);  // attaches the servo on pin 9 to the servo object 
  myservo.write(150);
  //setPlatform(0);

  Serial1.begin(115200);
  Serial.begin(115200);
  while(!Serial);
  while(!Serial1);
  
  //Setup Pins
  pinMode(NSTBY, OUTPUT);
  pinMode(PWMA, OUTPUT);
  pinMode(PWMB, OUTPUT);
  pinMode(AIN1, OUTPUT);
  pinMode(AIN2, OUTPUT);
  pinMode(BIN1, OUTPUT);
  pinMode(BIN2, OUTPUT);
  
  pinMode(servoPin, OUTPUT);
  //Setup motors
  dirEN = true;
  setDir('F'); //Set motor directions forward
  enableMotors(true); //Enable motors

  //Set initial speeds  
  speedA = 0;
  speedB = 0;
  mode = 0;
} 
 
void loop() { 
  //if (Serial1.available()){
  //  rxChar = Serial1.read();
  if (Serial1.available()){
    rxChar = Serial1.read();
    Serial.write("RECEIVED\n\r");
    
    // ----------- Special Commands ----------- //
    if (rxChar == 'm'){ //mode change
      if (Serial1.available()){
        modeRx = Serial1.read() - '0';
        if (modeRx <= 3 && modeRx >=1){
          mode = modeRx;
        } else {
          //TRANSMIT ERROR
        }
      } else {
        mode += 1;
        if (mode > 3) mode = 1; //Wrap counter
        Serial1.write("Mode "); //######CHANGE TO SERIAL1
        Serial1.write(mode+'0');
        Serial1.write("\n\r");
        //continue;
        return; //'continue' for main loop (?)
      }
    } else if (rxChar == 'n'){
      Serial1.write("TILTING\n\r");
     
      tiltPlatform();
    }
  }
  
  // ----------- Operation Modes ----------- //
  if (mode == 1) {       // 1. Command Stack Control
  
    // PUT STUFF HERE!!!
  
  } else if (mode == 2){ // 2. Direct Control (Continuous)      
    
    if (rxChar == 'w'){   //Forward
      setDir('F');
    } else if (rxChar == 'a'){ //Left
      setDir('L');
    } else if (rxChar == 's'){ //Reverse
      setDir('B');
    } else if (rxChar == 'd'){ //Right
      setDir('R');
    } else if (rxChar == 'q'){ //Stop
      stopMotors(); 
    } else if (rxChar == '!'){ //Brake
      brake(true);
    } else if (rxChar == 'r'){ //Release brake
      brake(false);
    } else if (rxChar == '0'){
      speedA = 0;
      speedB = 0;
    } else if (rxChar == '1'){
      speedA = 25;
      speedB = 25;
    } else if (rxChar == '2'){
      speedA = 35;
      speedB = 35;
    } else if (rxChar == '3'){
      speedA = 50;
      speedB = 50;
    } else if (rxChar == '4'){
      speedA = 90;
      speedB = 90;
    } else if (rxChar == '5'){
      speedA = 130;
      speedB = 130;
    } else if (rxChar == '6'){
      speedA = 180;
      speedB = 180;
    } else if (rxChar == '7'){
      speedA = 255;
      speedB = 255;
    } 
    analogWrite(PWMA, speedA);
    analogWrite(PWMB, speedB);
    //driveMotors(speedA,speedB); //Conflict occurs cos speed A and B are directioned
    delay(1);
    
    //Raise/lower servo
    if (rxChar == 0x20){ //Spacebar - Toggle servo position (30,90)
      servoUP = !servoUP;
      if (servoUP){
        stopMotors();        //Stop current running command
        enableMotors(false); //Disable motors
        Serial1.write("SERVO UP\n\r"); //####CHANGE TO SERIAL1
        for(pos = 145; pos >= 115; pos -= 1){ 
          myservo.write(pos);               
          delay(15);                        
        }
      } else {
        Serial1.write("SERVO DOWN\n\r"); //######CHANGE TO SERIAL1
        for(pos = 115; pos <= 145; pos += 1){ 
          myservo.write(pos);              
          delay(15);                      
        }
        stopMotors();
        enableMotors(true); //Re-enable motors
      }
    }
    rxChar = 0x00; //Reset rxChar
    delay(1);
  } else if (mode == 3){ //3. Wall follower
    speedA = 50;
    speedB = 50;
    currWFMode = rxChar;
    //if (prevWFMode != rxChar){
    //  currWFMode = rxChar;
    //}
    
    if (currWFMode == 'L' || currWFMode == 'R' || currWFMode == 'B'){
      followWall(rxChar, wfDist);
      prevWFMode = currWFMode;
      delay(50);
    } else if (rxChar > 5 && rxChar < 40) { //Set distance
      //wfDist = (int) rxChar;
      wfDist = 15;
      Serial1.write("Set Distance: ");
      Serial1.write(wfDist);
      Serial1.write("\n\r");
    } else if (rxChar != 0x00){ //Non-null char received
      Serial1.write("Invalid Value"); //#####CHANGE TO SERIAL1 and write ERROR
      // ###### ERROR ####
    }
    rxChar = 0x00; //Clear variable
  }
} 





//void readEncoders(void){
//  valENC1 = analogRead(ENC1
//  
//}


void setDir(char dir){  
  if (dirEN){
    Serial1.write("Direction "); //####CHANGE TO SERIAL1
    Serial1.write(dir);
    Serial1.write(0x0D); //CR
    Serial1.write(0x0A); //NL            
    if (dir == 'F'){
      setMotDir('A',1);
      setMotDir('B',1);
      /*digitalWrite(AIN1, HIGH);
      digitalWrite(AIN2, LOW);
      digitalWrite(BIN1, HIGH);
      digitalWrite(BIN2, LOW);
      */
    } else if (dir == 'B'){
      setMotDir('A',-1);
      setMotDir('B',-1);      
      /*digitalWrite(AIN1, LOW);
      digitalWrite(AIN2, HIGH);
      digitalWrite(BIN1, LOW);
      digitalWrite(BIN2, HIGH);
      */
    } else if (dir == 'L'){
      setMotDir('A',-1);
      setMotDir('B',1);      
      /*digitalWrite(AIN1, LOW);
      digitalWrite(AIN2, HIGH);
      digitalWrite(BIN1, HIGH);
      digitalWrite(BIN2, LOW);
      */
    } else if (dir == 'R'){
      setMotDir('A',1);
      setMotDir('B',-1);      
      /*digitalWrite(AIN1, HIGH);
      digitalWrite(AIN2, LOW);
      digitalWrite(BIN1, LOW);
      digitalWrite(BIN2, HIGH);
      */
    } else {
      Serial1.write("Errorrrr\n\r");
    }
  }  else {
    Serial1.write("Brake Engaged\n\r");
  } 
}




void enableMotors(boolean enable){
  if (enable){
    digitalWrite(NSTBY, HIGH); //Enable motors
  } else {
    digitalWrite(NSTBY, LOW);  //Disable motors 
  }
}

void brake(boolean enable){
  if (enable){ //Brake
    Serial1.write("Brake Engaged\n\r"); //####### CHANGE TO SERIAL1
    digitalWrite(AIN1, HIGH);
    digitalWrite(AIN2, HIGH);
    digitalWrite(BIN1, HIGH);
    digitalWrite(BIN2, HIGH);
    dirEN = false;
  } else {     //Switch to free-spinning
    Serial1.write("Brake Released\n\r"); //####### CHANGE TO SERIAL1
    stopMotors();
    dirEN = true;
  }
}

void stopMotors(){ //Free-running stop (short-brake).
    Serial1.write("Stopping\n\r"); //#########CHANGE TO SERIAL1
    digitalWrite(AIN1, LOW);
    digitalWrite(AIN2, LOW);
    digitalWrite(BIN1, LOW);
    digitalWrite(BIN2, LOW);
    //Set global speed to 0
    speedA = 0;
    speedB = 0;
    //Set speed to zero
    driveMotors(0,0);
}




void driveMotors(int8_t v_A, int8_t v_B){
  setMotDir('A',v_A);
  setMotDir('B',v_B);
  //To do: Perform a conversion for v_A and v_B to PWM values
  uint8_t pwmA_new = uint8_t(abs(v_A));
  uint8_t pwmB_new = uint8_t(abs(v_B));
  
  //Speed is limited to between 127 forward, 128 backward
  analogWrite(PWMA, pwmA_new);
  analogWrite(PWMB, pwmB_new);
}


void setMotDir(char motor, int8_t vMot){
  int IN1, IN2;
  //Select motor input pins
  switch(motor){
    case 'A':
      IN1 = AIN1;
      IN2 = AIN2;
      break;
    case 'B':
      IN1 = BIN1;
      IN2 = BIN2;
      break;
    default:
      //############Transmit Error
      break;
  }
  //Set motor pin directions
  if (dirEN){
    if (vMot >= 0){
      digitalWrite(IN1, HIGH);
      digitalWrite(IN2, LOW);
    } else {
      digitalWrite(IN1, LOW);
      digitalWrite(IN2, HIGH);
    }
  } else {
    Serial1.write("Brake is enabled\n\r");
  }
}





void followWall(char side, int dist){
  if (side == 'L'){
    distIRA = getDistanceCM('A');
    if (distIRA > (wfDist + 5)){// && distIRA < 40){ //Too Far. Max dist of 40cm
      setDir('L');
    } else if (distIRA < (wfDist - 5) || (distIRA < 5)){ //Too close
      setDir('R');
    } else {
      setDir('F');
    }
  } else if (side == 'R'){
    distIRB = getDistanceCM('B');
    if (distIRB > (wfDist + 5)){// && distIRB < 40){ //Too Far. Max dist of 40cm
      setDir('R');
    } else if (distIRB < (wfDist - 5) || (distIRB < 5)){ //Too close
      setDir('L');
    } else {
      setDir('F');
    }
  } else if (side == 'B'){
    distIRA = getDistanceCM('A');
    distIRB = getDistanceCM('B');
    if (abs(distIRA - distIRB) < 10){ //Close to centred (within 10cm error)
      setDir('F');
    } else if (distIRA > distIRB){ //Closer to Right
      setDir('L');
    } else { // Closer to left
      setDir('R');
    }
  }
  driveMotors(speedA,speedB); //Speed is in ?? units
}



uint8_t getDistanceCM(char sensor){
  uint16_t val;
  float millivolts;
  uint8_t distanceCM;
  const float m = 1.1946E-4;
  const float c = 0.0217;
  const float b1 = -0.7900;
  
  if (sensor == 'A'){
    val = analogRead(IRA);
  } else if (sensor == 'B'){
    val = analogRead(IRB);
  }
  
  millivolts = 1000.0 * 5.0 * ((float)val / 1023.0);
  distanceCM = round(pow((m * millivolts + c),(1.0/b1)));
  //Serial.print(millivolts);
  //Serial.print(" ");
  Serial.println(distanceCM);
  return round(distanceCM);
}



















void tiltPlatform(void){
  static boolean up = false; 
  //static uint8_t pos = 150;
  
  if (up){
      Serial1.write("Going down\n\r");
      setPlatform(0);
      stopMotors();
      enableMotors(true); //Re-enable motors
      myservo.detach();   //Allow other pin PWM to work 
      up = false;
  } else {
      Serial1.write("Going up\n\r");
      stopMotors();        //Stop current running command
      enableMotors(false); //Disable motors
      myservo.attach(10);  //Enable servo actuation 
      setPlatform(30);     //Raise platform
      up = true;
  }
}

void setPlatform(uint8_t angle){
  int pos;
  //Increasing servo angle decreases platform angle
  uint8_t servoAngle;
  static uint8_t currServoAngle = 150;
  
  //Conversion from platform angle to servo angle
  servoAngle = 150-angle;
  servoAngle = constrain(servoAngle, 120, 150); //Limit servo angles
  
  if (currServoAngle > servoAngle){ //Decrease to desired angle
    for (pos = currServoAngle; pos > servoAngle; pos-=1){
      myservo.write(pos);
      delay(10);
    }
  } else { //Increase to desired angle
    for (pos = currServoAngle; pos < servoAngle; pos+=1){
      myservo.write(pos);
      delay(10);
    } 
  }
  currServoAngle = servoAngle;  
}





void reinitTimer1(void){
  TCCR1B = 0;
  TCCR1B |= (1 << CS11); //Set prescaler to 64
  TCCR1A |= (1 << WGM10); //Put in 8 bit phase correct PWM

}
  

