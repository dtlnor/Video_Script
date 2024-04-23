
import sys
import os

import vapoursynth as vs
from vapoursynth import core
import havsfunc as haf
import mvsfunc as mvf
import vsmlrt
import muvsfunc_numpy as mufnp
import cv2

#OKE:PROJECTDIR
projDir = '.'
sys.path.insert(1, projDir)

os.environ["CUDA_MODULE_LOADING"] = "LAZY"

#OKE:INPUTFILE
a = R"F:\Tsundere-Mygo\BanG Dream! It's MyGO!!!!! S01E12 VOSTFR 1080p WEB x264 AAC -Tsundere-Raws (CR).mkv"
src8 = core.lsmas.LWLibavSource(a)
src16 = src8.fmtc.bitdepth(bits=16)

def mwlmask(clip, l1=80, h1=96, h2=None, l2=None):
    """
    luma mask
    Steal from other one's script. Most likely written by mawen1250.
    """
    sbitPS = clip.format.bits_per_sample
    black = 0
    white = (1 << sbitPS) - 1
    l1 = l1 << (sbitPS - 8)
    h1 = h1 << (sbitPS - 8)
    if h2 is None: h2 = white
    else: h2 = h2 << (sbitPS - 8)
    if l2 is None: l2 = white
    else: l2 = l2 << (sbitPS - 8)
    
    if h2 >= white:
        expr = '{white}'.format(white=white)
    else:
        expr = 'x {h2} <= {white} x {l2} < x {l2} - {slope2} * {black} ? ?'.format(black=black, white=white, h2=h2, l2=l2, slope2=white / (h2 - l2))
    expr = 'x {l1} <= {black} x {h1} < x {l1} - {slope1} * ' + expr + ' ? ?'
    expr = expr.format(black=black, l1=l1, h1=h1, slope1=white / (h1 - l1))
    
    clip = mvf.GetPlane(clip, 0)
    clip = clip.rgvs.RemoveGrain(4)
    clip = clip.std.Expr(expr)
    return clip

def pencil_color(rgb: vs.VideoNode)->vs.VideoNode:
    pencil_core2 = lambda img: cv2.pencilSketch(img)[1]
    output = mufnp.numpy_process(rgb, pencil_core2, input_per_plane=False, output_per_plane=False)
    return output

def pencil_grey(rgb: vs.VideoNode)->vs.VideoNode:
    # pencil_core1 = lambda img: cv2.pencilSketch(img, sigma_s=150, sigma_r=0.9, shade_factor=0.1)[0]
    pencil_core1 = lambda img: cv2.pencilSketch(img, sigma_s=30, sigma_r=0.065, shade_factor=0.09)[0]
    blank_clip = core.std.BlankClip(rgb, format=vs.GRAY8)
    output = mufnp.numpy_process([blank_clip, rgb], pencil_core1, input_per_plane=False, omit_first_clip=True)
    return output

def color_grad(
    clip: vs.VideoNode,
    gradients: dict[float, int] = {
        # https://github.com/itorr/one-last-image/blob/918fccdbfaf86512b08f9964ba56a4c8d1d31b05/html/louvre.js#L327
        0.0: 0xfbba30,
        0.4: 0xfc7235,
        0.6: 0xfc354e,
        0.7: 0xcf36df,
        0.8: 0x37b5d9,
        1.0: 0x3eb6da
    },
    position = "mean"):
    
    bps = clip.format.bits_per_sample

    def hex2rgb(value: int, bps: int) -> tuple[int, int, int]:
        mutiplier = ((1 << bps) - 1) / 0xFF
        return (value >> 16) * mutiplier, (value >> 8 & 0x00FF) * mutiplier, (value & 0x0000FF) * mutiplier

    blank = core.std.BlankClip(clip, format=vs.RGB24, length=1).fmtc.bitdepth(bits=bps)

    if position is None or position == "vector":
        pos = "X width / 2 pow Y height / 2 pow + 2 / sqrt pos! "
    elif position == "mean":
        pos = "X width / Y height / + 2 / pos! "
    else:
        pos = position

    grad_step = len(gradients) - 1

    thrp, rgbp = 0.0, gradients.pop(0)
    expr = [pos]*3
    for thr, rgb in gradients.items():
        for i, (vp, v) in enumerate(zip(hex2rgb(rgbp, bps), hex2rgb(rgb, bps))):
            newrconst = (v - vp) / (thr-thrp)
            # newr = newrconst * (pos-thrp)  + r
            expr[i] += f"pos@ {thr} <= " + f"pos@ {thrp} - {newrconst} * {vp} + "
            
        thrp = thr
        rgbp = rgb

    expr = [x + f"{v} " + "? "*grad_step for x, v in zip(expr, hex2rgb(gradients.pop(1.0), bps))]
    color_gradient = core.akarin.Expr(blank, expr)

    return color_gradient.std.Loop(clip.num_frames)


