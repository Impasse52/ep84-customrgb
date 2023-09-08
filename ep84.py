import enum
import usb
import math

# setup data for EP84 packets
BM_REQUEST_TYPE = 0x21
SET_REPORT = 0x09
W_VALUE = 0x0300
W_INDEX = 0x0

# enum of modes available on the EPOMAKER Driver app
modes = enum.Enum(
    "modes",
    [
        "OFF",
        "ALWAYS_ON",
        "BREATH",
        "NEON",
        "WAVE",
        "RIPPLE",
        "RAINDROP",
        "SNAKE",
        "PRESS_ACTION",
        "CONVERAGE",
        "SINE_WAVE",
        "KALEIDOSCOPE",
        "LINE_WAVE",
        "USER_PICTURE",
        "LASER",
        "CIRCLEWAVE",
        "DAZZING",
        # does not work
        # "MUSIC_FOLLOW_EDM",
        # "MUSIC_FOLLOW2_CLASSIC",
    ],
    start=0x0,
)

# flags enum to enable/disable dazzle
dazzle = enum.Enum(
    "flags",
    [
        "DAZZLE",
        "NO_DAZZLE",
    ],
    start=0x07,
)

options = {
    modes.WAVE: {"RIGHT": 0x00, "LEFT": 0x10, "DOWN": 0x20, "UP": 0x30},
    modes.SNAKE: {"ZIGZAG": 0x00, "RETURN": 0x10},
    modes.KALEIDOSCOPE: {"OUT": 0x00, "IN": 0x10},
    modes.CIRCLEWAVE: {"ANTI_CLOCKWISE": 0x00, "CLOCKWISE": 0x10},
}


def hex_message(msg: str, length: int = 64) -> bytes:
    return bytes.fromhex(msg.ljust(length * 2, "0"))


# used to create a packet
def ep84_rgb_control(
    mode: int = modes.ALWAYS_ON.value,
    speed: int = 0x05,  # 0x01 - 0x05 (0x01 is fastest, 0x05 is slowest)
    brightness: int = 0x04,  # 0x00 - 0x04
    options: int = 0x00,
    dazzle: int = dazzle.NO_DAZZLE.value,
    color_r: int = 0xFF,
    color_g: int = 0xFF,
    color_b: int = 0xFF,
) -> bytes:
    # byte that signals start of rgb modification packet
    cmd_hex = 0x07

    # mode "User Picture" will show a default scheme without fixing these parameters 
    if mode == modes.USER_PICTURE.value:
        options, dazzle = 0x00, 0x00

    verify_bits = sum(
        [
            cmd_hex,
            mode,
            speed,
            brightness,
            dazzle,
            options,
            color_r,
            color_g,
            color_b,
        ]
    )
    n_bits = math.ceil(math.log(verify_bits, 2))
    verification = 2 ** (n_bits) - verify_bits - 1

    return hex_message(
        f"{cmd_hex:02x}{mode:02x}{speed:02x}{brightness:02x}{options|dazzle:02x}{color_r:02x}{color_g:02x}{color_b:02x}{verification:02x}"
    )


# used to send a packet
def set_report(dev, msg):
    assert dev.ctrl_transfer(
        bmRequestType=BM_REQUEST_TYPE,
        bRequest=SET_REPORT,
        wValue=W_VALUE,
        wIndex=W_INDEX,
        data_or_wLength=msg,
    ) == len(msg)


if __name__ == "__main__":
    # setup device
    dev = usb.core.find(idVendor=0x3151, idProduct=0x4002)

    # check device availability
    if dev is None:
        raise ValueError("Device not found")

    dev.set_configuration()  # type: ignore

    msg_custom = ep84_rgb_control(
        mode=modes.WAVE.value,
        dazzle=dazzle.NO_DAZZLE.value,
        options=options[modes.WAVE]["LEFT"],
        brightness=0x04,
        speed=0x05,
        color_r=0xFF,
        color_g=0xFF,
        color_b=0xFF,
    )

    set_report(dev, msg_custom)
