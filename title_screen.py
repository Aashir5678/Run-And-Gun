import pygame
from utilities.constants import *
from utilities.asset_loader import load_player_assets
from utilities.map_generator import *
from sprites.player import Player
from random import randint

pygame.init()

def title_screen(seed=None):

	screen = pygame.display.set_mode(SCREEN_SIZE)

	run = True
	
	if seed is None:
		seed = randint(-9999, 9999)
		# seed = 7168

	
	surface_blocks, blocks = generate_new_terrain(screen, 0, seed, HEIGHT_FACTOR)
	title = pygame.transform.scale_by(pygame.image.load("Assets//run_and_gun_title.png"), 2)

	clock = pygame.time.Clock()
	avg_block_height = 0

	for block in surface_blocks:
		avg_block_height += block.y
	

	avg_block_height = avg_block_height / len(surface_blocks)



	while run:
		clock.tick(FPS)
		screen.fill(SKY_BLUE)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False
				break

		if pygame.mouse.get_pressed()[0] or pygame.mouse.get_pressed()[2]:
			break

		for block in blocks:
			block.draw()

		screen.blit(title, ((SCREEN_WIDTH // 2) - (title.get_width() // 2), avg_block_height - title.get_height()))
		pygame.display.update()


	return seed, run


if __name__ == "__main__":
	title_screen()