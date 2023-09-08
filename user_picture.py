from PIL import Image
import usb

from ep84 import ep84_rgb_control, hex_message, modes, set_report


def chunk_string(string, length):
    return (string[0 + i : length + i] for i in range(0, len(string), length))


# headers
h0 = "0c00800100000072"
h1 = "0c00800101000071"
h2 = "0c00800102000070"
h3 = "0c0080010300006f"
h4 = "0c0080010400006e"
h5 = "0c0080010500006d"
h6 = "0c0080010600006c"

# each packet has been built in such a way that it contains the key's "index" in the
# keyboard (i.e. FFXXYY), where XX and YY are the X and Y axis expressed as hex numbers.
p0 = "fe0000fe0001fe0002fe0003fe0004fe0005000000fe0101fe0102fe0103000000000000fe0100fe0201fe0202fe0203fe0104fe0105fe02"
p1 = "00fe0301fe0302fe0303fe0204fe0205fe0300fe0401fe0402fe0403fe0304000000fe0400fe0501fe0502fe0503fe0404000000fe0500fe"
p2 = "0601fe0602fe0603fe0504808080fe0600fe0701fe0702fe0703fe0604000000fe0700fe0801fe0802fe0803fe0704fe0305fe0800fe0901"
p3 = "fe0902fe0903fe0804fe0405fe0900fe0a01fe0a02fe0a03fe0904000000fe0a00fe0b01fe0b02fe0b03fe0a04fe0505fe0b00fe0c01fe0c"
p4 = "02000000fe0b04fe0605fe0c00fe0d01fe0d02fe0c03fe0c04fe0705ff0d00fe0e01fe0e02fe0d03fe0d04fe0805ff0e00ff0f0000000000"
p5 = "0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
p6 = "0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"

headers = [h0, h1, h2, h3, h4, h5, h6]
packets = [p0, p1, p2, p3, p4, p5, p6]


PACKET_SIZE = 112


def bitmap_to_userpicture(packets: str, img_dir: str) -> str:
    img = Image.open(img_dir).convert("RGB")
    
    width, height = img.size

    for x in range(width):
        for y in range(height):
            r, g, b = img.getpixel((x, y))

            old_pixel = f"fe{hex(x)[2:].rjust(2, '0')}{hex(y)[2:].rjust(2, '0')}"
            new_pixel = f"{hex(r)[2:]}{hex(g)[2:]}{hex(b)[2:]}"

            packets = packets.replace(old_pixel, new_pixel)

    return packets


if __name__ == "__main__":
    # setup device
    dev = usb.core.find(idVendor=0x3151, idProduct=0x4002)

    # check device availability
    if dev is None:
        raise ValueError("Device not found")

    dev.set_configuration()  # type: ignore

    split_packets = list(chunk_string("".join(packets), 6))

    usrimg_msg = ""
    for i in range(len(packets)):
        joined_packets = "".join(split_packets)

        joined_packets = bitmap_to_userpicture(joined_packets, r"E:\Desktop\Sprite-0001.png")

        usrimg_msg = (
            headers[i] + joined_packets[i * PACKET_SIZE : PACKET_SIZE * (i + 1)]
        )

        # switch to User Picture mode and send the new scheme
        set_report(dev, hex_message(usrimg_msg))

        print()
