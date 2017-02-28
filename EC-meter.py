# imports and stuff
from time import sleep
from gpiozero import *


LOW,HIGH = 0,1

class Sensors:

    def __init__(self):
        self.R1 = 1000
        self.Ra = 25
        self.R1 = (self.R1 + self.Ra)  # Taking into acount Powering Pin Resitance

        self.PPMconversion, self.TemperatureCoef, self.K = 0.7, 0.019, 2.88

        # arduino library references
        # OneWire oneWire(ONE_WIRE_BUS) # Setup a oneWie instance to communicate with any OneWire devices
        # DallasTemperature sensors( & oneWire) # Pass our oneWire reference to Dallas Temperature.

        self.Temperature = 10
        self.EC, self.EC25, self.ppm, = 0
        self.raw = 0
        self.Vin = 5
        self.Vdrop = 0
        self.Rc = 0
        self.buffer = 0

        self.ECPin, self.ECGround, self.ECPower, self.TempProbePositive, self.TempProbeNegative, = Pin()
        self.ECPin.function, self.ECPower.function = 'input'
        self.ECGround.input_with.state(LOW)
        self.TempProbePositive.output_with.state(HIGH)
        self.TempProbeNegative.output_with.state(LOW)
        # pinMode(TempProbeNegative, OUTPUT ) # seting ground pin as output for tmp probe
        # digitalWrite(TempProbeNegative, LOW ) # Seting it to ground so it can sink current
        # pinMode(TempProbePositive, OUTPUT ) # ditto but for positive
        # digitalWrite(TempProbePositive, HIGH )

        # pinMode(ECPin, INPUT)
        # pinMode(ECPower, OUTPUT) # Setting pin for sourcing current
        # pinMode(ECGround, OUTPUT) # setting pin for sinking current
        # digitalWrite(ECGround, LOW) # We can leave the ground connected permanantly

        sleep(1)
        # print('loaded sensor settings')

    def poll(self):
        # ** ** ** ** * Reading Temperature Of Solution ** ** ** ** ** ** ** ** ** * #
        # sensors.requestTemperatures()  # Send the command to get temperatures
        # Temperature = sensors.getTempCByIndex(0)  # Stores Value in Variable

        # ** ** ** ** ** ** Estimates Resistance of Liquid ** ** ** ** ** ** ** ** #
        self.ECPower._set_state(HIGH)
        raw = self.ECPin.get() # analogRead() ?
        sleep(0.1)
        raw = self.ECPin.get()  # This is not a mistake, First reading will be low beause if charged a capacitor
        self.ECPower._set_state(LOW)

        # ** ** ** ** ** ** ** ** * Converts to EC ** ** ** ** ** ** ** ** ** ** ** ** ** #
        self.Vdrop = (self.Vin * raw) / 1024.0
        self.Rc = (self.Vdrop * self.R1) / (self.Vin - self.Vdrop)
        self.Rc = self.Rc - self.Ra  # acounting for Digital Pin Resitance
        self.EC = 1000 / (self.Rc * self.K)

        # ** ** ** ** ** ** * Compensating For Temperaure ** ** ** ** ** ** ** ** ** ** #
        self.EC25 = self.EC / (1 + self.TemperatureCoef * (self.Temperature - 25.0))
        self.ppm = (self.EC25) * (self.PPMconversion * 1000)

    def PrintReadings(self):
        print("Rc:",self.Rc)
        print("EC:",self.EC25,"Simens  | ",self.ppm," ppm")
        print("Temperature:",self.Temperature,"*C ")

        # ** ** ** ** ** Usued for Debugging ** ** ** ** ** **
        # print("Vdrop: ",self.Vdrop)
        # print("Rc: ",self.Rc,self.EC,"Siemens")
        # ** ** ** ** ** end of Debugging Prints ** ** ** ** *

    def getEC(self):
        return self.EC25

    def getRc(self):
        return self.Rc

    def getTemperature(self):
        return self.Temperature

    def getPPM(self):
        return self.ppm



if __name__ == 'main':
    sleep(0.1)  # gives sensor time to settle
    sensors = Sensors()
    # ** Adding Digital Pin Resistance to[25 ohm] to the static Resistor ** ** ** ** * #
    # Consule Read-Me for Why, or just accept it as true


    # print("ElCheapo Arduino EC-PPM measurments")
    # print("By: Michael Ratcliffe  Mike@MichaelRatcliffe.com")
    # print("Free software: you can redistribute it and/or modify it under GNU ")
    # print("")
    # print("Make sure Probe and Temp Sensor are in Solution and solution is well mixed")
    # print("")
    # print("Measurments at 5's Second intervals [Dont read Ec morre than once every 5 seconds]:")

    while True:
        sensors.poll()  # Calls Code to Go into GetEC() Loop[Below Main Loop] dont call this more that 1 / 5 hhz[once every five seconds] or you will polarise the water
        sensors.PrintReadings()  # Cals Print routine[below main loop]
        sleep(5)
