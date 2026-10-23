#!/usr/bin/env python3
"""Plan an explicitly known CFR interval. Does not detect cuts or read source PTS."""
import argparse
from fractions import Fraction
import json
import math
from pathlib import Path

FORMAT = 'model-product-assets-frame-plan-v1'

def positive_fraction(value):
    try:
        result = Fraction(value)
        if result <= 0 or not math.isfinite(float(result)) or float(result) == 0:
            raise ValueError()
        return result
    except (ValueError, ZeroDivisionError, OverflowError):
        raise argparse.ArgumentTypeError('Use a finite positive rate, e.g. 24 or 2997/125')

def interval(value):
    try:
        a, b = map(int, value.split(':'))
        if a < 0 or b <= a:
            raise ValueError()
        return a, b
    except ValueError:
        raise argparse.ArgumentTypeError('Use start:end-exclusive with 0 <= start < end')

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fps', type=positive_fraction, required=True)
    parser.add_argument('--start', type=int, required=True, help='Zero-based source start')
    parser.add_argument('--end-exclusive', type=int, required=True)
    parser.add_argument('--cuts', type=int, nargs='*', default=[], help='Zero-based first frame of each following shot')
    parser.add_argument('--preserve', type=interval, action='append', default=[], help='Protected start:end-exclusive; repeatable')
    parser.add_argument('--source-zero-pts', default='0', help='PTS of source frame zero; exact decimal or fraction')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        offset = Fraction(args.source_zero_pts)
        if not math.isfinite(float(offset)):
            raise ValueError('Source zero PTS must be finite and representable')
        if args.start < 0 or args.end_exclusive <= args.start:
            raise ValueError('Require 0 <= start < end-exclusive')
        if args.cuts != sorted(set(args.cuts)) or any(c <= args.start or c >= args.end_exclusive for c in args.cuts):
            raise ValueError('Cuts must be sorted, unique and strictly within scope')
        protected = sorted(args.preserve)
        for i, (a, b) in enumerate(protected):
            if a < args.start or b > args.end_exclusive:
                raise ValueError('Protected interval is outside scope')
            if i and a < protected[i-1][1]:
                raise ValueError('Protected intervals overlap')
        if args.output.is_symlink():
            raise ValueError('Refusing a symlink output')
        if args.output.exists():
            previous = json.loads(args.output.read_text())
            if not isinstance(previous, dict) or previous.get('format') != FORMAT:
                raise ValueError('Refusing to overwrite a non-frame-plan file')
        boundaries = [args.start, *args.cuts, args.end_exclusive]
        def stamp(frame):
            pts = offset + Fraction(frame, 1) / args.fps
            if not math.isfinite(float(pts)):
                raise ValueError('Computed PTS must be finite and representable')
            return {'seconds_fraction': str(pts), 'seconds': float(pts)}
        shots = []
        for number, (a,b) in enumerate(zip(boundaries, boundaries[1:]), 1):
            shots.append({'shot': number, 'source_start': a, 'source_end_exclusive': b,
                          'frames': b-a, 'output_start_1based': a-args.start+1,
                          'output_end_inclusive_1based': b-args.start,
                          'first_pts': stamp(a), 'end_boundary_pts': stamp(b)})
        count = args.end_exclusive - args.start
        duration = Fraction(count, 1) / args.fps
        plan = {'format': FORMAT, 'assumption': 'Known constant cadence; computed timestamps, not observed PTS',
                'fps': str(args.fps), 'source_zero_pts': str(offset),
                'source_start': args.start, 'source_end_exclusive': args.end_exclusive,
                'frames': count, 'duration_fraction': str(duration), 'duration_seconds': float(duration),
                'shots': shots, 'protected_intervals': [{'start':a,'end_exclusive':b} for a,b in protected],
                'frame_map': [{'output_frame_1based': i+1, 'source_frame_0based': s,
                               'protected': any(a <= s < b for a,b in protected)}
                              for i,s in enumerate(range(args.start, args.end_exclusive))]}
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(plan, ensure_ascii=False, indent=2)+'\n')
        print('WROTE',count,'frames',len(shots),'shots')
        return 0
    except (OSError, ValueError, ZeroDivisionError, TypeError, OverflowError) as error:
        print('FAIL:',error)
        return 1

if __name__ == '__main__':
    raise SystemExit(main())
