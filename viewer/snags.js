// Local report collection; screenshots/photos never enter the model catalog.
export function selectionBox(start, end) {
  const clamp=v=>Math.max(0,Math.min(1,v));
  const a=start.map(clamp), b=end.map(clamp);
  return [Math.min(a[0],b[0]),Math.min(a[1],b[1]),Math.abs(a[0]-b[0]),Math.abs(a[1]-b[1])];
}

async function photoData(file) {
  if(!['image/jpeg','image/png','image/webp'].includes(file.type))throw new Error('Use JPEG, PNG or WebP photos.');
  if(file.size>25*1024*1024)throw new Error('Choose photos smaller than 25 MB.');
  const bitmap=await createImageBitmap(file);
  const scale=Math.min(1,2400/Math.max(bitmap.width,bitmap.height));
  const canvas=document.createElement('canvas');canvas.width=Math.max(1,Math.round(bitmap.width*scale));canvas.height=Math.max(1,Math.round(bitmap.height*scale));
  canvas.getContext('2d').drawImage(bitmap,0,0,canvas.width,canvas.height);bitmap.close();
  return {name:file.name||'Pasted photo',data:canvas.toDataURL('image/jpeg',.9)};
}
async function api(path, options) {
  const response=await fetch(path,options);
  if(!response.ok){
    let message='The snag server is unavailable. Restart tools/serve.py to enable the queue.';
    try{message=(await response.json()).error||message;}catch{}
    throw new Error(message);
  }
  return response.json();
}

