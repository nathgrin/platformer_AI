"""
Platformer Game
"""
import arcade
import numpy as np
from ai import perceptron


# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 650
SCREEN_TITLE = "Platformer"

# Constants used to scale our sprites from their original size
CHARACTER_SCALING = 1
TILE_SCALING = 0.5
COIN_SCALING = 0.5
ZOMBIE_SCALING = 0.7

# Enemy stuff
SPAWN_INTERVAL = 150
ZOMBIE_SPEED = -7

# Movement speed of player, in pixels per frame
PLAYER_MOVEMENT_SPEED = 5
GRAVITY = 1
PLAYER_JUMP_SPEED = 15
NUMBER_OF_JUMPS = 2 # includes the first jump

# GA extra
WATCH_GAMES = True


def signed_distance_between_sprites(sprite1: arcade.Sprite, sprite2: arcade.Sprite) -> float:
    """distance is signed in x direction"""
    return np.sign(sprite1.center_x - sprite2.center_x)*arcade.get_distance_between_sprites(sprite1,sprite2)

def get_closest_sprite_positive(sprite: arcade.Sprite, sprite_list: arcade.SpriteList) -> tuple[arcade.Sprite, float]:
    """
    Given a Sprite and SpriteList, returns the closest sprite, and its distance.

    STOLEN from pyarcade get_closest_sprite

    :param Sprite sprite: Target sprite
    :param SpriteList sprite_list: List to search for closest sprite.

    :return: A tuple containing the closest sprite and the minimum distance.
             If the spritelist is empty we return ``None``.
    :rtype: Optional[Tuple[Sprite, float]]
    """
    if len(sprite_list) == 0:
        return None

    min_pos = 0
    min_distance = signed_distance_between_sprites(sprite, sprite_list[min_pos])
    min_distance = max(0,min_distance) # Only to the right
    
    # print(min_distance)
    for i in range(1, len(sprite_list)):
        distance = signed_distance_between_sprites(sprite, sprite_list[i])
        distance = max(0,distance)
        if distance < min_distance:
            min_pos = i
            min_distance = distance
    return sprite_list[min_pos], min_distance

