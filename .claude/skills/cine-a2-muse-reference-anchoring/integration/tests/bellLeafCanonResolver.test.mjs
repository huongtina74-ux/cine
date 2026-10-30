import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {dirname,resolve} from 'node:path';
import {resolveShot, resolveCharacterRefs, resolveLocationRefs,buildBellLeafPrompt,runBellLeafQC,CanonBlocked} from '../src/bellLeafCanonResolver.ts';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const load=x=>JSON.parse(readFileSync(resolve(root,x),'utf8'));
const charBase=load('config/CHARACTER_CURRENT.json');const locBase=load('config/LOCATION_CURRENT.json');const origShot=load('examples/EP001_S010.shot.json');
const hash='a'.repeat(64);
const mkRef=id=>({asset_id:id,file:'fixtures/'+id+'.png',sha256:hash,status:'APPROVED_FOR_REFERENCE',approved_by:'fixture-reviewer',approved_at:'2026-10-29T10:00:00Z'});
function fixtures(){
 const c=structuredClone(charBase);const l=structuredClone(locBase);
 for(const t of ['Lia','bubu'])c.characters[t].approved_assets=[mkRef(`CH_${t}_MASTER_FRONT_FULL_BODY`)];
 l.locations.BELL.spaces['BH-ATELIER'].views.FORWARD=mkRef('BH-ATELIER_FORWARD');
 l.locations.BELL.spaces['BH-EXT'].views.MASTER_WIDE=mkRef('BH-EXT_MASTER_WIDE');
 return {c,l};
}
function failsCode(fn,code){assert.throws(fn,e=>e instanceof CanonBlocked && e.code===code);}
test('01 no reference images in source registry are approved by default',()=>{
 assert.equal(charBase.characters.Lia.approved_assets.length,0);
 assert.equal(Object.keys(locBase.locations.BELL.spaces['BH-ATELIER'].views).length,0);
});
test('02 2 visible characters resolve exactly 2 refs',()=>{
 const {c,l}=fixtures(); const r=resolveShot(origShot,c,l);
 assert.equal(r.character_refs.length,2);assert.equal(r.location_refs.length,1);
 assert.deepEqual(r.character_refs.map(x=>x.asset_id),['CH_Lia_MASTER_FRONT_FULL_BODY','CH_bubu_MASTER_FRONT_FULL_BODY']);
});
test('03 zero-character shot attaches zero refs but still requires BELL location ref',()=>{
 const {c,l}=fixtures();const s=load('examples/EP001_S001.zero_character.shot.json');const r=resolveShot(s,c,l);
 assert.equal(r.character_refs.length,0);assert.equal(r.location_refs.length,1);
});
test('04 missing approved character blocks, including source image only',()=>{
 const {l}=fixtures();failsCode(()=>resolveShot(origShot,charBase,l),'MISSING_APPROVED_CHARACTER');
});
test('05 missing approved location blocks rather than inventing room',()=>{
 const {c}=fixtures();failsCode(()=>resolveShot(origShot,c,locBase),'MISSING_APPROVED_LOCATION');
});
test('06 unknown tag, mixed case, duplicates, wrong space all fail',()=>{
 const {c,l}=fixtures();
 failsCode(()=>resolveShot({...origShot,activeCharacterTags:['lia']},c,l),'UNKNOWN_CHARACTER_TAG');
 failsCode(()=>resolveShot({...origShot,activeCharacterTags:['Lia','Lia']},c,l),'DUPLICATE_TAGS');
 failsCode(()=>resolveShot({...origShot,space_id:'WORKSHOP'},c,l),'UNKNOWN_SPACE');
});
test('07 me resolves only Mara when approved, never @me avatar',()=>{
 const {c,l}=fixtures();c.characters.me.approved_assets=[mkRef('CH_me_MASTER_FRONT_FULL_BODY')];
 const r=resolveShot({...origShot,activeCharacterTags:['me']},c,l);
 assert.equal(r.character_refs[0].asset_id,'CH_me_MASTER_FRONT_FULL_BODY');
});
test('08 paternal grandfather is distinct from Orin; no silent fallback',()=>{
 const {c,l}=fixtures();c.characters.ongngoai.approved_assets=[mkRef('CH_ongngoai_MASTER_FRONT_FULL_BODY')];
 failsCode(()=>resolveShot({...origShot,activeCharacterTags:['ongnoi']},c,l),'MISSING_APPROVED_CHARACTER');
});
test('09 generated prompt requires single frame, no subtitles, D55 and first moment',()=>{
 const {c,l}=fixtures();const p=resolveShot(origShot,c,l).prompt;
 for(const token of ['SINGLE','16:9','D55/5500K','No collage','FIRST FRAME ONLY','Lia, bubu'])assert.ok(p.includes(token),token);
});
test('10 QC distinguishes image obtained from human approval',()=>{
 const basic={width:1920,height:1080,panel_count:1,text_overlay:false,identity_review:'NOT_REVIEWED',location_review:'NOT_REVIEWED',color_review:'NOT_REVIEWED'};
 assert.equal(runBellLeafQC(basic).status,'QC_REVIEW_REQUIRED');
 assert.deepEqual(runBellLeafQC({...basic,panel_count:9}).flags,['QC_FAIL_MULTIPANEL']);
 assert.equal(runBellLeafQC({...basic,identity_review:'PASS',location_review:'PASS',color_review:'PASS',reviewer:'art director'}).status,'QC_PASS');
});
test('11 rendered image with text fails',()=>{
 assert.deepEqual(runBellLeafQC({width:1920,height:1080,panel_count:1,text_overlay:true,identity_review:'PASS',location_review:'PASS',color_review:'PASS',reviewer:'human'}).status,'QC_FAIL');
});
test('12 10-second duration must be explicit',()=>{
 const {c,l}=fixtures();failsCode(()=>resolveShot({...origShot,duration_seconds:8},c,l),'DURATION_MISMATCH');
});