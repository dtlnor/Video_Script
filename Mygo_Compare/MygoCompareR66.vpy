from typing import List

import vapoursynth as vs
import havsfunc as haf
import mvsfunc as mvf
core = vs.core

weblist = [
R"F:\Tsundere-Mygo\BanG Dream! It's MyGO!!!!! S01E01 VOSTFR 1080p WEB x264 AAC -Tsundere-Raws (CR).mkv",
R"F:\Tsundere-Mygo\BanG Dream! It's MyGO!!!!! S01E02 VOSTFR 1080p WEB x264 AAC -Tsundere-Raws (CR).mkv",
R"F:\Tsundere-Mygo\BanG Dream! It's MyGO!!!!! S01E03 VOSTFR 1080p WEB x264 AAC -Tsundere-Raws (CR).mkv",
R"F:\Tsundere-Mygo\BanG Dream! It's MyGO!!!!! S01E04 VOSTFR 1080p WEB x264 AAC -Tsundere-Raws (CR).mkv",
R"F:\Tsundere-Mygo\BanG Dream! It's MyGO!!!!! S01E05 VOSTFR 1080p WEB x264 AAC -Tsundere-Raws (CR).mkv",
R"F:\Tsundere-Mygo\BanG Dream! It's MyGO!!!!! S01E06 VOSTFR 1080p WEB x264 AAC -Tsundere-Raws (CR).mkv",
R"F:\Tsundere-Mygo\BanG Dream! It's MyGO!!!!! S01E07 VOSTFR 1080p WEB x264 AAC -Tsundere-Raws (CR).mkv",
R"F:\Tsundere-Mygo\BanG Dream! It's MyGO!!!!! S01E08 VOSTFR 1080p WEB x264 AAC -Tsundere-Raws (CR).mkv",
R"F:\Tsundere-Mygo\BanG Dream! It's MyGO!!!!! S01E09 VOSTFR 1080p WEB x264 AAC -Tsundere-Raws (CR).mkv",
R"F:\Tsundere-Mygo\BanG Dream! It's MyGO!!!!! S01E10 VOSTFR 1080p WEB x264 AAC -Tsundere-Raws (CR).mkv",
R"F:\Tsundere-Mygo\BanG Dream! It's MyGO!!!!! S01E11 VOSTFR 1080p WEB x264 AAC -Tsundere-Raws (CR).mkv",
R"F:\Tsundere-Mygo\BanG Dream! It's MyGO!!!!! S01E12 VOSTFR 1080p WEB x264 AAC -Tsundere-Raws (CR).mkv",
R"F:\Tsundere-Mygo\BanG Dream! It's MyGO!!!!! S01E13 VOSTFR 1080p WEB x264 AAC -Tsundere-Raws (CR).mkv",
]

