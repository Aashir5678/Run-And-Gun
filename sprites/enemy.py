from .player import Player, Bullet
from utilities.constants import *
from random import randint, uniform
import pygame

pygame.init()


class Enemy(Player):
	def __init__(self, screen, x, y, still_texture, walking_textures, aiming_texture, running_textures=None, flip_textures=None, aimed_shooting_textures=None, noaim_shooting_textures=None, hurt_textures=None, death_textures=None, standing_reload_textures=None):
		super().__init__(screen, x, y, still_texture, walking_textures, aiming_texture, running_textures=running_textures, flip_textures=flip_textures, aimed_shooting_textures=aimed_shooting_textures, noaim_shooting_textures=noaim_shooting_textures, hurt_textures=None, death_textures=death_textures, standing_reload_textures=None)
		self.shoot_dist = randint(MIN_ENEMY_SHOOT_DIST, MAX_ENEMY_SHOOT_DIST)
		self.at_shoot_dist = False
		self.flinged = False

	def follow_player(self, player, ticks, bullet_texture):
		dist_x = player.x - self.x

		if self.flinged:
			return

		# if self.flinged:
		# 	return

		# if dist_x == ENEMY_SHOOT_DIST:
		# 	self.aiming = True
		# 	self.aimed_shot = True



		if (abs(dist_x) >= player.get_width() + self.shoot_dist) or (self.x + self.get_width() + 10 > SCREEN_WIDTH):
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
			self.aimed_shot = True

			if ticks % ENEMY_SHOOTING_COOLDOWN == 0:
				bullet = Bullet(self.screen, (self.x, self.y + (self.get_height() // 4)), bullet_texture, flip=self.flipped, player_bullet=False)

				# print (abs(round(self.x - player.x)))
				distance_innaccuracy = abs(round(self.x - player.x)) // 10
				
				if not player.jumping and not player.running:
					innacuarte_x = player.x + randint(-ENEMY_INNACURACY + distance_innaccuracy, ENEMY_INNACURACY + distance_innaccuracy)
					innacuarte_y = player.y + (player.get_height() / 2) + randint(-ENEMY_INNACURACY + distance_innaccuracy, ENEMY_INNACURACY + distance_innaccuracy)

				else:
					innacuarte_x = player.x + uniform(-ENEMY_INNACURACY * 1.5, ENEMY_INNACURACY * 1.5)
					innacuarte_y = player.y + (player.get_height() / 2) + uniform(-ENEMY_INNACURACY * 1.5, ENEMY_INNACURACY * 1.5)

				valid_bullet = bullet.set_vel(innacuarte_x, innacuarte_y)


				if valid_bullet:
					return bullet 

	def fling(self, player):
		self.flinged = True
		self.initial_x = self.x
		self.initial_y = self.y
		self.current_texture = self.still_texture

		if self.flipped:
			self.current_texture = pygame.transform.flip(self.current_texture, True, False)

		if self.x < player.x:
			self.vel_x = uniform(-BLOCK_SIZE * FLING_CONSTANT, 0)

		else:
			self.vel_x = uniform(0, BLOCK_SIZE * FLING_CONSTANT)


		self.vel_y = -BLOCK_SIZE * FLING_CONSTANT



	def change_movement_texture(self, player, ticks):
		if self.flinged:
			return

		super().change_movement_texture(ticks)


		if self.aiming and self.vel_x == 0:
			if self.aiming_texture is not None:
				self.current_texture = self.aiming_texture

			if self.aimed_shot and ticks % ENEMY_SHOOT_ANIMATION_SPEED == 0:
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



			if self.x > player.x:
				self.flipped = True
				self.current_texture = pygame.transform.flip(self.aimed_shooting_textures[self.animation_stages["aimed_shot"]], True, False)

			else:
				self.flipped = False
				self.current_texture = self.aimed_shooting_textures[self.animation_stages["aimed_shot"]]


		# self.rect.x = self.x
		# self.rect.y = self.y

		# 
