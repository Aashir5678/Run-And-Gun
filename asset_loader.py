

import pygame
pygame.init()

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

	elif type_ == "standing_reload":
		path = f"Assets//standing_reload//standing_reload{str(index)}.png"

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
	standing_reload = []

	for i in range(1, 13):
		walking.append(load_player_asset(i, type_="walking"))
		running.append(load_player_asset(i, type_="running"))
		standing_reload.append(load_player_asset(i, type_="standing_reload"))

		if i <= 4:
			aimed_shooting.append(load_player_asset(i, type_="aimed shot"))
			no_aim_shooting.append(load_player_asset(i, type_="noaim shot"))

		if i <= 8:
			flips.append(load_player_asset(i, type_="flip"))


	return still_player_surf, walking, running, aim, aimed_shooting, standing_reload, no_aim_shooting, bullet, empty_bullet, flips


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
	reload_sfx = pygame.mixer.Sound("Assets//sfx//reload.mp3")


	return single_shot_sfx, reload_sfx


