void setup() {
  Serial.begin(9600);

  // setup digital outputs to control MUX switching
  pinMode(2, OUTPUT);
  pinMode(3, OUTPUT);
  pinMode(4, OUTPUT);
  pinMode(5, OUTPUT);

}

float Rref = 4720.0;

void loop() {
  // put your main code here, to run repeatedly:
  int nchan = 4;
  int channels[] = {7, 10, 14, 15};

  for(int jchan = 0; jchan < nchan; jchan++)
  {
    select_channel(channels[jchan]);
    delay(200);
    float V = read_voltage();
    delay(200);
    Serial.println(channels[jchan]);
    Serial.println(V);
    Serial.println();
  }
}


void select_channel(int chan)
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


float read_voltage()
{
  int ADCval = analogRead(0);
  float voltage = Rref * (1 - float(ADCval) / 1024.0) / (float(ADCval) / 1024.0);
  return voltage;
}

