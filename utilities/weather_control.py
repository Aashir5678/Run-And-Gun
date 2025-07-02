import pygame
from .constants import *
from random import uniform, randint
from numpy import interp

pygame.init()
pygame.mixer.init()


RAIN_WIDTH = 2 # 3
RAIN_HEIGHT = 7
RAIN_BLUE = (100, 100, 200)
MIN_RAIN_SPEED = 7
MAX_RAIN_SPEED = 12 
MAX_RAIN_FREQ = 15 # 15, Controls the number of rain drops per frame on average, larger frequency means lighter rain, smaller frequency means harder rain
RAIN_CHANCE = FPS * 20 # Chance that it will randomly start raining every tick
MAX_RAIN_DURATION = FPS * 90
TRANSITION_TO_RAIN = 15


class Weather:
	def __init__(self, screen, sky_color):
		self.screen = screen
		self.sky_color = sky_color
		self.raining = False
		self.drops = []
		self.ticks_rained = 0
		self.thunder_sound = pygame.mixer.Sound("Assets//sfx//thunder.wav")
		self.rain_sound = pygame.mixer.Sound("Assets//sfx//rain.mp3")
		self.rain_channel = pygame.mixer.Channel(2)
		self.thunder_channel = pygame.mixer.Channel(3)

		self.rain_channel.set_volume(0.25)
		self.thunder_channel.set_volume(0.7)

		self.red = self.sky_color[0]
		self.green = self.sky_color[1]
		self.blue = self.sky_color[2]

		self.rain_freq = 0
		self.thunder_freq = 0
		self.rain_speed = 0
		self.rain_duration = 0
		self.in_transition = False

	def stop(self):
		self.rain_channel.stop()
		self.thunder_channel.stop()


	def update(self, ticks, scroll_speed, player):
		if self.raining and self.sky_color == DULL_SKY:
			self.ticks_rained += 1

			self.screen.fill(self.sky_color)
			if self.ticks_rained % randint(1, self.rain_freq) == 1:
				if not self.rain_channel.get_busy():
					self.rain_channel.play(self.rain_sound, fade_ms=1500)

				self.drops.extend(generate_rain(self.screen, self.rain_speed, self.rain_freq))


			if player.health < 0.5:
				chance_of_thunder = self.thunder_freq // 2

			else:
				chance_of_thunder = self.thunder_freq

			if self.ticks_rained % chance_of_thunder == 0:
				self.thunder_channel.play(self.thunder_sound)
				self.thunder_channel.fadeout(7000)

				self.screen.fill(WHITE)

			if self.ticks_rained >= self.rain_duration:
				self.raining = False
				self.ticks_rained = 0
				return


		elif self.raining and self.sky_color != DULL_SKY:
			
			if self.red > DULL_SKY[0] and ticks % TRANSITION_TO_RAIN == 0:
				self.red -= 1

			if self.green > DULL_SKY[1] and ticks % TRANSITION_TO_RAIN == 0:
				self.green -= 2

			elif self.green <= DULL_SKY[1] and ticks % TRANSITION_TO_RAIN == 0:
				self.green = DULL_SKY[1]

			if self.blue > DULL_SKY[2] and ticks % TRANSITION_TO_RAIN == 0:
				self.blue -= 3

			elif self.blue <= DULL_SKY[2] and ticks % TRANSITION_TO_RAIN == 0:
				self.blue = DULL_SKY[2]

			self.sky_color = (self.red, self.green, self.blue)
			self.screen.fill(self.sky_color)

			if self.sky_color == DULL_SKY:
				self.in_transition = False

			else:
				self.in_transition = True

		elif not self.raining and self.sky_color != SKY_BLUE:
			if self.red < SKY_BLUE[0] and ticks % TRANSITION_TO_RAIN == 0:
				self.red += 1

			if self.green < SKY_BLUE[1] and ticks % TRANSITION_TO_RAIN == 0:
				self.green += 2

			elif self.green >= SKY_BLUE[1] and ticks % TRANSITION_TO_RAIN == 0:
				self.green = SKY_BLUE[1]

			if self.blue < SKY_BLUE[2] and ticks % TRANSITION_TO_RAIN == 0:
				self.blue += 3

			elif self.blue >= SKY_BLUE[2] and ticks % TRANSITION_TO_RAIN == 0:
				self.blue = SKY_BLUE[2]

			self.sky_color = (self.red, self.green, self.blue)
			self.screen.fill(self.sky_color)

			if self.sky_color == SKY_BLUE:
				self.in_transition = False

			else:
				self.in_transition = True

			# self.drops = []

		if not self.raining and self.rain_channel.get_busy():
			self.rain_channel.fadeout(5000)

		if len(self.drops) > 0:
			for drop in self.drops:
				drop.x -= scroll_speed
				if drop.y >= SCREEN_HEIGHT:
					self.drops.remove(drop)
					continue

				drop.update()
				drop.draw()



	def handle_rain(self):
		if not self.raining and randint(0, RAIN_CHANCE) == 0 and not self.in_transition:
			self.rain_freq = randint(2, MAX_RAIN_FREQ)
			# self.rain_freq = 2

			self.thunder_freq = (self.rain_freq * FPS * 4) # Range: Every 4 seconds to 1 minute
			self.rain_duration = randint(10 * FPS, MAX_RAIN_DURATION)

			self.rain_speed = round(interp(self.rain_freq, [1, MAX_RAIN_FREQ], [MAX_RAIN_SPEED, MIN_RAIN_SPEED]), 3)

			self.raining = True
			# self.transition_to_rain = 1
			print ("Raining...")
			print (f"Frequency: one in {str(self.rain_freq)} chance of drop of rain per frame (1/60 seconds)")
			print (f"Thunder: one in {str(self.thunder_freq)} chance of thunder per frame")
			print (f"Speed: {str(self.rain_speed)}")
			print (f"Duration: {str(self.rain_duration // 60)} seconds")
			print()
			self.rain = generate_rain(self.screen, self.rain_speed, self.rain_freq)



class Rain:
	def __init__(self, screen, x, y, vel_y):
		self.screen = screen
		self.x = x
		self.y = y
		self.vel_y = vel_y

		self.rect = pygame.Rect(self.x, self.y, RAIN_WIDTH, RAIN_HEIGHT)

	def draw(self):
		pygame.draw.rect(self.screen, RAIN_BLUE, self.rect)


	def update(self):
		self.y += self.vel_y
		self.rect = pygame.Rect(self.x, self.y, RAIN_WIDTH, RAIN_HEIGHT)

	def hit_block(self, block):
		return self.rect.colliderect(block.get_rect()) or (abs(self.y - block.y) < RAIN_HEIGHT and abs(self.x - block.x) < BLOCK_SIZE)

	def hit_entity(self, entity):
		return entity.get_rect().colliderect(self.rect) or (abs(self.x - entity.x) < self.rect.width and abs(self.y - entity.y) < self.rect.height)



def generate_rain(screen, speed, freq):

	rain_drops = []

	for x in range(0, SCREEN_WIDTH * 2, RAIN_WIDTH):

		if randint(0, freq) == 0:
			vel_y = uniform(speed - (speed // 2), speed)
			rain_drops.append(Rain(screen, x, -RAIN_HEIGHT, vel_y))


	return rain_drops