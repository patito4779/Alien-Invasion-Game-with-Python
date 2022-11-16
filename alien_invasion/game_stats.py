class GameStats:
	''' Track stats for the Alien Invasion GAME '''
	def __init__(self, ai_game):
		""" Initialize statistics for the Alien Invasion. """
		self.settings = ai_game.settings
		self.reset_stats()
		# Start the game in an inactive state, so the game can only start when a player presses a button.
		self.game_active = False
		# High Score should never be reset.
		self.high_score = 0

	def reset_stats(self):
		# Initialize stats that can change during the game.
		self.ships_left = self.settings.ship_limit
		self.score = 0
		self.level = 1

