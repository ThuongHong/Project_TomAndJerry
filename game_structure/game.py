import pygame
import sqlite3
from game_structure.grid import GridCell
from game_structure.energy_items import EnergyItem
from game_structure.maze import Maze
from game_structure.character import Tom, Jerry
from game_structure.utility import choose_k_point_in_path, choose_point_in_path
from algorithm.draw_utility import mark_grid
from algorithm.SBFS import SBFS
from algorithm.BDFS import BDFS
from algorithm.GBFS import GBFS
from solving_maze.solving_maze import solve_maze
import json
import random

def str_to_tuple(encode_str: str) -> tuple[int]:
    x, y = encode_str.lstrip('(').rstrip(')').split(',')
    return (int(x), int(y))


class GamePlay():
    Game_States = ['start', 'in_game', 'save_game', 'win_game']
    Game_K_Energy = [10, 20, 50]

    def __init__(self,
                 user_id: int = 1,
                 maze_size: int = 20,
                 grid_size: int = 30,
                 start_coord_screen: tuple[int] = (0, 0),
                 end_coord_screen: tuple[int] = (700, 700),
                 player_skin: str = 'Normal',
                 energy: int = 0,
                 scale: int = 1,
                 window_screen= None,
                 **kwargs):
        """Intialize the basic information of Game

        Args:
            maze_size (int, optional): Maze_size. Defaults to 20.
            grid_size (int, optional): Grid_size. Defaults to 30.
            start_coord_screen (tuple[int], optional): Start_coord_for draw_maze. Defaults to (0, 0).
            end_coord_screen (tuple[int], optional): End_coord_for_draw_maze. Defaults to (700, 700).
            screen (_type_, optional): The Game Screen. Defaults to None.
            player_skin (str, optional): Feature. Defaults to 'Normal'.
            energy (int, optional): Feature. Defaults to 0.
            scale (int, optional): Scale. Defaults to 1.
        """
        self.user_id = user_id

        # self.grid_size = int(20 * 28 / maze_size)
        self.grid_size = grid_size
        if maze_size == 100:
            self.grid_size = 19
        # 20 -> 28

        self._maze_size = maze_size

        self.window_screen = window_screen
        
        # Set the game mode -> easy to store in database
        if self.maze_size == 20:
            self.game_mode = 'Easy'
        elif self.maze_size == 40:
            self.game_mode = 'Medium'
        elif self.maze_size == 100:
            self.game_mode = 'Hard'
        else:
            self.game_mode = 'NULL'

        self.energy = energy
        if self.energy:
            self.Energy_Items = pygame.sprite.Group()
        else: self.Energy_Items = None

        self.player_skin = player_skin
        
        self.screen_size = (maze_size * self.grid_size, (maze_size + 2) * self.grid_size + 40)
        self.screen = pygame.Surface(self.screen_size, pygame.SCALED)
        self.screen_vector = pygame.math.Vector2(self.screen_size)
        self.screen_rect = self.screen.get_rect(center= (500, 325))

        self.maze_surface = pygame.Surface((650, 650))

        self.scale_surface_offset = pygame.math.Vector2()
        
        self.scale = scale
        
        self.is_draw_solution = False
                
        self.game_state = 'start'

        self.solve_maze_algorithm = 'BFS'

        self.solving_grid_process = None
        self.solve_position = None
        self.solve_index = 0
        
        self.is_move = False

        self.is_stop_process = True

        self.frame = 0
    
    @property
    def maze_size(self):
        return self._maze_size
    
    @maze_size.setter
    def maze_size(self, new_size):
        self._maze_size = new_size
        
        if self.maze_size == 20:
            self.game_mode = 'Easy'
        elif self.maze_size == 40:
            self.game_mode = 'Medium'
        elif self.maze_size == 100:
            self.game_mode = 'Hard'
        else:
            self.game_mode = 'NULL'

    @property
    def step_moves(self):
        return self.player.sprite.step_moves
    
    # @property
    # def info(self):
    #     return f"Game end in {self.get_time} after {self.step_moves} moves"
    
    @property
    def get_time(self):
        mili_sec = pygame.time.get_ticks() - self.start_time

        return f"{mili_sec / 1000} s"
    
    def visualize_solution(self, algorithm: str = 'GBFS'):
        self.is_draw_solution = True
        self.solve_maze_algorithm = algorithm
    def de_visualize_solution(self):
        self.is_draw_solution = False
    
    def visualize_process(self, algorithm: str = 'BFS'):
        self.is_move = True

        self.draw_solving_process = True
        
        self.solve_maze_algorithm = algorithm
        
        self.solving_grid_process = solve_maze(
            self.player.sprite,
            self.Maze,
            algorithm= self.solve_maze_algorithm,
            is_process= True,
            adjust_start_position= self.solve_position
        )

        self.solve_index = 0

        self.is_stop_process = False
    def de_visualize_process(self):
        self.is_stop_process = True
        if self.solving_grid_process:
            self.solve_position = self.solving_grid_process[self.solve_index]

    def create_start_end_energy(self, 
                                start: tuple[int, int], 
                                end: tuple[int, int], 
                                is_in: bool, 
                                energy_lst: list[tuple[int, int]]):
        if is_in:
            # TODO
            # path_list= SBFS(
            #     grids= self.Maze.grids,
            #     player_current_position= start,
            #     player_winning_position= end
            # )
            # OR 
            path_list= GBFS(
                grids= self.Maze.grids,
                player_current_position= start,
                player_winning_position= end
            )

        else:
            path_list= BDFS(
                grids= self.Maze.grids,
                player_current_position= start,
                player_winning_position= end,
                algorithm= 'BFS'
            )

        choosen_place = choose_point_in_path(
            path_list= path_list,
            energy_list= energy_lst,
            grids= self.Maze.grids
        )

        if choosen_place:
            if start not in choosen_place and start not in energy_lst:
                try: 
                    EnergyItem(
                        group= self.Energy_Items,
                        grid_position= start,
                        grid_size= self.grid_size,
                        hp= len(BDFS(
                            grids= self.Maze.grids,
                            player_current_position= start,
                            player_winning_position= choosen_place[0],
                            algorithm= 'BFS'
                        ))
                    )
                except ValueError:
                    print(start, choosen_place[0])

                energy_lst.append(start)
            
            for place_index in range(len(choosen_place)):
                
                place = choosen_place[place_index]
                
                try: 
                    EnergyItem(
                        group= self.Energy_Items,
                        grid_position= place,
                        grid_size= self.grid_size,
                        hp= len(BDFS(
                            grids= self.Maze.grids,
                            player_current_position= place,
                            player_winning_position= end if place_index + 1 == len(choosen_place) else choosen_place[place_index + 1],
                            algorithm= 'BFS'
                        ))
                    )
                except ValueError:
                    print(place, place_index, choosen_place)

                energy_lst.append(place)
        
        return energy_lst
            
    def generate_energy_item(self):
        # READ THE ENERGY_IDEA.TXT
        self.scale = 20 / self.Maze.maze_size
        # Placement Problem

            # Min path
        min_moves_lst_gbfs = solve_maze(player= self.player.sprite, 
                                   maze= self.Maze,
                                   algorithm= 'GBFS')
        min_moves_lst_bfs = solve_maze(player= self.player.sprite, 
                                   maze= self.Maze,
                                   algorithm= 'BFS')

            # Choose the start position of branch
        
        branch_place_lst_gbfs = choose_k_point_in_path(self.Maze.grids, min_moves_lst_gbfs, int(self.Maze.maze_size * 10 / 20))
        branch_place_lst_bfs = choose_k_point_in_path(self.Maze.grids, min_moves_lst_bfs, 0)

        branch_place_lst = branch_place_lst_gbfs
        
        if len(branch_place_lst_bfs) > len(branch_place_lst_gbfs):
            branch_place_lst = branch_place_lst_bfs

        real_index_lst = []
        real_index_lst.append(0)
        real_len = 1

        for i in range(1, len(branch_place_lst)):
            min_len = len(BDFS(
                self.Maze.grids,
                player_current_position= branch_place_lst[real_index_lst[real_len - 1]],
                player_winning_position= branch_place_lst[i],
                algorithm= 'BFS'
            ))

            another_len = len(SBFS(
                self.Maze.grids,
                player_current_position= branch_place_lst[real_index_lst[real_len - 1]],
                player_winning_position= branch_place_lst[i],
            ))

            if ((another_len < 7 and another_len >= min_len)
                or (min_len < another_len < 6 + min_len)
                or (10 <= another_len <= 13 and min_len > 4)):
                real_index_lst.append(i)
                real_len += 1
                    
        if branch_place_lst:
            real_branch_lst = [branch_place_lst[i] for i in real_index_lst]
        else: return []
        
        energy_lst = []
        
        for i in range(1, len(branch_place_lst)):
            branch_place = branch_place_lst[i]

            if i == len(branch_place_lst) - 1:
                start = branch_place
                end = self.Maze.end_position
            else:
                start = branch_place
                end = branch_place_lst[i + 1]
            
            energy_lst = self.create_start_end_energy(
                start= start,
                end= end,
                is_in= branch_place in real_branch_lst,
                energy_lst= energy_lst
            )

        return energy_lst

    def generate(self, 
                 algorithm= 'DFS', 
                 ondraw: bool = True,
                 draw_speed: str = 'FAST'):
        """This method will generate new game

        Args:
            algorithm (str, optional): Generate Algorithm. Defaults to 'DFS'.
            ondraw (bool, optional): Want to see process or not. Defaults to True.
            draw_speed (str, optional): Speed Showing Process. Defaults to 'FAST'.
        """
        # Intialize super basic maze
        self.Maze = Maze(
            maze_size= self.maze_size,
            maze_grid_size= self.grid_size,
            scale= self.scale,
            screen= self.screen,
            window_screen= self.window_screen
        )

        # Generate that maze
        self.Maze.generate_new_maze(algorithm= algorithm,
                                    draw= ondraw,
                                    draw_speed= draw_speed)
        
        # After generate maze -> Ingame -> Save game data to Database
        # Insert to database
        
        # Set the connecttion with Game database
        db_connect = sqlite3.connect(r'database/TomJerry.db')
        db_cursor = db_connect.cursor()

        # Insert to table games (this table store game_information)
        db_cursor.execute('''INSERT INTO "games"("maze_size", "game_mode", "energy_mode", "grid_size", "player_skin", "generate_algorithm")
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            self.Maze.maze_size,
            self.game_mode,
            self.energy,
            self.grid_size,
            self.player_skin,
            algorithm
        )            
        )
        
        # Set the id for this game
        # After insert to database. Database automatically give us an id for that game
        self.id = list(db_cursor.execute('SELECT "id" FROM "games" ORDER BY "id" DESC LIMIT 1'))[0][0]

        # Change the game_state to In game
        self.set_new_game_state('in_game')

        # Insert relative between user and game
        db_cursor.execute('INSERT INTO "played" VALUES(?, ?)', (self.user_id, self.id))

        # Push all the change information to the real database
        db_connect.commit()

    def spawn_random(self):
        self.Maze.spawn_start_end_position('TOP_BOTTOM')
        self.create_player()

    def select_position_spawn(self):
        self.scale = 20 / self.Maze.maze_size

        while True:
            counter = 0

            self.update_screen()            
            self.Maze.update(scale= self.scale)
            self.Maze.draw(self.screen)
            
            if self.Maze.is_have_start():
                mark_grid(self.Maze.grids,
                          self.screen,
                          self.Maze.start_position,
                          COLOR= (0, 0, 255))
                counter += 1
            
            if self.Maze.is_have_end():
                mark_grid(self.Maze.grids,
                          self.screen,
                          self.Maze.end_position,
                          COLOR= (255, 0, 0))
                counter += 1
            
            if counter == 2:
                if self.Maze.spawn_start_end_position(
                    option= 'SELECT',
                    start_position= self.Maze.start_position,
                    end_position= self.Maze.end_position
                ):
                    break
                else:
                    self.Maze.grids[self.Maze.start_position].is_start = False
                    self.Maze.grids[self.Maze.end_position].is_end = False
                    self.Maze.start_position = None
                    self.Maze.end_position = None

            scale_surface = pygame.transform.scale(self.screen, self.screen_vector * self.scale)
            scale_rect = scale_surface.get_rect(center= (500, 325))

            self.window_screen.blit(scale_surface, scale_rect.topleft + self.scale_surface_offset)

            events = pygame.event.get()

            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.Maze.update(maze= self.Maze,
                                     scale= self.scale, events= events, 
                                     screen= self.screen, 
                                     topleft_info= scale_rect.topleft + pygame.math.Vector2(0, 40) * self.scale)
            

                        
            pygame.display.update()
        self.scale = 1

        self.create_player()
        
    def create_player(self):
        """This method will create player like Tom after Maze are generate and start_end is good
        """
        self.player = pygame.sprite.GroupSingle()
        
        self.Tom = Tom(self.Maze.start_position, 
                self.grid_size, 
                self.scale,
                screen= self.screen,
                window_screen = self.window_screen)
        
        self.npc = pygame.sprite.GroupSingle()
        self.npc.add(
            Jerry(self.Maze.end_position, 
              self.grid_size, 
              self.scale,
              screen= self.screen,
              window_screen = self.window_screen
        ))

        self.player.add(self.Tom)
        
        if self.energy:
            self.energy_lst = self.generate_energy_item()

            if self.energy_lst:
                self.player.sprite.set_hp(first_energy= self.energy_lst[0],
                                        grids= self.Maze.grids)
            else:
                self.player.sprite.set_hp(first_energy= self.Maze.end_position,
                                        grids= self.Maze.grids)


        self.set_new_game_state('in_game')

        # self.Maze.draw(self.screen)
        
        # pygame.image.save(self.screen, f'database/maze_images/Game_{self.id}.png')

        # self.Maze.image = pygame.image.load(f'database/maze_images/Game_{self.id}.png').convert_alpha()

        self.start_time = pygame.time.get_ticks()

    def set_new_game_state(self, new_state: str):
        """Change the value of game_state

        Args:
            new_state (str): ENUM {'start', 'play', 'save', 'win'}
        """
        if new_state in self.Game_States:
            self.game_state = new_state

    def update_screen(self):
        # This one just for test -- DON'T HAVE ANY BEAUTIFUL !!!
        self.window_screen.fill((0, 0, 0))
        self.screen.fill((0, 0, 0))

    def run(self):
        """This method will use in a while loop
        Get all the event while th game is run and handle it
        """  
        # Draw background
        self.update_screen()        
        self.Maze.update(scale= self.scale)
        self.player.update(scale= self.scale, 
                           maze= self.Maze, 
                           offset= self.scale_surface_offset,
                           energy_grp= self.Energy_Items)
        self.npc.update(scale= self.scale,
                        offset= self.scale_surface_offset)
        
        self.Maze.draw(self.screen)
        # self.Maze.image_draw(self.screen)
        if self.Energy_Items: self.Energy_Items.draw(self.screen)
        self.npc.draw(self.screen)
        self.player.draw(self.screen)
        


        # Like normal
        events = pygame.event.get()
        for event in events:
            # QUIT
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            # MOVE -> Dang mac dinh la khi move thi show process se bi dung
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.player.update(direction= 'L', maze= self.Maze, energy_grp= self.Energy_Items)
                    # self.de_visualize_process()
                    # self.de_visualize_solution()
                    # self.is_move = True
                elif event.key == pygame.K_RIGHT:
                    self.player.update(direction= 'R', maze= self.Maze, energy_grp= self.Energy_Items)
                    # self.de_visualize_process()
                    # self.de_visualize_solution()
                    # self.is_move = True
                elif event.key == pygame.K_UP:
                    self.player.update(direction= 'T', maze= self.Maze, energy_grp= self.Energy_Items)
                    # self.de_visualize_process()                     
                    # self.de_visualize_solution()                   
                    # self.is_move = True
                elif event.key == pygame.K_DOWN:
                    self.player.update(direction= 'B', maze= self.Maze, energy_grp= self.Energy_Items)
                    # self.de_visualize_process()                      
                    # self.de_visualize_solution()                  
                    # self.is_move = True
                elif event.key == pygame.K_e:
                    self.scale += 0.1
                elif event.key == pygame.K_f:
                    self.scale -= 0.1
                elif event.key == pygame.K_w:
                    self.scale_surface_offset.y += 50 * self.scale
                elif event.key == pygame.K_a:
                    self.scale_surface_offset.x += 50 * self.scale
                elif event.key == pygame.K_s:
                    self.scale_surface_offset.y -= 50 * self.scale
                elif event.key == pygame.K_d:
                    self.scale_surface_offset.x -= 50 * self.scale
                elif event.key == pygame.K_SPACE:
                    self.game_centering()
            # elif event.type == pygame.MOUSEBUTTONDOWN:
            #     self.Maze.update(events= events)

        # Update if change scale and draw all the maze
        # self.Maze.update(scale= self.scale)

        # self.Maze.draw(self.screen)
        # self.Maze.image_draw(self.screen)
        # Same but for player
        # self.player.update(scale= self.scale, 
        #                    maze= self.Maze, 
        #                    offset= self.scale_surface_offset)

        # self.player.draw(self.screen)

        # If draw_process is True so this one will run
        self.draw_process()

        # Same
        self.draw_solution()

        # If the game is win -> Save to leaderboard
        if self.check_win():
            self.save_leaderboard()

        # scale_surface = pygame.transform.rotozoom(self.screen, 0, self.scale)
        scale_surface = pygame.transform.scale(self.screen, self.screen_vector * self.scale)
        scale_rect = scale_surface.get_rect(center= (500, 325))

        self.window_screen.blit(scale_surface, scale_rect.topleft + self.scale_surface_offset)

        # pygame.display.update()

    def draw_solution(self):
        """Draw solution from player current position
        """
        if self.is_draw_solution:
            self.player.update(maze= self.Maze,
                                scale= self.scale,
                                show_solution= True,
                                algorithm= self.solve_maze_algorithm)

    def draw_process(self):
        """Each one loop through this method. This one will draw one more grid in process list
        """

        # Neu khong bi dung va co process_list -> Draw tang dan
        if not self.is_stop_process and self.solving_grid_process:
            for i in range(self.solve_index + 1):
                mark_grid(self.Maze.grids,
                          self.screen,
                          self.solving_grid_process[i])
                            
            pygame.time.wait(5)

            self.solve_index += 1
            if self.solve_index == len(self.solving_grid_process):
                # self.solving_grid_process = []
                self.solve_index -= 1

                self.solve_position = None

                self.visualize_solution(algorithm= self.solve_maze_algorithm)

        # Neu bi dung va co process list -> Draw nhung cai hien tai
        elif self.is_stop_process and self.solving_grid_process:
            if not self.is_move:
                for i in range(self.solve_index):
                    mark_grid(self.Maze.grids,
                                self.screen,
                                self.solving_grid_process[i])

        # Neu nhan vat di chuyn hay khong co process_list va bi dung
        elif self.is_move:
            self.solve_position = None
            self.solving_grid_process = []
            self.solve_index = 0
            # self.solving_grid_process = []

    def check_win(self):
        if self.player.sprite.position == self.Maze.end_position:
            self.game_state = 'win'
            return True
        return False

    def save_game(self):
        """Save for the game for later load
        """
        db_connect = sqlite3.connect(r'database/TomJerry.db')

        db_cursor = db_connect.cursor()

        maze_data = []
        for i in range(self.Maze.maze_size):
            for j in range(self.Maze.maze_size):
                maze_data.append(
                    self.Maze.grids[i, j].walls
                )

        maze_data.append(
            self.Maze.grids[self.Maze.start_position[0], -1].walls
        )
        
        maze_data.append(
            self.Maze.grids[self.Maze.end_position[0], self.maze_size].walls
        )

        maze_data_str = json.dumps(maze_data, indent= 4) 

        db_cursor.execute(
            '''
            INSERT INTO "game_saves"("game_id", "maze", "current_position", "start_position", "end_position", "scale", "times", "moves")
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            (
                self.id,
                maze_data_str,
                self.player.sprite.position.__str__(),
                self.Maze.start_position.__str__(),
                self.Maze.end_position.__str__(),
                self.scale,
                self.get_time,
                self.step_moves
            )
        )
        pygame.image.save(self.window_screen, 'test.jpeg')

        db_connect.commit()

    def save_leaderboard(self):
        """Save leaderboard after win the game
        """
        # Connect to database
        db_connect = sqlite3.connect(r'database/TomJerry.db')
        
        db_cursor = db_connect.cursor()
        
        # Insert to leaderboard
        insert_query = 'INSERT INTO "leaderboard"("game_id", "times", "moves") VALUES(?, ?, ?)'

        db_cursor.execute(insert_query, (self.id, self.get_time, self.step_moves))

        # Push to Real Database
        db_connect.commit()
        # Done

        pygame.image.save(self.screen, f'database/save_game_images/Game_{self.id}.png')
  
    def game_centering(self):
        virtual_player_x_coord = (self.player.sprite.rect.centerx - self.screen_size[0] / 2) * self.scale
        virtual_player_y_coord = (self.player.sprite.rect.centery - self.screen_size[1] / 2) * self.scale
        self.scale_surface_offset = pygame.math.Vector2(- virtual_player_x_coord, - virtual_player_y_coord)
        # self.scale_surface_offset = pygame.math.Vector2(0, self.screen_size[1] / 2)

    def game_normal_view(self):
        self.scale_surface_offset = pygame.math.Vector2()

    def center_zoom_linear(self, max_frame):
        if self.frame == 0:
            self.scale = 0
        if self.frame < max_frame:
            self.scale += 1 / max_frame
            self.game_centering()
            self.frame += 1

