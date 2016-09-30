/*
  Serial Event example
 When new serial data arrives, this sketch adds it to a String.
 When a newline is received, the loop prints the string and
 clears it.
 A good test for this is to try it with a GPS receiver
 that sends out NMEA 0183 sentences.
 Created 9 May 2011
 by Tom Igoe
 This example code is in the public domain.
 http://www.arduino.cc/en/Tutorial/SerialEvent
 */

String inputString = "";         // a string to hold incoming data
boolean stringComplete = false;  // whether the string is complete
boolean run_loop = false;
String acknowledge = "received\n";
/* 
voidsetup() {
  // initialize serial:
  Serial.begin(9600);
  // reserve 200 bytes for the inputString:
  inputString.reserve(200);
}

void loop() {
  // print the string when a newline arrives:
  if (stringComplete) {
    Serial.println(inputString);
    // clear the string:
    inputString = "";
    stringComplete = false;
  }
}



  SerialEvent occurs whenever a new data comes in the
 hardware serial RX.  This routine is run between each
 time loop() runs, so using delay inside loop can delay
 response.  Multiple bytes of data may be available.

 Code that measures resistances is here

 Get everything to python with characters and then use python to
 parse the characters

*/
void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);

  // setup digital outputs to control MUX switching
  pinMode(4, OUTPUT);
  pinMode(5, OUTPUT);
  pinMode(6, OUTPUT);
  pinMode(7, OUTPUT);
  pinMode(8, OUTPUT);
  pinMode(9, OUTPUT);
  pinMode(10, OUTPUT);
  pinMode(11, OUTPUT);
  pinMode(12, OUTPUT);
  pinMode(13, OUTPUT);
  pinMode(14, OUTPUT);
  pinMode(15, OUTPUT);
  pinMode(16, OUTPUT);
  pinMode(17, OUTPUT);
  pinMode(23, OUTPUT);
  pinMode(25, OUTPUT);
  pinMode(27, OUTPUT);
  pinMode(29, OUTPUT);
  pinMode(31, OUTPUT);
  pinMode(33, OUTPUT);
}

int counter = 0;

float Rref = 994000.0;

