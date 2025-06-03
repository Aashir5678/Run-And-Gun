import pygame
from random import randint, choice
from sprites.player import Player, Bullet
from sprites.enemy import Enemy
from utilities.map_generator import *
from utilities.constants import *
from utilities.asset_loader import *
from utilities.stat_bars import Bar
from utilities.boosts import Boost
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


	still_player_texture, sitting_player_texture, lying_player_texture, walking_textures, running_textures, aim_texture, aimed_shooting_textures, sitting_shoot, standing_reload_textures, no_aim_shooting_textures, bullet_texture, empty_bullet_texture, flip_textures = load_player_assets()
	hurt_textures, death_textures = load_player_hurt_assets()
	heart_texture = load_boost_textures()
	single_shot_sfx, reload_sfx = load_sfx()


	gun_channel = pygame.mixer.Channel(0)
	music_channel = pygame.mixer.Channel(1)

	

	health_bar = Bar(screen, (20, 40), HEALTH_RED)
	stamina_bar = Bar(screen, (20, 80), STAMINA_YELLOW)

	ammo_texture = pygame.transform.scale_by(pygame.transform.rotate(bullet_texture, 90), 3)
	empty_ammo_texture = pygame.transform.scale_by(pygame.transform.rotate(empty_bullet_texture, 90), 3)

	enemy_standing_texture, enemy_walking_textures, enemy_running_textures, enemy_standing_shooting_textures = load_enemy_assets()
	# print (len(enemy_walking_textures))
	bullets = []

	enemies = []
	health_boosts = []
	difficulty = 0

	# enemies = [Enemy(screen, SCREEN_WIDTH * 3 // 4, 0, enemy_standing_texture, enemy_walking_textures, None)]


	if seed is None:
		seed = randint(-9999, 9999)

	noise_num = 0
	scroll_speed = 0

	surface_blocks, blocks = generate_new_terrain(screen, noise_num, seed, HEIGHT_FACTOR)
	clock = pygame.time.Clock()
	ticks = 0

	player = Player(screen, surface_blocks[0].y - still_player_texture.get_height(), 0, still_player_texture, walking_textures, aim_texture, sitting_shooting_textures=sitting_shoot, lying_player_texture=lying_player_texture, sitting_player_texture=sitting_player_texture, flip_textures=flip_textures, running_textures=running_textures, aimed_shooting_textures=aimed_shooting_textures, hurt_textures=hurt_textures, death_textures=death_textures, noaim_shooting_textures=no_aim_shooting_textures, standing_reload_textures=standing_reload_textures)

	print (f"Seed: {str(seed)}")


	fps_sum = []


	while run:
		# if not music_channel.get_busy():
		# 	music_channel.queue(song)
		# print (int(player.blocks_travelled))
		player.blocks_travelled += scroll_speed / BLOCK_SIZE


		ticks += 1
		clock.tick(FPS)
		draw_background(screen, player)
		pygame.display.set_caption(str(round(clock.get_fps())))


		fps_sum.append(clock.get_fps())
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False
				break


		keys = pygame.key.get_pressed()
		if player.health > 0 and not player.noaim_shooting:
			handle_movement(keys, player, ticks)

			if keys[pygame.K_r] and reload_sfx is not None and player.ammo < ROUNDS_IN_MAG:
				gun_channel.play(reload_sfx)



		for block in surface_blocks:
			spawn_health_boost = random.randint(0, HEALTH_BOOST_SPAWN_RATE + int(difficulty))

			if spawn_health_boost == 0 and player.health < 1.0 and len(health_boosts) < 5:
				health = Boost(screen, block.x, block.y - (heart_texture.get_height() * 4 / 3), heart_texture)
				health_boosts.append(health)


		for index, block in enumerate(blocks):
			
			if player.health > 0:
				block.draw()

			block.x -= scroll_speed
			block.block_rect.x = block.x

			if block.x < -SPRINTING_VEL * BLOCK_SIZE:
				blocks.remove(block)

				if block in surface_blocks:
					surface_blocks.remove(block)


			# Prevents player from sinking in to the floor
			if (player.on_block(block) and player.vel_y > 0) or (abs(player.x - block.x) <= BLOCK_SIZE and abs(player.y - block.y) < player.get_height()) and block in surface_blocks:
				player.y = block.y - player.get_height() + 1
				player.vel_y = 0


				if player.jumping and (player.animation_stages["flip"] != 0 and player.animation_stages["flip"] != len(player.flip_textures) - 1):
					player.health = 0

				player.jumping = False

				player.animation_stages["flip"] = 0


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
				if not player.sitting and not player.lying:
					player.hurt = True

				player.take_damage(bullet)
				bullets.remove(bullet)


			for enemy in enemies:
				if bullet.hit_entity(enemy) and bullet.is_player_bullet():
					# enemies.remove(enemy)

					enemy.take_damage(bullet)

					if enemy.health <= 0:
						enemies.remove(enemy)
					bullets.remove(bullet)
					break


				# Enemies advance on player if the player is camping behind a hill or if enemy has an ineffective shooting spot
				elif not bullet.is_player_bullet() and bullet.get_distance(player) > player.get_height() / 2 and enemy.at_shoot_dist:
					enemy.shoot_dist -= 5

			bullet.update()
			bullet.draw()
		




		mx, my = pygame.mouse.get_pos()
		
		if pygame.mouse.get_pressed()[2] and pygame.mouse.get_pressed()[0] and ticks % SHOOTING_COOLDOWN == 0 and player.ammo > 0 and not player.jumping and not player.hurt:

			if player.sitting:
				player.sitting_shot = True

			elif player.lying:
				pass

			else:
				player.aiming = True
				player.aimed_shot = True

			
			bullet = Bullet(screen, (player.x, player.y + (player.get_height() // 4)), bullet_texture, flip=player.flipped)

			
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
				player.aimed_shot = False


			

		elif pygame.mouse.get_pressed()[2] and not player.jumping and not player.hurt:
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
					enemy.vel_x = 0
					enemy.shoot_dist = enemy.x



		elif pygame.mouse.get_pressed()[0] and not pygame.mouse.get_pressed()[2] and player.ammo > 0 and not player.jumping and ticks % SHOOTING_COOLDOWN == 0 :
			player.noaim_shooting = True
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

		else:
			player.aiming = False
			player.noaim_shooting = False
			player.aimed_shot = False

		player.change_movement_texture(ticks)


		if surface_blocks[-1].x <= SCREEN_WIDTH:
			noise_num += int((SCREEN_WIDTH // BLOCK_SIZE) * RENDER_DISTANCE)
			new_suface_blocks, new_blocks = generate_new_terrain(screen, noise_num, seed, HEIGHT_FACTOR, start_x=SCREEN_WIDTH)

			surface_blocks.extend(new_suface_blocks)
			blocks.extend(new_blocks)

		if player.x > SCREEN_WIDTH // 4 and player.vel_x > 0:
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


		# Difficulty increases every BLOCKS_TILL_DIFFICULTY_INCREASE blocks travelled

		if player.blocks_travelled / BLOCKS_TILL_DIFFICULTY_INCREASE > difficulty:
			difficulty = player.blocks_travelled / BLOCKS_TILL_DIFFICULTY_INCREASE


		odds = int(ENEMY_SPAWN_RATE - difficulty)


		if odds < MAX_SPAWN_RATE:
			odds = MAX_SPAWN_RATE

		if random.randint(0, odds) == 0 and surface_blocks and len(enemies) < MAX_ENEMIES_AT_ONCE:
			random_block = choice(surface_blocks)
			
			
			if random_block.x > player.x + MIN_ENEMY_SPAWN_DIST and random_block.x < MAX_ENEMY_SPAWN_DIST:
				print (f"Distance to enemy: {str(random_block.x - player.x)}")
				print (f"Difficulty: {str(round(difficulty, 2))}")
				enemies.append(Enemy(screen, random_block.x, random_block.y - enemy_standing_texture.get_height(), enemy_standing_texture, enemy_walking_textures, None, running_textures=enemy_running_textures, aimed_shooting_textures=enemy_standing_shooting_textures))



		if player.health <= 0:
			enemies.clear()
			bullets.clear()
			health_boosts.clear()
			player.ammo = ROUNDS_IN_MAG

			if player.dead:
				return True


		handle_player_stats(player)

		health_bar.set_value(player.health)
		stamina_bar.set_value(player.stamina)
		# print (player.health)

		if player.health > 0:
			stamina_bar.draw()
			health_bar.draw()
			draw_ammo(screen, player.ammo, ammo_texture, empty_ammo_texture)


		for enemy in enemies:
			enemy.x -= scroll_speed
			# print (f"{enemy.direction} and {str(enemy.flipped)}")
			enemy.change_movement_texture(player, ticks)


			bullet = enemy.follow_player(player, ticks, bullet_texture)

			if bullet is not None:
				bullets.append(bullet)


			
			enemy.update()
			enemy.draw()


		player.update()
		player.draw()

		for health_boost in health_boosts:
			if health_boost.hit_player(player):
				player.health += HEALTH_BOOST
				if player.health > 1.0:
					player.health = 1.0

				health_boosts.remove(health_boost)

				continue

			health_boost.update(scroll_speed)
			health_boost.draw()



		pygame.display.flip()
		pygame.display.update()


	print (sum(fps_sum) / len(fps_sum))
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

	elif keys[pygame.K_c] and not player.jumping:
		player.lying = False

		if not player.sitting:
			player.sitting = True
			player.y += player.get_height() // 2



		# else:
		# 	# player.y -= player.get_height() 
		# 	player.sitting = False



		return

	elif keys[pygame.K_x] and (player.sitting or player.lying) and not player.aiming and not player.jumping:
		player.sitting = False

		if not player.lying:
			player.lying = True
			player.y += player.get_height()


		# else:
		# 	player.lying = False


	else:
		player.sitting = False
		player.lying = False

	# elif keys[pygame.K_q] and ticks % 5 == 0:
	# 	player.hurt = True
	# 	player.health -= 0.1

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
		player.update()

	elif keys[pygame.K_LSHIFT] and player.stamina >= 0.15:
		player.animation_stages["standing_reload"] = 0
		player.standing_reload = False
		player.sitting = False
		player.aiming = False
		player.aimed_shot = False

		player.running = True

	else:
		player.running = False


	if keys[pygame.K_r] and not player.standing_reload and not player.jumping and player.ammo < ROUNDS_IN_MAG and not player.aiming:
		player.running = False
		# player.sitting = False
		player.standing_reload = True

		
def handle_player_stats(player):
	if player.stamina <= 0.05 and not player.running:
		player.stamina += 0.01

	elif player.stamina < 1.0 and (player.sitting or player.lying):
		player.stamina *= (STAMINA_RECOVER_FACTOR ** 5)

	elif player.stamina < 1.0 and player.vel_x == 0 and not player.running:
		player.stamina *= (STAMINA_RECOVER_FACTOR ** 3)

	elif player.stamina < 1.0:
		player.stamina *= STAMINA_RECOVER_FACTOR


	if player.health <= 0.05 and not player.hurt and player.health > 0:
		player.health += 0.01

	elif player.health < 1.0 and player.health > 0 and (player.sitting or player.lying):
		player.health *= REGEN_FACTOR ** 4

	elif player.health < 1.0 and player.health > 0 and player.vel_x == 0 and not player.hurt:
		player.health *= REGEN_FACTOR ** 3

	elif player.health < 1.0 and player.health > 0:
		player.health *= REGEN_FACTOR




def draw_background(screen, player):
	if player.health > 0:
		screen.fill(SKY_BLUE)

	else:
		screen.fill(HEALTH_RED)




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