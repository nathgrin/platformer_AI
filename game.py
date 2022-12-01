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
ZOMBIE_SCALING = 1

# Enemy stuff
SPAWN_INTERVAL = 100
ZOMBIE_SPEED = -5

# Movement speed of player, in pixels per frame
PLAYER_MOVEMENT_SPEED = 5
GRAVITY = 0.75#1
PLAYER_JUMP_SPEED = 20


class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self):

        # Call the parent class and set up the window
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        
        
        # Initialize AI
        self.ai = None
        self.ai_input = np.array([0,0,0])
        

        # Our Scene Object
        self.scene = None

        # Separate variable that holds the player sprite
        self.player_sprite = None
        
        
        # Our physics engine
        self.physics_engine = None

        # A Camera that can be used for scrolling the screen
        self.camera = None

        # A Camera that can be used to draw GUI elements
        self.gui_camera = None

        # Keep track of the score
        self.score = 0

        # Load sounds
        self.collect_coin_sound = arcade.load_sound(":resources:sounds/coin1.wav")
        self.jump_sound = arcade.load_sound(":resources:sounds/jump1.wav")

        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)

    def setup(self):
        """Set up the game here. Call this function to restart the game."""

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
        self.player_sprite = arcade.Sprite(image_source, CHARACTER_SCALING)
        self.player_sprite.center_x = 128
        self.player_sprite.center_y = 96
        self.scene.add_sprite("Player", self.player_sprite)

        
        for y in range(96,3*96,96):
            spikes = arcade.Sprite(":resources:images/tiles/spikes.png", TILE_SCALING, angle=-90)
            spikes.center_x = 20
            spikes.center_y = y
            self.scene.add_sprite("Spikes", spikes)
        
        
        # Create the ground
        # This shows using a loop to place multiple sprites horizontally
        for x in range(0, 1250, 64):
            wall = arcade.Sprite(":resources:images/tiles/grassMid.png", TILE_SCALING)
            wall.center_x = x
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
        for x in range(128, 1250, 256):
            coin = arcade.Sprite(":resources:images/items/coinGold.png", COIN_SCALING)
            coin.center_x = x
            coin.center_y = 96
            self.scene.add_sprite("Coins", coin)
            
            
            
            
        # For incrementing spawns
        self.spawntimer = 0

        # Create the 'physics engine'
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite, gravity_constant=GRAVITY, walls=self.scene["Walls"]
        )

    def on_draw(self):
        """Render the screen."""

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

    def on_update(self, delta_time):
        """Movement and game logic"""

        # Move the player with the physics engine
        self.physics_engine.update()
        
        # Spawn enemies
        self.spawntimer += 1
        if self.spawntimer > SPAWN_INTERVAL:
            
            self.spawn_enemy()
            
            self.spawntimer = 0
        
        # Move enemies
        if "Enemies" in self.scene.name_mapping:
            self.scene["Enemies"].update()
            
            # Hit enemies
            
            # See if we hit any Enemies
            enemy_hit_list = arcade.check_for_collision_with_list(
                self.player_sprite, self.scene["Enemies"]
            )
            for enemy in enemy_hit_list:
                arcade.exit()
                enemy.remove_from_sprite_lists()
            
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

        # Position the camera
        self.center_camera_to_player()
        
        
        # Next move for the AI
        if self.ai is not None:
            self.AI_move()
            
    def AI_move(self):
    
        self.ai_input[0] = self.player_sprite.center_y
        if "Enemies" in self.scene.name_mapping:
            closest,min_dist = arcade.get_closest_sprite(self.player_sprite,self.scene["Enemies"])
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
            self._make_bee(randint)
            
    def _make_bee(self,randint):
        zombie = arcade.Sprite(":resources:images/enemies/bee.png", ZOMBIE_SCALING)
        zombie.center_x = SCREEN_WIDTH-50
        zombie.center_y = 96
        zombie.center_y = 96+randint*60 # ? Why is not same as character?
        
        zombie.change_x = ZOMBIE_SPEED
        
        self.scene.add_sprite("Enemies", zombie)
        
        
    def _make_zombie(self):
        
        zombie = arcade.Sprite(":resources:images/animated_characters/zombie/zombie_idle.png", ZOMBIE_SCALING)
        zombie.center_x = SCREEN_WIDTH-50
        zombie.center_y = 96
        zombie.center_y = 96+30 # ? Why is not same as character?
        
        zombie.change_x = ZOMBIE_SPEED
        
        self.scene.add_sprite("Enemies", zombie)
        


def main():
    """Main function"""
    window = MyGame()
    window.setup()
    
    window.ai = perceptron()
    window.ai.scales[1][0] = SCREEN_HEIGHT
    window.ai.scales[1][1] = SCREEN_WIDTH
    window.ai.scales[1][2] = SCREEN_HEIGHT
    
    
    arcade.run()

    
    print("DIED",window.score)

if __name__ == "__main__":
    main()