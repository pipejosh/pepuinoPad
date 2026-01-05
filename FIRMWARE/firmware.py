import time
import board
import digitalio
import neopixel
import usb_midi
import adafruit_midi
from adafruit_midi.note_on import NoteOn
from adafruit_midi.note_off import NoteOff

ROWS = 9
COLS = 9
LED_COUNT = 81

ROW_PINS = [
    board.GP2, board.GP3, board.GP4,
    board.GP5, board.GP6, board.GP7,
    board.GP8, board.GP9, board.GP10
]

COL_PINS = [
    board.GP11, board.GP12, board.GP13,
    board.GP14, board.GP15, board.GP16,
    board.GP17, board.GP18, board.GP19
]

LED_PIN = board.GP20
MIDI_CHANNEL = 0
BASE_NOTE = 36      # C2
BRIGHTNESS = 0.25

# MIDI
midi = adafruit_midi.MIDI(
    midi_out=usb_midi.ports[1],
    out_channel=MIDI_CHANNEL
)

# LEDs
pixels = neopixel.NeoPixel(
    LED_PIN,
    LED_COUNT,
    brightness=BRIGHTNESS,
    auto_write=False
)

# Matrix IO
rows = []
cols = []

for pin in ROW_PINS:
    io = digitalio.DigitalInOut(pin)
    io.direction = digitalio.Direction.OUTPUT
    io.value = False
    rows.append(io)

for pin in COL_PINS:
    io = digitalio.DigitalInOut(pin)
    io.direction = digitalio.Direction.INPUT
    io.pull = digitalio.Pull.DOWN
    cols.append(io)

# Key states
state = [[False for _ in range(COLS)] for _ in range(ROWS)]
last_state = [[False for _ in range(COLS)] for _ in range(ROWS)]

def key_index(r, c):
    return r * COLS + c

def is_action_key(r, c):
    return r == 0 or c == COLS - 1

def midi_note(r, c):
    return BASE_NOTE + (r * COLS + c)

def set_led(index, on):
    if on:
        pixels[index] = (0, 80, 255)   # blue
    else:
        pixels[index] = (0, 0, 0)

while True:
    for r in range(ROWS):
        rows[r].value = True
        time.sleep(0.0005)

        for c in range(COLS):
            state[r][c] = cols[c].value

            if state[r][c] != last_state[r][c]:
                idx = key_index(r, c)

                # LED feedback
                set_led(idx, state[r][c])
                pixels.show()

                # MIDI only for non-action keys
                if not is_action_key(r, c):
                    note = midi_note(r, c)
                    if state[r][c]:
                        midi.send(NoteOn(note, 100))
                    else:
                        midi.send(NoteOff(note, 0))

                last_state[r][c] = state[r][c]

        rows[r].value = False

    time.sleep(0.002)
