import pygame
from .constants import *


pygame.init()


class Bar:
	def __init__(self, screen, pos, color, back_ground_color=BLACK, value=1, orientation="horizontal"):
		self.screen = screen
		self.x, self.y = pos
		self.color = color
		self.back_ground_color = back_ground_color
		self.value = value # value of the bar as a decimal from 0.0 -> 1.0
		self.orientation = orientation


		if self.orientation == "horizontal":
			self.container_bar = pygame.Rect(self.x, self.y, SCREEN_WIDTH // 3, 30)
			self.value_bar = pygame.Rect(self.x + 5, self.y + 5, (SCREEN_WIDTH // 3) - 10, 20)

		else:
			self.container_bar = pygame.Rect(self.x, self.y, 30, SCREEN_HEIGHT // 2)
			self.value_bar = pygame.Rect(self.x + 5, self.y + 5, 20, (SCREEN_HEIGHT // 2) - 10)

		self.set_value(self.value)
	
	def mouse_over(self, mx, my):
		return mx > self.x and mx < (self.x + self.container_bar.width) and my > self.y and (my < (self.y + self.container_bar.height))

	def set_value(self, val):
		self.value = val
		if self.orientation == "horizontal":
			self.value_bar = pygame.Rect(self.x + 5, self.y + 5, ((SCREEN_WIDTH // 3) - 10) * self.value, 20)

		else:
			self.value_bar = pygame.Rect(self.x + 5, self.y + 5 + (self.container_bar.height - (self.value * self.container_bar.height)), 20, (self.container_bar.height * self.value) - 10)

	def draw(self):
		pygame.draw.rect(self.screen, self.back_ground_color, self.container_bar)
		pygame.draw.rect(self.screen, self.color, self.value_bar)

