import pygame
from constants import *


pygame.init()


class Bar:
	def __init__(self, screen, pos, color, back_ground_color=BLACK, value=1):
		self.screen = screen
		self.x, self.y = pos
		self.color = color
		self.back_ground_color = back_ground_color
		self.value = value # value of the bar as a decimal from 0.0 -> 1.0


		self.container_bar = pygame.Rect(self.x, self.y, SCREEN_WIDTH // 3, 30)
		self.value_bar = pygame.Rect(self.x + 5, self.y + 5, (SCREEN_WIDTH // 3) - 10, 20)

		self.set_value(self.value)
		

	def set_value(self, val):
		self.value = val
		self.value_bar = pygame.Rect(self.x + 5, self.y + 5, ((SCREEN_WIDTH // 3) - 10) * self.value, 20)

	def draw(self):
		pygame.draw.rect(self.screen, self.back_ground_color, self.container_bar)
		pygame.draw.rect(self.screen, self.color, self.value_bar)

