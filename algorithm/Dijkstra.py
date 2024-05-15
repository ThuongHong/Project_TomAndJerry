from algorithm.utility import HyperNode, SortedList
# Dijkstra = A* with h(node) = 0

# In short, Dijkstra will maintain a SortedList() of gridcells whose min number of moves has been found
# then, at each loop, it chooses the first element from the SortList(). This element has a min g(node) to optimize remaining gridcells

# note: g(node): cost that we consume to 'come' to 'node'. In this code, I suppose the cost is number of moves needing to come to that node

def h(fisrt_position: tuple, second_position: tuple):
    return abs(fisrt_position[0] - second_position[0]) + abs(fisrt_position[1] - second_position[1])

def f(node: HyperNode, player_winning_position):
    return h(node.state, player_winning_position) + node.g

def Dijkstra(grids: dict,
          player_current_position: tuple[int],
          player_winning_position: tuple[int],
          is_process: bool = False):
    # Intialize all_moves list to keep track on process
    all_player_moves = []

    # Intialize openlist and closelist

    # This list contains the nodes that we need to explore
    # Class SortedList() helps us when append new node, the list automatically sort increasingly
    open_list = SortedList() 
    # This list contains the nodes that we have explored and evaluated. 
    # When a node is in this list, it means the lowest-cost path to that node has been found
    close_list = []

    #Initialize start node
    start = HyperNode(state= player_current_position, 
                      action= None, parent= None, g=0)
    open_list.append(start)

    # Loop until find the goal or open_list is empty
    while not open_list.is_empty():
        # Take the first node (means the lowest-cost node)
        node = open_list.pop()
        all_player_moves.append(node.state)

        # If the node is goal -> return solution
        if node.state == player_winning_position:
            actions = []
            states = []
            # Bakctrack from the goal to find the path
            while node.parent is not None:
                actions.append(node.action)
                states.append(node.state)
                node = node.parent

            actions.reverse()
            states.reverse()
            
            all_player_moves.pop(0)

            if is_process: return all_player_moves
            else: return list(zip(actions, states))
        
        # If not the goal, evaluate the neighbor of current node
        for action, state in grids[node.state].get_neighbors(is_get_direction= True):
            # As you know the meaning of close_list, we pass the node that has been in close_list
            if state not in close_list:
                child = HyperNode(state=state, action=action, parent=node, g=node.g + 1)
                open_list.append(child)
        
        close_list.append(node.state)
    if is_process: return all_player_moves
    return []