#!/usr/bin/env python3
"""Hash files within an explicit delivery root, or verify a strict manifest."""
import argparse, hashlib, json
from pathlib import Path

def digest(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()

def inventory(root,exclude):
    rows=[]
    for p in sorted(root.rglob('*')):
        if p.is_symlink(): raise ValueError('Symlinks are not allowed in delivery: '+str(p.relative_to(root)))
        if p.is_file() and p.resolve()!=exclude:
            rows.append({'path':p.relative_to(root).as_posix(),'bytes':p.stat().st_size,'sha256':digest(p)})
    return rows

def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('root',type=Path)
    g=p.add_mutually_exclusive_group(required=True); g.add_argument('--output',type=Path); g.add_argument('--verify',type=Path)
    a=p.parse_args(); root=a.root.resolve()
    if not root.is_dir(): p.error('Root must be an existing directory')
    target=(a.output or a.verify).resolve()
    try:
        if target==root: raise ValueError('Manifest must be a file')
        if a.output and target.exists():
            try: previous=json.loads(target.read_text())
            except (ValueError, UnicodeError): raise ValueError('Refusing to overwrite an existing non-manifest file')
            if not isinstance(previous,dict) or set(previous)!={'format','files'} or previous['format']!='model-product-assets-manifest-v1':
                raise ValueError('Refusing to overwrite an existing non-manifest file')
        rows=inventory(root,target)
        if a.verify:
            saved=json.loads(target.read_text())
            if set(saved)!={'format','files'} or saved['format']!='model-product-assets-manifest-v1': raise ValueError('Invalid manifest schema')
            # Exact comparison also rejects traversal paths, duplicate entries, extra fields and missing/added files.
            if saved['files']!=rows: raise ValueError('Inventory/hash mismatch')
            print('PASS',len(rows),'files')
        else:
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_text(json.dumps({'format':'model-product-assets-manifest-v1','files':rows},ensure_ascii=False,indent=2)+'\n')
            print('WROTE',len(rows),'files')
    except (OSError,ValueError,TypeError) as e:
        print('FAIL:',e); return 1
    return 0
if __name__=='__main__': raise SystemExit(main())
