from pathlib import Path
import hashlib,json,sys
root=Path(__file__).resolve().parent
m=json.loads((root/'PARTS.json').read_text())
name=m['archive']
if Path(name).name!=name or not name.endswith('.zip'):raise SystemExit('Unsafe archive name')
verify='--verify-only' in sys.argv
out=None
if not verify:out=(root/name).open('xb')
whole=hashlib.sha256();total=0
try:
 for part in m['parts']:
  n=part['name']
  if Path(n).name!=n or not n.startswith(name+'.'):raise SystemExit('Unsafe part name')
  p=root/n
  if p.stat().st_size!=part['bytes']:raise SystemExit('Wrong size: '+n)
  h=hashlib.sha256()
  with p.open('rb') as f:
   for block in iter(lambda:f.read(1024*1024),b''):
    h.update(block);whole.update(block);total+=len(block)
    if out:out.write(block)
  if h.hexdigest()!=part['sha256']:raise SystemExit('Wrong hash: '+n)
 if total!=m['archive_bytes'] or whole.hexdigest()!=m['archive_sha256']:raise SystemExit('Whole ZIP mismatch')
finally:
 if out:out.close()
print('Verified parts and whole ZIP SHA256.' if verify else 'Created and verified '+name)
