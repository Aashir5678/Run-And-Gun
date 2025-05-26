
from constants import *
import pygame
import math

pygame.init()

class Player:
	def __init__(self, screen, x, y, still_texture, walking_textures, aiming_texture, running_textures=None, flip_textures=None, aimed_shooting_textures=None):
		self.screen = screen
		self.x = x
		self.y = y
		self.vel_x = 0
		self.vel_y = 0
		self.acc_y = GRAVITY

		self.still_texture = still_texture
		self.walking_textures = walking_textures
		self.aiming_texture = aiming_texture
		self.running_textures = running_textures
		self.flip_textures = flip_textures
		self.aimed_shooting_textures = aimed_shooting_textures

		self.stamina = 1.0


		self.flipped = False
		self.direction = "right"
		self.jumping = False
		self.aiming = False
		self.aimed_shot = False
		self.running = False

		self.walk_index = 0
		self.run_index = 0
		self.flip_index = 0
		self.aimed_shot_index = 0

		
		self.current_texture = self.still_texture
		self.rect = self.current_texture.get_rect()

	def get_height(self):
		return self.current_texture.get_height()


	def change_movement_texture(self, ticks):

		# Aiming

		if self.aiming:
			self.current_texture = self.aiming_texture

			if self.aimed_shot and ticks % SHOOT_ANIMATION_SPEED == 0:
				self.current_texture  = self.aimed_shooting_textures[self.aimed_shot_index]
				self.aimed_shot_index += 1

				if self.aimed_shot_index >= len(self.aimed_shooting_textures):
					self.aimed_shot = False
					self.aimed_shot_index = 0



			if self.flipped:
				self.current_texture = pygame.transform.flip(self.current_texture, True, False)


			return

		# Walking

		if self.vel_x != 0 and not self.running and ticks % WALK_ANIMATION_SPEED == 0 and not self.jumping:
			self.stamina -= STAMINA_TO_WALK
			self.walk_index += 1

			if self.walk_index >= len(self.walking_textures):
				self.walk_index = 0

			elif self.walk_index < 0:
				self.walk_index = len(self.walking_textures) - 1


			self.current_texture = self.walking_textures[self.walk_index]


			# Flip texture if walking backwards

			if self.direction == "right" and self.vel_x < 0:
				self.current_texture = pygame.transform.flip(self.current_texture, True, False)
				self.flipped = True

			else:
				self.flipped = False


		elif self.vel_x == 0 and not self.jumping:
			self.walk_index = 0
			self.current_texture = self.still_texture


			if self.flipped:
				self.current_texture = pygame.transform.flip(self.current_texture, True, False)



		# Running

		if self.vel_x != 0 and self.running and ticks % SPRINT_ANIMATION_SPEED == 0 and not self.jumping:
			self.stamina -= STAMINA_TO_RUN

			self.run_index += 1

			if self.run_index >= len(self.running_textures):
				self.run_index = 0

			elif self.run_index < 0:
				self.run_index = len(self.running_textures) - 1

			self.current_texture = self.running_textures[self.run_index]

			if self.direction == "right" and self.vel_x < 0:
				self.current_texture = pygame.transform.flip(self.current_texture, True, False)
				self.flipped = True

			else:
				self.flipped = False


		# Flipping

		if self.jumping and self.flip_textures is not None and ticks % FLIP_ANIMATION_SPEED == 0:
			self.current_texture = self.flip_textures[self.flip_index]

			self.flip_index += 1

			if self.flip_index >= len(self.flip_textures):
				self.jumping = False
				self.flip_index = 0


			if self.flipped:
				self.current_texture = pygame.transform.flip(self.current_texture, True, False)




		self.rect = self.current_texture.get_rect()

		self.rect.x = self.x
		self.rect.y = self.y



	def on_block(self, block):

		return self.rect.colliderect(block.block_rect)
		# if self.vel_x == 0:
		# 	return self.still_texture.get_rect().colliderect(block.block_rect)

		# elif not self.running:
		# 	return self.walking_textures[self.walk_index].get_rect().colliderect(block.block_rect)

		# return (abs(block.x - self.x) < BLOCK_SIZE and abs(self.y + BLOCK_SIZE - block.y) <= BLOCK_SIZE + 0.5)

	def update(self):


		if self.stamina > 1.0:
			self.stamina = 1.0

		elif self.stamina < 0:
			self.stamina = 0

		self.vel_y += self.acc_y
		self.x += self.vel_x

		self.y += self.vel_y

		self.rect.x = self.x
		self.rect.y = self.y

	def draw(self):

		self.screen.blit(self.current_texture, (self.x, self.y))




class Bullet:
	def __init__(self, screen, pos, image, flip=False):
		self.screen = screen
		self.x, self.y = pos
		self.bullet_img = image

		self.vel_x = 0
		self.vel_y = 0

		if flip:
			self.bullet_img = pygame.transform.flip(self.bullet_img, True, False)

	def set_vel(self, mx, my):
		dist_x = abs(mx - self.x)
		dist_y = abs(my - self.y)
		if dist_x == 0:
			self.vel_x = 0
			self.vel_y = BULLET_SPEED

		else:
			angle = abs(round(math.degrees(math.atan(dist_y/dist_x)), 2))

			# if mx > self.x:
			# 	angle = 90 + (90 - angle)

			# if my < self.y:
			# 	angle = 180 + (180 - angle)

			self.vel_x = math.cos(math.radians(angle)) * BULLET_SPEED

			self.vel_y = math.sin(math.radians(angle)) * BULLET_SPEED



	def update(self):
		self.x += self.vel_x
		self.y += self.vel_y

	def draw(self):
		self.screen.blit(self.bullet_img, (self.x, self.y))