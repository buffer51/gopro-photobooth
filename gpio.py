import RPi.GPIO as GPIO
import time

CHANNEL = 10
EVENT_DELAY = 2 # seconds

class GPIOButton():
	def __init__(self, event_hook):
		self.pressed = False
		self.last_press = None
		self.event_hook = event_hook
	
	def gpio_event(self, channel):
		if GPIO.input(CHANNEL):
			self.down()
		else:
			self.up()
	
	def down(self):
		self.pressed = True
	
	def up(self):
		if self.pressed:
			self.maybe_event()
		
		self.pressed = False
	
	def maybe_event(self):
		current_time = time.time()
		
		if not self.last_press or current_time-self.last_press > EVENT_DELAY:
			self.event_hook()
			self.last_press = current_time
		

if __name__ == '__main__':
	GPIO.setmode(GPIO.BOARD)
	GPIO.setup(CHANNEL, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
	
	def event_hook():
		print('Event')
	button = GPIOButton(event_hook)
	GPIO.add_event_detect(CHANNEL, GPIO.BOTH, callback=button.gpio_event)
    
	time.sleep(60)
