int LEDr = 3;
int LEDg = 5;
int LEDb = 9;

int r;
int g;
int b;


void setup() {
    Serial.begin(115200); // Serial Port at 9600 baud
    Serial.setTimeout(10); // Instead of the default 1000ms, in order
                            // to speed up the Serial.parseInt() 
  pinMode(LEDr,OUTPUT);
  pinMode(LEDg,OUTPUT);
  pinMode(LEDb,OUTPUT);
  analogWrite(LEDr,0);
  analogWrite(LEDg,0);
  analogWrite(LEDb,0);
}

void loop() {
    // Check if characters available in the buffer
    if (Serial.available() > 0) {
      
        r = Serial.parseInt();
        delay(1); // If not delayed, second character is not correctly read
        Serial.read();
        g = Serial.parseInt();
        Serial.read(); 
        b = Serial.parseInt(); 

        analogWrite(LEDr, r);
        analogWrite(LEDg, g);
        analogWrite(LEDb, b);
     
       
    }
}
