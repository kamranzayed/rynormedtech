(() => {
  'use strict';
  const learning=document.querySelector('[data-pd-learning]');
  const reduced=matchMedia('(prefers-reduced-motion: reduce)');
  if(learning){
    const phases={fill:['Fill: fresh fluid goes in','The cycler moves prescribed dialysis fluid through the catheter into the space inside the belly.'],dwell:['Dwell: give the fluid time','The fluid stays in the belly while waste and extra water pass across its lining into the fluid.'],drain:['Drain: used fluid leaves','The cycler drains used fluid through the catheter. Another prescribed cycle can then begin.']};
    const play=learning.querySelector('[data-cycle-play]');let timer=null,index=0;
    const stop=()=>{clearTimeout(timer);timer=null;learning.classList.remove('is-playing');play.textContent='Play the exchange';play.setAttribute('aria-pressed','false');};
    const show=phase=>{learning.dataset.phase=phase;learning.querySelector('[data-phase-title]').textContent=phases[phase][0];learning.querySelector('[data-phase-text]').textContent=phases[phase][1];learning.querySelectorAll('[data-phase-button]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.phaseButton===phase)));};
    const step=()=>{if(index>=3){stop();return;}show(['fill','dwell','drain'][index++]);timer=setTimeout(step,6000);};
    learning.querySelectorAll('[data-phase-button]').forEach(b=>b.addEventListener('click',()=>{stop();show(b.dataset.phaseButton);}));
    play.hidden=false;play.setAttribute('aria-pressed','false');
    play.addEventListener('click',()=>{if(timer){stop();return;}index=0;learning.classList.add('is-playing');play.textContent='Pause the exchange';play.setAttribute('aria-pressed','true');step();});
    document.addEventListener('visibilitychange',()=>{if(document.hidden)stop();});
    reduced.addEventListener('change',()=>{if(reduced.matches)stop();});
  }
  const quiz=document.querySelector('[data-pd-quiz]');
  if(quiz){
    const questions=[{q:'What moves through an APD cycler?',a:['Dialysis fluid','Blood outside the body'],correct:0,why:'The cycler moves dialysis fluid. Your blood stays inside your body.'},{q:'Who decides if PD is suitable for you?',a:['The kidney-care team','The result of a website quiz'],correct:0,why:'Your kidney-care team assesses your health, home situation and support needs.'},{q:'Does home PD remove the need for follow-up?',a:['Yes—no clinic reviews are needed','No—reviews and tests are still needed'],correct:1,why:'Home treatment still needs clinical monitoring, supplies and a daily care routine.'}];
    let index=0,answered=false;const buttons=[...quiz.querySelectorAll('[data-quiz-answer]')],next=quiz.querySelector('[data-quiz-next]'),feedback=quiz.querySelector('[data-quiz-feedback]');
    const show=()=>{const q=questions[index];answered=false;quiz.querySelector('[data-quiz-count]').textContent=`Question ${index+1} of 3`;quiz.querySelector('[data-quiz-question]').textContent=q.q;buttons.forEach((b,i)=>{b.textContent=q.a[i];b.setAttribute('aria-pressed','false');b.disabled=false;});feedback.hidden=true;next.hidden=true;};
    buttons.forEach((button,i)=>button.addEventListener('click',()=>{const q=questions[index];answered=true;buttons.forEach((b,j)=>b.setAttribute('aria-pressed',String(i===j)));feedback.textContent=(i===q.correct?'That’s right. ':'Here’s the key idea: ')+q.why;feedback.hidden=false;next.textContent=index===2?'Try the questions again ↻':'Next question →';next.hidden=false;}));
    next.addEventListener('click',()=>{if(!answered)return;index=(index+1)%3;show();quiz.querySelector('[data-quiz-question]').scrollIntoView({block:'nearest',behavior:'auto'});buttons[0].focus({preventScroll:true});});show();
  }
  const form=document.querySelector('[data-interest-form]');
  if(!form)return;
  const method=form.querySelector('[name=contact_method]'),contact=form.querySelector('#interest-contact'),name=form.querySelector('[name=name]');
  const organisation=form.querySelector('[name=organisation]'),doctorField=form.querySelector('[data-doctor-field]');
  const status=form.querySelector('[data-interest-status]'),submit=form.querySelector('[type=submit]'),label=form.querySelector('[data-interest-submit]');
  let sending=false;
  form.querySelector('[data-contact-choice]').hidden=false;
  function setMethod(clear=false){
    if(clear)contact.value='';
    const email=method.value==='email';contact.name=email?'email':'phone';contact.type=email?'email':'tel';contact.autocomplete=email?'email':'tel';contact.inputMode=email?'email':'tel';
    contact.maxLength=email?180:32;contact.placeholder=email?'you@example.com':'For example, +91 and your number';
    form.querySelector('[data-contact-label]').textContent=email?'Email address':'Phone number';contact.setCustomValidity('');
  }
  function setAudience(){const doctor=form.querySelector('[name=audience]:checked').value==='doctor';doctorField.hidden=!doctor;organisation.disabled=!doctor;label.textContent=doctor?'Connect with RYNOR':'Register my interest';if(!contact.value){method.value=doctor?'email':'phone';setMethod();}form.dataset.audience=doctor?'doctor':'patient_or_caregiver';}
  if(new URLSearchParams(location.search).get('audience')==='doctor')form.querySelector('[name=audience][value=doctor]').checked=true;
  form.querySelectorAll('[name=audience]').forEach(input=>input.addEventListener('change',setAudience));
  method.addEventListener('change',()=>setMethod(true));setMethod();setAudience();
  const showStatus=(state,text)=>{status.dataset.state=state;status.textContent=text;status.hidden=false;};
  form.addEventListener('input',()=>{name.setCustomValidity('');contact.setCustomValidity('');if(!sending)status.hidden=true;});
  form.addEventListener('submit',async event=>{
    event.preventDefault();if(sending)return;
    name.value=name.value.trim();contact.value=contact.value.trim();name.setCustomValidity(name.value?'':'Please enter your name.');
    const phone=method.value==='phone',digits=contact.value.replace(/\D/g,'');
    contact.setCustomValidity(phone && (digits.length<7||digits.length>15||!/^[+\d\s().-]+$/.test(contact.value))?'Please enter a phone number with 7 to 15 digits, including your country code if needed.':'');
    if(!form.reportValidity())return;
    const fields=new FormData(form),audience=fields.get('audience');
    fields.set('contact_method',phone?'phone':'email');
    fields.set(phone?'phone':'email',phone?(contact.value.startsWith('+')?'+':'')+digits:contact.value);
    fields.set('topic',audience==='doctor'?'Doctor / PD professional interest':'Patient / caregiver PD interest');
    fields.set('_subject','RYNOR PD interest — '+(audience==='doctor'?'Doctor / professional':'Patient / caregiver'));
    fields.set('consent_at_client',new Date().toISOString());
    fields.set('contact_consent','yes');fields.set('updates_consent',form.querySelector('[name=updates_consent]').checked?'yes':'no');
    fields.set('consent_text','I am 18 or over and agree that RYNOR may use these details to contact me about my PD interest, as described in the privacy notice.');
    for(const key of ['name','city','preferred_language','organisation'])if(fields.has(key))fields.set(key,String(fields.get(key)).trim());
    sending=true;form.setAttribute('aria-busy','true');const elements=[...form.querySelectorAll('input,select,button')];
    const previousDisabled=elements.map(e=>e.disabled);elements.forEach(e=>e.disabled=true);label.textContent='Sending…';showStatus('sending','Sending your interest to RYNOR…');
    const controller=new AbortController(),timeout=setTimeout(()=>controller.abort(),20000);
    try{
      const response=await fetch(form.action,{method:'POST',body:fields,headers:{Accept:'application/json'},signal:controller.signal});
      const result=await response.json();if(!response.ok||result.ok!==true)throw new Error('Submission not confirmed');
      form.reset();showStatus('success','Thank you. Your interest has been submitted to RYNOR. We can contact you using the method you chose. This is not a treatment booking or trial enrolment.');
    }catch{showStatus('error','We couldn’t confirm your submission. Your details are still here. Please try again, or email syedkamran@rynormedtech.com.');}
    finally{clearTimeout(timeout);sending=false;form.removeAttribute('aria-busy');elements.forEach((e,i)=>e.disabled=previousDisabled[i]);setMethod();setAudience();}
  });
})();
