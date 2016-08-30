/*
 * Code for analyzing the resistance between
 * any two pins on different mux boards
 * 
 * To be done: Work out a way to loop/automate this process.
 * 
 */

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);

  // setup digital outputs to control MUX switching
  pinMode(2, OUTPUT);
  pinMode(3, OUTPUT);
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

}

float Rref = 4720.0;

void loop() {
  // put your main code here, to run repeatedly:
  int channels_0[] = {0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15};
  int channels_1[] = {0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15};
  //int channels_0[] = {2,6,12};
  //int channels_1[] = {2,6,12};
  int enable_output[] = {10, 11};
  int nmuxes = sizeof(enable_output) / sizeof(enable_output[0]);
  digitalWrite(10, HIGH); 
  digitalWrite(11, HIGH); 
  digitalWrite(12, HIGH);
  digitalWrite(13, HIGH);
  int enable_readers[] = {12, 13};
  int nreaders = sizeof(enable_readers) / sizeof(enable_readers[0]);
  int nchan_0 = sizeof(channels_0) / sizeof(channels_0[0]); 
  int nchan_1 = sizeof(channels_1) / sizeof(channels_1[0]);  
  /*int channel_0 = 10;
  int channel_1 = 11;
  */
  for(int joutput = 0; joutput < nmuxes; joutput++)
  {
    digitalWrite(enable_output[joutput], LOW);
    delay(200);
    for(int jchan = 0; jchan < nchan_0; jchan++)
    {
      select_channel_0(channels_0[jchan]);
      delay(200);
      for(int kchan = 0; kchan < nchan_1; kchan++)
      {
        select_channel_1(channels_1[kchan]);
        delay(200);
        for(int jreader = 0; jreader < nreaders; jreader++)
        {
          digitalWrite(enable_readers[jreader], LOW);
          delay(200);
          if (channels_0[jchan]+joutput*16 != channels_1[kchan]+jreader*16)
            {
            float V = read_voltage();
            Serial.println(channels_0[jchan]+joutput*16);
            Serial.println(channels_1[kchan]+jreader*16);
            Serial.println(V);
            Serial.println();
            
            delay(200); 
          }
        digitalWrite(enable_readers[jreader], HIGH); 
        }
       }
    } 
    digitalWrite(enable_output[joutput], HIGH);
    delay(200); 
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
}

void select_channel_0(int chan)
{
  int pin_nums[] = {2,3,4,5};
  
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

void select_channel_1(int chan)
{
  int pin_nums[] = {6,7,8,9};
  
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
  int ADCval = analogRead(0);
  float voltage = Rref * (1 - float(ADCval) / 1024.0) / (float(ADCval) / 1024.0);
  return voltage;
}
