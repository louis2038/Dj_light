int LED1r = 3;
int LED1g = 5;
int LED1b = 6;
int LED2r = 9;
int LED2g = 10;
int LED2b = 11;
char mode;
int r;
int g;
int b;

void setup() {
    Serial.begin(115200); // Serial Port at 9600 baud
    Serial.setTimeout(10); // Instead of the default 1000ms, in order
                            // to speed up the Serial.parseInt() 
  pinMode(LED1r,OUTPUT);
  pinMode(LED1g,OUTPUT);
  pinMode(LED1b,OUTPUT);
  pinMode(LED2r,OUTPUT);
  pinMode(LED2g,OUTPUT);
  pinMode(LED2b,OUTPUT);
  analogWrite(LED1r,0);
  analogWrite(LED1g,0);
  analogWrite(LED1b,0);
  analogWrite(LED2r,0);
  analogWrite(LED2g,0);
  analogWrite(LED2b,0);
}

void loop() {
    // Check if characters available in the buffer
    if (Serial.available() > 0) {
        delay(1); // If not delayed, second character is not correctly read
        r = Serial.parseInt();
        mode = Serial.read();
        g = Serial.parseInt();
        Serial.read(); 
        b = Serial.parseInt(); 
        if(mode == 'a'){
          analogWrite(LED1r, r);
          analogWrite(LED1g, g);
          analogWrite(LED1b, b);
        }else{
          analogWrite(LED2r, r);
          analogWrite(LED2g, g);
          analogWrite(LED2b, b);
        }
        
    }
}
