import logging
import contextlib

import board
import neopixel
import gpiod
from adafruit_ht16k33.segments import Seg14x4

logger = logging.getLogger(__name__)

class RaspiBackend:
    def __init__(self, gpio_request, num_wires_and_pixels: int, port_number_of_pixels: list[int]):
        logger.debug("creating display...")
        self.i2c = board.I2C()
        self.display = Seg14x4(self.i2c, address=0x70)
        logger.debug("created display")

        logger.debug("creating pixels...")
        self.pixels = neopixel.NeoPixel(board.D18, num_wires_and_pixels, pixel_order=neopixel.GRB, auto_write=False)
        self.pixels.fill((0,0,0))
        self.pixels.show()
        logger.debug("created pixels")

        self.gpio_request = gpio_request
        self.port_number_of_pixels = port_number_of_pixels


    def write(self, string):
        logger.info("display %s", string)
        self.display.print(string)

    def set_pixels(self, values):
        logger.info("set pixels to %s", values)
        self.pixels[:] = values
        self.pixels.show()

    def is_cut(self) -> list[bool]:
        gpio_lines = self.gpio_request.get_values(self.port_number_of_pixels)
        values = [gpio_lines[port] == gpiod.line.Value.ACTIVE for port in self.port_number_of_pixels]
        logger.debug("read wires: %s", "".join(hex(i)[-1] if values[i] else "_" for i in range(len(self.port_number_of_pixels))))
        return values

def _get_chip_path() -> str:
    candidates = []
    for i in range(10):
        path = f"/dev/gpiochip{i}"
        try:
            chip = gpiod.Chip(path)
            info = chip.get_info()
            if info.num_lines != 16:
                logger.debug("gpio %s has %i lines, not a possible candidate", path, info.num_lines)
                continue
            candidates.append(path)
        except Exception as e:
            logger.debug("gpio %s excluded: %s", path, e)
    if len(candidates) == 0:
        raise RuntimeError("no suitable gpio expander chip found")
    elif len(candidates) > 1:
        raise RuntimeError("found %i matching gpio expanders (%s), not sure which one to take", len(candidates), ", ".join(candidates))
    return candidates[0]
            


@contextlib.contextmanager
def make_backend(num_wires_and_pixels: int, port_number_of_pixel: list[int]|None=None):
    if not port_number_of_pixel:
        port_number_of_pixel = list(range(num_wires_and_pixels))
    assert len(port_number_of_pixel) == num_wires_and_pixels
    assert len(set(port_number_of_pixel)) == num_wires_and_pixels, "port_number_of_pixel values must be unique"
    assert all((v <16 for v in port_number_of_pixel)), "port numbers must be <16"

    logger.debug("creating gpio expander chip...")
    with gpiod.Chip(path=_get_chip_path()) as chip:
        logger.debug("created gpio expander chip")
        settings = gpiod.LineSettings(direction=gpiod.line.Direction.INPUT, bias=gpiod.line.Bias.PULL_UP)
        request = chip.request_lines({port: settings for port in port_number_of_pixel})
        try:
            yield RaspiBackend(request, num_wires_and_pixels, port_number_of_pixel)
        finally:
            request.release()
    logger.info("backend cleaned up during normal exit")




