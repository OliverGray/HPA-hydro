# imports and stuff
from time import sleep,time
import gpiozero as zero
import RPi.GPIO as GPIO


LOW,HIGH = 0,1

class Sensors:

    def __init__(self, R1=1000, ECPin=10,ECGround=11,ECPower=12,TempPositive=13,TempNegative=14,echannel=0,):

        GPIO.setmode(GPIO.BCM)

        self.R1 = R1
        self.Ra = 25
        self.R1 = (self.R1 + self.Ra)  # Taking into account Powering Pin Resistance

        self.PPMconversion, self.TemperatureCoef, self.K = 0.7, 0.019, 2.88

        self.Temperature = 10
        self.EC, self.EC25, self.ppm, = 0
        self.raw = 0
        self.Vin = 5
        self.Vdrop = 0
        self.Rc = 0
        self.buffer = 0

        self.ltime = 0

        self.ECPin, self.ECGround, self.ECPower, self.TempProbePositive, self.TempProbeNegative, = zero
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

        '''adc'''
        # change these as desired - they're the pins connected from the
        # SPI port on the ADC to the Cobbler
        self.SPICLK = 18
        self.SPIMISO = 23
        self.SPIMOSI = 24
        self.SPICS = 25

        self.EC_channel = echannel

        # set up the SPI interface pins
        GPIO.setup(self.SPIMOSI, GPIO.OUT)
        GPIO.setup(self.SPIMISO, GPIO.IN)
        GPIO.setup(self.SPICLK, GPIO.OUT)
        GPIO.setup(self.SPICS, GPIO.OUT)
        '''adc'''

        sleep(1)
        # print('loaded sensor settings')


    # read SPI data from MCP3008 chip, 8 possible adc's (0 thru 7)
    def readadc(self, adcnum,):

        if ((adcnum > 7) or (adcnum < 0)):
            return -1
        GPIO.output(self.SPICS, True)

        GPIO.output(self.SPICLK, False)  # start clock low
        GPIO.output(self.SPICS, False)  # bring CS low

        commandout = adcnum
        commandout |= 0x18  # start bit + single-ended bit
        commandout <<= 3  # we only need to send 5 bits here
        for i in range(5):
            if (commandout & 0x80):
                GPIO.output(self.SPIMOSI, True)
            else:
                GPIO.output(self.SPIMOSI, False)
            commandout <<= 1
            GPIO.output(self.SPICLK, True)
            GPIO.output(self.SPICLK, False)

        adcout = 0
        # read in one empty bit, one null bit and 10 ADC bits
        for i in range(12):
            GPIO.output(self.SPICLK, True)
            GPIO.output(self.SPICLK, False)
            adcout <<= 1
            if (GPIO.input(self.SPIMISO)):
                adcout |= 0x1

        GPIO.output(self.SPICS, True)

        adcout >>= 1  # first bit is 'null' so drop it
        return adcout


    def poll(self,):

        if self.ltime <= time() - 5:

            try:
                # ** ** ** ** * Reading Temperature Of Solution ** ** ** ** ** ** ** ** ** * #
                # sensors.requestTemperatures()  # Send the command to get temperatures
                # Temperature = sensors.getTempCByIndex(0)  # Stores Value in Variable

                # ** ** ** ** ** ** Estimates Resistance of Liquid ** ** ** ** ** ** ** ** #
                self.ECPower._set_state(HIGH)

                # raw = self.ECPin.get() # analogRead() ?
                # sleep(0.1)
                # raw = self.ECPin.get()  # This is not a mistake, First reading will be low beause if charged a capacitor
                raw = self.readadc(self.EC_channel)

                self.ECPower._set_state(LOW)

                # ** ** ** ** ** ** ** ** * Converts to EC ** ** ** ** ** ** ** ** ** ** ** ** ** #
                self.Vdrop = (self.Vin * raw) / 1024.0
                self.Rc = (self.Vdrop * self.R1) / (self.Vin - self.Vdrop)
                self.Rc = self.Rc - self.Ra  # acounting for Digital Pin Resitance
                self.EC = 1000 / (self.Rc * self.K)

                # ** ** ** ** ** ** * Compensating For Temperaure ** ** ** ** ** ** ** ** ** ** #
                self.EC25 = self.EC / (1 + self.TemperatureCoef * (self.Temperature - 25.0))
                self.ppm = (self.EC25) * (self.PPMconversion * 1000)

                self.ltime = time()

                return True

            except:

                return False

        else:

            return False


    def PrintReadings(self,):
        print("Rc:",self.Rc)
        print("EC:",self.EC25,"Simens  | ",self.ppm," ppm")
        print("Temperature:",self.Temperature,"*C ")

        # ** ** ** ** ** Usued for Debugging ** ** ** ** ** **
        # print("Vdrop: ",self.Vdrop)
        # print("Rc: ",self.Rc,self.EC,"Siemens")
        # ** ** ** ** ** end of Debugging Prints ** ** ** ** *

    def getEC(self,):
        return self.EC25

    def getRc(self,):
        return self.Rc

    def getTemperature(self,):
        return self.Temperature

    def getPPM(self,):
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