bdlist = [
R"C:\Users\dtlnor\Videos\[BDMV] BanG Dream! It's MyGO!!!!!\[BDMV][240417][BRMM-10774][BanG Dream! It's MyGO!!!!!][上巻]\BRMM_10774\BDMV\STREAM\00000.m2ts",
R"C:\Users\dtlnor\Videos\[BDMV] BanG Dream! It's MyGO!!!!!\[BDMV][240417][BRMM-10774][BanG Dream! It's MyGO!!!!!][上巻]\BRMM_10774\BDMV\STREAM\00001.m2ts",
R"C:\Users\dtlnor\Videos\[BDMV] BanG Dream! It's MyGO!!!!!\[BDMV][240417][BRMM-10774][BanG Dream! It's MyGO!!!!!][上巻]\BRMM_10774\BDMV\STREAM\00002.m2ts",
R"C:\Users\dtlnor\Videos\[BDMV] BanG Dream! It's MyGO!!!!!\[BDMV][240417][BRMM-10774][BanG Dream! It's MyGO!!!!!][上巻]\BRMM_10774\BDMV\STREAM\00003.m2ts",
R"C:\Users\dtlnor\Videos\[BDMV] BanG Dream! It's MyGO!!!!!\[BDMV][240417][BRMM-10774][BanG Dream! It's MyGO!!!!!][上巻]\BRMM_10774\BDMV\STREAM\00004.m2ts",
R"C:\Users\dtlnor\Videos\[BDMV] BanG Dream! It's MyGO!!!!!\[BDMV][240417][BRMM-10774][BanG Dream! It's MyGO!!!!!][上巻]\BRMM_10774\BDMV\STREAM\00005.m2ts",
R"C:\Users\dtlnor\Videos\[BDMV] BanG Dream! It's MyGO!!!!!\[BDMV][240417][BRMM-10774][BanG Dream! It's MyGO!!!!!][上巻]\BRMM_10774\BDMV\STREAM\00006.m2ts",

R"C:\Users\dtlnor\Videos\[BDMV] BanG Dream! It's MyGO!!!!!\[BDMV][240417][BRMM-10775][BanG Dream! It's MyGO!!!!!][下巻 Fin]\BRMM_10775\BDMV\STREAM\00000.m2ts",
R"C:\Users\dtlnor\Videos\[BDMV] BanG Dream! It's MyGO!!!!!\[BDMV][240417][BRMM-10775][BanG Dream! It's MyGO!!!!!][下巻 Fin]\BRMM_10775\BDMV\STREAM\00001.m2ts",
R"C:\Users\dtlnor\Videos\[BDMV] BanG Dream! It's MyGO!!!!!\[BDMV][240417][BRMM-10775][BanG Dream! It's MyGO!!!!!][下巻 Fin]\BRMM_10775\BDMV\STREAM\00002.m2ts",
R"C:\Users\dtlnor\Videos\[BDMV] BanG Dream! It's MyGO!!!!!\[BDMV][240417][BRMM-10775][BanG Dream! It's MyGO!!!!!][下巻 Fin]\BRMM_10775\BDMV\STREAM\00003.m2ts",
R"C:\Users\dtlnor\Videos\[BDMV] BanG Dream! It's MyGO!!!!!\[BDMV][240417][BRMM-10775][BanG Dream! It's MyGO!!!!!][下巻 Fin]\BRMM_10775\BDMV\STREAM\00004.m2ts",
R"C:\Users\dtlnor\Videos\[BDMV] BanG Dream! It's MyGO!!!!!\[BDMV][240417][BRMM-10775][BanG Dream! It's MyGO!!!!!][下巻 Fin]\BRMM_10775\BDMV\STREAM\00005.m2ts",
]

labels = [
    [
        [1323, 1662, "sc1", R"樂器跟第三集之後的模型統一了\N最大的變化基本是吉他/貝斯的品記"],
        # [1454, 1454, ""],
        [2520, 2687, "sc2", R"很多類似的場景我就隨便挑一些了"],
        [3059, 3301, "sc3", "同上"],
        # [3300, 3300, ""],
        [3789, 3878, "sc4", R"這裡有多一點雜物的渲染變化"],
        # [3791, 3791, ""],
        # [3962, 3962, ""],
        [11511, 11605, "sc5", R"Ano醬頸子的陰影"],
        # [11517, 11517, ""],
        [16693, 16693, "ng1", R"穿幫鏡頭沒有修（燈的腳穿模了）"],
        [32054, 32054, "credit fix", R"頭三集補上了獨角獸老師Mygo原案的credit\N保持跟Web放送後面4~12集一致的頭銜"],
    ],
    [
        # [2631, 2659, "sc1", R"修復雲彩過曝"],
        [13863, 14016, "sc2", R"吉他的品記"],
        # [13923, 13923, ""],
        [14414, 14545, "sc3", R"修正貓貓的pick顏色為綠色\NWeb版有時候是銀色"],
        # [14470, 14470, ""],
        [26722+1032, 27888, "sc4", R"各種樂器的重新渲染，基本上是補個品記\N(其實仔細看官圖以及op的品記都是mygo的圖案，但正片從來沒出現過)"],
        # [27461, 27461, ""],
        # [27771, 27771, ""],
    ],
    [
        # [1297, 1297, ""],
        # [3114, 3114, ""],
        # [23017, 23727, "sc1"],
        [23406, 23478, "sc1", R"隨便挑一些場景"],
        # [23154, 23154, ""],
        # [24259, 24518, "sc2"],
        # [24265, 24265, ""],
        [31679, 31679, "credit fix", R"補上了燈媽媽的名字（高松光）"],
        # [31813, 31813, ""],
    ],
    [],
    [
        [18292, 18433, "sc1", R"後面的皮神被和諧了"],
        # [19321, 19321, ""],
        # [19814, 19814, ""],
        [19814, 19951, "sc2", R"A店招牌也被和諧了"],
        # [20644, 20644, ""],
    ],
    [],
    [
        [5623, 5623, "ng2", R"穿幫鏡頭沒有修（鏡子裡面的人沒有鏡像)"],
    ],
    [],
    [],
    [],
    [],
    [],
    [
        [32582, 32582, "credit fix", R"Mygo及avemujica原案的職位直接削除了\N(註：日本TOKYO MX的tv放送版第13集這裡也是沒有原案職位的)"],
    ],
]

