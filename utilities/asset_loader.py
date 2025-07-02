

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

	elif type_ == "sitting_shoot":
		path = f"Assets//sitting_shoot//sitting_shoot{str(index)}.png"

	elif type_ == "attack":
		path = f"Assets//attack//attack{str(index)}.png"

	try:
		asset = pygame.image.load(path)

	except:
		print (f"path {path} not found")
		return None


	return pygame.transform.scale_by(asset, 1.5).convert_alpha()


def load_player_offense_assets():
	aim = pygame.image.load("Assets//Aim.png")
	aim = pygame.transform.scale_by(aim, 1.5).convert_alpha()
	aimed_shooting = []
	attack = []
	sitting_shoot = []
	no_aim_shooting = []
	standing_reload = []


	for i in range(1, 13):
		standing_reload.append(load_player_asset(i, type_="standing_reload"))

		if i <= 4:
			aimed_shooting.append(load_player_asset(i, type_="aimed shot"))
			no_aim_shooting.append(load_player_asset(i, type_="noaim shot"))
			sitting_shoot.append(load_player_asset(i, type_="sitting_shoot"))
			attack.append(load_player_asset(i, type_="attack"))

	return aim, aimed_shooting, attack, sitting_shoot, standing_reload, no_aim_shooting

def load_player_movement_assets():
	walking = []
	running = []
	flips  = []

	for i in range(1, 13):
		walking.append(load_player_asset(i, type_="walking"))
		running.append(load_player_asset(i, type_="running"))

		if i <= 8:
			flips.append(load_player_asset(i, type_="flip"))

	return walking, running, flips


def load_player_still_assets():
	still_player_surf = pygame.image.load("Assets//Standing.png")
	still_player_surf = pygame.transform.scale_by(still_player_surf, 1.5).convert_alpha()

	sitting = pygame.image.load("Assets//Sitting.png")
	sitting = pygame.transform.scale_by(sitting, 1.5).convert_alpha()

	lying = pygame.image.load("Assets//Lie.png")
	lying = pygame.transform.scale_by(lying, 1.5).convert_alpha()

	return still_player_surf, sitting, lying


def load_bullet_assets():
	bullet = pygame.image.load("Assets//bullet.png")
	bullet = pygame.transform.scale_by(bullet, 0.25).convert_alpha()

	empty_bullet = pygame.image.load("Assets//empty_shell.png")
	empty_bullet = pygame.transform.scale_by(empty_bullet, 0.25).convert_alpha()

	return bullet, empty_bullet




# def load_player_assets():

# 	still_player_surf = pygame.image.load("Assets//Standing.png")
# 	still_player_surf = pygame.transform.scale_by(still_player_surf, 1.5).convert_alpha()

# 	sitting = pygame.image.load("Assets//Sitting.png")
# 	sitting = pygame.transform.scale_by(sitting, 1.5).convert_alpha()

# 	lying = pygame.image.load("Assets//Lie.png")
# 	lying = pygame.transform.scale_by(lying, 1.5).convert_alpha()

# 	aim = pygame.image.load("Assets//Aim.png")
# 	aim = pygame.transform.scale_by(aim, 1.5).convert_alpha()

# 	bullet = pygame.image.load("Assets//bullet.png")
# 	bullet = pygame.transform.scale_by(bullet, 0.25).convert_alpha()

# 	empty_bullet = pygame.image.load("Assets//empty_shell.png")
# 	empty_bullet = pygame.transform.scale_by(empty_bullet, 0.25).convert_alpha()

# 	walking = []
# 	running = []
# 	aimed_shooting = []
# 	no_aim_shooting = []
# 	flips = []
# 	standing_reload = []
# 	sitting_shoot = []
# 	attack = []

# 	for i in range(1, 13):
# 		walking.append(load_player_asset(i, type_="walking"))
# 		running.append(load_player_asset(i, type_="running"))
# 		standing_reload.append(load_player_asset(i, type_="standing_reload"))

# 		if i <= 4:
# 			aimed_shooting.append(load_player_asset(i, type_="aimed shot"))
# 			no_aim_shooting.append(load_player_asset(i, type_="noaim shot"))
# 			sitting_shoot.append(load_player_asset(i, type_="sitting_shoot"))
# 			attack.append(load_player_asset(i, type_="attack"))

# 		if i <= 8:
# 			flips.append(load_player_asset(i, type_="flip"))


# 	return still_player_surf, sitting, lying, walking, running, aim, aimed_shooting, attack, sitting_shoot, standing_reload, no_aim_shooting, bullet, empty_bullet, flips


def load_player_hurt_assets():
	hurt_textures = []
	death_textures = []

	for i in range(1, 6):
		death_textures.append(load_player_asset(i, type_="death"))

		if i <= 4:
			hurt_textures.append(load_player_asset(i, type_="hurt"))



	return hurt_textures, death_textures



def load_sfx():
	pygame.mixer.init()
	single_shot_sfx = pygame.mixer.Sound("Assets//sfx//single_shot.wav")
	reload_sfx = pygame.mixer.Sound("Assets//sfx//reload.mp3")
	rain_sfx = pygame.mixer.Sound("Assets//sfx//rain.mp3")


	return single_shot_sfx, reload_sfx, rain_sfx


def load_enemy_asset(index, type_="walking"):
	if type_ == "walking":
		path = f"Assets//enemy_walk//walk{str(index)}.png"

	elif type_ == "standing_shoot":
		path = f"Assets//enemy_standing_shoot//standing_shoot{str(index)}.png"

	elif type_ == "running":
		path = f"Assets//enemy_run//enemy_run{str(index)}.png"

	try:
		asset = pygame.image.load(path)

	except:
		print (f"path {path} not found")
		return None


	return pygame.transform.scale_by(asset, 1.5).convert_alpha()


def load_enemy_assets():
	enemy_standing = pygame.image.load("Assets//enemy_standing.png")
	enemy_standing = pygame.transform.scale_by(enemy_standing, 1.5).convert_alpha()

	walking = []
	running = []
	standing_shoot = []

	for i in range(1, 8):
		running.append(load_enemy_asset(i, type_="running"))
		walking.append(load_enemy_asset(i, type_="walking"))

		if i <= 4:
			standing_shoot.append(load_enemy_asset(i, type_="standing_shoot"))


	return enemy_standing, walking, running, standing_shoot


def load_boost_textures():
	heart_texture = pygame.transform.scale_by(pygame.image.load("Assets//boosts//heart.png"), 40/16).convert_alpha()
	stamina_texture = pygame.transform.scale_by(pygame.image.load("Assets//boosts//stamina.png"), 40/16).convert_alpha()


	return heart_texture, stamina_texture