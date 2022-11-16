class Settings():
	""" this stores all the settings for the alien invasion game"""
	def __init__(self):
		""" Init the game settings"""
		# screen settings
		self.screen_width = 1200
		self.screen_height = 800
		self.bg_color = (230, 230, 230)
		# ship settings 
		
		self.ship_limit = 3 # number of ships the player is allowed to start with.
		
		
		self.bullet_width = 3
		self.bullet_height = 15
		self.bullet_color = (60, 60, 60)
		self.bullets_allowed = 3 # This limits number of bullets allowed on the screen to 3
		
		self.fleet_drop_speed = 20
		
		# How quickly the game speeds up
		self.speedup_scale = 1.1

		# How quickly the alien point values increase
		self.score_scale = 1.5

		self.initialize_dynamic_settings()

	def initialize_dynamic_settings(self):
		''' Initialize settins that change throughout the game '''
		self.ship_speed = 1.5 # Now the position of the ship is adjusted by a value of 1.5pixels instead of 1px
		# The game bullet settings
		self.bullet_speed = 3.0
		# Alien settings
		self.alien_speed = 1.0
		# fleet_direction of 1 represents right; -1 represents left.
		self.fleet_direction = 1
		# Scoring
		self.alien_points = 50

	def increase_speed(self):
		# Increase speed settings and alien point values
		self.ship_speed *= self.speedup_scale
		self.bullet_speed *= self.speedup_scale
		self.alien_speed *= self.speedup_scale

		self.alien_points = int(self.alien_points * self.score_scale)
		#print(self.alien_points)
