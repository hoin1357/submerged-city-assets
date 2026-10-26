"""Verify A's chunks and reconstruct one ZIP. No network access or overwriting.
Run: python reassemble.py [--verify-only] [--output A_assets_final_r4.zip]
"""
import argparse,hashlib,json,pathlib
p=argparse.ArgumentParser();p.add_argument('--verify-only',action='store_true');p.add_argument('--output',default='A_assets_final_r4.zip');a=p.parse_args()
root=pathlib.Path(__file__).resolve().parent;m=json.loads((root/'parts_manifest.json').read_text());whole=hashlib.sha256();total=0
for row in m['parts']:
 assert pathlib.Path(row['name']).name==row['name']
 part=root/row['name'];h=hashlib.sha256();size=0
 with part.open('rb') as f:
  while block:=f.read(1024*1024):h.update(block);whole.update(block);size+=len(block)
 if size!=row['bytes'] or h.hexdigest()!=row['sha256']:raise ValueError('Part verification failed: '+row['name'])
 total+=size
if total!=m['archive_bytes'] or whole.hexdigest()!=m['archive_sha256']:raise ValueError('ZIP digest mismatch')
print('All parts and concatenated ZIP digest verified:',total,'bytes')
if not a.verify_only:
 out=pathlib.Path(a.output)
 with out.open('xb') as dst:
  for row in m['parts']:
   with (root/row['name']).open('rb') as src:
    while block:=src.read(1024*1024):dst.write(block)
 print('Created',str(out),'without modifying the chunks. Extract using a ZIP64-capable tool.')
