
from constants import *
import pygame
import math

pygame.init()

class Player:
	def __init__(self, screen, x, y, still_texture, walking_textures, aiming_texture, running_textures=None, flip_textures=None, aimed_shooting_textures=None, noaim_shooting_textures=None, hurt_textures=None, death_textures=None):
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
		self.noaim_shooting_textures = noaim_shooting_textures
		self.hurt_textures = hurt_textures
		self.death_textures = death_textures

		self.stamina = 1.0
		self.health = 1.0


		self.flipped = False
		self.direction = "right"
		self.jumping = False
		self.aiming = False
		self.noaim_shooting = False
		self.hurt = False
		self.aimed_shot = False
		self.running = False
		self.ammo = ROUNDS_IN_MAG


		# Indicies representing which stage of the movement animations to play

		# self.walk_index = 0
		# self.run_index = 0
		# self.flip_index = 0
		# self.aimed_shot_index = 0
		# self.hurt_index = -1
		# self.death_index = -1

		self.animation_stages = {"walk": 0, "run": 0, "flip": 0, "aimed_shot": 0, "noaim_shot": 0, "hurt": 0, "death": 0}

		
		self.current_texture = self.still_texture
		self.rect = self.current_texture.get_rect()

	def get_height(self):
		return self.current_texture.get_height()


	def change_movement_texture(self, ticks):

		# Death
		if self.health <= 0 and ticks % DEATH_ANIMATION_SPEED == 0:
			self.animation_stages["death"] += 1


			if self.animation_stages["death"] == len(self.death_textures):
				self.health = 1.0
				self.animation_stages["death"] = 0
				self.stamina = 1.0

				pygame.time.delay(2000)

			else:
				self.current_texture = self.death_textures[self.animation_stages["death"]]



			if self.flipped:
				self.current_texture = pygame.transform.flip(self.current_texture, True, False)


			return

		elif self.health <= 0:
			return


		# Hurt

		elif self.hurt and ticks % HURT_ANIMATION_SPEED == 0:
			self.animation_stages["hurt"] += 1

			if self.animation_stages["hurt"] == len(self.hurt_textures):
				self.animation_stages["hurt"] = 0
				self.hurt = False

			else:
				self.current_texture = self.hurt_textures[self.animation_stages["hurt"]]



			if self.flipped:
				self.current_texture = pygame.transform.flip(self.current_texture, True, False)


			return

		elif self.hurt:
			return


		# No aim shooting

		if self.noaim_shooting and ticks % NOAIM_SHOOT_ANIMATION_SPEED == 0:
			self.current_texture = self.noaim_shooting_textures[self.animation_stages["noaim_shot"]]

			self.animation_stages["noaim_shot"] += 1


			if self.flipped:
				self.x += RECOIL * 10

			else:
				self.x -= RECOIL * 10

			self.rect.x = self.x

			if self.animation_stages["noaim_shot"] >= len(self.noaim_shooting_textures):
				self.noaim_shooting = False
				self.animation_stages["noaim_shot"] = 0



			if self.flipped:
				self.current_texture = pygame.transform.flip(self.current_texture, True, False)


			return


		# Aiming

		if self.aiming:
			self.current_texture = self.aiming_texture

			if self.aimed_shot and ticks % SHOOT_ANIMATION_SPEED == 0:
				self.current_texture = self.aimed_shooting_textures[self.animation_stages["aimed_shot"]]

				self.animation_stages["aimed_shot"] += 1


				if self.flipped:
					self.x += RECOIL * 5

				else:
					self.x -= RECOIL * 5

				self.rect.x = self.x

				if self.animation_stages["aimed_shot"] >= len(self.aimed_shooting_textures):
					self.aimed_shot = False
					self.animation_stages["aimed_shot"] = 0



			if self.flipped:
				self.current_texture = pygame.transform.flip(self.current_texture, True, False)


			return

		# Walking

		if self.vel_x != 0 and not self.running and ticks % WALK_ANIMATION_SPEED == 0 and not self.jumping:
			self.stamina -= STAMINA_TO_WALK

			self.animation_stages["walk"] += 1

			if self.animation_stages["walk"] >= len(self.walking_textures):
				self.animation_stages["walk"] = 0

			self.current_texture = self.walking_textures[self.animation_stages["walk"]]

			# Flip texture if walking backwards

			if self.direction == "right" and self.vel_x < 0:
				self.current_texture = pygame.transform.flip(self.current_texture, True, False)
				self.flipped = True

			else:
				self.flipped = False


		elif self.vel_x == 0 and not self.jumping:
			self.animation_stages["walk"] = 0
			self.current_texture = self.still_texture


			if self.flipped:
				self.current_texture = pygame.transform.flip(self.current_texture, True, False)



		# Running

		if self.vel_x != 0 and self.running and ticks % SPRINT_ANIMATION_SPEED == 0 and not self.jumping:
			self.stamina -= STAMINA_TO_RUN
			self.animation_stages["run"] += 1

			if self.animation_stages["run"] >= len(self.running_textures):
				self.animation_stages["run"] = 0

			self.current_texture = self.running_textures[self.animation_stages["run"]]


			if self.direction == "right" and self.vel_x < 0:
				self.current_texture = pygame.transform.flip(self.current_texture, True, False)
				self.flipped = True

			else:
				self.flipped = False


		# Flipping

		if self.jumping and self.flip_textures is not None and ticks % FLIP_ANIMATION_SPEED == 0:
			self.current_texture = self.flip_textures[self.animation_stages["flip"]]
			self.animation_stages["flip"] += 1

			if self.animation_stages["flip"] >= len(self.flip_textures):
				self.jumping = False
				self.animation_stages["flip"] = 0


			if self.flipped:
				self.current_texture = pygame.transform.flip(self.current_texture, True, False)




		self.rect = self.current_texture.get_rect()

		self.rect.x = self.x
		self.rect.y = self.y



	def on_block(self, block):

		return self.rect.colliderect(block.block_rect)

	def update(self):


		if self.stamina > 1.0:
			self.stamina = 1.0

		elif self.stamina < 0:
			self.stamina = 0

		if self.health > 1.0:
			self.health = 1.0


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

		self.rect = None

	def set_vel(self, mx, my):
		dist_x = abs(mx - self.x)
		dist_y = abs(my - self.y)
		if dist_x == 0:
			self.vel_x = 0
			self.vel_y = BULLET_SPEED

		else:
			angle = (round(math.degrees(math.atan(dist_y/dist_x)), 2))
			# print (angle)

			if abs(angle) <= 20:
				if mx < self.x:
					self.vel_x =  math.cos(math.radians(angle)) * BULLET_SPEED * -1

				else:
					self.vel_x = math.cos(math.radians(angle)) * BULLET_SPEED

				if my < self.y:
					self.vel_y = math.sin(math.radians(angle)) * BULLET_SPEED * -1

				else:
					self.vel_y = math.sin(math.radians(angle)) * BULLET_SPEED


			else:
				return False

		self.rect = self.bullet_img.get_rect()
		self.rect.x = self.x
		self.rect.y = self.y

		return True



	def update(self):
		self.x += self.vel_x
		self.y += self.vel_y

		self.rect.x = self.x
		self.rect.y = self.y


	def hit_entity(self, entity):
		return entity.get_rect().colliderect(self.rect)

	def draw(self):
		self.screen.blit(self.bullet_img, (self.x, self.y))