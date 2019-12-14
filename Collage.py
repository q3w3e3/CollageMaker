import os
import time
import argparse
from tqdm import tqdm
from rectpack import packer, newPacker, GuillotineBssfSas
from PIL import Image, ImageFile

# Allow loading of truncated image files
ImageFile.LOAD_TRUNCATED_IMAGES = True

# Disable warnings on large images and those with iffy EXIF data
Image.warnings.simplefilter('ignore', Image.DecompressionBombWarning)
Image.warnings.filterwarnings("ignore", "(Possibly )?corrupt EXIF data", UserWarning)

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

    args = parse.parse_args()
    packer = newPacker(pack_algo = GuillotineBssfSas, rotation = False)

    print(args.folder)

    multiplier = args.multiplier

    if args.normalizeHeight:
        multiplier = args.resolution/args.height

    sizes = getSizes(args.folder, args.normalizeHeight, args.scaleFactor, args.height, packer)

    x, y = makeBins(sizes, multiplier, packer)

    print("Packing (this could take some time)")
    packer.pack()

    rectangles = makeRectangles(packer)

    background = makeCanvas(x,y)

    pasteImages(args.folder, args.normalizeHeight, args.scaleFactor, args.height, rectangles, x, y, background, args.output)

if __name__ == '__main__':
    main()