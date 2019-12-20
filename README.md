# CollageMaker
Bin packing collage maker

![Normalized](https://github.com/q3w3e3/CollageMaker/blob/master/Samples/hexagon.jpg)


Test/ contains a selection of images for testing

Samples/ contains a couple sample outputs

# optional arguments:

  -h, --help            show this help message and exit
  
  -f FOLDER, --folder FOLDER
                        folder with images (*.jpg)
                        
  -o OUTPUT, --output OUTPUT
                        output collage image filename
                        
  -n NORMALIZEHEIGHT, --normalize NORMALIZEHEIGHT
                        set True to normalize image heights
                        
  -H HEIGHT, --height HEIGHT
                        height of normalized image
                        
  -m MULTIPLIER, --multiplier MULTIPLIER
                        Scale final image by a factor of
                        
  -s SCALEFACTOR, --scaleFactor SCALEFACTOR
                        Scale each image by a factor of
                        
  -r RESOLUTION, --resolution RESOLUTION
                        Final image resolution

# ToDo

Stuff I plan to do:

- [ ] Automatic selection of automation (based on relative size of largest and smallest image)
- [ ] Have a min and max image size, but allow images between? Scale outside range to fit?
- [ ] Random image scale between a min and max?
- [ ] Automatic scale factor for different resolution?
- [ ] Allow selection of other packing algs
- [ ] Comment my code (whoops)
- [ ] Rewrite for readability (and maybe efficiency?)
- [ ] Add setup file to grab dependencies
- [x] Actually state my dependencies/requirements somewhere

