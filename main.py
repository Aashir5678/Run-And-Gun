import pygame
from random import randint
from player import Player, Bullet
from map_generator import *
from constants import *
from stat_bars import Bar
from math import e


"""
Sprites: https://craftpix.net/freebies/free-pixel-prototype-character-sprites-for-shooter/
"""


pygame.init()


def main():
	
	run = True
	screen = pygame.display.set_mode(SCREEN_SIZE)

	# Load assets


	still_player_texture, walking_textures, running_textures, aim_texture, aimed_shooting_textures, bullet_texture, flip_textures = load_assets()

	
	player = Player(screen, 0, 0, still_player_texture, walking_textures, aim_texture, flip_textures=flip_textures, running_textures=running_textures, aimed_shooting_textures=aimed_shooting_textures)

	health_bar = Bar(screen, (20, 40), HEALTH_RED)
	stamina_bar = Bar(screen, (20, 80), STAMINA_YELLOW)

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
		draw_background(screen)
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
		if not player.aiming:
			handle_movement(keys, player)


		for bullet in bullets:
			bullet.update()
			bullet.draw()

		for block in blocks:
			block.draw()
			block.x -= scroll_speed

			if block.x < -BLOCK_SIZE * 3 and block in blocks:
				blocks.remove(block)

			if (player.on_block(block) and player.vel_y > 0) or (abs(player.x - block.x) <= BLOCK_SIZE and abs(player.y - block.y) < player.get_height()) and block in surface_blocks:
				player.y = block.y - player.get_height()
				player.vel_y = 0
				player.jumping = False

				player.flip_index = 0

				if player.vel_x == 0:
					player.current_texture = player.still_texture
					player.walk_index = 0
					player.run_index = 0


		
		
		if pygame.mouse.get_pressed()[2] and pygame.mouse.get_pressed()[0]:
			player.aiming = True
			player.aimed_shot = True
			bullet = Bullet(screen, (player.x, player.y + (player.get_height() // 4)), bullet_texture, flip=player.flipped)

			mx, my = pygame.mouse.get_pos()
			bullet.set_vel(mx, my)

			bullets.append(bullet)
			pygame.time.delay(SHOOTING_COOLDOWN)

		elif pygame.mouse.get_pressed()[2]:
			player.aiming = True


		else:
			player.aiming = False
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


		if player.stamina <= 0.05 and not player.running:
			player.stamina += 0.01

		elif player.stamina < 1.0 and player.vel_x == 0 and not player.running:
			player.stamina *= (STAMINA_RECOVER_FACTOR ** 3)

		elif player.stamina < 1.0:
			player.stamina *= STAMINA_RECOVER_FACTOR


		stamina_bar.set_value(player.stamina)
		stamina_bar.draw()
		health_bar.draw()

		player.update()
		player.draw()

		pygame.display.flip()
		pygame.display.update()


	pygame.quit()


def handle_movement(keys, player):
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

	if keys[pygame.K_SPACE] and not player.jumping and player.current_texture not in player.flip_textures and player.stamina >= STAMINA_TO_FLIP:
		player.stamina -= STAMINA_TO_FLIP
		player.vel_y += -BLOCK_SIZE * JUMP_CONSTANT
		player.jumping = True
		player.update()

	elif keys[pygame.K_LSHIFT] and player.stamina >= 0.15:
		player.running = True

	else:
		player.running = False
	

def load_player_asset(index, type_="walking"):
	if type_ == "walking":
		path = f"Assets//walking//walk{str(index)}.png"

	elif type_ == "running":
		path = f"Assets//running/run{str(index)}.png"

	elif type_ == "flip":
		path = f"Assets//flip//flip{str(index)}.png"

	elif type_ == "aimed shot":
		path = f"Assets//shooting_standing//aimed_shot{str(index)}.png"

	try:
		asset = pygame.image.load(path)

	except:
		print (f"path {path} not found")
		return None


	return pygame.transform.scale_by(asset, 1.5).convert_alpha()



def load_assets():

	still_player_surf = pygame.image.load("Assets//Standing.png")
	still_player_surf = pygame.transform.scale_by(still_player_surf, 1.5)
	aim = pygame.image.load("Assets//Aim.png")
	aim = pygame.transform.scale_by(aim, 1.5)

	bullet = pygame.image.load("Assets//bullet.png")
	bullet = pygame.transform.scale_by(bullet, 0.25)

	walking = []
	running = []
	aimed_shooting = []
	flips = []

	for i in range(1, 13):
		walking.append(load_player_asset(i, type_="walking"))
		running.append(load_player_asset(i, type_="running"))

		if i <= 4:
			aimed_shooting.append(load_player_asset(i, type_="aimed shot"))

		if i <= 8:
			flips.append(load_player_asset(i, type_="flip"))


	return still_player_surf, walking, running, aim, aimed_shooting, bullet, flips

def draw_background(screen):
	screen.fill(SKY_BLUE)




if __name__ == "__main__":
	main()