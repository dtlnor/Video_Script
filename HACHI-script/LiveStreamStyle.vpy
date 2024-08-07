import vapoursynth as vs
from vapoursynth import core
import havsfunc as haf
import mvsfunc as mvf
import muvsfunc as muf
import nnedi3_resample as nnrs
import vsmlrt

import sys
import os
import math
import numbers
from typing import Optional, Callable
import typing
from functools import partial
import pathlib

#OKE:PROJECTDIR
projDir = '.'
sys.path.insert(1, projDir) # some packages rely on having '' as sys.path[0]
#import custom  # import python modules under the project directory
#core.std.LoadPlugin(os.path.join(projDir, 'libcustom.dll')) # or load custom plugins

from .vfxfunc import drawBorderMask, applySub, FadeIn, FadeOut, CrossFade


############################################
# 一般设置，这里开始是你可以自行设置的参数 #
###########################################

# 视频文件名（最好是完整路径），输入到双引号（""）里面
VideoFilename = R"D:\archive\HachiRelated\hachi_sub\24.8.7金鱼花火\【歌枠】しっとり歌枠！！-Midnight station -71 【HACHI】 [yxjcJkqBdn8]~1_1.mp4"
# 【无特效（必须）】字幕文件名（最好是完整路径），输入到双引号（""）里面
SubFilename = R"D:\archive\HachiRelated\hachi_sub\24.8.7金鱼花火\3金鱼花火24.8.6nofx.ass"
# 【有特效（必须）】如果有特效跟无特效是同一个文件，那就填同一个文件。
SubFilenameFx = R"D:\archive\HachiRelated\hachi_sub\24.8.7金鱼花火\3金鱼花火24.8.6.ass"

# 是否填充黑邊
# 0 = 不填充
# 1 = 填充黑邊，填充上下黑邊
blackBoarderSelect = 1
onlyLowerHalf = 0

# 渐入秒数（设置 0 等于不启用渐入）
FadeInDur = 0.5
# 渐出秒数（设置 0 等于不启用渐出）
FadeOutDur = 0.5

##########################################
# 高级设置，如果滤镜发生问题可以调整这些 #
##########################################

# 选择视频文件加载滤镜（一般 1 或者 2 都不行就喊会的人看看吧）
# 1 = LWLibavSource,
# 2 = FFmpegSource2, 
# 3 = LibavSMASHSource, 
# 4 = AVISource, # 這個可以讀取虛擬 .avi 文件
# 5 = AVIFileSource, 
sourceFilter = 1

# 选择字幕文件加载滤镜（一般 1 或者 2 都不行就喊会的人看看吧）
# 0 = 无字幕
# 1 = assrender, 基于 libass 的目前最有前景的字幕滤镜，性能比较好，新特性支持比较多
# 2 = vsfm, vsfilterMod，用于压制的特效专用的字幕滤镜，支持 vsfilterMod 专用的复杂特效
# 3 = xyvsf, xy-VSFilter，用于压制的最广泛的传统 VS 系字幕滤镜，不支持 vsfilterMod 专用的复杂特效
# 4 = vsf, VSFilter，通常不用于压制（用 3）
# 5 = sub, vapoursynth 内置的 libass 字幕渲染，没人用，除非用来输出字幕 alpha 通道
# 6 = vob, 远古字幕滤镜，我没用过，大概是用来加载 DVD 字幕的
SubFilter = 1

#############################################
# 下面脚本不建议动，除非你很清楚你在做什么 #
#############################################

if sourceFilter == 0:
    src8 = core.std.BlankClip(width=1920, height=1080, length=2000, format= vs.YUV420P8, color=[128]*3)
elif sourceFilter == 1:
    src8 = core.lsmas.LWLibavSource(VideoFilename)
    src8.set_output(1010)
elif sourceFilter == 2:
    src8 = core.ffms2.Source(source = VideoFilename)
elif sourceFilter == 3:
    src8 = core.lsmas.LibavSMASHSource(VideoFilename)
elif sourceFilter == 4:
    src8 = core.avisource.AVISource(VideoFilename)
elif sourceFilter == 5:
    src8 = core.avisource.AVIFileSource(VideoFilename)
else:
    src8 = core.lsmas.LWLibavSource(VideoFilename)

src16: vs.VideoNode = mvf.Depth(src8, 16)


### predeband+denoise
os.environ["CUDA_MODULE_LOADING"] = "LAZY"
USE_TRT = 1

mlrtBackend = vsmlrt.Backend.TRT(num_streams=2, fp16=True) if USE_TRT else vsmlrt.Backend.ORT_CUDA(fp16=True)
dpir_tiles = 1

rgb = mvf.ToRGB(src16, matrix="709", depth=32, full=False)
dpir = vsmlrt.DPIR(rgb, strength=3, model=vsmlrt.DPIRModel.drunet_color, tiles=dpir_tiles, backend=mlrtBackend)
nr16 = mvf.ToYUV(dpir, matrix="709", css="420", depth=16, full=False, kernel="spline16")

