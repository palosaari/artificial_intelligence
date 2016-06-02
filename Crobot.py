"""
Artificial Intelligence 521495A Programming Exercise. University of Oulu.
Antti Palosaari <crope@iki.fi>

This Reversi/Othello algorithm uses following techniques:
* multitasking
* Minimax with Alpha-beta pruning
* Many different evaluation methods
* iterative deepening search tree
"""
import reversi.ReversiAlgorithm
import reversi.Node
import reversi.Move
import reversi.VisualizeGraph
import time
import sys
import threading
import multiprocessing

def alphabeta_process(player, node, depth_current, depth_max, alpha, beta, timeout, mark_count_total, turn_timeout):
    """
    Actual process code which builds search tree and evaluates it.
    
    Ugly thing, but that process function must be outside of class due to Python limitation.
    """
    player_own = player
    player_opp = 1 - player
    mark_count_left = 64 - mark_count_total
    
    def eval_coin_parity(node):
        own = node.state.getMarkCount(player_own)
        opp = node.state.getMarkCount(player_opp)
        return (own - opp)

    def eval_mobility(node):
        own = node.state.getPossibleMoveCount(player_own)
        opp = node.state.getPossibleMoveCount(player_opp)
        return 70 * (own - opp)

    def eval_corners_captured(node):
        own = 0
        opp = 0
        for x in range(0, 8, 7):
            for y in range(0, 8, 7):
                # 0 = Player 0's disc, 1 = Player 1's disc, -1 = an empty square
                if node.state.getMarkAt(x, y) == player_own:
                    own += 1
                elif node.state.getMarkAt(x, y) == player_opp:
                    opp += 1
        return 40 * (own - opp)

    def eval_near_corners(node):
        # Eval discs near corners
        own = 0
        opp = 0
        own_bad = 0
        opp_bad = 0
        # 0 = Player 0's disc, 1 = Player 1's disc, -1 = an empty square
        if node.state.getMarkAt(0, 0) == player_own:
            if node.state.getMarkAt(0, 1) == player_own:
                own += 1
            if node.state.getMarkAt(1, 0) == player_own:
                own += 1
            if node.state.getMarkAt(1, 1) == player_own:
                own += 1
        elif node.state.getMarkAt(0, 0) == player_opp:
            if node.state.getMarkAt(0, 1) == player_opp:
                opp += 1
            if node.state.getMarkAt(1, 0) == player_opp:
                opp += 1
            if node.state.getMarkAt(1, 1) == player_opp:
                opp += 1
        else:
            if node.state.getMarkAt(0, 1) == player_own:
                own_bad -= 1
            elif node.state.getMarkAt(0, 1) == player_opp:
                opp_bad -= 1
            if node.state.getMarkAt(1, 0) == player_own:
                own_bad -= 1
            elif node.state.getMarkAt(1, 0) == player_opp:
                opp_bad -= 1
            if node.state.getMarkAt(1, 1) == player_own:
                own_bad -= 1
            elif node.state.getMarkAt(1, 1) == player_opp:
                opp_bad -= 1

        if node.state.getMarkAt(0, 7) == player_own:
            if node.state.getMarkAt(0, 6) == player_own:
                own += 1
            if node.state.getMarkAt(1, 7) == player_own:
                own += 1
            if node.state.getMarkAt(1, 6) == player_own:
                own += 1
        elif node.state.getMarkAt(0, 7) == player_opp:
            if node.state.getMarkAt(0, 6) == player_opp:
                opp += 1
            if node.state.getMarkAt(1, 7) == player_opp:
                opp += 1
            if node.state.getMarkAt(1, 6) == player_opp:
                opp += 1
        else:
            if node.state.getMarkAt(0, 6) == player_own:
                own_bad -= 1
            elif node.state.getMarkAt(0, 6) == player_opp:
                opp_bad -= 1
            if node.state.getMarkAt(1, 7) == player_own:
                own_bad -= 1
            elif node.state.getMarkAt(1, 7) == player_opp:
                opp_bad -= 1
            if node.state.getMarkAt(1, 6) == player_own:
                own_bad -= 1
            elif node.state.getMarkAt(1, 6) == player_opp:
                opp_bad -= 1

        if node.state.getMarkAt(7, 0) == player_own:
            if node.state.getMarkAt(7, 1) == player_own:
                own += 1
            if node.state.getMarkAt(6, 0) == player_own:
                own += 1
            if node.state.getMarkAt(6, 1) == player_own:
                own += 1
        elif node.state.getMarkAt(7, 0) == player_opp:
            if node.state.getMarkAt(7, 1) == player_opp:
                opp += 1
            if node.state.getMarkAt(6, 0) == player_opp:
                opp += 1
            if node.state.getMarkAt(6, 1) == player_opp:
                opp += 1
        else:
            if node.state.getMarkAt(7, 1) == player_own:
                own_bad -= 1
            elif node.state.getMarkAt(7, 1) == player_opp:
                opp_bad -= 1
            if node.state.getMarkAt(6, 0) == player_own:
                own_bad -= 1
            elif node.state.getMarkAt(6, 0) == player_opp:
                opp_bad -= 1
            if node.state.getMarkAt(6, 1) == player_own:
                own_bad -= 1
            elif node.state.getMarkAt(6, 1) == player_opp:
                opp_bad -= 1

        if node.state.getMarkAt(7, 7) == player_own:
            if node.state.getMarkAt(7, 6) == player_own:
                own += 1
            if node.state.getMarkAt(6, 7) == player_own:
                own += 1
            if node.state.getMarkAt(6, 6) == player_own:
                own += 1
        elif node.state.getMarkAt(7, 7) == player_opp:
            if node.state.getMarkAt(7, 6) == player_opp:
                opp += 1
            if node.state.getMarkAt(6, 7) == player_opp:
                opp += 1
            if node.state.getMarkAt(6, 6) == player_opp:
                opp += 1
        else:
            if node.state.getMarkAt(7, 6) == player_own:
                own_bad -= 1
            elif node.state.getMarkAt(7, 6) == player_opp:
                opp_bad -= 1
            if node.state.getMarkAt(6, 7) == player_own:
                own_bad -= 1
            elif node.state.getMarkAt(6, 7) == player_opp:
                opp_bad -= 1
            if node.state.getMarkAt(6, 6) == player_own:
                own_bad -= 1
            elif node.state.getMarkAt(6, 6) == player_opp:
                opp_bad -= 1

        return 30 * (own - opp) + 30 * (own_bad - opp_bad)
    
    def eval_utility(node):
        # Stability / Utility

        # Weights: http://othellomaster.com/OM/Report/HTML/report.html#SECTION00063000000000000000
        UTILITY_WEIGHTS = [
            [ 1000, -300,  100,   80,   80,  100, -300, 1000],
            [ -300, -500,  -45,  -50,  -50,  -45, -500, -300],
            [  100,  -45,    3,    1,    1,    3,  -45,  100],
            [   80,  -50,    1,    5,    5,    1,  -50,   80],
            [   80,  -50,    1,    5,    5,    1,  -50,   80],
            [  100,  -45,    3,    1,    1,    3,  -45,  100],
            [ -300, -500,  -45,  -50,  -50,  -45, -500, -300],
            [ 1000, -300,  100,   80,   80,  100, -300, 1000],
        ]

        own = 0
        opp = 0        
        for x in range(0, 8):
            for y in range(0, 8):
                if node.state.getMarkAt(x, y) == player_own:
                    own += UTILITY_WEIGHTS[x][y]
                elif node.state.getMarkAt(x, y) == player_opp:
                    opp += UTILITY_WEIGHTS[x][y]
        return (own - opp)

    def eval_stability_sides(node):
        # Stability side bars
        own = 0
        opp = 0
        own_side = 0
        opp_side = 0
        for y in range(0, 8):
            if node.state.getMarkAt(0, y) == player_own:
                own_side += 1
            elif node.state.getMarkAt(0, y) == player_opp:
                opp_side += 1
        if own_side == 8:
            own += 1
        elif opp_side == 8:
            opp += 1

        own_side = 0
        opp_side = 0
        for y in range(0, 8):
            if node.state.getMarkAt(7, y) == player_own:
                own_side += 1
            elif node.state.getMarkAt(7, y) == player_opp:
                opp_side += 1
        if own_side == 8:
            own += 1
        elif opp_side == 8:
            opp += 1

        own_side = 0
        opp_side = 0
        for x in range(0, 8):
            if node.state.getMarkAt(x, 0) == player_own:
                own_side += 1
            elif node.state.getMarkAt(x, 0) == player_opp:
                opp_side += 1
        if own_side == 8:
            own += 1
        elif opp_side == 8:
            opp += 1

        own_side = 0
        opp_side = 0
        for x in range(0, 8):
            if node.state.getMarkAt(x, 7) == player_own:
                own_side += 1
            elif node.state.getMarkAt(x, 7) == player_opp:
                opp_side += 1
        if own_side == 8:
            own += 1
        elif opp_side == 8:
            opp += 1

        return 40 * (own - opp)
    
    def alphabeta_inner(node, depth_current, alpha, beta):
        # Limit execution time
        if timeout < time.time():
            return 0

        # Evaluation
        elif depth_current == depth_max:
            if mark_count_left <= 11:
                return eval_coin_parity(node)
            else:
                return eval_utility(node) + eval_mobility(node) + eval_stability_sides(node) + eval_corners_captured(node) + eval_near_corners(node)
        
        # Minimize
        elif depth_current % 2:
            value = +sys.maxsize
            moves = node.state.getPossibleMoves(1 - player)
            for move in moves:
                child = reversi.Node.Node(node.state.getNewInstance(move.x, move.y, move.player), move)
                node.addChild(child)                    
                value = min(value, alphabeta_inner(child, depth_current + 1, alpha, beta))
                if value < alpha:
                    return value
                else:
                    beta = min(beta, value)
            return value
        
        # Maximize
        else:
            value = -sys.maxsize
            moves = node.state.getPossibleMoves(player)
            for move in moves:
                child = reversi.Node.Node(node.state.getNewInstance(move.x, move.y, move.player), move)
                node.addChild(child)
                value = max(value, alphabeta_inner(child, depth_current + 1, alpha, beta))
                if value > beta:
                    return value
                else:
                    alpha = max(alpha, value)
            return value
    
    node.score = alphabeta_inner(node, depth_current, alpha, beta)
    return node