def statoutput(clip: vs.VideoNode, channel: int) -> vs.VideoNode:
    clip.std.PlaneStats().resize.Bicubic(format=vs.YUV444P8).hist.Levels().text.FrameProps().set_output(channel)

def frameNoToSampleNo(frameNo: int, clip: vs.VideoNode, sampleRate: int) -> int:
    return int(frameNo * clip.fps_den * sampleRate / clip.fps_num)

def StoreTimeLine(clip: vs.VideoNode, **kwargs) -> vs.VideoNode:
    return (clip
           .akarin.PropExpr(lambda: dict(_CurrentTime="N 1.001 * 24 /", **kwargs))
           .akarin.PropExpr(lambda: dict(_Sec="x._CurrentTime 60 % trunc", _Min="x._CurrentTime 60 / trunc"))
           .akarin.Text(R"{_Min:02d}:{_Sec:02d}", prop="_TimeLine"))

nglist: List[vs.VideoNode] = []
creditlist: List[vs.VideoNode] = []

vlist: List[vs.VideoNode] = []
alist: List[vs.AudioNode]  = []
for ep in range(1, 14):
    bdclip = core.lsmas.LWLibavSource(bdlist[ep-1])
    webclip = core.lsmas.LWLibavSource(weblist[ep-1])

    audioclip = core.bs.AudioSource(bdlist[ep-1])

    src : vs.VideoNode = mvf.Depth(bdclip, 16, fulld=False, fulls=True)
    src = StoreTimeLine(src,  _ep=str(ep))
    web : vs.VideoNode = mvf.Depth(webclip, 16)
    web = StoreTimeLine(web,  _ep=str(ep))
    
    for start, end, label, subtitle in labels[ep-1]:
        if end == start:
            still_duration = 24*5
            bdcut = src[start].std.Loop(still_duration)
            webcut = web[start].std.Loop(still_duration)

            audiocut = audioclip.std.BlankAudio(length=frameNoToSampleNo(still_duration, bdclip, audioclip.sample_rate))
        else:
            bdcut = src[start:end]
            webcut = web[start:end]

            audiocut = audioclip[frameNoToSampleNo(start, bdclip, audioclip.sample_rate):frameNoToSampleNo(end, bdclip, audioclip.sample_rate)]

        # flash to and fro between bd and web every 12 frames
        interleave = core.std.Interleave([
            bdcut.akarin.Text(R"{{\fnSarasa Gothic TC\b1\an7\bord2\shad0\fs40}}第{_ep}集 {_TimeLine}\NBlu-ray 藍光版", prop="ass").assrender.FrameProp(), 
            webcut.akarin.Text(R"{{\fnSarasa Gothic TC\b1\an7\bord2\shad0\fs40}}第{_ep}集 {_TimeLine}\NWeb 放送版", prop="ass").assrender.FrameProp()
        ])
        selected = core.std.SelectEvery(interleave, cycle=48, offsets=list(range(0,24,2))+list(range(25,48,2)))
        videocut = selected.assrender.Subtitle(R"{\fnSarasa Gothic TC\b1\an1\bord2\shad0\fs40}"+subtitle)

        if "ng" in label:
            nglist.append(videocut)
            continue

        if "credit" in label:
            creditlist.append(videocut)
            continue

        vlist.append(videocut)
        alist.append(audiocut)

# add prolog
prolog = videocut.std.BlankClip(length=24).assrender.Subtitle(R"{\fnSarasa Gothic TC\b1\an5\bord2\shad0\fs160}BanG Dream! It's MyGO!!!!!\N一些BD畫面上的改動")
prologa = audiocut.std.BlankAudio(length=frameNoToSampleNo(prolog.num_frames, prolog, audiocut.sample_rate))

# credit and nglist
appedix = core.std.Splice(
    [core.std.BlankClip(bdcut, length=24).assrender.Subtitle(R"{\fnSarasa Gothic TC\b1\an5\bord2\shad0\fs160}一些staff表的改動")]
    + creditlist
    + [core.std.BlankClip(bdcut, length=24).assrender.Subtitle(R"{\fnSarasa Gothic TC\b1\an5\bord2\shad0\fs160}一些沒修的穿幫鏡頭")]
    + nglist
    + [core.std.BlankClip(bdcut, length=48)\
       .assrender.Subtitle(R"{\fnSarasa Gothic TC\b1\an5\bord2\shad0\fs160}以及武士道\N完全搞錯掉的\N藍光的色彩範圍\N{\fs80}(沒錯前面的畫面對比全部都已經被我修復過了)")]
)

