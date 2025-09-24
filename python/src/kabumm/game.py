import datetime
import random
import logging

logger = logging.getLogger(__name__)


def now():
    return datetime.datetime.now()

class Countdown:
    def __init__(self, backend):
        self.backend = backend
        self.end_time = None
        self.punishments = 0

    def init(self, remaining_seconds):
        self.end_time = now() + datetime.timedelta(seconds=remaining_seconds)

    def tick(self):
        if self.time_over():
            self.backend.write("BUMM")
        else:
            if self.punishments > 0:
                self.punishments -= 1
                self.end_time -= datetime.timedelta(seconds=1)
            self.print_time()

    def time_over(self) -> bool:
        return now() > self.end_time

    def punish(self, seconds):
        self.punishments += seconds

    def remaining_time(self) -> tuple[int, int]:
        seconds = (self.end_time - now()).seconds
        s = seconds % 60
        m = seconds // 60
        return m, s

    def print_time(self):
        m, s = self.remaining_time()
        self.backend.write(f"{m:0>2}{s:0>2}")

class Level:
    def __init__(self, game_state):
        self.game_state = game_state
        self.selected_leds = []

    def select_random_leds(self, count=1):
        self.selected_leds = random.sample(self.game_state.remaining_leds, k=count)

    def tick(self) -> bool:
        raise NotImplementedError()

class StandardLevel(Level):
    def __init__(self, backend, game_state, time_between_rerandomization: int|None, num_selected: int=1):
        super().__init__(game_state)
        self.backend = backend
        self.time_between_rerandomizations = time_between_rerandomization
        self.num_selected = num_selected
        if num_selected > 1:
            self.time_between_rerandomizations = None
            logger.warning("disabled rerandomization for multi-LED level")
        self.select()

    def select(self):
        self.select_random_leds(self.num_selected)

    def leds_cut(self) -> tuple[bool, bool]:
        cuts = self.backend.is_cut()
        correct_cuts = []
        for i in self.selected_leds:
            if cuts[i]:
                logger.info("correct cut at LED %i", i)
                correct_cuts.append(i)
        for i in self.game_state.remaining_leds:
            if cuts[i]:
                logger.info("WRONG cut at LED %i", i)
                self.punish()
        for cut in correct_cuts:
            self.selected_leds.remove(cut)

    def punish(self):
        self.game_state.punish(60)

    def tick(self) -> bool:
        # TODO: randomization
        self.animate()
        self.leds_cut()
        return len(self.selected_leds) == 0

    def animate(self):
        raise NotImplementedError()


class LevelGreenRed1(StandardLevel):
    def __init__(self, backend, game_state):
        super().__init__(backend, game_state, None, 1)

    def animate(self):
        red = (255, 0, 0)
        green = (0, 255, 0)
        for led in self.game_state.remaining_leds:
            self.game_state.leds[led] = green if led in self.selected_leds else red

class GameState:
    def __init__(self, backend, countdown, num_leds):
        self.backend = backend
        self.countdown = countdown
        self.leds = [(0, 0, 0) for i in range(num_leds)]
        self.remaining_leds = [i for i in range(num_leds)]

    def punish(self, seconds):
        self.countdown.punish(seconds)

    def tick(self):
        leds = [led if i in self.remaining_leds else (0, 0, 0) for i, led in enumerate(self.leds)]
        self.backend.set_pixels(leds)


class Game:
    def __init__(self, backend):
        self.backend = backend
        self.countdown = Countdown(backend)
        self.countdown.init(5*60)
        self.game_state = GameState(backend, self.countdown, backend.num_wires)
        self.remaining_levels = [
                LevelGreenRed1(backend, self.game_state),
                ]
        self.finished = False

    def tick(self):
        if self.finished:
            return
        level_finished = self.remaining_levels[0].tick()
        if level_finished:
            logger.info("finished level")
            self.remaining_levels.pop(0)
            if not remaining_levels:
                logger.info("finished game")
                self.finished = False
        self.game_state.tick()
        self.countdown.tick()