class Crobot(reversi.ReversiAlgorithm.ReversiAlgorithm):
    visualize = False
#    visualize = True
    
    def __init__(self):
        self.time0 = time.time()
        threading.Thread.__init__(self)
        self.pool = multiprocessing.Pool(processes = 16)
        return
        
    def __del__(self):
        self.pool.terminate()
        self.pool.close()
        return
    
    def requestMove(self, requester):
        requester.doMove(self.move)
        if self.move:
            move_str = self.move.toString()
        else:
            move_str = None
        print "Crobot: final  move=%s time=%f" % (move_str, time.time() - self.time)
        
        return
    
    def init(self, game_controller, game_state, player, turn_timeout):
        self.timeout = time.time() + turn_timeout
        self.time = time.time()
        self.move = None
        self.mark_count_total = game_state.getMarkCount(player) + game_state.getMarkCount(1 - player)

        if self.visualize:
            # Limit visualization to 4 ply
            if game_state.getMarkCount(player) > 2:
                return self.requestMove(game_controller)

        # Take first step and start own process for each possible move in order to multiprocess search tree computation
        def alphabeta(node, depth_current, depth_max, alpha, beta):
            moves = node.state.getPossibleMoves(player)
            multiple_results = []
            for move in moves:
                child = reversi.Node.Node(node.state.getNewInstance(move.x, move.y, move.player), move)
                multiple_results.append(self.pool.apply_async(alphabeta_process, (player, child, depth_current + 1, depth_max, alpha, beta, self.timeout, self.mark_count_total, turn_timeout)))
        
            value = -sys.maxsize
            for res in multiple_results:
                try:
                    res_node = res.get(self.timeout - time.time())
                except multiprocessing.TimeoutError:
                    return
                else:
                    node.addChild(res_node)
                    value = max(value, res_node.score)

            node.score = value
            return

        for ply in range(1, 12):
            root_node = reversi.Node.Node(game_state, None)
            alphabeta(root_node, 0, ply, -sys.maxsize, +sys.maxsize)
            if self.timeout < time.time():
                break

            if self.visualize:
                vis_graph = reversi.VisualizeGraph.VisualizeGraph()
                vis_graph.drawSearchTree(root_node, ply)
            
            if root_node.getOptimalChild():
                self.move = root_node.getOptimalChild().getMove()
                move_str = self.move.toString()
            else:
                self.move = None
                move_str = None

            print "Crobot: ply=%2d move=%s alphabeta=%5d" % (ply, move_str, root_node.score)
            
        return self.requestMove(game_controller)
    
    @property
    def name(self):
        return "Crobot"

    def cleanup(self):
        return

    def run(self):
        return
    