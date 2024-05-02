import vapoursynth as vs
from vapoursynth import core
import havsfunc as haf
import mvsfunc as mvf
import vsmlrt
from functools import partial
from vfxfunc import fade_blur

import sys

projDir = '.'
sys.path.insert(1, projDir)

# 视频文件名（最好是完整路径），输入到双引号（""）里面
VideoFilename = R"バスタイムプラネタリウム ⧸ HACHI 【Official MV ⧸ 4K】 [dE-9WZaW3Gs].mkv"
# 【无特效（必须）】字幕文件名（最好是完整路径），输入到双引号（""）里面
SubFilename = R"9th-nofx.ass"


def AmbientBorderAroundSubMask(n, f: vs.VideoFrame, vfxClip: vs.VideoNode, target_width = None, target_height = None) -> vs.VideoNode:
    if target_width is None:
        target_width = f.width
    if target_height is None:
        target_height = f.height
    clip_scale_x = target_width/vfxClip.width
    clip_scale_y = target_height/vfxClip.height

    label_num = f.props['_CCLStatNumLabels']
    if label_num <= 1:
        return vfxClip.fmtc.resample(target_width, target_height, kernel="gauss")
    else:
        # exclude the first label which is the background
        heights = f.props.get('_CCLStatHeights', None)[1:]
        lefts = f.props.get('_CCLStatLefts', None)[1:]
        tops = f.props.get('_CCLStatTops', None)[1:]
        widths = f.props.get('_CCLStatWidths', None)[1:]

        max_left = min(lefts)-2
        max_top = min(tops)-2
        max_right = max(lefts[i] + widths[i] for i in range(label_num-1))+2
        max_bottom = max(tops[i] + heights[i] for i in range(label_num-1))+2
        # return vfxClip.akarin.Expr(f"X {max_left} > X {max_right} < and Y {max_top} > and Y {max_bottom} < and 255 0 ?")
        xscale = target_width/(max_right-max_left) / clip_scale_x
        yscale = target_height/(max_bottom-max_top) / clip_scale_y
        return vfxClip.fmtc.resample(target_width, target_height, kernel="gauss", sx=-max_left*xscale, sy=-max_top*yscale, sh=target_height*yscale, sw=target_width*xscale)

src8 = core.lsmas.LWLibavSource(VideoFilename)
src16 = src8.fmtc.bitdepth(bits=16)

sub = core.sub.TextFile(src16, SubFilename, blend=False)
alpha = sub.std.PropToClip().fmtc.bitdepth(bits=16)
# src8.set_output()
# sub.set_output(1)
# alpha.set_output(2)

# expand = haf.mt_inflate_multi(mufm.gauss(alpha.std.Maximum(), 1), radius=50)
expand = alpha.std.Maximum().std.Maximum().std.Maximum().std.Maximum()
# expand.set_output(3)
sub_mask = expand.box.Blur(0, 3,3,3,3)
# sub_mask = core.akarin.Expr([sub_mask, alpha], "x y max")


sub_mask = fade_blur(sub_mask, [ 944,  972], 10, True)
sub_mask = fade_blur(sub_mask, [1310, 1317], 5, False)
sub_mask = fade_blur(sub_mask, [2868, 2910], 7, True)
sub_mask = fade_blur(sub_mask, [3574, 3605], 4, False)
sub_mask = fade_blur(sub_mask, [5117, 5177], 10, True)
sub_mask = fade_blur(sub_mask, [6459, 6471], 7, False)
sub_mask = fade_blur(sub_mask, [6471, 6494], 7, True)
# sub_mask = fade_blur(sub_mask, [1629, 1673], 0, False, 10, 50)
sub_mask = fade_blur(sub_mask, [1630, 1673], 0, False, 20, 75, 0, 1)
# sub_mask.set_output(4)

srcBlurHalf = src16.fmtc.resample(1920,1080, kernel="gauss")
srcBlurHalf = srcBlurHalf.box.Blur([0,1,2], 512, 3, 512, 3)
# srcBlur = srcBlurHalf.fmtc.resample(3840, 2160, kernel="gauss", sy=-970*15, sh=1080*15)

info: vs.VideoNode = sub_mask.std.ShufflePlanes(0, vs.GRAY).fmtc.bitdepth(bits=8).std.BinarizeMask(1).std.Maximum()
info = core.cv_ccl.ExcludeCCLUnder(info, 10).cv_ccl.GetCCLStats()
info.text.FrameProps().set_output(2)

srcBlur = core.std.FrameEval(src16, partial(AmbientBorderAroundSubMask, vfxClip=srcBlurHalf, target_width = src16.width, target_height = src16.height), prop_src=info)

sub_p = core.std.MaskedMerge(srcBlur, srcBlur.std.BlankClip(color=[235<<8, 32768, 32768]), alpha, first_plane=True)
sub_p = fade_blur(sub_p, [ 944,  972], 10, True)
sub_p = fade_blur(sub_p, [1310, 1317], 5, False)
sub_p = fade_blur(sub_p, [2868, 2910], 7, True)
sub_p = fade_blur(sub_p, [3574, 3605], 4, False)
sub_p = fade_blur(sub_p, [5117, 5177], 10, True)
sub_p = fade_blur(sub_p, [6459, 6471], 7, False)
sub_p = fade_blur(sub_p, [6471, 6494], 7, True)
sub_p = fade_blur(sub_p, [1630, 1673], 0, False, 20, 75, 0, 1)
# sub_p.set_output(5)

src16: vs.VideoNode = mvf.ToYUV(src8, depth=16, css="420")
# subed = applySub(nr16.std.AddBorders(top=130, bottom=130), SubFilename=SubFilenameFx, SubFilter = SubFilter)

src_in = mvf.ToRGB(src16, matrix="709", depth=32, full=False)
dpir = vsmlrt.DPIR(src_in, strength=3, model=vsmlrt.DPIRModel.drunet_color, tiles=1, backend=vsmlrt.Backend.TRT(num_streams=2, fp16=True))
nr16: vs.VideoNode = mvf.ToYUV(dpir, matrix="709", css="420", depth=16, full=False, kernel="spline36")

subed = nr16.std.MaskedMerge(sub_p, sub_mask, first_plane=True)

res = subed

#输出
#Debug=1，片源与成品对比；Debug=0，输出成品，准备压制。
Debug = 0
if Debug:
    pass
    mvf.Preview(res).set_output(0)
    mvf.Preview(src8).set_output(1)
else:
    pass
    res.set_output()
    src8.set_output(1)
