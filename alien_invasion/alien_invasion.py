import sys
import pygame
from settings import Settings
from ship import Ship
from bullet import Bullet
from alien import Alien
from time import sleep
from game_stats import GameStats
from button import Button
from scoreboard import ScoreBoard


class AlienInvasion:
	"""Overall class to manage game assets and behaviour. """
	def __init__(self):
		"""initialize the game, and create the game resources"""
		pygame.init()
		self.settings = Settings()
		self.screen = pygame.display.set_mode((self.settings.screen_width, self.settings.screen_height))
		pygame.display.set_caption("Alien Invasion")
		# Create an instance to store game statistics and create a scoreboard
		self.stats = GameStats(self)
		self.sb = ScoreBoard(self)
		# Create an isntance of the ship class
		self.ship = Ship(self)  # the self argument here refers to the current instance of AlienInvasion(This gives Ship access to the games resources.)
		self.aliens = pygame.sprite.Group()
		self._create_fleet()
		# Make the play button
		self.play_button = Button(self, "Play")
		self.bullets = pygame.sprite.Group()
		# Set the background color, They are RGB colors (red = 255, 0, 0 ; green = 0, 255, 0 ; blue = 0, 0, 255)
		self.bg_color = (230, 230, 230)

	def run_game(self):
		"""Start the main loop for the game."""
		while True:
			# we call the method from inside the class using the dot notation with the variable self and the method name(these are helper methods)
			self._check_events()
			if self.stats.game_active:
				# call the ships update method.
				self.ship.update()
				self._update_bullets()
				self._update_aliens()
			self._update_screen()
			
	def _check_events(self):
		# Watch for the keyboard and mouse events.
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				sys.exit()
			elif event.type == pygame.KEYDOWN:
				self._check_keydown_events(event)	
			elif event.type == pygame.KEYUP:
				self._check_keyup_events(event)
			elif event.type == pygame.MOUSEBUTTONDOWN:
				mouse_pos = pygame.mouse.get_pos()
				self._check_play_button(mouse_pos)


	def _check_keydown_events(self, event):
		''' This responds to keypresses.'''
		if event.key == pygame.K_RIGHT:
			# Move the ship to the right.
			self.ship.moving_right = True
		elif event.key == pygame.K_LEFT:
			# Move ship to the left
			self.ship.moving_left = True
		elif event.key == pygame.K_q:
			sys.exit()
		elif event.key == pygame.K_SPACE:
			self._fire_bullet()

	def _check_keyup_events(self, event):
		''' This responds to release of key.'''
		if event.key == pygame.K_RIGHT:
			self.ship.moving_right = False
		elif event.key == pygame.K_LEFT:
			self.ship.moving_left = False

	def _check_play_button(self, mouse_pos):
		""" Start a new gaem when the player clicks play """
		button_clicked = self.play_button.rect.collidepoint(mouse_pos)
		if button_clicked and not self.stats.game_active:
			# Reset the games settings.
			self.settings.initialize_dynamic_settings()
			# Reset game statistics
			self.stats.reset_stats()
			self.stats.game_active = True
			self.sb.prep_score() # This sets the scoreboard back to zero after resetting the game stats.
			self.sb.prep_score()
			self.sb.prep_level()
			self.sb.prep_ships()

			# Hide the mouse cursor.
			pygame.mouse.set_visible(False)

			# get rid of remaining aliens and bullets.
			self.aliens.empty()
			self.bullets.empty()

			# Create a new fleet and center the ship.
			self._create_fleet()
			self.ship.center_ship()


	def _fire_bullet(self):
		""" Create a new bullet and add it to the bullet group """
		if len(self.bullets) < self.settings.bullets_allowed:
			new_bullet = Bullet(self)
			self.bullets.add(new_bullet)

	def _update_bullets(self):
		
		# Get rid of bullets that have disppeared from the screen on top.
		for bullet in self.bullets.copy():
			if bullet.rect.bottom <= 0:
				self.bullets.remove(bullet)
		#print(len(self.bullets))
		#print(self.bullets.copy())
		self._check_bullet_alien_collisions()

	def _check_bullet_alien_collisions(self):
		""" Respond to bullet alien collisions. """
		# Remove any bullets and aliens that have collided.
		self.bullets.update()
		''' Check for bullets that have hit aliens, if so get rid of the bullet and the alien '''
		collisions = pygame.sprite.groupcollide(self.bullets, self.aliens, True, True) # This is a dictionary.
		if collisions:
			for aliens in collisions.values(): # Each value in the collision dictionary is a list of aliens hit by a single bullet.
				self.stats.score += self.settings.alien_points * len(aliens)
			self.sb.prep_score()
			self.sb.check_high_score()

		# Below is to check if a fleet is destroyed.
		if not self.aliens:
			# Then destroy existing bullets and create a new fleet.
			self.bullets.empty()
			self._create_fleet()
			self.settings.increase_speed()

			# Increase level.
			self.stats.level += 1 # Increase the game level by 1
			self.sb.prep_level()  # Make sure the new level displays correctly

	def _create_fleet(self):
		# create a fleet of aliens
		# Create an alien and find the number of aliens in a row.
		# Spacing between each alien is equal to one alien width.
		alien = Alien(self)
		alien_width, alien_height = alien.rect.size
		# Calculation for available screen space to place aliens
		available_space_x = self.settings.screen_width - (2 * alien_width)
		# Calculation for the number of aliens that can be placed with 1 alien width space in between consecutive aliens.
		number_aliens_x = available_space_x // (2 * alien_width)

		# Determine the number of rows of aliens that can fit on the screen vertically
		ship_height = self.ship.rect.height
		available_space_y = (self.settings.screen_height - (3 * alien_height) - ship_height)
		number_rows = available_space_y // (2 * alien_height)

		# Create the full fleet of aliens.
		for row_number in range(number_rows):
			for alien_number in range(number_aliens_x):
				self._create_alien(alien_number, row_number)

	# Create a helper method for create alien and call it from _create_fleet
	def _create_alien(self, alien_number, row_number):
		# Create an alien and place it in the row
		alien = Alien(self)
		alien_width, alien_height = alien.rect.size
		alien.x = alien_width + 2 * alien_width * alien_number
		alien.rect.x = alien.x
		alien.rect.y = alien_height + 2 * alien.rect.height * row_number
		self.aliens.add(alien)

	def _check_fleet_edges(self):
		""" Respond appropritately if any aliens have reached an edge. """
		for alien in self.aliens.sprites():
			if alien.check_edges():
				self._change_fleet_direction()
				break

	def _change_fleet_direction(self):
		# Drop the entire fleet and change the fleet's direction.
		for alien in self.aliens.sprites():
			alien.rect.y += self.settings.fleet_drop_speed
		self.settings.fleet_direction *= -1

	def _update_aliens(self):
		''' Check if the fleet is at an edge, then update the positions of all aliens in the fleet. '''
		self._check_fleet_edges()
		self.aliens.update()

		# check for alien-ship collisions.
		if pygame.sprite.spritecollideany(self.ship, self.aliens):
			self._ship_hit()

		# Look for aliens hitting the bottom of the screen
		self._check_aliens_bottom()

	def _ship_hit(self):
		""" Respond to the ship being hit by an alien """
		if self.stats.ships_left > 0:
			# Decrement the ships left, and update the scoreboard.
			self.stats.ships_left -= 1
			self.sb.prep_ships()
		 

			# Get rid of any remaining aliens and bullets.
			self.aliens.empty()
			self.bullets.empty()

			# Create a new fleet and center the ship.
			self._create_fleet()
			self.ship.center_ship()
       
			# Pause.
			sleep(0.5)
		else:
			self.stats.game_active = False
			pygame.mouse.set_visible(True)

	def _check_aliens_bottom(self):
		""" Check if any aliens have reached the bottom of the screen. """
		screen_rect = self.screen.get_rect()
		for alien in self.aliens.sprites():
			if alien.rect.bottom >= screen_rect.bottom:
				# Treat this same as a ship got hit.
				self._ship_hit()
				break

	def _update_screen(self):
		# Updates images on the screen and flips to a new screen.
		self.screen.fill(self.settings.bg_color)
		self.ship.blitme()
		for bullet in self.bullets.sprites():
			bullet.draw_bullet()
		# Make alien appear on screen
		self.aliens.draw(self.screen)
		# Draw the play button if the game is inactive
		if not self.stats.game_active:
			self.play_button.draw_button()
		# Draw the score information to the screen
		self.sb.show_score()
		# make the most recently drawn screen visible.
		pygame.display.flip()



if __name__== "__main__":
	# Make the game instance, and run the game.
	ai = AlienInvasion()
	ai.run_game()


