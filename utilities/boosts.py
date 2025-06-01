from .constants import *


class Boost:
	def __init__(self, screen, x, y, image):
		self.screen = screen
		self.x = x
		self.start_y = y

		self.y = self.start_y
		self.image = image

		self.vel_y = BOOST_FLOAT_SPEED

		self.rect = self.image.get_rect()

		self.rect.x = self.x
		self.rect.y = self.y


	def hit_player(self, player):
		return self.rect.colliderect(player.rect) or (abs(self.x - player.x) < player.get_width())

	def update(self, scroll_speed):
		self.x -= scroll_speed
		self.y += self.vel_y

		if self.y >= (self.image.get_height() / 3) + self.start_y:
			self.vel_y = -BOOST_FLOAT_SPEED

		elif self.y <= self.start_y - (self.image.get_height() / 3):
			self.vel_y = BOOST_FLOAT_SPEED

		self.rect = self.image.get_rect()

		self.rect.x = self.x
		self.rect.y = self.y

	def draw(self):
		self.screen.blit(self.image, (self.x, self.y))