class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self,enable_camera=True):

        # Call the parent class and set up the window
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        
        self.SCREEN_WIDTH = SCREEN_WIDTH
        self.SCREEN_HEIGHT = SCREEN_HEIGHT
        
        # Initialize AI
        self.ai = None
        self.multiple_ai = False
        self.ai_input = np.array([0,0,0,0])
        self.players_alive = None
        
        self.score_list = None
        
        # Our Scene Object
        self.scene = None

        # Separate variable that holds the player sprite
        self.player_sprite = None
        self.player_sprites = None
        
        # Our physics engine
        self.physics_engine = None
        self.physics_engines = None

        # Watch the game played?
        self.enable_camera = enable_camera

        # A Camera that can be used for scrolling the screen
        self.camera = None

        # A Camera that can be used to draw GUI elements
        self.gui_camera = None

        # Keep track of the score
        self.score = 0

        # Load sounds
        # self.collect_coin_sound = arcade.load_sound(":resources:sounds/coin1.wav")
        # self.jump_sound = arcade.load_sound(":resources:sounds/jump1.wav")

        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)

    def setup(self):
        """Set up the game here. Call this function to restart the game."""

        if self.enable_camera:
            # Set up the Game Camera
            self.camera = arcade.Camera(self.width, self.height)

            # Set up the GUI Camera
            self.gui_camera = arcade.Camera(self.width, self.height)

        # Keep track of the score
        self.score = 0

        # Initialize Scene
        self.scene = arcade.Scene()

        # Set up the player, specifically placing it at these coordinates.
        image_source = ":resources:images/animated_characters/female_person/femalePerson_idle.png"
        if self.multiple_ai:
            self.players_alive = [True for i in self.ai]
            self.number_alive = len(self.players_alive)
            self.score_list = [ 0 for i in self.ai]
            self.player_sprites = arcade.SpriteList()
            self.physics_engines = []
            # print("Add AIs")
            for i in range(len(self.ai)):
                player_sprite = arcade.Sprite(image_source, CHARACTER_SCALING)
                player_sprite.center_x = 256
                player_sprite.center_y = 96
                player_sprite.alpha = 100
                self.player_sprites.append(player_sprite)
                self.scene.add_sprite("Players", player_sprite)
        else:
            self.player_sprite = arcade.Sprite(image_source, CHARACTER_SCALING)
            self.player_sprite.center_x = 128
            self.player_sprite.center_y = 96
            self.scene.add_sprite("Player", self.player_sprite)

        
        # Spikewall of death
        spikes = arcade.Sprite("sprites/spikewall.png",hit_box_algorithm="None")
        spikes.center_x = 10
        spikes.center_y = SCREEN_HEIGHT//2
        self.scene.add_sprite("Spikes", spikes)
        
        
        # Create the ground
        wall = arcade.Sprite("sprites/ground.png", TILE_SCALING)
        wall.center_x = SCREEN_WIDTH//2
        wall.center_y = 32
        self.scene.add_sprite("Walls", wall)
    

        # Put some crates on the ground
        # This shows using a coordinate list to place sprites
        coordinate_list = [[512, 96], [256, 96], [768, 96]]
        if False:
            for coordinate in coordinate_list:
                # Add a crate on the ground
                wall = arcade.Sprite(
                    ":resources:images/tiles/boxCrate_double.png", TILE_SCALING
                )
                wall.position = coordinate
                self.scene.add_sprite("Walls", wall)

        # Use a loop to place some coins for our character to pick up
        # for x in range(128, 1250, 256):
        #     coin = arcade.Sprite(":resources:images/items/coinGold.png", COIN_SCALING)
        #     coin.center_x = x
        #     coin.center_y = 96
        #     self.scene.add_sprite("Coins", coin)
            
            
            
            
        # For incrementing spawns
        self.spawntimer = SPAWN_INTERVAL-5 # spawn almost immediately

        # Create the 'physics engine'
        if self.multiple_ai:
            for i in range(len(self.ai)):
                self.physics_engines.append(arcade.PhysicsEnginePlatformer(
                    self.player_sprites[i], gravity_constant=GRAVITY, walls=self.scene["Walls"]
                ))
                self.physics_engines[-1].enable_multi_jump(NUMBER_OF_JUMPS)
        else:
            self.physics_engine = arcade.PhysicsEnginePlatformer(
                self.player_sprite, gravity_constant=GRAVITY, walls=self.scene["Walls"]
            )

    def on_draw(self):
        """Render the screen."""
        if not self.enable_camera:
            return
        # Clear the screen to the background color
        self.clear()

        # Activate the game camera
        self.camera.use()

        # Draw our Scene
        self.scene.draw()

        # Activate the GUI camera before drawing GUI elements
        self.gui_camera.use()

        # Draw our score on the screen, scrolling it with the viewport
        score_text = f"Score: {self.score}"
        arcade.draw_text(
            score_text,
            10,
            10,
            arcade.csscolor.WHITE,
            18,
        )
        if self.multiple_ai:
            alive_text = f"Alive: {self.number_alive}"
            arcade.draw_text(
                alive_text,
                self.width-150,
                10,
                arcade.csscolor.WHITE,
                18,
            )

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed."""

        if key == arcade.key.UP or key == arcade.key.W:
            if self.physics_engine.can_jump():
                self.player_sprite.change_y = PLAYER_JUMP_SPEED
                # arcade.play_sound(self.jump_sound)
        elif key == arcade.key.LEFT or key == arcade.key.A:
            return
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            return
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key."""

        if key == arcade.key.LEFT or key == arcade.key.A:
            self.player_sprite.change_x = 0
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_sprite.change_x = 0

    def center_camera_to_player(self):
        screen_center_x = self.player_sprite.center_x - (self.camera.viewport_width / 2)
        screen_center_y = self.player_sprite.center_y - (
            self.camera.viewport_height / 2
        )
        if screen_center_x < 0:
            screen_center_x = 0
        if screen_center_y < 0:
            screen_center_y = 0
        player_centered = screen_center_x, screen_center_y

        self.camera.move_to(player_centered)


    def set_sprite_aside(self,sprite,x,y):
        
        sprite.center_x = x
        sprite.center_y = y
        sprite.change_x = 0
        sprite.change_y = 0

    def on_update(self, delta_time):
        """Movement and game logic"""

        # Move the player with the physics engine
        if self.multiple_ai:
            for i,engine in enumerate(self.physics_engines):
                if self.players_alive[i]:
                    engine.update()
        else:
            self.physics_engine.update()
        
        # Spawn enemies
        self.spawntimer += 1
        if self.spawntimer > SPAWN_INTERVAL: # Perhaps use arcade.schedule()
            
            self.spawn_enemy()
            
            self.spawntimer = 0
        
        # move ai players if multiple
        if self.multiple_ai:
            self.scene["Players"].update()
                
                
        
        # Move enemies
        if "Enemies" in self.scene.name_mapping:
            self.scene["Enemies"].update()
            
            # Hit enemies
            
            # See if we hit any Enemies
            the_list = self.scene["Players"] if self.multiple_ai else [ self.player_sprite ]
            for i,player_sprite in enumerate(the_list):
                if self.players_alive[i]:
                    enemy_hit_list = arcade.check_for_collision_with_list(
                        player_sprite, self.scene["Enemies"]
                    )
                    
                    for enemy in enemy_hit_list:
                        self.players_alive[i] = False
                        self.number_alive += -1
                        self.score_list[i] = self.score
                        self.set_sprite_aside(player_sprite,self.SCREEN_WIDTH-i*50,self.SCREEN_HEIGHT-50)
                        # print("Someone died",self.players_alive,self.score_list)
                        if sum(self.players_alive) == 0:
                            self.end_game()
                        break
                        # enemy.remove_from_sprite_lists()
                
                
            # See if enemy hit the spikes
            for spike in self.scene["Spikes"]:
                enemy_hit_list = arcade.check_for_collision_with_list(
                    spike, self.scene["Enemies"]
                )
                for enemy in enemy_hit_list:
                    enemy.remove_from_sprite_lists()
        
        
        
        if False:
            # See if we hit any coins
            coin_hit_list = arcade.check_for_collision_with_list(
                self.player_sprite, self.scene["Coins"]
            )

            # Loop through each coin we hit (if any) and remove it
            for coin in coin_hit_list:
                # Remove the coin
                coin.remove_from_sprite_lists()
                # Play a sound
                # arcade.play_sound(self.collect_coin_sound)
                # Add one to the score
                self.score += 1
        
        
        # Increment score each frame!
        self.score += 1
        
        if self.score > 10000:
            if self.multiple_ai:
                for i,alive in enumerate(self.players_alive):
                    if alive:
                        self.score_list[i] = self.score
            self.end_game()

        # Position the camera
        # if self.enable_camera:
        #     self.center_camera_to_player()
        
        
        # Next move for the AI
        if self.ai is not None:
            self.AI_move()
            
    def end_game(self):
        arcade.exit()
    
    def generate_ai_input(self,player_sprite: arcade.Sprite, physics_engine:arcade.PhysicsEnginePlatformer):
        self.ai_input[0] = int(physics_engine.can_jump())
        
        self.ai_input[1] = player_sprite.center_y
        if "Enemies" in self.scene.name_mapping:
            res = get_closest_sprite_positive(player_sprite,self.scene["Enemies"])
            if res is not None:
                closest,min_dist = res
                self.ai_input[2] = closest.center_x-player_sprite.center_x
                self.ai_input[3] = closest.center_y
        else:
            self.ai_input[2],self.ai_input[3] = 0,0
        
        return self.ai_input # 
    
    def AI_move(self):
        
        if self.multiple_ai:
            for i,ai in enumerate(self.ai):
                player_sprite = self.player_sprites[i]
                
                the_input = self.generate_ai_input(player_sprite,self.physics_engines[i])
                
                move = self.ai[i].run_net(the_input)
                if move == 1:
                    if self.physics_engines[i].can_jump():
                        # self.player_sprites[i].change_y = PLAYER_JUMP_SPEED
                        self.physics_engines[i].jump(PLAYER_JUMP_SPEED) # also calls increment_jump_counter
                        
                
            
            
        else:
            self.ai_input[0] = self.player_sprite.center_y
            if "Enemies" in self.scene.name_mapping:
                res = arcade.get_closest_sprite(self.player_sprite,self.scene["Enemies"])
                if res is not None:
                    closest,min_dist = res
                    self.ai_input[1] = closest.center_x-self.player_sprite.center_x
                    self.ai_input[2] = closest.center_y
            else:
                self.ai_input[1],self.ai_input[2] = 0,0
            
            move = self.ai.run_net(self.ai_input)
            
            if move == 1:
                self.on_key_press(arcade.key.UP,None)
        
            
    def spawn_enemy(self):
        
        randint = np.random.randint(3)
        if randint == 0:
            self._make_zombie()
        else:
            self._make_bee()
            
    def _make_bee(self):
        zombie = arcade.Sprite(":resources:images/enemies/bee.png", ZOMBIE_SCALING)
        
        randint = np.random.randint(16)
        
        zombie.center_x = SCREEN_WIDTH-50
        zombie.center_y = 96
        zombie.center_y = 100+randint*30 # ? Why is not same as character?
        
        zombie.change_x = ZOMBIE_SPEED
        
        self.scene.add_sprite("Enemies", zombie)
        
        
    def _make_zombie(self):
        
        zombie = arcade.Sprite(":resources:images/animated_characters/zombie/zombie_idle.png", ZOMBIE_SCALING)
        zombie.center_x = SCREEN_WIDTH-50
        zombie.center_y = 96
        zombie.center_y = 96+10 # ? Why is not same as character?
        
        zombie.change_x = ZOMBIE_SPEED
        
        self.scene.add_sprite("Enemies", zombie)
        

def main():
    """Main function"""
    window = MyGame()
    
    window.ai = [ perceptron() for i in range(8) ]
    window.multiple_ai = True
    
    window.setup()
    
    
    for i in range(len(window.ai)):
        # window.ai[i].scales[1][0] = 1
        window.ai[i].scales[1][1] = SCREEN_HEIGHT
        window.ai[i].scales[1][2] = SCREEN_WIDTH
        window.ai[i].scales[1][3] = SCREEN_HEIGHT
    
    
    arcade.run()

    
    print("DIED",window.score)
    print(window.score_list)

if __name__ == "__main__":
    main()