# Sadly cannot implement this in GamePlay class like a classmethod so this one is spilt outside 
def load_GamePlay(game_id: int) -> GamePlay:
    screen = pygame.display.get_surface()
    # Connect to database
    db_connect = sqlite3.connect(r'database/TomJerry.db')

    db_cursor = db_connect.cursor()
    
    # Check if that game is save or not save ??
    is_save = list(db_cursor.execute(f'SELECT * FROM "game_saves" WHERE "game_id" = {game_id} AND "save_state" = 1'))
    if not is_save: raise FileNotFoundError('This game is no longer save!!!')
    
    # If the game_id is fine -> Go Go to load
    game_data_1 = list(db_cursor.execute(f'SELECT * FROM "game_saves" WHERE "game_id" = {game_id}'))[0] # Get that row

    game_data_2 = list(db_cursor.execute(f'SELECT * FROM "games" WHERE "id" = {game_id}'))[0] # Get that row

    # Category the info that we get
    # Get the data that useful
    maze_size = int(game_data_2[2])

    grid_size = int(game_data_2[5])

    player_skin = game_data_2[6]

    is_energy = int(game_data_2[4])

    scale = int(game_data_1[5])

    times = float(game_data_1[-2].rstrip(' s')) * 1000

    moves = int(game_data_1[-1])

    # Intialize a basic Game
    Game = GamePlay(
        maze_size= maze_size,
        grid_size= grid_size,
        player_skin= player_skin,
        energy= is_energy,
        scale= scale
    )

    current_position = str_to_tuple(game_data_1[2])
    start_position = str_to_tuple(game_data_1[3])
    end_position = str_to_tuple(game_data_1[4])
    
    # Set the game.id to according to the data
    Game.id = game_id

    # Read the maze
    tmp_maze = Maze(
        maze_size= Game.maze_size,
        maze_grid_size= grid_size,
        scale= scale
    )

    maze_info = json.loads(game_data_1[1])

    for i in range(maze_size):
        for j in range(maze_size):
            tmp_maze.grids[i, j].walls = maze_info[i * maze_size + j].copy()
        
    tmp_maze.grids[start_position[0], -1] = GridCell(
        grid_position= (start_position[0], -1),
        grid_size= grid_size,
        scale= scale,
        group= tmp_maze
    )
    tmp_maze.grids[end_position[0], maze_size] = GridCell(
        grid_position= (end_position[0], maze_size),
        grid_size= grid_size,
        scale= scale,        
        group= tmp_maze
    )
    tmp_maze.grids[start_position[0], start_position[1] - 1].walls = maze_info[-2].copy()
    tmp_maze.grids[end_position[0], maze_size].walls = maze_info[-1].copy()

    print(tmp_maze.grids[end_position].walls)
    print(end_position)

    for grid in tmp_maze.grids:
        tmp_maze.grids[grid].is_visited = True
        tmp_maze.grids[grid].set_image()

    Game.Maze = tmp_maze
    
    Game.Maze.start_position = start_position
    Game.Maze.end_position = end_position

    # Create player
    Game.player = pygame.sprite.GroupSingle()
    Game.player.add(
        Tom(current_position, 
            Game.grid_size, 
            Game.scale,
            screen= Game.screen)
    )

    # Get the delta times and plus that to the times that player play
    Game.player.sprite.step_moves = moves
    Game.start_time = pygame.time.get_ticks() - times

    # After load all the game -> Go to game
    Game.set_new_game_state('in_game')


    return Game




    

