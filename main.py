import pygame
from random import randint, choice
from math import sqrt
from sprites.player import Player, Bullet
from sprites.enemy import *
from utilities.map_generator import *
from utilities.constants import *
from utilities.asset_loader import *
from utilities.stat_bars import Bar
from utilities.boosts import Boost
from utilities.weather_control import Weather
from title_screen import title_screen



"""
Sprites: https://craftpix.net/freebies/free-pixel-prototype-character-sprites-for-shooter/
"""


pygame.init()
pygame.mixer.init()





def main(seed=None):
	
	run = True
	screen = pygame.display.set_mode(SCREEN_SIZE)

	# Load assets



	# still_player_texture, sitting_player_texture, lying_player_texture, walking_textures, running_textures, aim_texture, aimed_shooting_textures, attack_textures, sitting_shoot, standing_reload_textures, no_aim_shooting_textures, bullet_texture, empty_bullet_texture, flip_textures = load_player_assets()
	hurt_textures, death_textures = load_player_hurt_assets()
	heart_texture, stamina_texture = load_boost_textures()
	single_shot_sfx, reload_sfx, rain_sfx = load_sfx()

	still_player_texture, sitting_player_texture, lying_player_texture = load_player_still_assets()
	walking_textures, running_textures, flip_textures = load_player_movement_assets()
	aim_texture, aimed_shooting_textures, attack_textures,  sitting_shooting_textures, standing_reload_textures, no_aim_shooting_textures = load_player_offense_assets()
	bullet_texture, empty_bullet_texture =  load_bullet_assets()

	prev_vol = 1.0
	volume = 1.0

	gun_channel = pygame.mixer.Channel(0)
	music_channel = pygame.mixer.Channel(1)

	gun_channel.set_volume(GUN_MAX_VOLUME * volume)

	health_bar = Bar(screen, (20, 40), HEALTH_RED, back_ground_color=(40, 3, 3))
	stamina_bar = Bar(screen, (20, 80), STAMINA_YELLOW, back_ground_color=(88, 94, 4))
	sound_bar = Bar(screen, (SCREEN_WIDTH -  50, (SCREEN_HEIGHT // 2) - (SCREEN_HEIGHT // 4)), DARK_BLUE, orientation="vertical")

	ammo_texture = pygame.transform.scale_by(pygame.transform.rotate(bullet_texture, 90), 3)
	empty_ammo_texture = pygame.transform.scale_by(pygame.transform.rotate(empty_bullet_texture, 90), 3)

	enemy_standing_texture, enemy_walking_textures, enemy_running_textures, enemy_standing_shooting_textures, enemy_hurt_textures, enemy_dead_textures, enemy_grenade_textures = load_enemy_assets()
	# print (len(enemy_walking_textures))
	bullets = []

	enemies = []
	# health_boosts = []
	# stamina_boosts = []

	boosts = []
	difficulty = 0
	enemies_killed = 0

	rain_freq = 10
	rain_speed = 20
	# rain = generate_rain(screen, rain_speed, rain_freq)
	weather = Weather(screen, SKY_BLUE)

	# enemies = [Enemy(screen, SCREEN_WIDTH * 3 // 4, 0, enemy_standing_texture, enemy_walking_textures, None)]


	if seed is None:
		seed = randint(-9999, 9999)

	noise_num = 0
	scroll_speed = 0

	surface_blocks, blocks = generate_new_terrain(screen, noise_num, seed, HEIGHT_FACTOR)
	clock = pygame.time.Clock()
	ticks = 0
	grenade = None


	player = Player(screen, 0, surface_blocks[0].y - still_player_texture.get_height(), still_player_texture, walking_textures, aim_texture, sitting_shooting_textures=sitting_shooting_textures, lying_player_texture=lying_player_texture, sitting_player_texture=sitting_player_texture, flip_textures=flip_textures, running_textures=running_textures, aimed_shooting_textures=aimed_shooting_textures, hurt_textures=hurt_textures, death_textures=death_textures, noaim_shooting_textures=no_aim_shooting_textures, standing_reload_textures=standing_reload_textures, attack_textures=attack_textures)
	print (f"Seed: {str(seed)}")


	fps_sum = []


	while run:
		# if not music_channel.get_busy():
		# 	music_channel.queue(song)
		# print (int(player.blocks_travelled))
		clock.tick(FPS)

		player.blocks_travelled += scroll_speed / BLOCK_SIZE

		ticks += 1
		draw_background(screen, player, ticks, scroll_speed, weather)

		pygame.display.set_caption(str(round(clock.get_fps())))


		fps_sum.append(clock.get_fps())
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False
				break

			elif event.type == pygame.MOUSEWHEEL:
				if event.y > 0 and volume < 1.0:
					prev_vol = volume
					volume += 0.05
					sound_bar.set_value(volume)
					gun_channel.set_volume(volume * GUN_MAX_VOLUME)
					weather.adjust_volume(volume)

				elif event.y < 0 and volume > 0:
					prev_vol = volume
					volume -= 0.05

					sound_bar.set_value(volume)
					gun_channel.set_volume(volume * GUN_MAX_VOLUME)
					weather.adjust_volume(volume)


		keys = pygame.key.get_pressed()
		if player.health > 0 and not player.noaim_shooting:
			handle_movement(keys, player, ticks)

			if keys[pygame.K_r] and reload_sfx is not None and player.ammo < ROUNDS_IN_MAG:
				gun_channel.play(reload_sfx)

			elif keys[pygame.K_m] and volume > 0 and ticks % 5 == 0:
				prev_vol = volume
				volume = 0
				sound_bar.set_value(volume)
				gun_channel.set_volume(volume * GUN_MAX_VOLUME)
				weather.adjust_volume(volume)

			elif keys[pygame.K_m] and volume == 0 and ticks % 5 == 0:
				volume = prev_vol
				sound_bar.set_value(volume)
				gun_channel.set_volume(volume * GUN_MAX_VOLUME)
				weather.adjust_volume(volume)






		for block in surface_blocks:
			spawn_health_boost = randint(0, HEALTH_BOOST_SPAWN_RATE) #   + int(difficulty * DIFFICULTY_MULTIPLIER)
			spawn_stamina_boost = randint(0, STAMINA_BOOST_SPAWN_RATE) # + int(difficulty * DIFFICULTY_MULTIPLIER)

			if spawn_health_boost == 0 and player.health < 1.0 and len(boosts) < 10:
				health = Boost(screen, block.x, block.y - (heart_texture.get_height() * 4 / 3), heart_texture, "health")
				boosts.append(health)

			if spawn_stamina_boost == 0 and player.stamina < 1.0 and len(boosts) < 10:
				stamina = Boost(screen, block.x, block.y - (stamina_texture.get_height() * 4 / 3), stamina_texture, "stamina")
				boosts.append(stamina)



		for index, block in enumerate(blocks):
			
			# if player.health > 0:
			
			if block.x >= -BLOCK_SIZE and block.x <= SCREEN_WIDTH:
				block.draw()

			block.x -= scroll_speed
			block.block_rect.x = block.x

			if block.x < -SPRINTING_VEL * BLOCK_SIZE:
				blocks.remove(block)
				if block in surface_blocks:
					surface_blocks.remove(block)




			# Prevents player from sinking in to the floor
			if (player.on_block(block) and (player.vel_y) > 0) or (abs(player.x - block.x) <= BLOCK_SIZE and abs(player.y - block.y) < player.get_height()) and block in surface_blocks and not player.jumping:
				player.y = block.y - player.get_height() # + 1
				player.vel_y = 0
				player.block_standing_on = block


				# if player.jumping and (player.animation_stages["flip"] != 0 and player.animation_stages["flip"] != len(player.flip_textures) - 1):
				# 	player.health = 0

				# player.jumping = False

				# player.animation_stages["flip"] = 0


				if player.vel_x == 0 and not player.in_animation:
					player.current_texture = player.still_texture
					player.animation_stages["walk"] = 0
					player.animation_stages["run"] = 0



			for bullet in bullets:
				if bullet.hit_entity(block):
					bullets.remove(bullet)
					break



			for enemy in enemies:
				if (enemy.on_block(block) and enemy.vel_y > 0) or (abs(enemy.x - block.x) <= BLOCK_SIZE and abs(enemy.y - block.y) < enemy.get_height()) and block in surface_blocks:
					enemy.y = block.y - enemy.get_height() + 1
					enemy.vel_y = 0
					if (enemy.flinged or not enemy.flipped) and enemy.health > 0:
						enemy.flinged = False
						enemy.at_shoot_dist = True
						enemy.vel_x = 0
						enemy.shoot_dist = enemy.x


					# enemy.acc_y = 0


					if enemy.vel_x == 0 and not enemy.in_animation:
						enemy.current_texture = enemy.still_texture
						enemy.animation_stages["walk"] = 0
						enemy.animation_stages["run"] = 0




		for i, bullet in enumerate(bullets):
			if bullet.x > SCREEN_WIDTH or bullet.x < 0 or bullet.y > SCREEN_HEIGHT or bullet.y < 0:
				bullets.pop(i)
				break

			elif bullet.hit_entity(player) and not bullet.is_player_bullet():
				if not player.sitting and not player.lying and not player.sliding:
					player.hurt = True

				player.take_damage(weapon=bullet)
				bullets.remove(bullet)


			for enemy in enemies:

				if bullet.hit_entity(enemy) and bullet.is_player_bullet():
					# enemies.remove(enemy)

					enemy.take_damage(weapon=bullet)
					enemy.hurt = True

					bullets.remove(bullet)
					break


				# Enemies advance on player if the player is camping behind a hill or if enemy has an ineffective shooting spot
				elif not bullet.is_player_bullet() and bullet.get_distance(player) > player.get_height() / 2 and enemy.at_shoot_dist:
					enemy.aimed_shot = False
					enemy.at_shoot_dist = False
					enemy.aiming = False

					if enemy.shoot_dist > enemy.get_width() + player.get_width() and player.health > 0:
						enemy.shoot_dist -= randint(0, abs(round(enemy.x - player.x - player.get_width())))


				
			bullet.update()
			bullet.draw()
		




		mx, my = pygame.mouse.get_pos()

		
		if pygame.mouse.get_pressed()[2] and pygame.mouse.get_pressed()[0] and ticks % SHOOTING_COOLDOWN == 0 and player.ammo > 0 and not player.jumping and not player.hurt and player.health > 0:

			if player.sitting:
				player.sitting_shot = True

			elif player.lying:
				pass

			else:
				player.aiming = True
				player.aimed_shot = True

			
			bullet = Bullet(screen, (player.x, player.y + (player.get_height() // 4)), bullet_texture, flip=player.flipped)

			if not player.sitting:
				mx += randint(-AIMED_ACCURACY, AIMED_ACCURACY)
				my += randint(-AIMED_ACCURACY, AIMED_ACCURACY)

			valid_bullet = bullet.set_vel(mx, my)

			if bullet.vel_x < 0 and valid_bullet:
				player.flipped = True

			elif bullet.vel_x > 0 and valid_bullet:
				player.flipped = False


			if valid_bullet:
				player.ammo -= 1
				bullets.append(bullet)

				gun_channel.play(single_shot_sfx)

				# Make enemies in range start shooting if player is shooting
				for enemy in enemies:
					if abs(enemy.x - player.x) < MAX_ENEMY_SHOOT_DIST:
						enemy.aiming = True
						enemy.aimed_shot = True
						enemy.at_shoot_dist = True
						if not enemy.flinged:
							enemy.vel_x = 0

						enemy.shoot_dist = enemy.x


			else:
				player.sitting_shot = False
				player.aimed_shot = False

		elif pygame.mouse.get_pressed()[2] and pygame.mouse.get_pressed()[0] and player.ammo > 0 and not player.jumping and not player.hurt and player.health > 0:
			if player.sitting:
				player.sitting_shot = True

			elif player.lying:
				pass

			else:
				player.aiming = True
				player.aimed_shot = True

				# Make enemies in range start shooting if player is shooting
				for enemy in enemies:
					if abs(enemy.x - player.x) < MAX_ENEMY_SHOOT_DIST:
						enemy.aiming = True
						enemy.aimed_shot = True
						enemy.at_shoot_dist = True
						if not enemy.flinged:
							enemy.vel_x = 0
							
						enemy.shoot_dist = enemy.x

			

		elif pygame.mouse.get_pressed()[2] and not player.jumping and not player.hurt and player.health > 0:
			player.aiming = True

			if mx < player.x and not player.flipped:
				player.flipped = True

			elif mx > player.x and player.flipped:
				player.flipped = False



			# Make enemies in range start shooting if player takes aim
			for enemy in enemies:
				if abs(enemy.x - player.x) < MAX_ENEMY_SHOOT_DIST:
					enemy.aiming = True
					enemy.aimed_shot = True
					enemy.at_shoot_dist = True
					if not enemy.flinged:
						enemy.vel_x = 0
						
					enemy.shoot_dist = enemy.x



		elif pygame.mouse.get_pressed()[0] and not pygame.mouse.get_pressed()[2] and player.ammo > 0 and not player.hurt and not player.jumping and ticks % SHOOTING_COOLDOWN == 0 and player.health > 0:
			player.noaim_shooting = True
			player.sitting = False
			bullet = Bullet(screen, (player.x, player.y + (player.get_height() // 2)), bullet_texture, flip=player.flipped)

			mx += randint(-SPRAY_INNACURACY, SPRAY_INNACURACY)
			my += randint(-SPRAY_INNACURACY, SPRAY_INNACURACY)

			valid_bullet = bullet.set_vel(mx, my)

			if bullet.vel_x < 0 and valid_bullet:
				player.flipped = True

			elif bullet.vel_x > 0 and valid_bullet:
				player.flipped = False


			if valid_bullet:
				player.ammo -= 1
				bullets.append(bullet)

				gun_channel.play(single_shot_sfx)


			else:
				player.noaim_shooting = False


			# Make enemies in range start shooting if player starts spraying
			for enemy in enemies:
				if abs(enemy.x - player.x) < MAX_ENEMY_SHOOT_DIST:
					enemy.aiming = True
					enemy.aimed_shot = True
					enemy.at_shoot_dist = True
					enemy.vel_x = 0
					enemy.shoot_dist = enemy.x



		elif pygame.mouse.get_pressed()[0] and not pygame.mouse.get_pressed()[2] and player.ammo > 0 and not player.jumping and player.health > 0:
			player.noaim_shooting = True

		else:
			player.aiming = False
			player.noaim_shooting = False
			player.aimed_shot = False

		player.change_movement_texture(ticks, scroll_speed=scroll_speed, raining=weather.raining)


		if surface_blocks[-1].x <= SCREEN_WIDTH:
			noise_num += int((SCREEN_WIDTH // BLOCK_SIZE) * RENDER_DISTANCE)
			new_suface_blocks, new_blocks = generate_new_terrain(screen, noise_num, seed, HEIGHT_FACTOR, start_x=SCREEN_WIDTH)

			surface_blocks.extend(new_suface_blocks)
			blocks.extend(new_blocks)

		if player.x > SCREEN_WIDTH // 4 and (player.vel_x > 0):
			scroll_speed = player.vel_x
			player.vel_x = 0


		elif player.x < SCREEN_WIDTH // 4 and player.vel_x < 0 or player.in_animation:
			scroll_speed = 0 # player.vel_x
			# player.vel_x = 0

			if player.x < 0:
				player.vel_x = 0
				player.running = False
				player.x = 0

		else:
			scroll_speed = 0

		if player.y >= SCREEN_HEIGHT:
			player.x = SCREEN_WIDTH // 2
			player.y = 0
			player.health = 1.0
			player.stamina = 1.0


		# Difficulty increases by 1.0 every BLOCKS_TILL_DIFFICULTY_INCREASE blocks travelled

		if player.blocks_travelled / BLOCKS_TILL_DIFFICULTY_INCREASE > difficulty:
			difficulty = player.blocks_travelled / BLOCKS_TILL_DIFFICULTY_INCREASE


		odds = int(ENEMY_SPAWN_RATE - int((difficulty) * DIFFICULTY_MULTIPLIER))



		if odds < MAX_SPAWN_RATE:
			odds = MAX_SPAWN_RATE
		

		if randint(0, odds) == 0 and surface_blocks and len(enemies) < MAX_ENEMIES_AT_ONCE:
			print (f"1 in {str((odds + 1))} chance per frame")

			min_dist_block = None

			for block in surface_blocks:
				dist_x = block.x - player.x
				if dist_x >= MIN_ENEMY_SPAWN_DIST:
					min_dist_block = block
					break

			random_block = choice(surface_blocks[surface_blocks.index(min_dist_block)::])
			

			# if random_block.x > player.x + MIN_ENEMY_SPAWN_DIST and random_block.x < MAX_ENEMY_SPAWN_DIST:
			print (f"Distance to enemy: {str(round(random_block.x - player.x))}")
			print (f"Difficulty: {str(round(difficulty, 2))}")

			enemy = Enemy(screen, random_block.x, random_block.y - enemy_standing_texture.get_height(), enemy_standing_texture, enemy_walking_textures, None, running_textures=enemy_running_textures, aimed_shooting_textures=enemy_standing_shooting_textures, hurt_textures=enemy_hurt_textures, death_textures=enemy_dead_textures, enemy_grenade_textures=enemy_grenade_textures)
			enemies.append(enemy)

			# if grenade is None:
			# 	grenade = Grenade(screen, player, 6)
			# 	grenade.find_trajectory(enemy)



		if player.health <= 0:
			# enemies.clear()
			# bullets.clear()
			# boosts.clear()

			# gun_channel.stop()
			# music_channel.stop()
			# weather.stop()

			# player.ammo = ROUNDS_IN_MAG

			if player.dead:
				gun_channel.stop()
				music_channel.stop()
				weather.stop()

				return True


		handle_player_stats(player, raining=weather.raining)

		health_bar.set_value(player.health)
		stamina_bar.set_value(player.stamina)

		# print (player.health)

		# if player.health > 0:

		stamina_bar.draw()
		health_bar.draw()
		sound_bar.draw()
		draw_ammo(screen, player.ammo, ammo_texture, empty_ammo_texture)


		for enemy in enemies:
			enemy.x -= scroll_speed

			if enemy.grenade is not None:
				enemy.grenade.x -= scroll_speed

			# print (f"{enemy.direction} and {str(enemy.flipped)}")
			enemy.change_movement_texture(player, ticks)


			bullet = enemy.follow_player(player, ticks, bullet_texture)

			if enemy.dead:
				enemies.remove(enemy)
				enemies_killed += 1
				continue


			if bullet is not None:
				bullets.append(bullet)



			throwing_grenade = randint(0, ENEMY_GRENADE_THROW_CHANCE - (int(difficulty) * DIFFICULTY_MULTIPLIER))

			if abs(enemy.x - player.x) <= ATTACK_RANGE and (player.attacking or player.sliding) and not enemy.flinged and player.stamina >= STAMINA_TO_ATTACK and enemy.health > 0:
				enemy.aimed_shot = False
				enemy.take_damage()

				if enemy.health > 0:
					enemy.fling(player)
					enemy.throwing_grenade = False

				# # Possibly add fling with an angle upwards
				# if player.x > enemy.x:
				# 	if player.vel_x != 0:
				# 		enemy.vel_x = -ATTACK_KNOCKBACK * player.vel_x

				# 	else:
				# 		enemy.vel_x = -ATTACK_KNOCKBACK

				# else:
				# 	if player.vel_x != 0:
				# 		enemy.vel_x = ATTACK_KNOCKBACK * player.vel_x

				# 	else:
				# 		enemy.vel_x = ATTACK_KNOCKBACK

			elif abs(enemy.x - player.x) < SCREEN_WIDTH * 3 / 4 and throwing_grenade == 0 and enemy.grenade is None and enemies_killed >= 4 and enemy.health > 0:
				enemy.throwing_grenade = True
				enemy.aimed_shot = False
				enemy.aiming = False


			if enemy.grenade is not None and not enemy.grenade.explode:
				# enemy.grenade.update()
				# enemy.grenade.draw()


				if enemy.grenade.hit_entity(player):
					player.hurt = True
					enemy.grenade.y -= enemy.grenade.explosion_textures[0].get_height()
					enemy.grenade.x -= (enemy.grenade.explosion_textures[0].get_width()) / 2
					enemy.grenade.explode = True

					# enemy.grenade = None


				else:

					for block in surface_blocks:
						if enemy.grenade.hit_entity(block):

							enemy.grenade.explode = True

							# enemy.grenade.x = block.x + BLOCK_SIZE // 2
							enemy.grenade.y = block.y - enemy.grenade.explosion_textures[0].get_height()
							enemy.grenade.x = block.x - (enemy.grenade.explosion_textures[0].get_width() / 2)
							# enemy.grenade = None
							break

			elif enemy.grenade is not None and enemy.grenade.explode:
				if enemy.grenade.hit_entity(player):
					player.hurt = True
					player.health -= MAX_GRENADE_DAMAGE

				elif enemy.grenade.distance_from_entity(player) <= GRENADE_RADIUS:
					player.hurt = True


					if enemy.grenade.x < player.x:
						dist = abs(player.x - enemy.grenade.x)

					else:
						dist = abs(player.x - enemy.grenade.x  + player.get_width())

					
					damage = (- MAX_GRENADE_DAMAGE *  dist / (GRENADE_RADIUS)) + MAX_GRENADE_DAMAGE
					player.health -= damage

				player.take_damage(weapon=enemy.grenade)



			enemy.update(ticks)
			
			if (enemy.x + enemy.get_width() > 0 and enemy.x < SCREEN_WIDTH) or (enemy.grenade is not None):
				enemy.draw()


		player.update()
		player.draw()

		if grenade is not None:
			# grenade.update(dt)

			if grenade.y > SCREEN_HEIGHT:
				grenade = None
				continue

			grenade.draw()

		for boost in boosts:
			if boost.hit_player(player):
				boosts.remove(boost)

				if boost.type == "health":
					player.health += HEALTH_BOOST
					if player.health > 1.0:
						player.health = 1.0

					continue

				else:
					player.stamina += STAMINA_BOOST

					if player.stamina > 1.0:
						player.stamina = 1.0



			elif not boost.alive():
				boosts.remove(boost)


			# if boost.hit_player(player) and boost.type == "health":
			# 	player.health += HEALTH_BOOST
			# 	if player.health > 1.0:
			# 		player.health = 1.0

			# 	continue

			# elif boost.hit_player(player) and boost.type == "stamina":
			# 	player.stamina += STAMINA_BOOST

			# 	if player.stamina > 1.0:
			# 		player.stamina = 1.0

			# 	boosts.remove(boost)

			boost.update(scroll_speed)
			boost.draw()



		pygame.display.flip()
		pygame.display.update()



	print (round(sum(fps_sum) / len(fps_sum), 2))
	# pygame.quit()
	return False



def draw_ammo(screen, ammo, bullet_texture, empty_bullet_texture):

	x = (SCREEN_WIDTH - ((bullet_texture.get_width()) * ROUNDS_IN_MAG)) + 70
	y = 40


	for i in range(1, ROUNDS_IN_MAG+1):
		if i == (ROUNDS_IN_MAG / 2) + 1:
			y += bullet_texture.get_height()
			x = (SCREEN_WIDTH - ((bullet_texture.get_width()) * ROUNDS_IN_MAG)) + 70

		if ammo >= i:
			screen.blit(bullet_texture, (x, y))

		else:
			screen.blit(empty_bullet_texture, (x, y))

		x += bullet_texture.get_width() * 1.5





def handle_movement(keys, player, ticks):
	# Sliding
	if keys[pygame.K_c] and keys[pygame.K_LSHIFT] and not player.jumping and not player.sliding and player.stamina >= 0.15 and player.running:
		player.sitting = True
		player.sliding = True
		player.vel_x = SPRINTING_VEL
		player.y += player.get_height() // 2
		player.stamina -= STAMINA_TO_SLIDE
		player.vel_x = SPRINTING_VEL

		player.running = False
		player.animation_stages["standing_reload"] = 0
		player.standing_reload = False


	elif not player.sliding:
		# player.vel_x = 0
		if keys[pygame.K_c] and not player.jumping:
			player.sitting = True
			player.y += player.get_height() // 2

		elif player.sitting:
			player.sitting = False
			player.y -= player.get_height() // 2

	elif not keys[pygame.K_c] or not keys[pygame.K_LSHIFT]:
		player.sliding = False



	if keys[pygame.K_d] and not player.sitting and not player.lying and not player.aiming:
		if not player.running:
			player.vel_x = WALKING_VEL

		else:
			player.vel_x = SPRINTING_VEL

		player.animation_stages["standing_reload"] = 0
		player.standing_reload = False

	elif keys[pygame.K_a] and not player.sitting and not player.lying and not player.aiming:
		if not player.running:
			player.vel_x = -WALKING_VEL

		else:
			player.vel_x = -SPRINTING_VEL

		player.animation_stages["standing_reload"] = 0
		player.standing_reload = False



		# return

	elif keys[pygame.K_x] and (player.sitting or player.lying) and not player.aiming and not player.jumping:
		player.sitting = False

		if not player.lying:
			player.lying = True
			player.y += player.get_height()


		# else:
		# 	player.lying = False

	elif keys[pygame.K_f] and not player.attacking and player.ticks_since_attack >= ATTACK_COOLDOWN and player.stamina >= STAMINA_TO_ATTACK:
		player.attacking = True
		player.stamina -= STAMINA_TO_ATTACK


		return


	else:

		if not player.sitting:
			player.sliding = False

		# player.sitting = False
		player.vel_x = 0
		player.lying = False


	if keys[pygame.K_SPACE] and not player.jumping and player.current_texture not in player.flip_textures and player.stamina >= STAMINA_TO_FLIP:
		player.animation_stages["standing_reload"] = 0
		player.standing_reload = False

		player.stamina -= STAMINA_TO_FLIP
		player.vel_y += -BLOCK_SIZE * JUMP_CONSTANT
		player.jumping = True
		player.lying = False
		player.aiming = False
		player.aimed_shot = False
		player.sitting = False
		player.attacking =  False
		player.update()

	elif keys[pygame.K_LSHIFT] and player.stamina >= 0.15 and not player.sliding and abs(player.vel_x) > 0: #  and abs(player.vel_x) > 0
		player.animation_stages["standing_reload"] = 0
		player.standing_reload = False
		player.sitting = False
		player.aiming = False
		player.aimed_shot = False
		player.attacking = False

		player.running = True


	elif not player.sitting:
		player.running = False


	if keys[pygame.K_r] and not player.standing_reload and not player.jumping and player.ammo < ROUNDS_IN_MAG and not player.aiming and not player.attacking:
		player.running = False
		# player.sitting = False
		player.standing_reload = True

		
def handle_player_stats(player, raining=False):
	if player.stamina <= 0.05 and not player.running:
		player.stamina += 0.01

	elif player.stamina < 1.0 and (player.sitting or player.lying):
		player.stamina *= (STAMINA_RECOVER_FACTOR ** 5)

	elif player.stamina < 1.0 and player.vel_x == 0 and not player.running:
		player.stamina *= (STAMINA_RECOVER_FACTOR ** 3)

	elif player.stamina < 1.0:
		player.stamina *= STAMINA_RECOVER_FACTOR


	if player.health <= 0.05 and not player.hurt and player.health > 0:
		if not raining:
			player.health += 0.01

		else:
			player.health += 0.05

	elif player.health < 1.0 and player.health > 0 and (player.sitting or player.lying):
		if not raining:
			player.health *= REGEN_FACTOR ** 4

		else:
			player.health *= REGEN_FACTOR ** 4.5

	elif player.health < 1.0 and player.health > 0 and player.vel_x == 0 and not player.hurt:
		if not raining:
			player.health *= REGEN_FACTOR ** 3

		else:
			player.health *= REGEN_FACTOR ** 3.5

	elif player.health < 1.0 and player.health > 0:
		if not raining:
			player.health *= REGEN_FACTOR

		else:
			player.health *= REGEN_FACTOR ** 1.5




def draw_background(screen, player, ticks, scroll_speed, weather):

	weather.handle_rain()
	weather.update(ticks, scroll_speed, player)

	if not weather.raining and not weather.in_transition:
		screen.fill(SKY_BLUE)

	# elif player.health <= 0:
	# 	screen.fill(HEALTH_RED)

	# if len(rain) > 0 and player.health > 0:
	# 	for drop in rain:
	# 		drop.x -= scroll_speed
	# 		if drop.y > SCREEN_HEIGHT:
	# 			rain.remove(drop)
	# 			continue

	# 		drop.update()
	# 		drop.draw()


	# 	return rain

	# return []


if __name__ == "__main__":

	seed, title_run = title_screen()
	main_run = True

	while title_run and main_run:
		main_run = main(seed=seed)

		if not main_run:
			break

		seed, title_run = title_screen()

	pygame.quit()
	quit()