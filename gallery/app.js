const $ = id => document.getElementById(id);
const fixtureMode = new URLSearchParams(location.search).get('fixture') === '1';
const manifestURL = new URL(fixtureMode ? '../tests/fixtures/manifest.json' : './manifest.json', location.href);
const state = { categories: [], assets: [], category: 'all', selected: null, viewer: null, timer: null, serial: 0 };
let viewerReady;
function readyViewer() {
  return viewerReady ||= import('./vendor/model-viewer-4.1.0.min.js').then(() => customElements.whenDefined('model-viewer')).catch(error => { viewerReady = null; throw error; });
}
function safeURL(value, base = manifestURL) {
  const url = new URL(value, base);
  if (!['http:', 'https:'].includes(url.protocol)) throw new Error('HTTP(S) 파일 주소만 지원합니다.');
  return url.href;
}
function validateManifest(data) {
  if (data.version !== 1 || !Array.isArray(data.categories) || !Array.isArray(data.assets)) throw new Error('manifest 형식이 올바르지 않습니다.');
  const ids = new Set();
  for (const cat of data.categories) {
    if (!cat.id || typeof cat.label !== 'string' || !Number.isInteger(cat.delivered) || cat.delivered < 0 || ids.has(cat.id)) throw new Error('카테고리를 확인하세요.');
    ids.add(cat.id);
  }
  const assetIds = new Set();
  for (const asset of data.assets) {
    if (!asset.id || typeof asset.name !== 'string' || !ids.has(asset.category) || assetIds.has(asset.id) || typeof asset.src !== 'string' || !asset.src.trim()) throw new Error('모델 ID, 이름, 카테고리, src를 확인하세요.');
    if (!/\.(glb|gltf)$/i.test(new URL(safeURL(asset.src)).pathname)) throw new Error('GLB / glTF 파일만 지원합니다.');
    if (asset.tags && (!Array.isArray(asset.tags) || asset.tags.some(tag => typeof tag !== 'string'))) throw new Error('tags는 문자열 배열이어야 합니다.');
    if (asset.download) safeURL(asset.download);
    if (asset.fixture && !fixtureMode) throw new Error('운영 목록에는 테스트 모델을 넣을 수 없습니다.');
    assetIds.add(asset.id);
  }
  return data;
}
function renderCategories() {
  $('category-count').textContent = state.categories.length.toLocaleString('ko-KR');
  $('categories').replaceChildren();
  for (const cat of [{id:'all', label:'전체 에셋', delivered:state.categories.reduce((n,c)=>n+c.delivered,0)}, ...state.categories]) {
    const b = document.createElement('button');
    b.type = 'button'; b.setAttribute('aria-pressed', String(state.category === cat.id));
    const label = document.createElement('span'); label.textContent = cat.label;
    const count = document.createElement('small'); count.textContent = cat.delivered;
    b.append(label,count); b.onclick=()=>{state.category=cat.id;renderCategories();renderList();}; $('categories').append(b);
  }
}
function renderList() {
  const q=$('search').value.trim().toLocaleLowerCase();
  const assets=state.assets.filter(a=>(state.category==='all'||a.category===state.category)&&[a.name,a.id,...(a.tags||[])].join(' ').toLocaleLowerCase().includes(q));
  $('category-title').textContent=state.categories.find(c=>c.id===state.category)?.label||'전체 에셋';
  $('result-count').textContent=`${assets.length}개 연결`;
  $('models').replaceChildren();
  for(const asset of assets){
    const b=document.createElement('button');b.className='model';b.setAttribute('aria-pressed',String(asset.id===state.selected?.id));
    const name=document.createElement('strong');name.textContent=asset.name;
    const meta=document.createElement('small');meta.textContent=`${asset.id} · ${asset.fixture?'합성 테스트 모델':state.categories.find(c=>c.id===asset.category).label}`;
    b.append(name,meta);b.onclick=()=>select(asset);$('models').append(b);
  }
  $('catalog-status').hidden=assets.length>0;
  $('catalog-status').textContent=state.assets.length===0?'아직 연결된 3D 파일이 없습니다. 실제 모델 파일을 manifest.json에 등록하면 이 목록에 표시됩니다.':'조건에 맞는 모델이 없습니다. 검색어나 카테고리를 바꿔보세요.';
}
function message(title, detail) {
  $('viewer-message').hidden=false;
  $('viewer-message').querySelector('strong').textContent=title;
  $('viewer-message').querySelector('p').textContent=detail;
}
function controls(enabled) { $('reset').disabled=!enabled; $('rotate').disabled=!enabled; }
async function select(asset) {
  const serial=++state.serial;
  clearTimeout(state.timer);state.selected=asset;state.viewer=null;
  $('viewer-host').replaceChildren();controls(false);$('rotate').setAttribute('aria-pressed','false');$('retry').hidden=true;
  $('asset-id').textContent=asset.id;$('asset-name').textContent=asset.name;
  $('asset-description').textContent=asset.description||(asset.fixture?'합성 도형으로 3D 기능을 검증합니다. 실제 에셋이 아닙니다.':'설명이 등록되지 않았습니다.');
  $('tags').replaceChildren(...(asset.tags||[]).map(tag=>{const s=document.createElement('span');s.textContent=tag;return s;}));
  $('format').textContent=new URL(safeURL(asset.src)).pathname.split('.').pop().toUpperCase();
  $('download').href=safeURL(asset.download||asset.src);$('download').setAttribute('download','');$('download').target='_blank';$('download').rel='noopener noreferrer';$('download').hidden=false;$('download-note').hidden=false;
  renderList();message('3D 모델을 불러오는 중…','처음에는 뷰어를 준비하는 데 시간이 걸릴 수 있습니다.');
  const fail=()=>{if(serial!==state.serial)return;clearTimeout(state.timer);state.serial++;state.viewer=null;$('viewer-host').replaceChildren();controls(false);message('모델을 표시할 수 없습니다','파일 주소, 인터넷 연결, CORS 또는 WebGL 지원을 확인하세요. 원본 다운로드도 이용할 수 있습니다.');$('retry').hidden=false;};
  state.timer=setTimeout(fail,45000);
  try {
    await readyViewer();if(serial!==state.serial)return;
    const viewer=document.createElement('model-viewer');state.viewer=viewer;
    viewer.setAttribute('camera-controls','');viewer.setAttribute('touch-action','pan-y');viewer.setAttribute('shadow-intensity','1');viewer.setAttribute('alt',`${asset.name} — 드래그 또는 방향키로 회전, 휠 또는 두 손가락으로 확대`);
    viewer.setAttribute('camera-orbit','0deg 70deg 105%');viewer.setAttribute('interaction-prompt','none');
    viewer.addEventListener('load',()=>{if(serial!==state.serial)return;clearTimeout(state.timer);$('viewer-message').hidden=true;controls(true);});
    viewer.addEventListener('error',fail);
    viewer.addEventListener('progress',e=>{if(serial===state.serial)$('viewer-message').querySelector('p').textContent=`불러오는 중 ${Math.round(e.detail.totalProgress*100)}%`;});
    viewer.src=safeURL(asset.src);$('viewer-host').append(viewer);
  } catch {fail();}
}
$('search').addEventListener('input',renderList);
$('reset').onclick=()=>{if(state.viewer){state.viewer.cameraOrbit='0deg 70deg 105%';state.viewer.cameraTarget='auto auto auto';state.viewer.fieldOfView='auto';state.viewer.jumpCameraToGoal();}};
$('rotate').onclick=()=>{const active=$('rotate').getAttribute('aria-pressed')!=='true';$('rotate').setAttribute('aria-pressed',String(active));if(state.viewer)state.viewer.autoRotate=active;};
$('retry').onclick=()=>state.selected&&select(state.selected);
async function loadManifest(){
  $('reload-manifest').hidden=true;$('catalog-status').hidden=false;$('catalog-status').textContent='에셋 목록을 불러오는 중…';
  try{const response=await fetch(manifestURL,{cache:'no-cache'});if(!response.ok)throw new Error(`HTTP ${response.status}`);const data=validateManifest(await response.json());state.categories=data.categories;state.assets=data.assets;
    $('delivered').textContent=data.categories.reduce((n,c)=>n+c.delivered,0).toLocaleString('ko-KR');$('connected').textContent=data.assets.filter(a=>!a.fixture).length.toLocaleString('ko-KR');
    renderCategories();renderList();
  }catch(error){$('catalog-status').textContent=`목록을 불러오지 못했습니다. ${error.message}`;$('reload-manifest').hidden=false;}
}
$('reload-manifest').onclick=loadManifest;$('fixture-banner').hidden=!fixtureMode;
loadManifest();
