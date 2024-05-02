import vapoursynth as vs
from vapoursynth import core
import havsfunc as haf
import mvsfunc as mvf
import muvsfunc as muf

import sys
import os
from typing import Optional, Callable, List
from functools import partial
import pathlib


def applySub(clip: vs.VideoNode, SubFilename: str, SubFilter: int, blend = True):
    if not blend:
        return core.sub.TextFile(clip, SubFilename, blend=blend) # defalut vs subtext plugin (subtext.dll)
        
    if SubFilter == 0:
        subed = clip
    elif SubFilter == 1:
        subed = core.assrender.TextSub(clip, file=SubFilename) # assrender (assrender.dll)
    elif SubFilter == 2:
        subed = core.vsfm.TextSubMod(clip, SubFilename) # VSFilterMod - VSFilterMod, (VSFilterMod.dll)
    elif SubFilter == 3:
        subed = core.xyvsf.TextSub(clip, SubFilename) # xy-VSFilter (xy-VSFilter.dll)
    elif SubFilter == 4:
        subed = core.vsf.TextSub(clip, SubFilename) # VSFilter (VSFilter.dll)
    elif SubFilter == 5:
        subed = core.sub.TextFile(clip, SubFilename) # defalut vs subtext plugin (subtext.dll)
    elif SubFilter == 6:
        subed = core.vsfm.VobSub(clip, file=SubFilename)
    else:
        subed = core.assrender.TextSub(clip,file=SubFilename) # assrender (assrender.dll)
    
    return subed


def drawHachiOBSBorderMask(clip: vs.VideoNode, limited = False) -> vs.VideoNode:
    # if width > 0:
    #     BRx = TLx + width
    # if height > 0:
    #     BRy = TLy + height

    sFormat = clip.format
    sColorFamily = sFormat.color_family
    #mvf.CheckColorFamily(sColorFamily)
    sIsYUV = sColorFamily == vs.YUV
    # sIsGRAY = sColorFamily == vs.GRAY
    #sIsRGB = sColorFamily == vs.RGB
    sIsInteger = sFormat.sample_type == vs.INTEGER
    sbitPS = sFormat.bits_per_sample

    if sIsYUV:
        if sIsInteger:
            # neutral = 1 << (sbitPS - 1)
            if limited:
                peak = 235 << (sbitPS - 8)
                foot = 1 << (sbitPS - 4)
            else:
                peak = (1 << sbitPS) - 1
                foot = 0

        else:
            # neutral = 0.0
            peak = 1.0
            foot = -1.0

    else:
        if sIsInteger:
            # neutral = 1 << (sbitPS - 1)
            if limited:
                peak = 235 << (sbitPS - 8)
                foot = 1 << (sbitPS - 4)
            else:
                peak = (1 << sbitPS) - 1
                foot = 0

        else:
            # neutral = 0.0
            peak = 1.0
            foot = -1.0


    # default border const
    TLx = 996
    TLy = 961

    BRx = 1920
    BRy = 1080

    BLx = 853
    BLy = BRy

    slope = (TLx-BLx) / (BLy-TLy)

    # get luma and extract sub mask
    grayClip = clip.std.ShufflePlanes(0, vs.GRAY)
    binarizeSub = grayClip.std.Binarize()

    # padding and fill border
    borderH = 120
    subPaddingW = 50
    binarizeSubExpand = haf.mt_expand_multi(binarizeSub, sw=subPaddingW, sh=borderH, mode="rect")

    # draw and mask rect border
    insideBorderHeight = f"Y {TLy} >= Y {BRy} <= and"
    fillDefaultRect = f"X {TLx} >= X {BRx} <= and {peak} x[0,0] ?"
    lowerBorderExpr = f"{insideBorderHeight} {fillDefaultRect} {foot} ?"
    lowerBorderMasked = binarizeSubExpand.akarin.Expr([lowerBorderExpr])
    upperBorderMasked = binarizeSubExpand.std.Turn180().akarin.Expr([lowerBorderExpr]).std.Turn180()

    # merge two border
    rectBorderMasked = haf.Overlay(lowerBorderMasked,upperBorderMasked,mode="addition")

    # extendW = (Y - TLy) * slope
    # calTLx = TLx - extendW
    borderHeight = f"Y {TLy} -"
    extendW = f"{borderHeight} {slope} *"

    # staticBorderMask
    doDraw = peak
    noDraw = foot
    targetWOffset = TLx

    def drawMask(baseClip: vs.VideoNode):
        calTLx = f"{targetWOffset} {extendW} -"
        BottomMaskExpr = f"X {calTLx} >= Y {TLy} >= and X {BRx} <= and Y {BRy} <= and {doDraw} {noDraw} ?"
        BottomMask = baseClip.akarin.Expr([BottomMaskExpr])
        UpperMask = baseClip.std.Turn180().akarin.Expr([BottomMaskExpr]).std.Turn180()
        return haf.Overlay(BottomMask,UpperMask,mode="addition")

    staticBorderMask = drawMask(binarizeSubExpand)

    # dynamicBorderMask
    doDraw = peak
    noDraw = "x[0,0]"
    absXSearch = f"{extendW} trunc X +"
    targetWOffset = f"{absXSearch} Y x[] {peak} = X {TLx} ?"

    dynamicBorderMask = drawMask(rectBorderMasked)

    return (dynamicBorderMask,staticBorderMask)


