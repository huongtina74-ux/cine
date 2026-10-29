import {readFileSync, realpathSync} from "node:fs";
import {resolve,sep} from "node:path";
import {createHash} from "node:crypto";
/** CINE Slow English A2 / Bell & Leaf production reference resolution.
 * Fail closed, never infer approvals or tags from prompt text.
 * Pure metadata functions: caller must verify file bytes and SHA-256 before invoking generation.
 */
export type CharacterTag = 'bo'|'me'|'juno'|'Lia'|'bubu'|'bix'|'ongngoai'|'bangoai'|'ongnoi'|'banoi';
export type SiteId = 'BELL'|'ORIN'|'ROSE'|'SCHOOL'|'SQUARE'|'POST'|'LIBRARY'|'BRIDGE'|'FOREST'|'BAKERY'|'STATION'|'LAKE';
export type ViewId = 'MASTER_WIDE'|'FORWARD'|'REVERSE_TRUE'|'LEFT_3_4'|'RIGHT_3_4'|'DETAIL_ANCHORS'|'PLAN_TOP';
export type Camera = 'extreme_wide'|'wide'|'medium_wide'|'medium'|'close_up'|'extreme_close_up';
export interface Ref { asset_id:string; file:string; sha256:string; status:string; approved_by?:string|null; approved_at?:string|null; }
export interface CharacterRec { display_name:string; source_original:Ref; approved_assets:Ref[]; pending_new_render_slots:number; approval_state:string; }
export interface Characters {characters: Record<CharacterTag,CharacterRec>}
export interface SpaceRec {display_name:string; views:Partial<Record<ViewId,Ref>>; approval_state:string}
export interface LocationRec {display_name:string; site_id:SiteId; spaces:Record<string,SpaceRec>; status:string}
export interface Locations {locations:Record<SiteId,LocationRec>}
export interface Shot {shot_id:string; activeCharacterTags:CharacterTag[];location_id:SiteId;space_id:string;location_view_id:ViewId;camera_type:Camera;first_frame_action:string;emotion:string[];outfits:Record<string,string>;duration_seconds:10;dialogue_wav?:string|null}
export class CanonBlocked extends Error { readonly code:string; constructor(code:string, message:string){super(message);this.name='CanonBlocked';this.code=code;}}
const TAGS = new Set<CharacterTag>(['bo','me','juno','Lia','bubu','bix','ongngoai','bangoai','ongnoi','banoi']);
const SITES = new Set<SiteId>(['BELL','ORIN','ROSE','SCHOOL','SQUARE','POST','LIBRARY','BRIDGE','FOREST','BAKERY','STATION','LAKE']);
function approved(r:Ref|undefined):r is Ref {
 return !!r && r.status==='APPROVED_FOR_REFERENCE' && /^[a-f0-9]{64}$/.test(r.sha256) && !!r.file && !!r.approved_by && !!r.approved_at;
}
function unique<T>(a:T[]) {return [...new Set(a)];}
function validateShot(shot:Shot) {
 if (!/^EP\d{3,}_S\d{3,}$/.test(shot.shot_id)) throw new CanonBlocked('BAD_SHOT_ID','Unknown shot ID');
 if (!Array.isArray(shot.activeCharacterTags)) throw new CanonBlocked('BAD_TAG_LIST','Must explicitly supply [] or valid tags');
 if (unique(shot.activeCharacterTags).length !== shot.activeCharacterTags.length) throw new CanonBlocked('DUPLICATE_TAGS','Repeated character tag');
 for (const tag of shot.activeCharacterTags) if(!TAGS.has(tag)) throw new CanonBlocked('UNKNOWN_CHARACTER_TAG',`Unknown tag ${tag}`);
 if(!SITES.has(shot.location_id)) throw new CanonBlocked('UNKNOWN_LOCATION',`Unknown site ${shot.location_id}`);
 if(!shot.space_id)throw new CanonBlocked('MISSING_SPACE','Missing location space');
 if(shot.duration_seconds!==10) throw new CanonBlocked('DURATION_MISMATCH','Bell & Leaf I2V duration must be 10s');
 if(!shot.first_frame_action || shot.first_frame_action.length<10)throw new CanonBlocked('MISSING_FIRST_FRAME','Need beginning-of-shot action');
}
export function resolveCharacterRefs(shot:Shot,characters:Characters):Ref[] {
 validateShot(shot);
 const out:Ref[]=[];
 for(const tag of shot.activeCharacterTags){
  const rec=characters.characters[tag];
  if (!rec)throw new CanonBlocked('UNKNOWN_CHARACTER_TAG',`No registry entry for ${tag}`);
  const available=rec.approved_assets.filter(approved);
  if(!available.length)throw new CanonBlocked('MISSING_APPROVED_CHARACTER',`${tag}: master/angle not approved yet`);
  // Angle/face selection can be enriched by explicit tag/view role metadata; no guessing from filenames.
  const master=available.find(r=>r.asset_id===`CH_${tag}_MASTER_FRONT_FULL_BODY`)
   ??available.find(r=>r.asset_id.includes('MASTER')) ?? available[0];
  out.push(master);
 }
 return out;
}
export function resolveLocationRefs(shot:Shot,locations:Locations):Ref[] {
 validateShot(shot);
 const site=locations.locations[shot.location_id];
 if(!site)throw new CanonBlocked('UNKNOWN_LOCATION',`Missing site ${shot.location_id}`);
 const space=site.spaces[shot.space_id];
 if(!space)throw new CanonBlocked('UNKNOWN_SPACE',`Missing space ${shot.location_id}/${shot.space_id}`);
 const ref=space.views[shot.location_view_id];
 if (!approved(ref))throw new CanonBlocked('MISSING_APPROVED_LOCATION',`No approved ${shot.location_id}/${shot.space_id}/${shot.location_view_id} plate`);
 return [ref];
}
export function buildBellLeafPrompt(shot:Shot, charRefs:Ref[], locRefs:Ref[]):string {
 validateShot(shot);
 if(charRefs.length!==shot.activeCharacterTags.length)throw new CanonBlocked('REF_COUNT_MISMATCH','Wrong number of character references');
 if(locRefs.length!==1)throw new CanonBlocked('LOCATION_REF_MISMATCH','Expected one approved location plate');
 return [`One SINGLE professional cinematic 3D CGI animation first-frame image, native full-bleed 16:9.`,
 `Shot ${shot.shot_id}. Visible characters: ${shot.activeCharacterTags.length?shot.activeCharacterTags.join(', '):'none'}.`,
 `Use ONLY attached individually APPROVED original character image references; never recast faces as live-action humans.`,
 `Use the exact approved ${shot.location_id}/${shot.space_id}/${shot.location_view_id} location plate; preserve doors, windows, room layout and fixed props.`,
 `FIRST FRAME ONLY: ${shot.first_frame_action}`,
 `Camera ${shot.camera_type}; emotional tone: ${shot.emotion.join(', ')||'neutral'}.`,
 `Physically credible stylized feature-quality CGI materials, natural neutral D55/5500K photographic white balance, soft physically motivated shadows, true whites, no global yellow/orange cast.`,
 `No collage, no multiple panels, no embedded subtitles, labels, text, watermark, duplicate characters or arbitrary new furniture.`].join(' ');
}
export type QCInput={width:number;height:number;panel_count:number;text_overlay:boolean;identity_review:'PASS'|'FAIL'|'NOT_REVIEWED';location_review:'PASS'|'FAIL'|'NOT_REVIEWED';color_review:'PASS'|'FAIL'|'NOT_REVIEWED';reviewer?:string};
export function runBellLeafQC(q:QCInput):{status:'QC_FAIL'|'QC_REVIEW_REQUIRED'|'QC_PASS';flags:string[]} {
 const flags:string[]=[];
 if(q.width<=0||q.height<=0||Math.abs(q.width/q.height-16/9)>0.02)flags.push('QC_FAIL_ASPECT');
 if(q.panel_count!==1)flags.push('QC_FAIL_MULTIPANEL');
 if(q.text_overlay)flags.push('QC_FAIL_TEXT');
 for(const k of ['identity_review','location_review','color_review'] as const){if(q[k]==='FAIL')flags.push(`QC_FAIL_${k.replace('_review','').toUpperCase()}`)}
 if(flags.length)return {status:'QC_FAIL',flags};
 if(!q.reviewer||q.identity_review!=='PASS'||q.location_review!=='PASS'||q.color_review!=='PASS')return {status:'QC_REVIEW_REQUIRED',flags:['HUMAN_VISUAL_APPROVAL_REQUIRED']};
 return {status:'QC_PASS',flags:[]};
}
export function resolveShot(shot:Shot,characters:Characters,locations:Locations){
 const character_refs=resolveCharacterRefs(shot,characters);
 const location_refs=resolveLocationRefs(shot,locations);
 return {shot_id:shot.shot_id,character_refs,location_refs,prompt:buildBellLeafPrompt(shot,character_refs,location_refs),status:'READY_FOR_SHOT_GENERATION' as const};
}

/** Verify immutable original bytes after metadata resolution; reject missing files and traversal. */
export function verifyReferenceFiles(refs:Ref[], approvedAssetRoot:string):void {
 const root=realpathSync(approvedAssetRoot);
 for(const ref of refs){
  if(!approved(ref))throw new CanonBlocked('REFERENCE_NOT_APPROVED',ref.asset_id);
  const full=realpathSync(resolve(root,ref.file));
  if(full!==root && !full.startsWith(root+sep))throw new CanonBlocked('REFERENCE_PATH_OUTSIDE_ROOT',ref.file);
  const actual=createHash('sha256').update(readFileSync(full)).digest('hex');
  if(actual!==ref.sha256)throw new CanonBlocked('REFERENCE_HASH_MISMATCH',ref.asset_id);
 }
}