import c4d
import importlib
import Jlibsv2
importlib.reload(Jlibsv2)
import os


def extend_bmp(width, height, source_bmp, start_x=0, start_y=0):
    """ 将原先的png图进行扩展"""
    bmp = c4d.bitmaps.BaseBitmap()
    bmp.Init(width, height, depth=32, flags=c4d.INITBITMAPFLAGS_NONE)
    bmp.AddChannel(1, 1)
    bmp_alphaChannel = bmp.GetInternalChannel()
    source_bmp_alphaChannel = source_bmp.GetInternalChannel()
    for x in range(width):
        for y in range(height):
            px = x-start_x
            py = y-start_y
            alpha = 0
            if source_bmp.Within(px, py):
                color = source_bmp.GetPixel(px, py)
                bmp.SetPixel(x, y, color[0], color[1], color[2])
                alpha = source_bmp.GetAlphaPixel(source_bmp_alphaChannel, px, py)
            bmp.SetAlphaPixel(bmp_alphaChannel, x, y, alpha)
    return bmp

def main() -> None:
    width, height = 1000, 1000
    sequnce_path = r"G:\C4D JACK Plugins\G4Designer\libs\ualib\sequnce2"

    bmp = c4d.bitmaps.BaseBitmap()
    bmp.Init(width, height, depth=32, flags=c4d.INITBITMAPFLAGS_NONE)
    bmp.AddChannel(1, 1)
    bmp_alphaChannel = bmp.GetInternalChannel()
    start_x = 0
    start_y = 0
    counter = 0
    for index, img in enumerate(os.listdir(sequnce_path)):
        if not img.endswith(".png"):
            continue
        file_path = os.path.join(sequnce_path, img)

        source_bmp = c4d.bitmaps.BaseBitmap()
        source_bmp.InitWith(file_path)
        source_bmp_alphaChannel = source_bmp.GetInternalChannel()
        for x in range(width):
            for y in range(height):
                px = x-start_x
                py = y-start_y
                alpha = 0
                if source_bmp.Within(px, py):
                    color = source_bmp.GetPixel(px, py)
                    bmp.SetPixel(x, y, color[0], color[1], color[2])
                    #bmp.SetPixel(x, y, 150, 150, 150)
                    alpha = source_bmp.GetAlphaPixel(source_bmp_alphaChannel, px, py)
                    bmp.SetAlphaPixel(bmp_alphaChannel, x, y, alpha)

        counter+=1
        if counter % 5 == 0:
            start_x = 0
            start_y += 200
        else:
            start_x += 200

    c4d.bitmaps.ShowBitmap(bmp)

if __name__ == '__main__':
    main()
    c4d.EventAdd()