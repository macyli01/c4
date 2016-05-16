import random
from functools import partial

import numpy as np

from c4.board import Board
from c4.evaluate import Evaluator, INF


class MoveOrder(object):
    def __init__(self, name):
        if name == 'seq':
            self._order = self._order_seq
        elif name == 'random':
            self._order = self._order_random
        elif name == 'eval':
            self._order = self._order_eval
        elif name == 'diff':
            self._order = self._order_diff
        else:
            raise NotImplemented()

    def _order_seq(self, board, moves):
        return moves

    def _order_random(self, board, moves):
        random.shuffle(moves)
        return moves

    def _order_eval(self, board, moves):
        if not hasattr(self, 'evaluate'):
            self.evaluate = Evaluator().evaluate

        if len(moves) <= 1:
            return moves

        return sorted(moves,
                      key=lambda m: -self.evaluate(board.move(m)),
                      reverse=True)

    def _order_diff(self, board, moves):
        if len(moves) <= 1:
            return moves

        return sorted(moves, key=partial(evaldiff, board),
                      reverse=True)

    def order(self, board, moves, hint=None):
        if hint is not None:
            yield hint

        for x in self._order(board, moves):
            if x == hint:
                continue
            yield x


def evaldiff(board, m):
    r = board.freerow(m)

    stm = board.stm
    other = board.other

    threat = False
    score = 0

    for s in Board.segments_around(board, r, m):
        c = np.bincount(s, minlength=3)
        c[0] -= 1
        c[stm] += 1

        if c[0] + c[stm] == 4:
            # add player advantages on this area
            if c[stm] == 4:
                return INF
            score += (c[stm] - 1) ** 2
        elif c[stm] == 1:
            # remove enemy advantages on this area
            score += c[other] ** 2

            # check if this is a threat, without this move the opponent has a
            # chance to win
            if c[0] == 0:
                threat = True

    # let's give a very high score to blocked threats as it is almost like a
    # victory to block an opponent mate
    if threat:
        return INF - 1

    return score
