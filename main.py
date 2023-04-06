from time import sleep_ms
from utime import ticks_ms
from math import trunc
from machine import Pin, PWM
from ds18x20 import DS18X20
from onewire import OneWire
from pid import PID

## constants
duty_u16_max = 65535                          # maximum duty cycle
duty_u16_min = trunc(0.01 * duty_u16_max)     # minimum duty cycle

## parameters
target =  22.0                                 # target temperature in degrees celcius
frequency = 25000                             # pwm frequency in Hz
period = 1000                                 # control loop period in ms

# An error of 2 degrees Celcius should be proportional to the maximum duty cycle
# gains as fraction of 100% duty
kp = 0.50                                     # proportional gain
ki = 0.05                                     # integral gain
kd = 0.00                                     # derivative gain

## temperature sensor setup
temp_pin = Pin(22)
probe = DS18X20(OneWire(temp_pin))
roms = probe.scan()
print('INFO Found DS devices: ', roms)

## pid setup
def sampler() -> float:
    """
      Sample the value of the DS18X20 temperature probe. Cf.the (DS18X20 tutorial)[https://how2electronics.com/interfacing-ds18b20-sensor-with-raspberry-pi-pico/].
    """
    probe.convert_temp()
    sleep_ms(750)  # minumum time to wait until the value can be read.
    return round(probe.read_temp(roms[0]), 1)

pid = PID(22.0, sampler, duty_u16_min, duty_u16_max, True)

pid.kp = int(kp * duty_u16_max)
pid.ki = int(ki * duty_u16_max)
pid.kd = int(kd * duty_u16_max)

## pwm fan setup
pwm = PWM(Pin(15))
pwm.freq(frequency)

## main loop
while True:
  ticks = ticks_ms()

  current, signal = pid.sample()
  pwm.duty_u16(signal)

  # duty cycle expressed as a percentage of the full cycle
  duty = round((signal * 100) / duty_u16_max, 1)

  # log details of the current control cycle
  print(f'INFO target={target}°; current={current}°; duty={duty}%; p={pid.p()}; i={pid.i()}; d={pid.d()}')

  # sleep for the remainder of the period
  duration = ticks_ms() - ticks
  if(period - duration > 0):
     sleep_ms(period - duration)
  else:
     print(f'WARN control loop duration of {duration} ms longer than {period} ms')
