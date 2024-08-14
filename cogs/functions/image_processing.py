'''
圖片處理
'''

import numpy as np
from PIL import Image, ImageDraw


def imgRoundFunc(img):
    img = img.convert("RGB") #convert to RGB
    img.resize((263,263))
    arrImg = np.array(img) #convert to numpy array
    alph = Image.new('L', img.size, 0) #create a new image with alpha channel
    draw = ImageDraw.Draw(alph) #create a draw object
    draw.pieslice([0, 0, img.size[0], img.size[1]], 0, 360, fill = 255, outline= 0) #create a circle
    arAlpha = np.array(alph) #conver to numpy array
    arrImg = np.dstack((arrImg, arAlpha)) #add alpha channel to the image
    return Image.fromarray(arrImg)

def drawRect(img, pos,**kwargs):
    transp = Image.new('RGBA', img.size, (0,0,0,0))
    draw = ImageDraw.Draw(transp, "RGBA")
    draw.rounded_rectangle(pos, 30, **kwargs)
    img.paste(Image.alpha_composite(img, transp))