def CrossFade(clipa: vs.VideoNode, clipb: vs.VideoNode, number_frames: int):
    """
    https://github.com/vcb-s/guides/blob/master/Advanced/%5B30%5D%20Expr%E4%B8%8E%E5%90%8E%E7%BC%80%E8%A1%A8%E8%BE%BE%E5%BC%8F/fade.vpy
    """
    
    number_frames = min(number_frames, clipa.num_frames, clipb.num_frames)

    src_a_end = clipa[-number_frames+1:-1]
    src_b_begin = clipb[1:number_frames-1]

    fade = core.akarin.Expr([src_a_end, src_b_begin], f"N 1 + {number_frames-1} / y * 1 N 1 + {number_frames-1} / - x * +")

    res = clipa[:-number_frames+1] + fade + clipb[number_frames-1:]

    return res


def FadeIn(clip, duration):
    fps = clip.fps_num/clip.fps_den
    number_frames = int(duration * fps)
    return CrossFade(core.std.BlankClip(clip, length=number_frames), clip, number_frames)


def FadeOut(clip, duration):
    fps = clip.fps_num/clip.fps_den
    number_frames = int(duration * fps)
    return CrossFade(clip, core.std.BlankClip(clip, length=number_frames), number_frames)


def gauss(clip, sigma=None, sigmaV=None, algo=0):
    """Gaussian filter using tcanny
    Borrowed from https://github.com/IFeelBloated/Oyster

    Args:
        sigma: Standard deviation of gaussian.

        algo: (int) Algorithm. 0:auto, 1:tcanny.TCanny(mode=-1), 2:bilateral.Gaussian()

    """
    if sigmaV is None:
        sigmaV = sigma

    if (algo == 0 and sigma is not None and sigma >= 10) or algo == 2:
        return core.bilateral.Gaussian(clip, sigma=sigma, sigmaV=sigmaV)
    else: # algo == 1 or (algo == 0 and (sigma is None or sigma < 10))
        return core.tcanny.TCanny(clip, sigma=sigma, sigma_v=sigmaV, mode=-1)


def fade_blur(clip, clip_range, blur_strength=5, reverse=False, blur_strength_v = None, banding = 0, strength_add = 0, strength_add_v = 0) -> vs.VideoNode:
    """
    Args:
        clip: clip to be processed
        clip_range: tuple of start and end frame
        blur_strength: strength of blur
        reverse: reverse the fade blur
        blur_strength_v: strength of vertical blur
        banding: the banding of the curve (-100 < banding < 100)
        strength_add: additional strength
        strength_add_v: additional vertical strength
    """

    start, end = clip_range
    cliped = clip[start:end]
    num_frames = cliped.num_frames
    # 0.99 to get more curve
    curve = banding / 100
    if blur_strength_v is None:
        def animator(n, clip):
            x = (num_frames-1-n)/(num_frames-1) if reverse else n/(num_frames-1)
            strength = ((curve*x-x)/(2*curve*x-curve-1)) * blur_strength + strength_add
            return gauss(clip, strength)
    else:
        def animator(n, clip):
            x = (num_frames-1-n)/(num_frames-1) if reverse else n/(num_frames-1)
            strength_h = ((curve*x-x)/(2*curve*x-curve-1)) * blur_strength + strength_add
            strength_v = ((curve*x-x)/(2*curve*x-curve-1)) * blur_strength_v + strength_add_v
            return gauss(clip, strength_h, strength_v)

    flt = core.std.FrameEval(cliped, partial(animator, clip=cliped))
    return clip[:start] + flt + clip[end:]
