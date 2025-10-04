import PCF8591 as ADC
import time
ADC.setup(0x48) 
while True:

    
  ADC0_units = ADC.read(1)
  ADC0_volts = (ADC0_units*3.3)/256
  print("ADC 0 units={}".format(ADC0_units))
  print("ADC 0 volts={} V".format(ADC0_volts), end='\n\n')
    
  ADC.write(ADC0_units)
  Temp_v=ADC0_volts/0.01

  time.sleep(1)
  
  #control intensity of LED  based on speed
  #drive led dont connect to GPIO
    
  
  
