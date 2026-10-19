(() => {
  'use strict';
  const script = document.currentScript;
  const root = document.querySelector('[data-machine-viewer]');
  if (!root) return;
  const asset = name => new URL(name, script.src).href;
  const stage = root.querySelector('[data-viewer-stage]');
  const start = root.querySelector('[data-viewer-start]');
  const controls = root.querySelector('[data-viewer-controls]');
  const help = root.querySelector('[data-viewer-help]');
  const status = root.querySelector('[data-viewer-status]');
  const frontButton = root.querySelector('[data-lid=front]');
  const heatButton = root.querySelector('[data-lid=heat]');
  const viewControl = root.querySelector('[data-viewer-view]');
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const state = { front: 0, heat: 0, yaw: .57, pitch: .29, zoom: 1 };
  const views = { perspective: [.57,.29], front: [0,.07], right: [Math.PI/2,.1], rear: [Math.PI,.1], top: [0,1.49] };
  let renderer, scene, camera, model, front, heater, environment, resizeObserver;
  let frame = 0, loading = false, disposed = false, visible = true, lastTime = 0;
  let currentFront = 0, currentHeat = 0, yaw = state.yaw, pitch = state.pitch;
  let generation = 0, contextLostHandler;
  start.hidden=false;

  function loadScript(url, ready) {
    if (ready()) return Promise.resolve();
    return new Promise((resolve, reject) => {
      let tag = [...document.scripts].find(s => s.src === url);
      const owned = !tag;
      if (!tag) { tag = document.createElement('script'); tag.src = url; }
      const timeout = setTimeout(() => finish(new Error('3D library timeout')),15000);
      const onLoad = () => finish(ready() ? null : new Error('3D library unavailable'));
      const onError = () => finish(new Error('3D library unavailable'));
      function finish(error) {
        clearTimeout(timeout);tag.removeEventListener('load',onLoad);tag.removeEventListener('error',onError);
        if (error) { if (owned) tag.remove(); reject(error); } else resolve();
      }
      tag.addEventListener('load',onLoad,{once:true});tag.addEventListener('error',onError,{once:true});
      if (owned) document.head.append(tag);
      if (ready()) finish();
    });
  }
  function releaseResources() {
    cancelAnimationFrame(frame);frame=0;
    resizeObserver?.disconnect();resizeObserver=null;
    const geometries = new Set(), materials = new Set(), textures = new Set();
    scene?.traverse(o => {
      if (o.geometry) geometries.add(o.geometry);
      for (const mat of o.material ? (Array.isArray(o.material) ? o.material : [o.material]) : []) {
        materials.add(mat);
        for (const value of Object.values(mat)) if (value?.isTexture) textures.add(value);
      }
    });
    geometries.forEach(g=>g.dispose());materials.forEach(m=>m.dispose());textures.forEach(t=>t.dispose());
    environment?.dispose();environment=null;
    if (renderer) { renderer.domElement.removeEventListener('webglcontextlost',contextLostHandler);renderer.dispose();renderer.forceContextLoss();renderer.domElement.remove(); }
    renderer=null;scene=null;model=null;
  }
  function fallback() {
    releaseResources();root.dataset.state='fallback';controls.hidden=true;help.hidden=true;start.hidden=false;
    start.textContent='Retry 3D view';start.disabled=false;
  }
  function render(now) {
    frame=0;
    if (!renderer || !model || !visible || document.hidden || disposed) return;
    const THREE=window.THREE;
    const dt=lastTime?Math.max(0,(now-lastTime)/1000):1;lastTime=now;
    const immediate=reduced.matches||document.documentElement.dataset.motion==='off';
    const rate=immediate?1:1-Math.exp(-12*dt);
    currentFront+=(state.front-currentFront)*rate;currentHeat+=(state.heat-currentHeat)*rate;
    yaw+=(state.yaw-yaw)*rate;pitch+=(state.pitch-pitch)*rate;
    front.rotation.x=THREE.MathUtils.degToRad(currentFront);
    heater.rotation.x=-THREE.MathUtils.degToRad(currentHeat);
    model.updateMatrixWorld(true);
    const bounds=new THREE.Box3().setFromObject(model);
    bounds.expandByVector(new THREE.Vector3(.018,.018,.018));
    const center=bounds.getCenter(new THREE.Vector3());
    const direction=new THREE.Vector3(Math.cos(pitch)*Math.sin(yaw),Math.sin(pitch),Math.cos(pitch)*Math.cos(yaw));
    const right=new THREE.Vector3(Math.cos(yaw),0,-Math.sin(yaw));
    const up=new THREE.Vector3().crossVectors(direction,right);
    const tanV=Math.tan(THREE.MathUtils.degToRad(camera.fov/2))*.92;
    let distance=.1;
    for(const x of [bounds.min.x,bounds.max.x])for(const y of [bounds.min.y,bounds.max.y])for(const z of [bounds.min.z,bounds.max.z]){
      const delta=new THREE.Vector3(x,y,z).sub(center),depth=delta.dot(direction);
      distance=Math.max(distance,depth+Math.abs(delta.dot(up))/tanV,depth+Math.abs(delta.dot(right))/(tanV*camera.aspect));
    }
    camera.position.copy(center).addScaledVector(direction,distance*state.zoom);camera.lookAt(center);
    renderer.render(scene,camera);
    const moving=Math.abs(currentFront-state.front)+Math.abs(currentHeat-state.heat)+Math.abs(yaw-state.yaw)+Math.abs(pitch-state.pitch)>.005;
    if (moving) requestRender();
  }
  function requestRender() { if(!frame && renderer && visible && !document.hidden && !disposed) {lastTime=performance.now();frame=requestAnimationFrame(render);} }
  function resize() {
    if(!renderer || !stage.clientWidth || !stage.clientHeight)return;
    camera.aspect=stage.clientWidth/stage.clientHeight;camera.updateProjectionMatrix();
    renderer.setSize(stage.clientWidth,stage.clientHeight,false);requestRender();
  }
  function setLid(which) {
    const isFront=which==='front',key=isFront?'front':'heat',angle=isFront?90:105;
    state[key]=state[key]?0:angle;
    const button=isFront?frontButton:heatButton;
    button.setAttribute('aria-pressed',String(state[key]>0));
    button.setAttribute('aria-label',(state[key]?'Close ':'Open ')+(isFront?'front lid':'heating lid'));
    status.textContent=(isFront?'Front lid':'Heating lid')+(state[key]?' open':' closed');requestRender();
  }
  frontButton.addEventListener('click',()=>setLid('front'));
  heatButton.addEventListener('click',()=>setLid('heat'));
  viewControl.addEventListener('change',()=>{[state.yaw,state.pitch]=views[viewControl.value];state.zoom=1;requestRender();});
  root.querySelectorAll('[data-viewer-zoom]').forEach(button=>button.addEventListener('click',()=>{
    state.zoom=Math.max(.72,Math.min(1.6,state.zoom*Number(button.dataset.viewerZoom)));requestRender();
  }));

  async function initialize() {
    if(loading || renderer || disposed)return;
    loading=true;const id=++generation;
    start.textContent='Loading 3D…';start.disabled=true;start.hidden=false;root.dataset.state='loading';
    let controller;
    try {
      const probe=document.createElement('canvas'),context=probe.getContext('webgl2')||probe.getContext('webgl');
      if(!context)throw new Error('WebGL unavailable');
      context.getExtension('WEBGL_lose_context')?.loseContext();
      await loadScript(asset('vendor/three-0.134.0.min.js'),()=>Boolean(window.THREE));
      await loadScript(asset('vendor/gltf-loader-0.134.0.js'),()=>Boolean(window.THREE?.GLTFLoader));
      controller=new AbortController();const timeout=setTimeout(()=>controller.abort(),15000);
      let data;
      try {
        const response=await fetch(root.dataset.model,{signal:controller.signal});
        if(!response.ok)throw new Error('Model unavailable');data=await response.arrayBuffer();
      } finally {clearTimeout(timeout);}
      if(id!==generation || disposed)return;
      const THREE=window.THREE;
      const gltf=await new Promise((resolve,reject)=>new THREE.GLTFLoader().parse(data,'',resolve,reject));
      if(id!==generation || disposed)return;
      scene=new THREE.Scene();model=gltf.scene;scene.add(model);
      front=model.getObjectByName('FrontLidPivot');heater=model.getObjectByName('HeatingLidPivot');
      if(!front || !heater)throw new Error('Model parts unavailable');
      renderer=new THREE.WebGLRenderer({antialias:true,alpha:true,powerPreference:'low-power'});
      renderer.setPixelRatio(Math.min(window.devicePixelRatio||1,1.75));
      renderer.outputEncoding=THREE.sRGBEncoding;renderer.physicallyCorrectLights=true;
      renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.05;
      renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFSoftShadowMap;
      camera=new THREE.PerspectiveCamera(36,1,.005,5);
      scene.add(new THREE.HemisphereLight(0xeaf3ff,0x747b85,2.1));
      const light=new THREE.DirectionalLight(0xfffaf4,3.2);light.position.set(-.4,.85,.65);light.castShadow=true;
      light.shadow.mapSize.set(1024,1024);Object.assign(light.shadow.camera,{left:-.65,right:.65,top:.7,bottom:-.5,near:.05,far:2.5});
      light.shadow.bias=-.00012;light.shadow.normalBias=.0005;scene.add(light);
      const fill=new THREE.DirectionalLight(0xdbeeff,1.6);fill.position.set(.6,.3,-.5);scene.add(fill);
      model.traverse(o=>{if(o.isMesh){o.castShadow=true;o.receiveShadow=true;if(o.material)o.material.envMapIntensity=.8;}});
      const room=new THREE.Scene();room.background=new THREE.Color(0x9faabc);
      const box=new THREE.Mesh(new THREE.BoxGeometry(10,10,10),new THREE.MeshBasicMaterial({color:0xabb6c3,side:THREE.BackSide}));room.add(box);
      for(const [w,h,pos,rot] of [[4,4,[0,4,0],[Math.PI/2,0,0]],[3,5,[-4,0,1],[0,Math.PI/2,0]],[2,4,[3,1,3],[0,-Math.PI/4,0]]]){
        const plane=new THREE.Mesh(new THREE.PlaneGeometry(w,h),new THREE.MeshBasicMaterial({color:new THREE.Color(3,3,3),side:THREE.DoubleSide}));
        plane.position.set(...pos);plane.rotation.set(...rot);room.add(plane);
      }
      const pmrem=new THREE.PMREMGenerator(renderer);environment=pmrem.fromScene(room,.07);scene.environment=environment.texture;pmrem.dispose();
      room.traverse(o=>{if(o.isMesh){o.geometry.dispose();o.material.dispose();}});
      const ground=new THREE.Mesh(new THREE.PlaneGeometry(3,3),new THREE.ShadowMaterial({opacity:.13}));
      ground.rotation.x=-Math.PI/2;ground.position.y=-.0005;ground.receiveShadow=true;scene.add(ground);
      const canvas=renderer.domElement;
      canvas.setAttribute('role','img');canvas.setAttribute('aria-label','Interactive RYNOR machine concept with fixed touchscreen, opening front and heating lids, side power controls and rear vent');
      canvas.setAttribute('aria-describedby','machine-viewer-help');canvas.dataset.lenisPrevent='';
      let pointer=null,lastX=0,lastY=0;
      canvas.addEventListener('pointerdown',event=>{
        if(event.button!==0 || pointer!==null)return;
        pointer=event.pointerId;lastX=event.clientX;lastY=event.clientY;canvas.setPointerCapture(pointer);
      });
      canvas.addEventListener('pointermove',event=>{
        if(event.pointerId!==pointer)return;
        state.yaw-=(event.clientX-lastX)*.008;
        if(event.pointerType!=='touch')state.pitch=Math.max(-.08,Math.min(1.49,state.pitch+(event.clientY-lastY)*.007));
        lastX=event.clientX;lastY=event.clientY;requestRender();
      });
      const release=event=>{if(event.pointerId===pointer)pointer=null;};
      canvas.addEventListener('pointerup',release);canvas.addEventListener('pointercancel',release);
      contextLostHandler=event=>{event.preventDefault();if(!disposed)fallback();};
      canvas.addEventListener('webglcontextlost',contextLostHandler,{once:true});
      stage.prepend(canvas);controls.hidden=false;help.hidden=false;
      resizeObserver=new ResizeObserver(resize);resizeObserver.observe(stage);resize();
      frontButton.setAttribute('aria-pressed',String(state.front>0));heatButton.setAttribute('aria-pressed',String(state.heat>0));
      currentFront=state.front;currentHeat=state.heat;yaw=state.yaw;pitch=state.pitch;
      render(performance.now());root.dataset.state='ready';root.querySelector('.machine-viewer__badge').textContent='Interactive concept';start.hidden=true;
    } catch {if(id===generation && !disposed)fallback();}
    finally {loading=false;}
  }
  start.addEventListener('click',initialize);
  const observer=new IntersectionObserver(entries=>{
    visible=entries[0].isIntersecting;
    if(visible){if(!renderer && root.dataset.state==='idle' && !navigator.connection?.saveData)initialize();else requestRender();}
    else {cancelAnimationFrame(frame);frame=0;}
  },{rootMargin:'100px 0px'});
  observer.observe(root);
  document.addEventListener('visibilitychange',()=>{if(document.hidden){cancelAnimationFrame(frame);frame=0;}else requestRender();});
  reduced.addEventListener('change',requestRender);
  window.addEventListener('pagehide',()=>{disposed=true;generation++;releaseResources();});
  window.addEventListener('pageshow',event=>{if(event.persisted){disposed=false;loading=false;root.dataset.state='idle';if(visible && !navigator.connection?.saveData)initialize();}});
})();