void loop() {
  if (Serial.available() > 0) {
    // put your main code here, to run repeatedly:
    int channels[] = {0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,
                      17,18,19,20,21,22,23,24,25,26,27,28,29,30,
                      31,32,33,34,35,36,37,38,39,40,41,42,43,44,
                      45,46,47,48,49,50,51,52,53,54,55,56,57,58,
                      59,60,61,62,63,64,65,66,67,68,69,70,71,72,
                      73,74,75,76,77,78,79,80,81,82,83,84,85,86,
                      87,88,89};
    int channels_0[] = {15,14,13,12,11,10,9,8,7,6,5,4,3,2,1,0};
    int channels_1[] = {15,14,13,12,11,10,9,8,7,6,5,4,3,2,1,0};
    //int channels_0[] = {2,6,12};
    //int channels_1[] = {2,6,12};
    int enable_output[] = {4,5,6,7,8,9};
    int nmuxes = sizeof(enable_output) / sizeof(enable_output[0]);
    digitalWrite(4, HIGH); 
    digitalWrite(5, HIGH); 
    digitalWrite(6, HIGH); 
    digitalWrite(7, HIGH); 
    digitalWrite(8, HIGH);
    digitalWrite(9, HIGH);
    digitalWrite(23, HIGH); 
    digitalWrite(25, HIGH);
    digitalWrite(27, HIGH);
    digitalWrite(29, HIGH);   
    digitalWrite(31, HIGH); 
    digitalWrite(33, HIGH); 
    int enable_readers[] = {33, 31, 29, 27, 25, 23};
    int nreaders = sizeof(enable_readers) / sizeof(enable_readers[0]);
    int nchan = sizeof(channels) / sizeof(channels[0]);
    int nchan_0 = sizeof(channels_0) / sizeof(channels_0[0]); 
    int nchan_1 = sizeof(channels_1) / sizeof(channels_1[0]);
    for(int jchan = 0; jchan < nchan; jchan++)  
    {
      int choose_mux = 0;
      int choose_mux_compare = 0;
      int choose_chan = jchan;
      int channel_compare = jchan + 1;
      while(choose_chan > 15)
      {
        choose_chan = choose_chan - 16;
        choose_mux ++;
      }
      digitalWrite(enable_output[choose_mux], LOW);
      delay(200);

      while(channel_compare > 15)
      {
        channel_compare = channel_compare - 16;
        choose_mux_compare ++;
      }
      digitalWrite(enable_readers[choose_mux_compare], LOW);
      delay(200);
      select_channel_0(jchan);
      select_channel_1(jchan+1);
      float V = read_voltage();
      Serial.println(15-channels_0[choose_chan]+choose_mux*16);
      //counter ++;
      Serial.println(15-channels_1[channel_compare]+choose_mux_compare*16);
      //counter ++;
      Serial.println(V);
      /*if(jchan = 20)
        {
        delay(2000);
      }
      */
      //counter ++;
      Serial.println();     
      digitalWrite(enable_output[choose_mux], HIGH);
      delay(200);
      digitalWrite(enable_readers[choose_mux_compare], HIGH);
      delay(200);

    }
    /*int channel_0 = 10;
    int channel_1 = 11;

    for(int joutput = 0; joutput < nmuxes; joutput++)
    {
      digitalWrite(enable_output[joutput], LOW);
      delay(200);
      for(int jchan = 0; jchan < nchan_0-1; jchan++)
      {
        select_channel_0(channels_0[jchan]);
        delay(200);
        //for(int kchan = 0; kchan < nchan_1; kchan++)
        //{
          int kchan = jchan++;
          select_channel_1(channels_1[kchan]);
          delay(200);
          for(int jreader = 0; jreader < nreaders; jreader++)
          {
            digitalWrite(enable_readers[jreader], LOW);
            delay(200);
              float V = read_voltage();
              Serial.println(channels_0[jchan]+joutput*16);
              counter ++;
              Serial.println(channels_1[kchan]+jreader*16);
              counter ++;
              Serial.println(V);
              counter ++;
              Serial.println();
              counter = 0;
              
              delay(200); 
            
          digitalWrite(enable_readers[jreader], HIGH); 
          }
         //}
      } 
      digitalWrite(enable_output[joutput], HIGH);
      delay(200); 
    }    */
  }
    /*
    select_channel_0(channel_0);
    select_channel_1(channel_1);
    delay(200);
    float V = read_voltage();
     Serial.println(channel_0);
     Serial.println(channel_1);
     Serial.println(V);
     Serial.println();
     */
  run_loop = 0;
}

void serialEvent() {
  while (Serial.available() > 0) {
    // get the new byte:
    char inChar = (char)Serial.read();
    // add it to the inputString:
    inputString += inChar;
    // if the incoming character is a newline, set a flag
    // so the main loop can do something about it:
    run_loop = true;
    
  }
}


void select_channel_1(int chan)
{
  int pin_nums[] = {14, 15, 16, 17};
  
  for(int jbit = 0; jbit<4; jbit++)
  {
    int k = chan >> jbit;
    if(k & 1)
    {
      digitalWrite(pin_nums[jbit], HIGH);
    }
    else
    {
      digitalWrite(pin_nums[jbit], LOW);
    }
  }
}


void select_channel_0(int chan)
{
  int pin_nums[] = {10,11,12,13};
  
  for(int jbit = 0; jbit<4; jbit++)
  {
    int k = chan >> jbit;
    if(k & 1)
    {
      digitalWrite(pin_nums[jbit], HIGH);
    }
    else
    {
      digitalWrite(pin_nums[jbit], LOW);
    }
  }
}


float read_voltage()
{
  int ADCval = analogRead(15);
  float voltage = Rref * (1 - float(ADCval) / 1024.0) / (float(ADCval) / 1024.0);
  return voltage;
}
/*
void setup(){
  Serial.begin(9600);
  pinMode(13, OUTPUT);
  Serial.write('1');
}

void loop(){
  if(Serial.available() > 0){
    delay(500);
    Serial.write('0');
  }
}

 * 
*/
