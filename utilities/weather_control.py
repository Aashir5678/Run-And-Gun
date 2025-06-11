import pygame
from .constants import *
from random import uniform, randint

pygame.init()


RAIN_WIDTH = 3
RAIN_HEIGHT = 7
RAIN_BLUE = (100, 100, 200)
RAIN_SPEED = 30 # Control rain speed
RAIN_FREQ = 30 # Controls the number of rain drops per frame, larger frequency means less rain drops
RAIN_CHANCE = FPS * 2 # Chance that it will randomly start raining
RAIN_DURATION = FPS * 50
THUNDER_FLASH_FREQ = FPS * 6
TRANSITION_TO_RAIN = 15


class Weather:
	def __init__(self, screen, sky_color):
		self.screen = screen
		self.sky_color = sky_color
		self.raining = False
		self.drops = []

		self.red = self.sky_color[0]
		self.green = self.sky_color[1]
		self.blue = self.sky_color[2]

	def update(self, ticks, scroll_speed):
		if self.raining and self.sky_color == DULL_SKY:
			self.screen.fill(self.sky_color)
			if ticks % randint(1, RAIN_FREQ) == 1:
				self.drops.extend(generate_rain(self.screen, RAIN_SPEED, RAIN_FREQ))

			if ticks % randint(THUNDER_FLASH_FREQ - 20, THUNDER_FLASH_FREQ) == 0:
				self.screen.fill(WHITE)

			if ticks % RAIN_DURATION == 0:
				self.raining = False
				return

			for drop in self.drops:
				drop.x -= scroll_speed
				if drop.y >= SCREEN_HEIGHT:
					self.drops.remove(drop)
					continue

				drop.update()
				drop.draw()

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

			self.drops = []


	def handle_rain(self):
		if not self.raining and randint(0, RAIN_CHANCE) == 0:
			self.raining = True
			self.transition_to_rain = 1
			self.rain = generate_rain(self.screen, RAIN_SPEED, RAIN_FREQ)



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



def generate_rain(screen, speed, freq):

	rain_drops = []

	for x in range(0, SCREEN_WIDTH, RAIN_WIDTH):

		if randint(0, freq) == 0:
			vel_y = uniform(speed - (speed // 2), speed)
			rain_drops.append(Rain(screen, x, -RAIN_HEIGHT, vel_y))


	return rain_drops