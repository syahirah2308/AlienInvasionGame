import sys
from time import sleep

import pygame

from settings import Settings
from game_stats import GameStats  
from scoreboard import Scoreboard
from button import Button
from ship import Ship
from bullet import Bullet
from alien import Alien

class AlienInvasion:
    """Overall class to manage game assets and behaviour """

    def __init__(self):
        """ Initialising the game, and create game resources """
        pygame.init()
        self.settings = Settings()

        #smaller screen mode
        self.screen = pygame.display.set_mode((self.settings.screen_width, self.settings.screen_height))
        self.screen = pygame.display.set_mode((1200, 800))

        #Full screen mode
        #self.screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
        #self.settings.screen_width  = self.screen.get_rect().width
        #self.settings.screen_height = self.screen.get_rect().height

        pygame.display.set_caption("Alien Invasion")

        #create an instances to store game statistics and scoreboards. 
        self.stats = GameStats(self)
        self.sb = Scoreboard(self)
        
        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()

        self._create_fleet()

        #make the play button. 
        self.play_button = Button(self,"Play")

        #set background color.
        self.bg_color = (230, 230, 230)

    def run_game(self):
        """ Start the main loop for the games. """

        while True:
            # watch the keyboard and mouse events.
            self._check_events()
            if self.stats.game_active:
                self.ship.update()
                #self.bullets.update()
                self._update_bullets()
                self._update_aliens()

            self._update_screen()

            #Get rid of bullets that ave dissapeared. 
            for bullet in self.bullets.copy():
                if bullet.rect.bottom <= 0:
                    self.bullets.remove(bullet)
            #print(len(self.bullets))   
            #          
            #self._update_bullets()
            #self._update_screen()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()

            #Redraw the screen during each pass through the loop. 
            self.screen.fill(self.settings.bg_color)
            self.ship.blitme()

            # Make the most recently drawn visible.
            pygame.display.flip()


    def _check_events(self):
        """ Responds to keypress and mouse events.""" 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                    sys.exit()
            elif event.type == pygame.KEYDOWN:
                #if event.key == pygame.K_RIGHT:
                    # move the ship to the righht. 
                    #self.ship.rect.x += 1
                    #self.ship.moving_right = True
                #elif event.key == pygame.K_LEFT:
                 #   self.ship.moving_left = True
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP: 
               # if event.key == pygame.K_RIGHT:
                #    self.ship.moving_right = False
               # elif event.key == pygame.K_LEFT:
                #    self.ship.moving_left = False
                self._check_keyup_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)


    def _check_play_button(self, mouse_pos):
        """ Start a new game when player click Play button. """ 
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.stats.game_active:
            #reset the game settings. 
            self.settings.initialize_dynamic_settings()

            #reset the game statistic. 
            self.stats.reset_stats()
            self.stats.game_active = True 
            self.sb.prep_score()
            self.sb.prep_level()
            self.sb.prep_ships()

            #get rid of remaining aliens and bullets. 
            self.aliens.empty()
            self.bullets.empty()

            #create new fleet and center the ship. 
            self._create_fleet()
            self.ship.center_ship()

            #hide the mouse cursor. 
            pygame.mouse.set_visible(False)
    
    def _check_keydown_events(self, event):
        """ Responds to keypress.""" 
        if event.key == pygame.K_RIGHT:
            #move the ship to the righht. 
            #self.ship.rect.x += 1
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_a:
            self.ship.moving_left = True
        elif event.key == pygame.K_d:
            self.ship.moving_right = True
        elif event.key == pygame.K_q:
            sys.exit()
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()

    def _check_keyup_events(self, event):
        """ Responds to key release. """ 
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False
        elif event.key == pygame.K_a:
            self.ship.moving_left = False
        elif event.key == pygame.K_d:
            self.ship.moving_right = False
        elif event.key == pygame.K_q:
            sys.exit()

    def _fire_bullet(self):
        """ Create a new bullet and it to the bullets group. """ 
        if len(self.bullets )< self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)

    def _update_bullets(self):
        """ Update positions of bullets and get rid of old bullets.""" 
        #Update bullets positions. 
        self.bullets.update()

        #Get rid of bullets that have dissapeared. 
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)
            
        self._check_bullet_alien_collision()


    def _check_bullet_alien_collision(self):
        """ Responds to bullet-alien collision. """ 
        #Remove any bullets and aliens that have collied. 
        #check for any bullets that have hit aliens. 
        #if so, get rid o the bullet and aliens. 
        collisions = pygame.sprite.groupcollide(self.bullets, self.aliens, True, True)

        if collisions:
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points * len(aliens)
            self.sb.prep_score()
            self.sb.check_high_score()

        if not self.aliens:
            #destroy existing bullets and create new fleet. 
            self.bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()

            #increase level. 
            self.stats.level += 1
            self.sb.prep_level()

    def _update_aliens(self):
        """Check if the fleet is at an edge, then update the positions of all aliens in the fleet.""" 
        self._check_fleet_edges()
        self.aliens.update()

        #look for alien-ship collision. 
        if pygame.sprite.spritecollideany(self.ship, self.aliens): 
            self._ship_hit()

        #look for aliens hitting the bottoms of the screen. 
        self._check_aliens_bottom()    

        
    def _update_screen(self):
        """ Update images on the scree, and flup to new screen. """ 
        self.screen.fill(self.settings.bg_color)
        self.ship.blitme()

        for bullet in self.bullets.sprites():
            bullet.draw_bullet()

        self.aliens.draw(self.screen)

        #draw the score information. 
        self.sb.show_score()

        #DRAW THE PLAY BUTTON IF THE GAME IS INACTIVE
        if not self.stats.game_active:
            self.play_button.draw_button()

        pygame.display.flip()

    def _create_fleet(self):
        """ Create the fleet of alien. """ 
        #make an alien  and find the amount of alien in a row. 
        alien = Alien(self)
        #self.aliens.add(alien)
        #alien_width = alien.rect.width
        alien_width, alien_height = alien.rect.size
        available_space_x = self.settings.screen_width - (2 * alien_width)
        number_aliens_x = available_space_x // (2 * alien_width)

        #determine the number of rows of aliens that fit on the screen. 
        ship_height = self.ship.rect.height
        available_space_y = (self.settings.screen_height - (3 * alien_height) - ship_height)
        number_rows = available_space_y // (2 * alien_height)

        #create the full fleet of aliens. 
        for row_number in range(number_rows):
            #create the first row of aliens. 
            for alien_number in range(number_aliens_x):
                #create an alien and place it in the row. 
                self._create_alien(alien_number, row_number)


    def _create_alien(self, alien_number, row_number):
        """ Create an alien and place it in the rows """ 
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        alien.x = alien_width + 2 * alien_width * alien_number
        alien.rect.x = alien.x
        alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number
        self.aliens.add(alien)

    def _check_fleet_edges(self):
        """Respond appropriately if any aliens have reached an edge. """ 
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_directions()
                break

    def _change_fleet_directions(self):
        """ Drop the entire fleet and change the fleets direction. """ 
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed 
        self.settings.fleet_direction *= -1

    def _ship_hit(self): 
        """ Responds to the ship being hit by an alien. """ 
        if self.stats.ships_left > 0:
            #decrement ships_left and update the scoreboard . 
            self.stats.ships_left -= 1
            self.sb.prep_ships()

            #get rid of any remaining aliens and bullets. 
            self.aliens.empty()
            self.bullets.empty()

            #create new fleet and center the ship. 
            self._create_fleet()
            self.ship.center_ship()

            #create a new fleet and center the ship. 
            self._create_fleet()
            self.ship.center_ship()

            #Pause. 
            sleep(0.5)
        else: 
            self.stats.game_active = False
            pygame.mouse.set_visible(True)


    def _check_aliens_bottom(self):
        """Check if any aliens have reached the bottom of the screen. """ 
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                #treat this the same as ship got hit. 
                self._ship_hit()
                break
 
if __name__ == '__main__':
    #Make a game instance, and run the game
    ai = AlienInvasion()
    ai.run_game()
