import pygame
from random import randint
from player import Player, Bullet
from map_generator import *
from constants import *
from stat_bars import Bar



"""
Sprites: https://craftpix.net/freebies/free-pixel-prototype-character-sprites-for-shooter/
"""


pygame.init()
pygame.mixer.init()




def main():
	
	run = True
	screen = pygame.display.set_mode(SCREEN_SIZE)

	# Load assets


	still_player_texture, walking_textures, running_textures, aim_texture, aimed_shooting_textures, no_aim_shooting_textures, bullet_texture, empty_bullet_texture, flip_textures = load_assets()
	hurt_textures, death_textures = load_hurt_assets()
	single_shot_sfx, reload_sfx = load_sfx()


	# single_shot_sfx, reload_sfx = load_sfx()

	player = Player(screen, 0, 0, still_player_texture, walking_textures, aim_texture, flip_textures=flip_textures, running_textures=running_textures, aimed_shooting_textures=aimed_shooting_textures, hurt_textures=hurt_textures, death_textures=death_textures, noaim_shooting_textures=no_aim_shooting_textures)

	health_bar = Bar(screen, (20, 40), HEALTH_RED)
	stamina_bar = Bar(screen, (20, 80), STAMINA_YELLOW)

	ammo_texture = pygame.transform.scale_by(pygame.transform.rotate(bullet_texture, 90), 3)
	empty_ammo_texture = pygame.transform.scale_by(pygame.transform.rotate(empty_bullet_texture, 90), 3)

	bullets = []

	seed = randint(0, 999)
	noise_num = 0
	height_factor = 0.5
	scroll_speed = 0

	noise_map = generate_noise_map(octaves=OCTAVES, seed=seed, start = noise_num, end=int((SCREEN_WIDTH // BLOCK_SIZE) * RENDER_DISTANCE))
	surface_blocks, blocks, noise_number = get_blocks(screen, noise_map, surface_color=SURFACE_GROUND_COLOR, block_color=GROUND_COLOR, height_factor=height_factor)
	clock = pygame.time.Clock()
	ticks = 0


	while run:
		ticks += 1
		clock.tick(FPS)
		draw_background(screen, player)
		pygame.display.set_caption(str(round(clock.get_fps())))

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False
				break


		# if pygame.mouse.get_pressed()[0]:
		# 	seed = randint(0, 999)
		# 	noise_map = generate_noise_map(octaves=OCTAVES, seed=seed, start = noise_num, end=int((SCREEN_WIDTH // BLOCK_SIZE) * RENDER_DISTANCE))
		# 	surface_blocks, blocks, noise_number = get_blocks(screen, noise_map, surface_color=SURFACE_GROUND_COLOR, block_color=GROUND_COLOR, height_factor=height_factor)


		keys = pygame.key.get_pressed()
		if not player.aiming and player.health > 0:
			handle_movement(keys, player, ticks)

			if keys[pygame.K_r] and reload_sfx is not None:
				reload_sfx.play()


		for bullet in bullets:
			if bullet.x > SCREEN_WIDTH or bullet.x < 0 or bullet.y > SCREEN_HEIGHT or bullet.y < 0:
				bullets.remove(bullet)
				continue

			bullet.update()
			bullet.draw()

		for block in blocks:
			if player.health > 0:
				block.draw()

			block.x -= scroll_speed

			if block.x < -BLOCK_SIZE * 3 and block in blocks:
				blocks.remove(block)

			if (player.on_block(block) and player.vel_y > 0) or (abs(player.x - block.x) <= BLOCK_SIZE and abs(player.y - block.y) < player.get_height()) and block in surface_blocks:
				player.y = block.y - player.get_height() + 1
				player.vel_y = 0


				if player.jumping and (player.animation_stages["flip"] != 0 and player.animation_stages["flip"] != len(player.flip_textures) - 1):
					player.health = 0

				player.jumping = False

				player.animation_stages["flip"] = 0


				if player.vel_x == 0 and not player.hurt and player.health > 0 and not player.aimed_shot and not player.noaim_shooting:
					player.current_texture = player.still_texture
					player.animation_stages["walk"] = 0
					player.animation_stages["run"] = 0



			# for bullet in bullets:
			# 	if bullet.hit_entity(block):
			# 		bullets.remove(bullet)
			# 		break


		mx, my = pygame.mouse.get_pos()
		
		if pygame.mouse.get_pressed()[2] and pygame.mouse.get_pressed()[0] and ticks % SHOOTING_COOLDOWN == 0 and player.ammo > 0 and not player.jumping:

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

				if pygame.mixer.get_busy():
					pygame.mixer.stop()

				single_shot_sfx.play()

			else:
				player.aimed_shot = False


			

		elif pygame.mouse.get_pressed()[2] and not player.jumping:
			player.aiming = True

			if mx < player.x and not player.flipped:
				player.flipped = True

			elif mx > player.x and player.flipped:
				player.flipped = False



		elif pygame.mouse.get_pressed()[0] and not pygame.mouse.get_pressed()[2] and player.ammo > 0 and not player.jumping and ticks % SHOOTING_COOLDOWN == 0 :
			player.noaim_shooting = True
			bullet = Bullet(screen, (player.x, player.y + (player.get_height() // 2)), bullet_texture, flip=player.flipped)

			mx += randint(-50, 50)
			my += randint(-50, 50)

			valid_bullet = bullet.set_vel(mx, my)

			if bullet.vel_x < 0 and valid_bullet:
				player.flipped = True

			elif bullet.vel_x > 0 and valid_bullet:
				player.flipped = False


			if valid_bullet:
				player.ammo -= 1
				bullets.append(bullet)

				if pygame.mixer.get_busy():
					pygame.mixer.stop()

				single_shot_sfx.play()

			else:
				player.noaim_shooting = False

		else:
			player.aiming = False
			player.noaim_shooting = False
			player.aimed_shot = False

		player.change_movement_texture(ticks)


		if blocks[-1].x <= SCREEN_WIDTH:
			surface_blocks, blocks, noise_number = generate_new_terrain(screen, noise_number, seed, height_factor)

		if player.x > SCREEN_WIDTH // 4 and player.vel_x > 0:
			scroll_speed = player.vel_x
			player.vel_x = 0

		elif player.x < SCREEN_WIDTH // 4 and player.vel_x < 0:
			scroll_speed = player.vel_x
			player.vel_x = 0

		else:
			scroll_speed = 0

		if player.y >= SCREEN_HEIGHT:
			player.x = SCREEN_WIDTH // 2
			player.y = 0
			player.health = 1.0
			player.stamina = 1.0

		# if player.health <= 0:
		# 	game_over(screen, player)
		# 	screen.fill(WHITE)
		# 	main()

		handle_player_stats(player)

		health_bar.set_value(player.health)
		stamina_bar.set_value(player.stamina)
		# print (player.health)

		if player.health > 0:
			stamina_bar.draw()
			health_bar.draw()
			draw_ammo(screen, player.ammo, ammo_texture, empty_ammo_texture)

		player.update()
		player.draw()

		pygame.display.flip()
		pygame.display.update()


	pygame.quit()



def draw_ammo(screen, ammo, bullet_texture, empty_bullet_texture):

	x = SCREEN_WIDTH - (bullet_texture.get_width() * ROUNDS_IN_MAG)
	y = 40


	for i in range(1, ROUNDS_IN_MAG+1):
		if i == (ROUNDS_IN_MAG / 2) + 1:
			y += bullet_texture.get_height()
			x = SCREEN_WIDTH - (bullet_texture.get_width() * ROUNDS_IN_MAG)

		if ammo >= i:
			screen.blit(bullet_texture, (x, y))

		else:
			screen.blit(empty_bullet_texture, (x, y))

		x += bullet_texture.get_width() * 1.5



def handle_movement(keys, player, ticks):
	if keys[pygame.K_d]:
		if not player.running:
			player.vel_x = WALKING_VEL

		else:
			player.vel_x = SPRINTING_VEL

	elif keys[pygame.K_a]:
		if not player.running:
			player.vel_x = -WALKING_VEL

		else:
			player.vel_x = -SPRINTING_VEL

	elif keys[pygame.K_q] and ticks % 5 == 0:
		player.hurt = True
		player.health -= 0.1

	if keys[pygame.K_SPACE] and not player.jumping and player.current_texture not in player.flip_textures and player.stamina >= STAMINA_TO_FLIP:
		player.stamina -= STAMINA_TO_FLIP
		player.vel_y += -BLOCK_SIZE * JUMP_CONSTANT
		player.jumping = True
		player.update()

	elif keys[pygame.K_LSHIFT] and player.stamina >= 0.15:
		player.running = True

	else:
		player.running = False


	if keys[pygame.K_r]:
		player.ammo = ROUNDS_IN_MAG
		player.running = False
		
def handle_player_stats(player):
	if player.stamina <= 0.05 and not player.running:
		player.stamina += 0.01

	elif player.stamina < 1.0 and player.vel_x == 0 and not player.running:
		player.stamina *= (STAMINA_RECOVER_FACTOR ** 3)

	elif player.stamina < 1.0:
		player.stamina *= STAMINA_RECOVER_FACTOR


	if player.health <= 0.05 and not player.hurt and player.health > 0:
		player.health += 0.01

	elif player.health < 1.0 and player.health > 0 and player.vel_x == 0 and not player.hurt:
		player.health *= REGEN_FACTOR ** 3

	elif player.health < 1.0 and player.health > 0:
		player.health *= REGEN_FACTOR


def load_player_asset(index, type_="walking"):
	if type_ == "walking":
		path = f"Assets//walking//walk{str(index)}.png"

	elif type_ == "running":
		path = f"Assets//running/run{str(index)}.png"

	elif type_ == "flip":
		path = f"Assets//flip//flip{str(index)}.png"

	elif type_ == "aimed shot":
		path = f"Assets//shooting_standing//aimed_shot{str(index)}.png"

	elif type_ == "noaim shot":
		path = f"Assets//shooting_standing//noaim{str(index)}.png"

	elif type_ == "hurt":
		path = f"Assets//hurt_death//hurt{str(index)}.png"

	elif type_ == "death":
		path = f"Assets//hurt_death//dead{str(index)}.png"

	try:
		asset = pygame.image.load(path)

	except:
		print (f"path {path} not found")
		return None


	return pygame.transform.scale_by(asset, 1.5).convert_alpha()



def load_assets():

	still_player_surf = pygame.image.load("Assets//Standing.png")
	still_player_surf = pygame.transform.scale_by(still_player_surf, 1.5).convert_alpha()

	aim = pygame.image.load("Assets//Aim.png")
	aim = pygame.transform.scale_by(aim, 1.5).convert_alpha()

	bullet = pygame.image.load("Assets//bullet.png")
	bullet = pygame.transform.scale_by(bullet, 0.25).convert_alpha()

	empty_bullet = pygame.image.load("Assets//empty_bullet.png")
	empty_bullet = pygame.transform.scale_by(empty_bullet, 0.25).convert_alpha()

	walking = []
	running = []
	aimed_shooting = []
	no_aim_shooting = []
	flips = []

	for i in range(1, 13):
		walking.append(load_player_asset(i, type_="walking"))
		running.append(load_player_asset(i, type_="running"))

		if i <= 4:
			aimed_shooting.append(load_player_asset(i, type_="aimed shot"))
			no_aim_shooting.append(load_player_asset(i, type_="noaim shot"))

		if i <= 8:
			flips.append(load_player_asset(i, type_="flip"))


	return still_player_surf, walking, running, aim, aimed_shooting, no_aim_shooting, bullet, empty_bullet, flips


def load_hurt_assets():
	hurt_textures = []
	death_textures = []

	for i in range(1, 6):
		death_textures.append(load_player_asset(i, type_="death"))

		if i <= 4:
			hurt_textures.append(load_player_asset(i, type_="hurt"))



	return hurt_textures, death_textures



def load_sfx():
	single_shot_sfx = pygame.mixer.Sound("Assets//sfx//single_shot.wav")
	# reload_sfx = pygame.mixer.Sound("Assets//sfx//reload.wav")


	return single_shot_sfx, None


def draw_background(screen, player):
	if player.health > 0:
		screen.fill(SKY_BLUE)

	else:
		screen.fill(HEALTH_RED)




if __name__ == "__main__":
	main()
