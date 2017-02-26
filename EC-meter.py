# imports and stuff
from time import sleep

R1 = 1000
Ra = 25
ECPin = A0
ECGround = A1
ECPower = A4

PPMconversion = 0.7

TemperatureCoef = 0.019
K=2.88

TempProbePossitive =8
TempProbeNegative=9

# arduino library references
# OneWire oneWire(ONE_WIRE_BUS) # Setup a oneWie instance to communicate with any OneWire devices
# DallasTemperature sensors( & oneWire) # Pass our oneWire reference to Dallas Temperature.

Temperature=10
EC=0
EC25 =0
ppm =0


raw= 0
Vin= 5
Vdrop= 0
Rc= 0
buffer=0


pinMode(TempProbeNegative, OUTPUT ) # seting ground pin as output for tmp probe
digitalWrite(TempProbeNegative, LOW ) # Seting it to ground so it can sink current
pinMode(TempProbePossitive, OUTPUT ) # ditto but for positive
digitalWrite(TempProbePossitive, HIGH )
pinMode(ECPin, INPUT)
pinMode(ECPower, OUTPUT) # Setting pin for sourcing current
pinMode(ECGround, OUTPUT) # setting pin for sinking current
digitalWrite(ECGround, LOW) # We can leave the ground connected permanantly

sleep(0.1) # gives sensor time to settle
sensors.begin()
sleep(0.1)
# ** Adding Digital Pin Resistance to[25 ohm] to the static Resistor ** ** ** ** * #
# Consule Read-Me for Why, or just accept it as true
R1=(R1+Ra) # Taking into acount Powering Pin Resitance

print("ElCheapo Arduino EC-PPM measurments")
print("By: Michael Ratcliffe  Mike@MichaelRatcliffe.com")
print("Free software: you can redistribute it and/or modify it under GNU ")
print("")
print("Make sure Probe and Temp Sensor are in Solution and solution is well mixed")
print("")
print("Measurments at 5's Second intervals [Dont read Ec morre than once every 5 seconds]:")


def loop():
	GetEC() # Calls Code to Go into GetEC() Loop[Below Main Loop] dont call this more that 1 / 5 hhz[once every five seconds] or you will polarise the water
	PrintReadings() # Cals Print routine[below main loop]
	sleep(5)


def GetEC():
	# ** ** ** ** * Reading Temperature Of Solution ** ** ** ** ** ** ** ** ** * #
	sensors.requestTemperatures() # Send the command to get temperatures
	Temperature=sensors.getTempCByIndex(0) # Stores Value in Variable

	# ** ** ** ** ** ** Estimates Resistance of Liquid ** ** ** ** ** ** ** ** #
	digitalWrite(ECPower, HIGH)
	raw= analogRead(ECPin)
	raw= analogRead(ECPin) # This is not a mistake, First reading will be low beause if charged a capacitor
	digitalWrite(ECPower, LOW)

	# ** ** ** ** ** ** ** ** * Converts to EC ** ** ** ** ** ** ** ** ** ** ** ** ** #
	Vdrop= (Vin * raw) / 1024.0
	Rc=(Vdrop * R1) / (Vin-Vdrop)
	Rc=Rc-Ra # acounting for Digital Pin Resitance
	EC = 1000 / (Rc * K)

	# ** ** ** ** ** ** * Compensating For Temperaure ** ** ** ** ** ** ** ** ** ** #
	EC25  =  EC / (1+ TemperatureCoef * (Temperature-25.0))
	ppm=(EC25) * (PPMconversion * 1000)


def PrintReadings():
	print("Rc: ")
	print(Rc)
	print(" EC: ")
	print(EC25)
	print(" Simens  ")
	print(ppm)
	print(" ppm  ")
	print(Temperature)
	print(" *C ")

	#
	# ** ** ** ** ** Usued for Debugging ** ** ** ** ** **
	print("Vdrop: ")
	print(Vdrop)
	print("Rc: ")
	print(Rc)
	print(EC)
	print("Siemens")
	# ** ** ** ** ** end of Debugging Prints ** ** ** ** *