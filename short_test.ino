#include <stdio.h>

float Rref = 99500.0;
int MUXfactor = 16;

// Pin numerology on Arduino, MUXs, and ZIFs.
// "0" refers to MUXs on the bottom row of the board.
// "1" refers to MUXs on the top row of the board.
int zifPins[] = {0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,
                  17,18,19,20,21,22,23,24,25,26,27,28,29,30,
                  31,32,33,34,35,36,37,38,39,40,41,42,43,44,
                  45,46,47,48,49,50,51,52,53,54,55,56,57,58,
                  59,60,61,62,63,64,65,66,67,68,69,70,71,72,
                  73,74,75,76,77,78,79,80,81,82,83,84,85,86,
                  87,88,89};
int gndPinsRev1[] = {0,89};
int gndPinRev2 = 90;
int muxPins0[] = {15,14,13,12,11,10,9,8,7,6,5,4,3,2,1,0};
int muxPins1[] = {15,14,13,12,11,10,9,8,7,6,5,4,3,2,1,0};
int logicPins0[] = {10,11,12,13};
int logicPins1[] = {14,15,16,17};
int enablePins0[] = {4,5,6,7,8,9};
int enablePins1[] = {33,31,29,27,25,23};
int nZifPins = sizeof(zifPins) / sizeof(zifPins[0]);
int nLogicPins0 = sizeof(logicPins0) / sizeof(logicPins0[0]);
int nLogicPins1 = sizeof(logicPins1) / sizeof(logicPins1[0]);
int nEnablePins0 = sizeof(enablePins0) / sizeof(enablePins0[0]);
int nEnablePins1 = sizeof(enablePins1) / sizeof(enablePins1[0]);


void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);

  // setup digital outputs to control MUX switching
  for(int jPin = 0; jPin < nLogicPins0; jPin++)
    pinMode(logicPins0[jPin], OUTPUT);
  for(int jPin = 0; jPin < nLogicPins1; jPin++)
    pinMode(logicPins1[jPin], OUTPUT);
  for(int jPin = 0; jPin < nEnablePins0; jPin++)
    pinMode(enablePins0[jPin], OUTPUT);
  for(int jPin = 0; jPin < nEnablePins1; jPin++)
    pinMode(enablePins1[jPin], OUTPUT);
}


void loop() {
  if (Serial.available() > 0) {
    // eat the input message; we don't care what it says
    String command = Serial.readString();
    
    // Pre-emptively set all the enable pins to high (disabled)
    for(int jPin = 0; jPin < nEnablePins0; jPin++)
      digitalWrite(enablePins0[jPin], HIGH);
    for(int jPin = 0; jPin < nEnablePins1; jPin++)
      digitalWrite(enablePins1[jPin], HIGH);

    // do the tests
    if(command == "TESshorts\n")
    {
      // lists of pin combos to check
      // TES-TES shorts
      int tesShortsList0[89];
      int tesShortsList1[89];
      for(int jPin = 0; jPin < 89; jPin++)
      {
        tesShortsList0[jPin] = jPin;
        tesShortsList1[jPin] = jPin + 1;
      }
      int nPinsTESShorts0 = sizeof(tesShortsList0) / sizeof(tesShortsList0[0]);
      int nPinsTESShorts1 = sizeof(tesShortsList1) / sizeof(tesShortsList1[0]);
    
      checkPins(tesShortsList0, tesShortsList1, nPinsTESShorts1);
    }
    else if(command == "GNDshorts0\n" || command == "GNDshorts1\n" || command == "GNDshortsRev2\n")
    {
      // Shorts to GND
      int gndShortsList0[90];
      int gndShortsList1[90];
      for(int jPin = 0; jPin < 90; jPin++)
      {
        gndShortsList0[jPin] = jPin;
        if(command == "GNDshorts0\n")
          gndShortsList1[jPin] = gndPinsRev1[0];
        else if(command == "GNDshorts1\n")
          gndShortsList1[jPin] = gndPinsRev1[1];
        else if(command == "GNDshortsRev2\n")
          gndShortsList1[jPin] = gndPinRev2;
      }
      int nPinsGNDShorts0 = sizeof(gndShortsList0) / sizeof(gndShortsList0[0]);
      int nPinsGNDShorts1 = sizeof(gndShortsList1) / sizeof(gndShortsList1[0]);
    
      checkPins(gndShortsList0, gndShortsList1, nPinsGNDShorts1);
    }

    Serial.println("end"); // termination string
  }
}


void checkPins(int *pinList0, int *pinList1, int nPins)
{ 
  for(int jpin = 0; jpin < nPins; jpin++)  
  {
    // find channels to measure on each bank of MUXs
    int mux0 = pinList0[jpin] / MUXfactor;
    int mux0_chan = pinList0[jpin] % MUXfactor;
    int mux1 = pinList1[jpin] / MUXfactor;
    int mux1_chan = pinList1[jpin] % MUXfactor;

    // enable MUXs
    digitalWrite(enablePins0[mux0], LOW);
    digitalWrite(enablePins1[mux1], LOW);

    // set logic pins on MUXs to appropriate channel
    selectChannel(muxPins0[mux0_chan], logicPins0);
    selectChannel(muxPins1[mux1_chan], logicPins1);

    // delay to let ADC equilibrate (necessary since we are using a large ~100kOhm
    // limiting resistor, resulting in a slow RC time constant for the ADC).
    delay(20);
    
    float R = readResistance();
    sendData(pinList0[jpin], pinList1[jpin], R);

    // disable the MUX channels
    digitalWrite(enablePins0[mux0], HIGH);
    digitalWrite(enablePins1[mux1], HIGH);
  }
}


// select a MUX channel using an array of four logic pin numbers on the Arduino
void selectChannel(int chan, int *logicPins)
{
  for(int jbit = 0; jbit<4; jbit++)
  {
    int k = chan >> jbit;
    if(k & 1)
      digitalWrite(logicPins[jbit], HIGH);
    else
      digitalWrite(logicPins[jbit], LOW);
  }
}


// Read the ADC pin and converts to a resistance.
float readResistance()
{
  int ADCval = analogRead(A15);
  float R = Rref * (1 - float(ADCval) / 1024.0) / (float(ADCval) / 1024.0);
  return R;
}


// Send a data message back over serial
void sendData(int chan0, int chan1, float R)
{
  int R_int = R;
  
  // package the message and send to serial
  char data_msg[40];
  
  if(isinf(R) == 1 || isinf(R) == -1)
    sprintf(data_msg, "%d,%d,inf\n", chan0, chan1);
  else
    // note that we need to sprintf the resistance as an integer in milliohms
    // because the version of sprintf that writes floats is too large to fit 
    // on the Arduino, and therefore isn't supported by the C compiler used by
    // the Arduino
    sprintf(data_msg, "%d,%d,%d\n", chan0, chan1, R_int);
    
  Serial.print(data_msg);
}