src16 = nr16 # temp

if blackBoarderSelect:

    # get sub Mask from no efx subtitle
    rawSub = applySub(src8.std.BlankClip(color=[128]*3), SubFilename=SubFilename, SubFilter=SubFilter)
    subMask = core.akarin.Expr(mvf.GetPlane(rawSub, 0), "x 128 = 0 255 ?", format=vs.GRAY8)

    # get dynamic border mask, and static border mask
    dmask, smask = drawBorderMask(subMask)

    extBorderMask = haf.Overlay(dmask,smask,mode="difference")
    # extBorderMask = extBorderMask.std.BoxBlur(hradius=2,vradius=1) #边缘润线？不用吧

    # 16bit
    dmask16: vs.VideoNode = mvf.Depth(dmask, 16)
    fillcolor16 = src16.std.BlankClip(color=[35*256, 120*256, 132*256]).std.MaskedMerge(src16, dmask16)
    extBorder: vs.VideoNode = haf.Overlay(fillcolor16,fillcolor16.std.BlankClip(), mask=mvf.Depth(extBorderMask,16),opacity=0.73)

    # 8bit
    borderContentMask = mvf.GetPlane(src8,0).akarin.Expr(f"x {70.75} > 255 0 ?", format=vs.GRAY8)
    borderContentMask = core.std.MaskedMerge(borderContentMask.std.BlankClip(), borderContentMask, smask)
    extBorderSeam = core.akarin.Expr([smask,extBorderMask],f"Y {smask.height/2} < {'x[-5,0] y[-1,0] +'} {'x[5,0] y[1,0] +'} ? 510 = 255 0 ?")
    borderContentMask = core.akarin.Expr([extBorderSeam,borderContentMask],"x y +")

    # inpainting old
    # import cv2
    # import muvsfunc_numpy as mufnp

    # def inpaint_core(img, mask, radius=1, flags=cv2.INPAINT_NS):
    #     return cv2.inpaint(img, mask, inpaintRadius=radius, flags=flags)

    # borderContentMask = haf.mt_inflate_multi(borderContentMask, radius=1)
    # inpainting = mufnp.numpy_process([mvf.ToRGB(extBorder, depth=8), borderContentMask], inpaint_core, input_per_plane=False, output_per_plane=False, radius=4, flags=cv2.INPAINT_TELEA)
    # inpainting = mvf.ToYUV(inpainting, css="420", depth=16)

    # inpainting new
    borderContentMask = haf.mt_inflate_multi(borderContentMask, radius=1)
    inpainting = core.cv_inpaint.InpaintTelea(mvf.ToRGB(extBorder, depth=8), borderContentMask, radius=4)
    inpainting = mvf.ToYUV(inpainting, css="420", depth=16)

    # borderContentMask.set_output(3)
    # inpainting.set_output(4)

    blurBorder = core.tcanny.TCanny(inpainting.zsmooth.TemporalSoften(radius = 3), sigma=2.5, mode=-1)

    # apply final masked border
    fadeDMask = haf.mt_expand_multi(dmask,sw=2,sh=2).box.Blur(0,1,2,1,2).std.AverageFrames([1,1,1,1,1])
    masked16 = src16.std.MaskedMerge(blurBorder, mvf.Depth(fadeDMask,16))

else:
    masked16 = src16

if onlyLowerHalf:
    masked16 = core.akarin.Expr([masked16, src16], expr="Y height 2 / > x y ?")

# apply subtitle
subed = applySub(masked16, SubFilename=SubFilenameFx, SubFilter=SubFilter)


if FadeInDur > 0:
    subed = FadeIn(clip=mvf.Depth(subed,8), duration=1)
if FadeOutDur > 0:
    subed = FadeOut(clip=subed, duration=1)

res = subed

#输出
#Debug=1，片源与成品对比；Debug=0，输出成品，准备压制。
Debug = 0
if Debug:
    pass
    mvf.Preview(res).set_output(0)
    src8.set_output(1)
    # smask.set_output(11)
    dmask.set_output(12)
    # extBorder.set_output(2)
    # extBorderMask.set_output(13)
    extBorderSeam.set_output(14)
    borderContentMask.set_output(3)
    inpainting.set_output(4)
    # logonr.set_output(41)
    # fillcolor16.set_output(15)
    # fillcolor.set_output(42)
    # blurBorderNR.set_output(5)
    blurBorder.set_output(51)
    masked16.set_output(6)
    #mvf.Preview([src8,res],depth=8).set_output()
else:
    pass
    # res = res.std.PlaneStats()
    # Y = core.akarin.Expr(mvf.GetPlane(res,0),f"x x.PlaneStatsAverage < x._ColorRange {235 << (res.format.bits_per_sample-8)} {(1 << res.format.bits_per_sample - 1)} ? x ?")
    
    mvf.Depth(res,8).set_output()
    mvf.Depth(src8,8).set_output(1)
    # core.bas.Source(VideoFilename, track=1).set_output(1)
