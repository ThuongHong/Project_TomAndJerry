from game_structure.maze import Maze
from game_structure.character import Tom
from game_structure.game import GamePlay, load_GamePlay
import pygame
import time

def main():
    test_saveGame()
    # test_loadGame(59)

# ------- LOAD -------- #
def test_loadGame(id):
    pygame.init()

    screen = pygame.display.set_mode((1000, 650))
    screen.fill((0, 0, 0))
    clock = pygame.time.Clock()

    Game = load_GamePlay(id)
    # Game.spawn_random()
    # Game.game_centering()
    # pygame.time.wait(1000)
    i = 0
    j = 0 
    # Game.visualize_solution('GBFS')
    clock.tick(120)

    while Game.game_state == 'in_game':
        # Game.center_zoom_linear(10)
        Game.run()
        # i += 1
        # if i == 50:    
        #     Game.de_visualize_process()
        #     Game.visualize_process('DFS')
        #     Game.game_normal_view()


        pygame.display.update()

# ------- SAVE -------- #
def test_saveGame(): 
    pygame.init()

    screen = pygame.display.set_mode((1000, 650))
    screen.fill((0, 0, 0))
    clock = pygame.time.Clock()

    Game = GamePlay(user_id= 1,
                    maze_size= 20,
                    grid_size= 28,
                    start_coord_screen= (0, 0),
                    end_coord_screen= (500, 500),
                    scale= 1,
                    window_screen= screen,
                    energy= 1)
    Game.generate(algorithm= 'HAK', ondraw= False)
    # Game.select_position_spawn()
    Game.spawn_random()
    # Game.game_centering()
    # pygame.time.wait(1000)
    i = 0
    j = 0 
    # Game.visualize_solution('GBFS')
    clock.tick(120)

    while Game.game_state == 'in_game':
        # Game.center_zoom_linear(10)
        Game.run()
        i += 1
        if i == 50:    
            # Game.save_game()
            print('Save done')
        #     Game.de_visualize_process()
        #     Game.visualize_process('DFS')
        #     Game.game_normal_view()


        pygame.display.update()

if __name__ == '__main__':
    main()