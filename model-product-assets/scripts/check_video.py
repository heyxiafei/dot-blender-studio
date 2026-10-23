#!/usr/bin/env python3
"""Read-only video QA. Does not claim visual or rights acceptance."""
import argparse, hashlib, json, math, subprocess
from fractions import Fraction
from pathlib import Path

def run(args):
    return subprocess.run(args, capture_output=True, text=True, check=True)

def fps_arg(value):
    try:
        result=Fraction(value)
        if result<=0 or not math.isfinite(float(result)) or float(result)==0: raise ValueError()
        return result
    except (ValueError,ZeroDivisionError,OverflowError):
        raise argparse.ArgumentTypeError('FPS must be finite and positive, e.g. 24 or 2997/125')

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('video',type=Path)
    for k in ('frames','width','height'): p.add_argument('--'+k,type=int,required=True)
    p.add_argument('--fps',type=fps_arg,required=True,help='Exact rate, e.g. 24 or 2997/125')
    p.add_argument('--audio',choices=['silent','present','any'],default='silent')
    p.add_argument('--report',type=Path,required=True)
    a=p.parse_args()
    if any(x<=0 for x in [a.frames,a.width,a.height,a.fps]) or not math.isfinite(a.fps): p.error('Expected metrics must be finite and positive')
    if a.video.resolve()==a.report.resolve(): p.error('Report must not overwrite video')
    if a.report.is_symlink(): p.error('Report must not be a symlink')
    if a.report.exists():
        try:
            prior=json.loads(a.report.read_text())
            if not isinstance(prior,dict) or not {'checks','observed','visual_review'}<=set(prior): raise ValueError()
        except (OSError,ValueError,UnicodeError): p.error('Refusing to overwrite a non-video-QA file')
    try:
        expected_duration=float(a.frames/a.fps)
        if not math.isfinite(expected_duration): raise ValueError()
    except (ValueError,OverflowError): p.error('Expected duration must be finite and representable')
    checks={}; detail={}; error=None
    try:
        raw=json.loads(run(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(a.video)]).stdout)
        streams=raw['streams']; videos=[s for s in streams if s['codec_type']=='video']; audios=[s for s in streams if s['codec_type']=='audio']
        checks['one_video_stream']=len(videos)==1
        if len(videos)!=1: raise ValueError('Expected exactly one video stream')
        v=videos[0]; fps_fraction=Fraction(v['avg_frame_rate']); fps=float(fps_fraction); frames=int(v['nb_read_frames'])
        duration_value=v.get('duration')
        if duration_value is None: duration_value=raw.get('format',{}).get('duration')
        duration=float(duration_value)
        detail=dict(width=v['width'],height=v['height'],fps=fps,fps_fraction=str(fps_fraction),frames=frames,duration=duration,audio_streams=len(audios))
        checks.update(width=v['width']==a.width,height=v['height']==a.height,frames=frames==a.frames,fps=fps_fraction==a.fps,duration=abs(duration-expected_duration)<=max(.002,.5/a.fps),audio=a.audio=='any' or (len(audios)==0 if a.audio=='silent' else len(audios)>0))
        run(['ffmpeg','-v','error','-xerror','-i',str(a.video),'-map','0','-f','null','-'])
        checks['full_decode']=True
    except (OSError,ValueError,TypeError,KeyError,ZeroDivisionError,OverflowError,subprocess.CalledProcessError) as e:
        error=str(e)
        if isinstance(e,subprocess.CalledProcessError) and e.stderr:
            error += ': '+e.stderr[-2000:].strip()
        checks['execution']=False
    report={'status':'PASS' if checks and all(checks.values()) else 'FAIL','checks':checks,'observed':detail,'error':error,'visual_review':'NOT_PERFORMED_BY_THIS_SCRIPT','rights_review':'NOT_PERFORMED_BY_THIS_SCRIPT','audio_content_review':'NOT_PERFORMED_BY_THIS_SCRIPT','cadence_review':'AVERAGE_FPS_ONLY_NOT_PER_FRAME_PTS'}
    if a.video.is_file():
        h=hashlib.sha256()
        with a.video.open('rb') as f:
            for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
        report.update(sha256=h.hexdigest(),bytes=a.video.stat().st_size)
    a.report.parent.mkdir(parents=True,exist_ok=True); a.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(report['status']); return 0 if report['status']=='PASS' else 1
if __name__=='__main__': raise SystemExit(main())
