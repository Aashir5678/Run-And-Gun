from .player import Player, Bullet
from utilities.map_generator import Block
from utilities.constants import *
from random import randint, uniform
from math import sqrt
import pygame

pygame.init()
GRENADE_TEXTURE = pygame.transform.scale_by(pygame.image.load("Assets//grenade.png"), 0.7)

EXPLOSION_TEXTURES = []

for i in range(1, 10):
	texture = pygame.transform.scale_by(pygame.image.load(f"Assets//enemy_grenade//explosion{str(i)}.png"), 2)
	EXPLOSION_TEXTURES.append(texture)


class Enemy(Player):
	def __init__(self, screen, x, y, still_texture, walking_textures, aiming_texture, running_textures=None, flip_textures=None, aimed_shooting_textures=None, noaim_shooting_textures=None, hurt_textures=None, death_textures=None, standing_reload_textures=None, enemy_grenade_textures=None):
		super().__init__(screen, x, y, still_texture, walking_textures, aiming_texture, running_textures=running_textures, flip_textures=flip_textures, aimed_shooting_textures=aimed_shooting_textures, noaim_shooting_textures=noaim_shooting_textures, hurt_textures=hurt_textures, death_textures=death_textures, standing_reload_textures=None)
		self.shoot_dist = randint(MIN_ENEMY_SHOOT_DIST, MAX_ENEMY_SHOOT_DIST)
		self.enemy_grenade_textures = enemy_grenade_textures


		self.animation_stages["grenade"] = 0
		self.throwing_grenade = False
		self.at_shoot_dist = False
		self.flinged = False
		self.grenade = None

	def follow_player(self, player, ticks, bullet_texture):
		dist_x = player.x - self.x

		if self.flinged or self.hurt or self.health <= 0 or self.dead or self.throwing_grenade:
			return

		# if self.flinged:
		# 	return

		# if dist_x == ENEMY_SHOOT_DIST:
		# 	self.aiming = True
		# 	self.aimed_shot = True



		if (abs(dist_x) >= player.get_width() + self.shoot_dist) or (self.x + self.get_width() + 10 > SCREEN_WIDTH) and player.health > 0:
			self.at_shoot_dist = False
			self.aimed_shot = False

			if dist_x > MAX_ENEMY_SHOOT_DIST:
				self.vel_x = SPRINTING_VEL
				self.running = True

			elif abs(dist_x) > MAX_ENEMY_SHOOT_DIST:
				self.vel_x = -SPRINTING_VEL
				self.running = True


			elif dist_x > 0:
				self.vel_x = WALKING_VEL
				# self.running = False

			else:
				self.vel_x = -WALKING_VEL
				# self.running = False
				# self.flipped = True

		else:
			self.vel_x = 0
			self.at_shoot_dist = True
			self.aiming = True
			self.running = False
			if player.health > 0:
				self.aimed_shot = True

			else:
				self.current_texture = self.aimed_shooting_textures[0]
				self.aimed_shot = False

				if self.flipped:
					self.current_texture = pygame.transform.flip(self.aimed_shooting_textures[0], True, False)

				return None

			if ticks % ENEMY_SHOOTING_COOLDOWN == 0 and player.health > 0:
				bullet = Bullet(self.screen, (self.x, self.y + (self.get_height() // 4)), bullet_texture, flip=self.flipped, player_bullet=False)

				# print (abs(round(self.x - player.x)))
				distance_innaccuracy = abs(round(self.x - player.x)) // 10
				
				if not player.jumping and not player.running:
					innacuarte_x = player.x + randint(-ENEMY_INNACURACY + distance_innaccuracy, ENEMY_INNACURACY + distance_innaccuracy)
					innacuarte_y = player.y + randint(-ENEMY_INNACURACY + distance_innaccuracy, ENEMY_INNACURACY + distance_innaccuracy) # + (player.get_height() / 2) 

				else:
					innacuarte_x = player.x + uniform(-ENEMY_INNACURACY * 1.5, ENEMY_INNACURACY * 1.5)
					innacuarte_y = player.y + (player.get_height() / 2) + uniform(-ENEMY_INNACURACY * 1.5, ENEMY_INNACURACY * 1.5)

				valid_bullet = bullet.set_vel(innacuarte_x, innacuarte_y)


				if valid_bullet:
					return bullet 

	def fling(self, player):
		# if self.health <= 0:
		# 	self.flinged = False
		# 	return

		self.flinged = True
		self.initial_x = self.x
		self.initial_y = self.y
		if self.health > 0:
			self.current_texture = self.still_texture


			if self.flipped:
				self.current_texture = pygame.transform.flip(self.still_texture, True, False)

		# else:
		# 	self.current_texture = self.still_texture

		if self.x < player.x:
			self.vel_x = uniform(-BLOCK_SIZE * FLING_CONSTANT, 0)

		else:
			self.vel_x = uniform(0, BLOCK_SIZE * FLING_CONSTANT)


		self.vel_y = -BLOCK_SIZE * FLING_CONSTANT



	def change_movement_texture(self, player, ticks):
		if self.flinged and self.health > 0:
			return

		super().change_movement_texture(ticks, enemy=True)



		if self.hurt or self.dead or self.health <= 0:
			return


		if self.throwing_grenade and ticks % ENEMY_GRENADE_ANIMATION_SPEED == 0:
			self.aiming = False
			self.vel_x = 0

			self.current_texture = self.enemy_grenade_textures[self.animation_stages["grenade"]]


			self.animation_stages["grenade"] += 1

			if self.animation_stages["grenade"] >= len(self.enemy_grenade_textures):
				self.animation_stages["grenade"] = 0
				self.throwing_grenade = False

			elif self.animation_stages["grenade"] == 7:
				self.grenade = Grenade(self.screen, self)
				self.grenade.find_trajectory(player)

			if self.x > player.x + player.get_width():
				self.flipped = True
				self.current_texture = pygame.transform.flip(self.enemy_grenade_textures[self.animation_stages["grenade"]], True, False)

			else:
				self.flipped = False
				self.current_texture = self.enemy_grenade_textures[self.animation_stages["grenade"]]


		elif self.throwing_grenade:
			return

		if self.aiming and self.vel_x == 0:
			if self.aiming_texture is not None:
				self.current_texture = self.aiming_texture

			if self.aimed_shot and ticks % ENEMY_SHOOT_ANIMATION_SPEED == 0 and player.health > 0:
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


			# self.vel_x = 0



			if self.x > player.x + player.get_width() - ATTACK_RANGE:
				self.flipped = True
				self.current_texture = pygame.transform.flip(self.aimed_shooting_textures[self.animation_stages["aimed_shot"]], True, False)

			else:
				self.flipped = False
				self.current_texture = self.aimed_shooting_textures[self.animation_stages["aimed_shot"]]





		# self.rect.x = self.x
		# self.rect.y = self.y

		# 

	def update(self, ticks):
		super().update()

		if self.grenade is not None:
			still_exploding = self.grenade.update(ticks)

			if not still_exploding:
				self.grenade = None


	def draw(self):
		super().draw()

		if self.grenade is not None:
			self.grenade.draw()




class Grenade:
	def __init__(self, screen, user):
		self.screen = screen
		self.x = user.x
		self.y = user.y
		self.vel_x = 0
		self.vel_y = 0
		self.explode = False
		self.damaged_player = False

		self.user = user
		self.current_texture = GRENADE_TEXTURE
		self.explosion_textures = EXPLOSION_TEXTURES
		self.explosion_index = 0
		self.rect = self.current_texture.get_rect()

	def get_height(self):
		return self.current_texture.get_height()

	def find_trajectory(self, player):

		time = randint(FPS // 2, FPS * 2)
		x = player.x

		if player.x > 0:
			x += randint(0, ENEMY_GRENADE_INNACURACY)

		elif player.x < 0:
			x += player.x + randint(-ENEMY_GRENADE_INNACURACY, 0)



		self.vel_x = (x - self.x) / time

		self.vel_y = (((player.y - self.y) / time) - 0.5 * GRAVITY * time)



	def hit_entity(self, entity):
		if isinstance(entity, Player) and entity.health <= 0:
			return False

		to_right_of_entity = self.x > entity.x
		dist_x = abs(self.x - entity.x)
		dist_y = abs(self.y - entity.y)

		return ((to_right_of_entity and dist_x <= entity.get_width()) or (dist_x <= self.current_texture.get_width())) and dist_y <= self.current_texture.get_height()

	def distance_from_entity(self, entity):
		dist_x = abs(self.x - entity.x)
		dist_y = abs(self.y - entity.y)

		euclid_dist = sqrt(dist_x ** 2 + dist_y ** 2)
		return euclid_dist


	def update(self, ticks):
		# print (self.x)
		# print (self.y)
		if not self.explode:
			self.vel_y += GRAVITY
			self.x += self.vel_x
			self.y += self.vel_y


		elif ticks % EXPLODE_ANIMATION_SPEED == 0 and self.explode:
			self.current_texture = self.explosion_textures[self.explosion_index]

			self.explosion_index += 1

			if self.explosion_index >= len(self.explosion_textures):
				self.explosion_index = 0
				self.explode = False

				return False



		return True


	def draw(self):
		self.screen.blit(self.current_texture, (self.x, self.y))

		# if self.grenade is not None:
		# 	self.screen.blit(self.grenade.current_texture, (self.grenade.x, self.grenade.y))