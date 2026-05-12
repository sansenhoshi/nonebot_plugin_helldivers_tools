from PIL import *

def image_paste(paste_image, under_image, pos):
    if paste_image.mode == 'RGBA':
        under_image.paste(paste_image, pos, mask=paste_image.split()[3])
    else:
        under_image.paste(paste_image, pos)
    return under_image