# load op and comment
ep=3
bdop8 = core.lsmas.LWLibavSource(bdlist[ep-1])
webop8 = core.lsmas.LWLibavSource(weblist[ep-1])

bdop16 : vs.VideoNode = mvf.Depth(bdop8, 16)
bdop16 = StoreTimeLine(bdop16,  _ep=str(ep))
webop16 : vs.VideoNode = mvf.Depth(webop8, 16)
webop16 = StoreTimeLine(webop16,  _ep=str(ep))

bdopcut = bdop16[appedix.num_frames:2158]
webopcut = webop16[appedix.num_frames:2158]

opcontent = core.std.StackVertical([bdopcut, webopcut])

bdtitle = bdopcut.std.BlankClip().std.CopyFrameProps(bdopcut)\
    .akarin.Text(R"{{\fnSarasa Gothic TC\b1\an5\bord0\shad0\fs160\fsp10}}第{_ep}集 {_TimeLine}\NBlu-ray 藍光原版", prop="ass")\
    .assrender.FrameProp()
webtitle = webopcut.std.BlankClip().std.CopyFrameProps(webopcut)\
    .akarin.Text(R"{{\fnSarasa Gothic TC\b1\an5\bord0\shad0\fs160\fsp10}}第{_ep}集 {_TimeLine}\NWeb 放送色彩正确版", prop="ass")\
    .assrender.FrameProp()

titles = core.std.StackVertical([bdtitle, webtitle])
op_comp = core.std.StackHorizontal([titles, opcontent])
op_comp_commented = op_comp.fmtc.resample(1920, 1080, kernel="spline36")\
        .assrender.Subtitle(R"{\fnSarasa Gothic TC\b1\an4\bord2\shad0\fs60}色彩範圍錯誤是指\N武士道把full-range(0~255)的內容\N標記成了tv-range(16~235)來播放",start=0, end=24*3)\
        .assrender.Subtitle(R"{\fnSarasa Gothic TC\b1\an4\bord2\shad0\fs60}這就導致正常播放藍光的話\N你無法觀賞到正確的色彩\N畫面是過曝/過暗的",start=24*3, end=24*6)\
        .assrender.Subtitle(R"{\fnSarasa Gothic TC\b1\an4\bord2\shad0\fs60}這裡幾位主角偉大的臉\N在藍光版裡面就明顯過曝了\N而部分剧中场景黑得人都没了",start=24*6, end=24*9)\
        .assrender.Subtitle(R"{\fnSarasa Gothic TC\b1\an4\bord2\shad0\fs60}如果手上有原盤想要正常觀看\N可以嘗試在播放器裡面\N強行指定來源是full-range\N或者等壓製組修復的BDRip",start=24*9, end=24*12)\
        .assrender.Subtitle(R"{\fnSarasa Gothic TC\b1\an4\bord2\shad0\fs50}最後一點想對藍光吐槽的就是\N一般動畫藍光大概有40Mb碼率\NMygo這個動態那麼多的只有30Mb\N雖然是用x264 2pass製作的\N但還是給得太少了吧(比web好就是了，\N但該糊的地方還是會糊那麼點)",start=24*12, end=24*17)\
        .assrender.Subtitle(R"{\fnSarasa Gothic TC\b1\an4\bord2\shad0\fs50}最後的最後再追加一點\N一般動畫出現op/ed祭天的情況\N藍光都會附送無staff表版本的正片切片\N但Mygo只有無staff表的oped\N我那坐地鐵的祥子還是得頂著一堆staff前進\N太重啦",start=24*17, end=24*22)\
        .assrender.Subtitle(R"{\fnSarasa Gothic TC\b1\an4\bord2\shad0\fs60}最後把op聽完吧",start=24*22, end=24*25)

# cover appendix and op_comp_commented
opaudio = core.bs.AudioSource(bdlist[ep-1])[:frameNoToSampleNo(2158, bdop16, 48000)]

finalvideo = core.std.Splice([prolog]+vlist+[appedix]+[op_comp_commented]).std.AssumeFPS(fpsnum=24000, fpsden=1001)
finalvideo.set_output(0)
finalaudio = core.std.AudioSplice([prologa]+alist+[opaudio])
finalaudio.set_output(1)
