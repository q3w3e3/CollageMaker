import os
import time
import argparse
import math
import numpy as np
from tqdm import tqdm
from rectpack import packer, newPacker, GuillotineBssfSas
from PIL import Image, ImageFile, ImageDraw

# Allow loading of truncated image files
ImageFile.LOAD_TRUNCATED_IMAGES = True

# Disable warnings on large images and those with iffy EXIF data
Image.warnings.simplefilter('ignore', Image.DecompressionBombWarning)
Image.warnings.filterwarnings("ignore", "(Possibly )?corrupt EXIF data", UserWarning)

CANVAS_HEIGHT, CANVAS_WIDTH = (2000,2000)

def getSizes(directory, normalizeHeight, scaleFactor, tileHeight, packer):
    print("Gathering Sizes")

    sizes = []

    for file in tqdm(os.listdir(directory)):
        if file.endswith(".jpg"):
            im = Image.open("%s/%s" % (directory, file))
        else: print("%s is not a .jpg")

        if normalizeHeight:
            scaleFactor = tileHeight/im.size[1]
        packer.add_rect(round(im.size[0]*scaleFactor),round(im.size[1]*scaleFactor),file)
        sizes.append(tuple(round(res*scaleFactor) for res in im.size))

    return(sizes)

def crop_center(pil_img, crop_width, crop_height):
    img_width, img_height = pil_img.size
    return pil_img.crop(((img_width - crop_width) // 2,
                         (img_height - crop_height) // 2,
                         (img_width + crop_width) // 2,
                         (img_height + crop_height) // 2))

def cropMaxSquare(pil_img):
    return crop_center(pil_img, min(pil_img.size), min(pil_img.size))

def _scale_coordinates(generator, image_width, image_height, side_length):
    side_length = round(math.sqrt(side_length))
    scaled_width = int(image_width / side_length) + 2
    scaled_height = int(image_height / side_length) + 2

    for coords in generator(scaled_width, scaled_height):
        yield [(x * side_length, y * side_length) for (x, y) in coords]

def generate_unit_hexagons(image_width, image_height):
    """Generate coordinates for a tiling of unit hexagons."""
    # Half the height of the hexagon
    h = math.sin(math.pi / 3)
    for x in range(-1, image_width, 3):
        for y in range(-1, int(image_height / h) + 1):

            # Add the horizontal offset on every other row
            x_ = x if (y % 2 == 0) else x + 1.5
            yield [
                (x_,        y * h),
                (x_ + 1,    y * h),
                (x_ + 1.5, (y + 1) * h),
                (x_ + 1,   (y + 2) * h),
                (x_,       (y + 2) * h),
                (x_ - 0.5, (y + 1) * h),
            ]

def generate_hexagons(*args, **kwargs):
    """Generate coordinates for a tiling of hexagons."""
    return _scale_coordinates(generate_unit_hexagons, *args, **kwargs)

def draw_tiling(coord_generator, filename, **kwargs):
    """
    Given a coordinate generator and a filename, render those coordinates
    in a new image and save them to the file.
    """
    im = Image.new('L', size=(CANVAS_WIDTH, CANVAS_HEIGHT))
    for shape in coord_generator(CANVAS_WIDTH, CANVAS_HEIGHT, **kwargs):
        ImageDraw.Draw(im).polygon(shape, outline='white')
    im.save(filename)

def makeHexagonal(directory, side_length):
    index = 0
    imageList = []
    imageOut = Image.new('RGB', size=(CANVAS_WIDTH, CANVAS_HEIGHT))
    print(imageOut.size)

    for file in tqdm(os.listdir(directory)):
        if file.endswith(".jpg"):
            imageList.append("%s/%s" % (directory, file))
    for shape in tqdm(generate_hexagons(CANVAS_WIDTH, CANVAS_HEIGHT, side_length)):
        coord0 = (int(shape[0][0]),int(shape[0][1]))
        coord1 = (int(shape[1][0]),int(shape[1][1]))
        coord2 = (int(shape[2][0]),int(shape[2][1]))
        coord3 = (int(shape[3][0]),int(shape[3][1]))
        coord4 = (int(shape[4][0]),int(shape[4][1]))
        coord5 = (int(shape[5][0]),int(shape[5][1]))

        im = Image.open(imageList[index])
        im = cropMaxSquare(im)
        newSize=int(math.sqrt(2)*CANVAS_HEIGHT/math.sqrt(side_length))
        im = im.resize((newSize,newSize))
        mask = Image.new('RGBA', im.size)
        d = ImageDraw.Draw(mask)
        
        h = newSize/2 * math.sin(math.pi / 3)
        halfNewSize = newSize/2

        normalizedCoord0 = (halfNewSize/2,0)
        normalizedCoord1 = (3*halfNewSize/2, 0)
        normalizedCoord2 = (newSize, h)
        normalizedCoord3 = (3*halfNewSize/2, 2*h)
        normalizedCoord4 = (halfNewSize/2,2*h)
        normalizedCoord5 = (0, h)



        #d.polygon((), fill='#000')
        d.polygon((normalizedCoord0, normalizedCoord1, normalizedCoord2, normalizedCoord3, normalizedCoord4, normalizedCoord5), fill='#000')
        imageOut.paste(im, (int(coord0[0]),int(coord0[1])), mask)
        index += 1
    print(imageOut.size)
    imageOut.save("hexagon.jpg", "JPEG")

def makeBins(sizes, multiplier, packer):
    print("Defining bins")

    bins = []

    maxx = max(x[0] for x in sizes)
    maxy = max(y[1] for y in sizes)
    squareMax = min(maxx,maxy)

    x = round(squareMax * multiplier)
    y = round(squareMax * multiplier)
    newbin = (x,y)
    bins.append(newbin)

    for b in bins:
        packer.add_bin(*b)
    return(x,y)

def makeRectangles(packer):
    print("Making List of Rectangles:")
    rectangles = []
    all_rects = packer.rect_list()
    for rect in tqdm(all_rects):
        rectangles.append(rect)
    return(rectangles)

def makeCanvas(x,y):
    # plotting stuff
    print("Creating canvas (%s x %s)" % (x,y))
    background = Image.new('RGB', (x, y), (0, 0, 0))

    return(background)

def pasteImages(directory, normalizeHeight, scaleFactor, tileHeight, rectangles, x, y, background, outfile):
    print("Pasting Images")

    for i in tqdm(rectangles):
        corner = (i[1],i[2])
        height = i[4]
        rid = i[5]

        left = corner[0]
        bottom = y - corner[1]
        top = bottom - height

        offset = (left,top)

        im = Image.open("%s/%s" % (directory, rid))

        if normalizeHeight:
            scaleFactor = tileHeight/im.size[1]
        if scaleFactor != 1:
            im = im.resize(tuple(round(size*scaleFactor) for size in im.size))
        background.paste(im, offset)
    print("Saving Image (%s x %a) (this could take some time)" % (x,y))
    background.save(outfile, "JPEG")

def main():
    parse = argparse.ArgumentParser(description='collage maker')
    parse.add_argument('-f', '--folder', dest='folder', help='folder with images (*.jpg)', default='.')
    parse.add_argument('-o', '--output', dest='output', help='output collage image filename', default='collage.jpg')
    parse.add_argument('-n', '--normalize', dest='normalizeHeight', type=bool, help='set True to normalize image heights', default=False)
    parse.add_argument('-H', '--height', dest='height', type=int, help='height of normalized image', default=100)
    parse.add_argument('-m', '--multiplier', dest='multiplier', type=float, help='Scale final image by a factor of', default=3)
    parse.add_argument('-s', '--scaleFactor', dest='scaleFactor', type=float, help='Scale each image by a factor of', default=1)
    parse.add_argument('-r', '--resolution', dest='resolution', type=int, help='Final image resolution', default=2000)
    parse.add_argument('-p', '--productivityHexagon', dest='hexagonal', type=bool, help='set to make hexagonal (other flags will not effect this output)', default=False)


    args = parse.parse_args()
    packer = newPacker(pack_algo = GuillotineBssfSas, rotation = False)


    multiplier = args.multiplier
    if not args.hexagonal:
        if args.normalizeHeight:
            multiplier = args.resolution/args.height

        sizes = getSizes(args.folder, args.normalizeHeight, args.scaleFactor, args.height, packer)

        x, y = makeBins(sizes, multiplier, packer)

        print("Packing (this could take some time)")
        packer.pack()

        rectangles = makeRectangles(packer)

        background = makeCanvas(x,y)

        pasteImages(args.folder, args.normalizeHeight, args.scaleFactor, args.height, rectangles, x, y, background, args.output)
    
    else:
        directory = args.folder
        count = len([file for file in os.listdir(directory) if file.endswith(".jpg")])
        print(count)
        for file in tqdm(os.listdir(directory)):
            if file.endswith(".jpg"):
                im = Image.open("%s/%s" % (directory, file))
            else: print("%s is not a .jpg")
        makeHexagonal(directory, side_length=count) 
            # do image pasting stufffs




if __name__ == '__main__':
    main()