export function installSnags({capture,restore,setActive}) {
  const dialog=document.createElement('dialog');dialog.className='snag-dialog';
  dialog.innerHTML=`<div class="snag-heading"><h2 id="snag-title">Report a snag</h2><button type="button" id="snag-close" aria-label="Close snag panel">Close</button></div>
    <p id="snag-help">Drag a box around the detail, then describe what needs fixing. You can paste photos into the comment.</p>
    <div class="snag-workspace"><div class="snag-preview"><div class="snag-stage" id="snag-stage"><img id="snag-image" alt="Captured camera view"><div id="snag-box" hidden></div></div></div>
    <form id="snag-form"><label for="snag-comment">What needs fixing?</label><textarea id="snag-comment" rows="6" maxlength="10000" required placeholder="Describe the detail and what it should look like…"></textarea>
    <label class="snag-upload" for="snag-files">Add reference photos <input id="snag-files" type="file" accept="image/jpeg,image/png,image/webp" multiple></label><small>Or paste photos here. Up to five; large photos are resized.</small>
    <div id="snag-photos"></div><button type="submit" id="snag-submit">Queue snag</button><button type="button" id="snag-restore" hidden>Return to this camera view</button></form></div>
    <div id="snag-list" hidden></div><p id="snag-message" role="status" aria-live="polite"></p>`;
  dialog.setAttribute('aria-labelledby','snag-title');document.body.append(dialog);
  const $=id=>dialog.querySelector('#'+id);
  let draft=null,photos=[],box=null,start=null,report=null,busy=false,readingPhotos=0,previousFocus=null;
  const message=text=>{$('snag-message').textContent=text;};
  function drawBox(){
    $('snag-box').hidden=!box;
    if(box)Object.assign($('snag-box').style,{left:box[0]*100+'%',top:box[1]*100+'%',width:box[2]*100+'%',height:box[3]*100+'%'});
  }
  function photoList(){
    $('snag-photos').replaceChildren(...photos.map((photo,index)=>{
      const figure=document.createElement('figure'),img=document.createElement('img');img.src=photo.data;img.alt=photo.name;
      const remove=document.createElement('button');remove.type='button';remove.textContent='Remove photo '+(index+1);remove.onclick=()=>{photos.splice(index,1);photoList();};figure.append(img,remove);return figure;
    }));
  }
  async function addPhotos(files){
    if(busy||report)return;
    readingPhotos++;$('snag-submit').disabled=true;
    try{
      for(const file of files){
        if(photos.length>=5)throw new Error('You can attach up to five photos.');
        photos.push(await photoData(file));photoList();
      }
      message('Photos attached.');
    }catch(error){message(error.message);}
    finally{readingPhotos--;if(!readingPhotos)$('snag-submit').disabled=false;}
  }
  function open(){previousFocus=document.activeElement;setActive(true);dialog.showModal();}
  function close(){if(busy||readingPhotos)return;dialog.close();}
  dialog.addEventListener('close',()=>{setActive(false);previousFocus?.focus();});
  dialog.addEventListener('cancel',event=>{if(busy||readingPhotos)event.preventDefault();});
  $('snag-close').onclick=close;
  function composer(){
    if(readingPhotos||busy)return;
    draft=capture();report=null;photos=[];box=null;start=null;
    $('snag-title').textContent='Report a snag';$('snag-help').textContent='Drag a box around the detail, then describe what needs fixing. You can paste photos into the comment.';
    $('snag-list').hidden=true;dialog.querySelector('.snag-workspace').hidden=false;
    $('snag-form').hidden=false;$('snag-comment').value='';$('snag-comment').readOnly=false;
    $('snag-submit').hidden=false;$('snag-restore').hidden=true;$('snag-files').value='';$('snag-files').disabled=false;
    $('snag-image').src=draft.screenshot;$('snag-stage').classList.add('drawing');photoList();drawBox();message('');open();
  }
  const point=event=>{const rect=$('snag-image').getBoundingClientRect();return [(event.clientX-rect.left)/rect.width,(event.clientY-rect.top)/rect.height];};
  $('snag-stage').addEventListener('pointerdown',event=>{
    if(report||busy||event.button!==0)return;
    event.preventDefault();start=point(event);$('snag-stage').setPointerCapture(event.pointerId);box=selectionBox(start,start);drawBox();
  });
  $('snag-stage').addEventListener('pointermove',event=>{if(!start)return;box=selectionBox(start,point(event));drawBox();});
  $('snag-stage').addEventListener('pointerup',event=>{
    if(!start)return;box=selectionBox(start,point(event));start=null;drawBox();
    if(box[2]<.003||box[3]<.003){box=null;drawBox();message('Drag a larger box around the detail.');}else{$('snag-comment').focus();message('Area selected.');}
  });
  $('snag-stage').addEventListener('pointercancel',()=>{start=null;});
  $('snag-image').ondragstart=()=>false;
  $('snag-files').onchange=event=>addPhotos([...event.target.files]);
  dialog.addEventListener('paste',event=>{
    if(report||$('snag-list').hidden===false)return;
    const files=[...event.clipboardData.items].filter(item=>item.kind==='file'&&item.type.startsWith('image/')).map(item=>item.getAsFile()).filter(Boolean);
    if(files.length){event.preventDefault();addPhotos(files);}
  });
  $('snag-form').onsubmit=async event=>{
    event.preventDefault();if(busy||readingPhotos||report)return;
    if(!box){message('Draw a box around the detail first.');return;}
    busy=true;$('snag-submit').disabled=true;$('snag-close').disabled=true;message('Saving snag…');
    try{
      const saved=await api('/api/snags',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({...draft,box,comment:$('snag-comment').value,photos})});
      await showReport(saved);message('Saved to the local queue. You can close this panel and add another.');refreshCount();
    }catch(error){message(error.message+' Your report is still here; you can retry.');}
    finally{busy=false;$('snag-submit').disabled=false;$('snag-close').disabled=false;}
  };
  async function showReport(saved){
    report=saved;box=saved.box;start=null;
    $('snag-title').textContent='Queued snag · '+saved.status.replace('_',' ');
    $('snag-help').textContent='Saved '+new Date(saved.created_at).toLocaleString()+' · '+saved.id;
    $('snag-list').hidden=true;dialog.querySelector('.snag-workspace').hidden=false;
    $('snag-image').src=`/api/snags/${saved.id}/files/${saved.screenshot}`;
    $('snag-stage').classList.remove('drawing');drawBox();
    $('snag-form').hidden=false;$('snag-comment').value=saved.comment;$('snag-comment').readOnly=true;
    $('snag-submit').hidden=true;$('snag-restore').hidden=false;$('snag-files').disabled=true;
    $('snag-photos').replaceChildren(...saved.photos.map(photo=>{
      const link=document.createElement('a'),img=document.createElement('img');link.href=`/api/snags/${saved.id}/files/${photo.file}`;link.target='_blank';link.rel='noopener';img.src=link.href;img.alt=photo.name;link.append(img);return link;
    }));
    $('snag-restore').onclick=()=>{restore(saved.view);close();};
  }
  async function queue(){
    report=null;$('snag-title').textContent='Snag queue';$('snag-help').textContent='Saved locally on the machine serving this viewer. Select a report to see its marked view and photos.';
    dialog.querySelector('.snag-workspace').hidden=true;$('snag-list').hidden=false;$('snag-list').replaceChildren();message('Loading queue…');open();
    try{
      const {snags}=await api('/api/snags');
      $('snag-list').replaceChildren(...snags.map(saved=>{
        const button=document.createElement('button');button.className='snag-list-item';button.type='button';
        const title=document.createElement('strong'),detail=document.createElement('span');title.textContent=saved.comment;detail.textContent=saved.status.replace('_',' ')+' · '+new Date(saved.created_at).toLocaleString();button.append(title,detail);button.onclick=()=>{message('');showReport(saved);};return button;
      }));message(snags.length?'':'No snags yet. Position the camera and choose Report snag.');
    }catch(error){message(error.message);}
  }
  async function refreshCount(){try{const {snags}=await api('/api/snags');document.getElementById('snag-queue').textContent=`Snag queue (${snags.filter(s=>s.status!=='done').length})`;}catch{}}
  document.getElementById('snag-new').onclick=composer;document.getElementById('snag-queue').onclick=queue;
  refreshCount();
  return {openReport:async id=>{open();try{await showReport(await api('/api/snags/'+encodeURIComponent(id)));}catch(error){message(error.message);}}};
}