src16y = src16.std.ShufflePlanes(0, vs.GRAY)
# res = pencil_color(mvf.ToRGB(src8))
src_rgbs: vs.VideoNode = mvf.ToRGB(src8, depth=32, matrix="709")
dpired = vsmlrt.DPIR(src_rgbs, strength=6, model=vsmlrt.DPIRModel.drunet_color, tiles=1, backend=vsmlrt.Backend.TRT(fp16=True, num_streams=2, workspace=None))
autogain: vs.VideoNode = dpired.julek.AutoGain(planes=[0,1,2])
autogain8: vs.VideoNode = mvf.Depth(autogain, depth=8)
pen = pencil_grey(autogain8).fmtc.bitdepth(bits=16)

penmask = pen#.box.Blur(0, hradius=0, vradius=0)
color = color_grad(src16,{
            0.0: 0xfbba30, # yellow orange
            0.2: 0xfc7235, # orange
            0.5: 0xfc354e, # pink red
            0.65: 0xcf36df, # purple
            0.75: 0x37b5d9, # light blue
            1.0: 0x3eb6da # a bit darker light blue
        },
        position="vector")

color.set_output(2)
color_pen = haf.Overlay(color, penmask, mode="screen")#core.std.MaskedMerge(color, core.std.BlankClip(color, color=[255]*3), penmask)
# color_pen.set_output(3)

texture = core.imwri.Read(R"pencil-texture.jpg")

# t_list = []
# import random
# random.seed(0x0721)
# for i in range(src8.num_frames):
#     top = random.randint(0,3)
#     t_list.append(texture.std.Crop(top=top, bottom=525-top))

# texture_crop = core.std.Splice(t_list)

texture_crop = texture.std.Crop(top=0, bottom=525)

penciltexture: vs.VideoNode = mvf.ToYUV(texture_crop, full=False, depth=16, matrix="709")
penciltexture = penciltexture.std.ShufflePlanes(0, vs.GRAY).resize.Spline36(width=src8.width, height=src8.height)
penciltexture = penciltexture.std.Loop(src8.num_frames)

penciltexture = haf.Overlay(color, penciltexture, mode="screen")#core.std.MaskedMerge(color, core.std.BlankClip(color, color=[255]*3), penciltexture)
penciltexture_dark = haf.Overlay(penciltexture, src16y, mode="screen")#core.std.MaskedMerge(penciltexture, core.std.BlankClip(color, color=[255]*3), src_y)
penciltexture_dark = haf.Overlay(penciltexture_dark, mwlmask(src16y, l1=30, h1=96), mode="screen")#core.std.MaskedMerge(penciltexture_dark, core.std.BlankClip(color, color=[255]*3), mwlmask(src8))
# penciltexture_dark.set_output(5)

res = haf.Overlay(color_pen, penciltexture_dark, mode="multiply", opacity=0.5)
res = mvf.ToYUV(res, css="420", full=False, matrix="709")

#OKE:DEBUG
Debug = 0
if Debug:
    res = mvf.Preview(res)

else: res = mvf.Depth(res, 10)

res.set_output(0)
src8.set_output(1)
