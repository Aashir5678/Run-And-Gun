from .player import Player, Bullet
from utilities.constants import *
from random import randint
import pygame

pygame.init()


class Enemy(Player):
	def __init__(self, screen, x, y, still_texture, walking_textures, aiming_texture, running_textures=None, flip_textures=None, aimed_shooting_textures=None, noaim_shooting_textures=None, hurt_textures=None, death_textures=None, standing_reload_textures=None):
		super().__init__(screen, x, y, still_texture, walking_textures, aiming_texture, running_textures=running_textures, flip_textures=flip_textures, aimed_shooting_textures=aimed_shooting_textures, noaim_shooting_textures=noaim_shooting_textures, hurt_textures=None, death_textures=death_textures, standing_reload_textures=None)


	def follow_player(self, player, ticks, bullet_texture):
		dist_x = player.x - self.x

		# if dist_x == ENEMY_SHOOT_DIST:
		# 	self.aiming = True
		# 	self.aimed_shot = True


		if abs(dist_x) > self.get_width() + player.get_width() + ENEMY_SHOOT_DIST:
			if dist_x > 0:
				self.vel_x = WALKING_VEL

			else:
				self.vel_x = -WALKING_VEL
			
				# self.flipped = True

		else:
			self.vel_x = 0

			self.aiming = True
			self.aimed_shot = True

			if ticks % ENEMY_SHOOTING_COOLDOWN == 0:
				bullet = Bullet(self.screen, (self.x, self.y + (self.get_height() // 4)), bullet_texture, flip=self.flipped, player_bullet=False)

				
				innacuarte_x = player.x + randint(-ENEMY_INNACURACY, ENEMY_INNACURACY)
				innacuarte_y = player.y + randint(-ENEMY_INNACURACY, ENEMY_INNACURACY)

				valid_bullet = bullet.set_vel(innacuarte_x, innacuarte_y)


				if player.direction == self.direction:
					if player.direction == "left":
						self.direction = "right"

					else:
						self.direction = "left"


					self.flipped = True

				else:
					self.flipped = False
				# if bullet.vel_x < 0 and valid_bullet:
				# 	self.flipped = True

				# elif bullet.vel_x > 0 and valid_bullet:
				# 	self.flipped = False

				
				if valid_bullet:
					return bullet 

			# if self.flipped:
			# 	self.current_texture = pygame.transform.flip(self.current_texture, True, False)
			# 	# self.flipped = False