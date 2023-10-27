"""simple script to process the logo.png image to remove all whitespace and 
trim to minimum size.

Returns:
    logo.png: saves over logo.png file
"""

from PIL import Image
import shutil

def convertImage(img):
    img = img.convert("RGBA")
    datas = img.getdata()
    newData = []
    for item in datas:
        if item[0] == 255 and item[1] == 255 and item[2] == 255:
            newData.append((255, 255, 255, 0))
        else:
            newData.append(item)
    img.putdata(newData)
    return img


img = Image.open("images/logo.png")
img = convertImage(img)
img.getbbox()
im2 = img.crop(img.getbbox())
im2.save("images/logo.png")
shutil.copyfile("images/logo.png", "../images/logo.png")

img = Image.open("images/favicon.png")
img = convertImage(img)
img.getbbox()
im2 = img.crop(img.getbbox())
im2.save("images/favicon.png")


