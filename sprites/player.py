
from utilities.constants import *
from utilities.map_generator import Block
import pygame
import math

pygame.init()

class Player:
	def __init__(self, screen, x, y, still_texture, walking_textures, aiming_texture, sitting_shooting_textures=None, lying_player_texture=None, running_textures=None, flip_textures=None, aimed_shooting_textures=None, noaim_shooting_textures=None, hurt_textures=None, death_textures=None, standing_reload_textures=None, sitting_player_texture=None, attack_textures=None):
		self.screen = screen
		self.x = x
		self.y = y
		self.vel_x = 0
		self.vel_y = 0
		self.acc_y = GRAVITY
		self.acc_x = 0

		self.still_texture = still_texture
		self.walking_textures = walking_textures
		self.aiming_texture = aiming_texture
		self.running_textures = running_textures
		self.flip_textures = flip_textures
		self.aimed_shooting_textures = aimed_shooting_textures
		self.noaim_shooting_textures = noaim_shooting_textures
		self.hurt_textures = hurt_textures
		self.death_textures = death_textures
		self.standing_reload_textures = standing_reload_textures
		self.sitting_player_texture = sitting_player_texture
		self.lying_player_texture = lying_player_texture
		self.sitting_shooting_textures = sitting_shooting_textures
		self.attack_textures  = attack_textures

		self.stamina = 1.0
		self.health = 1.0
		self.ticks_since_death = 0
		self.ticks_since_attack = 0


		self.flipped = False
		self.jumping = False
		self.aiming = False
		self.noaim_shooting = False
		self.hurt = False
		self.aimed_shot = False
		self.running = False
		self.standing_reload = False
		self.sitting = False
		self.lying = False
		self.sitting_shot = False
		self.dead = False
		self.sliding = False
		self.attacking = False

		self.in_animation = False
		self.block_standing_on = None
		self.ammo = ROUNDS_IN_MAG

		self.blocks_travelled = 1


		# Indicies representing which stage of the movement animations to play

		self.animation_stages = {"walk": 0, "run": 0, "flip": 0, "aimed_shot": 0, "noaim_shot": 0, "standing_reload": 0, "hurt": 0, "death": 0, "sitting_shot": 0, "attack": 0}

		
		self.current_texture = self.still_texture
		self.rect = self.current_texture.get_rect()

	def get_height(self):
		return self.current_texture.get_height()

	def get_width(self):
		return self.current_texture.get_width()

	def get_rect(self):
		return self.rect


	def change_movement_texture(self, ticks, scroll_speed=None, raining=False, enemy=False):

		# Death

		if (not enemy and self.health <= 0 and ticks % DEATH_ANIMATION_SPEED == 0) or (enemy and self.health <= 0 and ticks % ENEMY_DEATH_ANIMATION_SPEED == 0):
			self.ticks_since_death += 1
			self.vel_x = 0
			self.vel_y = 0
			self.animation_stages["death"] += 1

			if self.ticks_since_death >= 5 * FPS:
				self.dead = True
				return


			# if self.animation_stages["death"] == len(self.death_textures) and self.ticks_since_death < 5 * FPS:
			# 	# self.health = 1.0
			# 	# self.stamina = 1.0
			# 	self.animation_stages["death"] = 0

			# 	# pygame.time.delay(5000)



			if self.death_textures is not None and self.animation_stages["death"] < len(self.death_textures):
				self.current_texture = self.death_textures[self.animation_stages["death"]]





			if self.flipped and not enemy or (not self.flipped and enemy):
				# if not enemy:
				# 	self.current_texture = pygame.transform.flip(self.current_texture, True, False)

				if self.animation_stages["death"] < len(self.death_textures):
					self.current_texture = pygame.transform.flip(self.death_textures[self.animation_stages["death"]], True, False)


			return

		elif self.health <= 0:
			self.ticks_since_death += 1
			return


		# Hurt

		elif not enemy and self.hurt and ticks % HURT_ANIMATION_SPEED == 0 or (enemy and self.hurt and ticks % ENEMY_HURT_ANIMATION_SPEED == 0):
			self.animation_stages["hurt"] += 1

			if self.animation_stages["hurt"] == len(self.hurt_textures):
				self.animation_stages["hurt"] = 0
				self.hurt = False
				self.current_texture = self.still_texture

			else:
				self.current_texture = self.hurt_textures[self.animation_stages["hurt"]]



			if self.flipped:
				self.current_texture = pygame.transform.flip(self.current_texture, True, False)


			if self.sliding:
				self.handle_slide(raining=raining)

			return


		elif self.hurt:
			return


		# Attacking 

		if self.attacking and ticks % ATTACK_ANIMATION_SPEED == 0 and self.stamina >= STAMINA_TO_ATTACK and not self.jumping and self.vel_x == 0:
			self.current_texture = self.attack_textures[self.animation_stages["attack"]]
			if self.animation_stages["attack"] == 0:
				self.ticks_since_attack = 0
				
			self.animation_stages["attack"] += 1

			if self.animation_stages["attack"] >= len(self.attack_textures):
				self.animation_stages["attack"] = 0
				self.attacking = False

			if self.flipped:
				self.current_texture = pygame.transform.flip(self.current_texture, True, False)



			return

		elif self.attacking:
			return

		# Reloading

		if self.standing_reload and ticks % STANDING_RELOAD_ANIMATION_SPEED == 0:
			self.current_texture = self.standing_reload_textures[self.animation_stages["standing_reload"]]
			self.animation_stages["standing_reload"] += 1
			

			if self.animation_stages["standing_reload"] >= len(self.standing_reload_textures):
				self.animation_stages["standing_reload"] = 0
				self.standing_reload = False
				self.ammo = ROUNDS_IN_MAG



			if self.flipped:
				self.current_texture = pygame.transform.flip(self.current_texture, True, False)



			return

		elif self.standing_reload:
			return


		# No aim shooting

		if self.noaim_shooting and ticks % NOAIM_SHOOT_ANIMATION_SPEED == 0:
			self.sitting = False
			self.lying = False
			self.current_texture = self.noaim_shooting_textures[self.animation_stages["noaim_shot"]]
			self.animation_stages["noaim_shot"] += 1


			if self.flipped:
				self.x += RECOIL * 10
				self.current_texture = pygame.transform.flip(self.current_texture, True, False)

			else:
				self.x -= RECOIL * 10


			if self.animation_stages["noaim_shot"] >= len(self.noaim_shooting_textures):
				self.noaim_shooting = False
				self.animation_stages["noaim_shot"] = 0



			return




		# Sitting / lying

		if self.sitting or self.lying:
			if self.sitting:
				self.current_texture = self.sitting_player_texture

				if self.sliding:
					self.handle_slide(scroll_speed=scroll_speed, raining=raining)

				if self.sitting_shot and ticks % SHOOT_ANIMATION_SPEED == 0:
					self.current_texture = self.sitting_shooting_textures[self.animation_stages["sitting_shot"]]

					self.animation_stages["sitting_shot"] += 1

					if self.flipped:
						self.x += RECOIL * 2
						self.current_texture = pygame.transform.flip(self.current_texture, True, False)

					else:
						self.x -= RECOIL * 2

					if self.animation_stages["sitting_shot"] >= len(self.sitting_shooting_textures):
						self.animation_stages["sitting_shot"] = 0
						self.sitting_shot = False



			else:
				self.current_texture = self.lying_player_texture

			if self.flipped:
				self.current_texture = pygame.transform.flip(self.sitting_player_texture, True, False)

			return



		# Aiming

		if self.aiming:
			if self.aiming_texture is not None:
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

			if self.vel_x < 0:
				# if isinstance(self, Enemy):
				self.current_texture = pygame.transform.flip(self.walking_textures[self.animation_stages["walk"]], True, False)
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


			if self.vel_x < 0:
				self.current_texture = pygame.transform.flip(self.walking_textures[self.animation_stages["run"]], True, False)
				self.flipped = True

			else:
				self.flipped = False


		# Flipping

		if self.jumping and self.flip_textures is not None and ticks % FLIP_ANIMATION_SPEED == 0:
			self.current_texture = self.flip_textures[self.animation_stages["flip"]]
			self.animation_stages["flip"] += 1

			if self.animation_stages["flip"] >= len(self.flip_textures):
				self.jumping = False
				print ("not jumping")
				self.animation_stages["flip"] = 0


			if self.flipped:
				self.current_texture = pygame.transform.flip(self.current_texture, True, False)


		self.rect = self.current_texture.get_rect()
		self.ticks_since_attack += 1
		self.rect.x = self.x
		self.rect.y = self.y

	def take_damage(self, bullet=None):
		if bullet is None:
			self.health -= ATTACK_DAMAGE

			return

		if not self.sitting and not self.lying:
			if bullet.y <= (self.y + (self.get_height() // 4)):
				self.health -= HEAD_SHOT_DAMAGE

			elif bullet.y <= (self.y + (self.get_height() // 2)):
				self.health -= BODY_SHOT_DAMAGE

			else:
				self.health -= LEG_SHOT_DAMAGE



		elif self.sitting:
			if bullet.y <= (self.y + (self.get_height() // 3)):
				self.health -= HEAD_SHOT_DAMAGE

			else:
				self.health -= BODY_SHOT_DAMAGE



		else:
			if bullet.y <= (self.y + (self.get_height() // 2)):
				self.health -= HEAD_SHOT_DAMAGE

			else:
				self.health -= BODY_SHOT_DAMAGE


	def handle_slide(self, scroll_speed=None, raining=False):
		# print (self.vel_x)

		if self.vel_x == 0 and scroll_speed is not None:
			self.vel_x = scroll_speed

		if self.vel_x > 0:
			if not raining:
				acc_x = FRICTIONAL_FORCE / PLAYER_MASS

			else:
				acc_x = RAIN_FRICTIONAL_FORCE / PLAYER_MASS

			self.vel_x -= acc_x

			if self.vel_x <= 0:
				self.vel_x = 0
				self.sliding = False
				self.lying = True


		elif self.vel_x < 0:
			if not raining:
				acc_x = FRICTIONAL_FORCE / PLAYER_MASS

			else:
				acc_x = RAIN_FRICTIONAL_FORCE / PLAYER_MASS


			self.vel_x += acc_x

			if self.vel_x >= 0:
				self.vel_x = 0
				self.sliding = False

		elif scroll_speed == 0:
			self.sliding = False



	def on_block(self, block):
		# if self.rect.colliderect(block.block_rect):
		# 	return True

		if self.rect.y > block.block_rect.y:
			return False



		diff_x = abs(block.block_rect.x - self.rect.x)
		diff_y = abs(block.block_rect.y - self.rect.y)

		if self.rect.x > block.block_rect.x:
			width = BLOCK_SIZE

		else:
			width = self.get_width()



		return diff_x <= width and diff_y <= self.get_height() and self.rect.colliderect(block.block_rect)
		# if block.block_rect.x > self.rect.x:
		# return diff_x <= self.get_width() and diff_y <= self.get_height() and self.rect.colliderect(block.block_rect)

	def update(self):

		self.in_animation = False

		for stage in self.animation_stages.values():
			if stage != 0:
				self.in_animation = True
				break


		if self.stamina > 1.0:
			self.stamina = 1.0

		elif self.stamina < 0:
			self.stamina = 0

		if self.health > 1.0:
			self.health = 1.0


		# print (self.vel_y)
		self.vel_y += self.acc_y
		self.x += self.vel_x

		self.y += self.vel_y

		if self.vel_x != 0:
			self.blocks_travelled += self.vel_x / BLOCK_SIZE


		# print (self.y)
		self.rect.x = self.x
		self.rect.y = self.y

	def draw(self):
		self.screen.blit(self.current_texture, (self.x, self.y))




class Bullet:
	def __init__(self, screen, pos, image, flip=False, player_bullet=True):
		self.screen = screen
		self.x, self.y = pos
		self.bullet_img = image
		self.player_bullet = player_bullet

		self.vel_x = 0
		self.vel_y = 0

		self.flip = flip
		if self.flip:
			self.bullet_img = pygame.transform.flip(self.bullet_img, True, False)

		self.rect = None

	def is_player_bullet(self):
		return self.player_bullet

	def set_flipped(self, flip_x, flip_y):
		self.bullet_img = pygame.transform.flip(self.bullet_img, flip_x, flip_y)


	def set_vel(self, mx, my):
		dist_x = abs(mx - self.x)
		dist_y = abs(my - self.y)
		if dist_x == 0:
			self.vel_x = 0
			self.vel_y = BULLET_SPEED

		else:
			angle = (round(math.degrees(math.atan(dist_y/dist_x)), 2))
			# print (angle)

			if abs(angle) <= PLAYER_SHOOT_RANGE or not self.player_bullet:
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

		if not isinstance(entity, Block) and entity.health <= 0:
			return False

		if self.y  + self.rect.height < entity.y:
			return False

		dist_x = self.x - entity.x
		dist_y = self.y - entity.y

		bullet_to_left_of_entity =  self.x < entity.x

		within_range = (abs(dist_x) < entity.get_width()) and (abs(dist_y) < entity.get_height())

		return entity.get_rect().colliderect(self.rect) or (within_range and not bullet_to_left_of_entity) or (within_range and dist_x == 0)
		# return entity.get_rect().colliderect(self.rect) or (abs(self.x - entity.x) < entity.get_width() and abs(self.y - entity.y) < entity.get_height())

	def get_distance(self, entity):
		dx = self.x - entity.x
		dy = self.y - entity.y
		return math.sqrt((dx ** 2) + (dy ** 2))

	def draw(self):
		self.screen.blit(self.bullet_img, (self.x, self.y))
		