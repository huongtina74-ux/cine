"""Audit 2026-11-11 step 2: one mutually exclusive primary_format (A1-A9) per video.

Input (read-only copy of the owner-PC dataset): DATA = .../2026-11-11_niche_compare/{rows,channels}.json
Output: classified_videos.csv / .json next to this script.
Channel overrides carry their evidence level: THUMBNAIL_VERIFIED = the top sampled long video's thumbnail was looked at
on 2026-11-11 in the owner's browser; METADATA_ONLY = title/channel name only. Everything else = keyword rule (low).
"""
import collections
import csv
import json
import os
import re
import sys

DATA = sys.argv[1] if len(sys.argv) > 1 else '/mnt/user-data/uploads/Downloads/cine_niche_survey/out/2026-11-11_niche_compare/'
HERE = os.path.dirname(os.path.abspath(__file__))
R = json.load(open(os.path.join(DATA, 'rows.json')))
C = json.load(open(os.path.join(DATA, 'channels.json')))
TV, MD = 'THUMBNAIL_VERIFIED', 'METADATA_ONLY'
O = {}


def o(names, fmt, tags, conf, ev, lvl=MD):
    for n in names:
        O[n] = (fmt, tags, conf, ev, lvl)


o(['Nobody Gets In', 'Beanie Survives', 'DoodleSurvivals', 'Kit vs The End', 'StickFallout', 'Stick Through Collapse', 'WhyThat',
   'Wild Instinct', 'Marrow  ', 'LateVids', 'Jack Stone', 'Stickvival'], 'A3', 'zombie_survival|day_counter|2d_stick', 'high',
  '2D stick-figure characters on painted backgrounds in thumbnail; no Minecraft blocks', TV)
o(['Başına Gelse¿'], 'A3', 'zombie_survival', 'medium', 'Turkish Day-N outbreak title (metadata)')
o(['Day Zero', 'BlakeCraft', 'Tomatikk', 'KnightMC', 'unsorted guy', 'IsKevin', 'Wrld'], 'A1', 'survival|100_days|realistic', 'high',
  'Minecraft blocks/shaders visible in thumbnail; 100-days survival title', TV)
o(['Clooless Gaming'], 'A1', 'modded|horror|facecam', 'high', 'facecam + Minecraft in thumbnail', TV)
o(['imKaiL00L', 'SirCloaked', 'Sage', 'Byzor', 'Rumble Ron'], 'A5', 'horror_mod', 'high', 'Minecraft + horror creature in thumbnail', TV)
o(['Smellzzy+'], 'A5', 'concept_mod|phobia', 'medium', 'Minecraft skins + disease/phobia concept in thumbnail', TV)
o(['BionicTV', 'ItzHydra'], 'A6', 'investigation', 'high', 'mystery/investigation thumbnail (deleted mob / glitched face)', TV)
o(['GupMC', 'Sticks', 'MarBear', 'LookOut2DD', 'Banazen Craft'], 'A2', 'machinima', 'medium', 'scripted Minecraft-style film/roleplay thumbnail', TV)
o(['Veynor', 'CarMe', 'GameToons', 'EmortalMarcus', 'Mob Rift'], 'A9', 'not_minecraft_or_ai_compare', 'high',
  'non-Minecraft animation or AI real-life comparison in thumbnail', TV)
o(['Automa'], 'A9', 'verity_ip_physics_sim', 'medium', '3D physics sim of third-party Verity character', TV)
o(['Maizen', 'MSToons', 'Cubeee Animations', 'Ligabka', 'Морфиз', 'Mine Block', 'Takuto - Minecraft Animation', 'Chapapa Animation',
   'Plomby – Mikey & JJ Minecraft', 'Mikey Spikey', 'Mikey Maizen - Minecraft', 'Mikey & JJ - Minecraft', 'Maizen - Minecraft Family',
   'Maizen Squad', 'Zentry - JJ & Mikey Minecraft', 'MyMy toon', 'GameToons Movies', 'GameToons +', 'my MONSTER SCHOOL', 'Alien Being',
   'Squared Media', 'Aphmau', 'Salt', 'Milo and Chip', 'Mizzi', 'MV Channel', 'JoofyLooby', 'Knoxy', 'sequence'],
  'A2', 'machinima|roleplay', 'medium', 'known Minecraft animation/roleplay channel (metadata)')
o(['ZAMination', 'Alan Becker', 'SlicK', 'George Pig - Official Channel', 'LunioVerse', 'Joe Bart Games', 'Silver', 'Flight Gamer',
   'Granty', 'Dr Duke', 'wat007', 'NotGamerFleet', 'KTG Gaming', 'Camodo Gaming', 'Caylus  ', 'iCrimax', 'Mahjong Blonsky', 'Maruf',
   'aCookieGod', 'Felipe Neto', 'More jessetc', 'Dash Roblox', 'Zubair Trabzada | AI Workshop', 'Stefan 3D AI', 'We Do Tech',
   'Kauã Miguel - Dev', 'Vitor Menoli', 'HORSE 4U', 'onue onue', 'The Film Theorists', 'Krastalax', 'Cool Tool WOW', 'MasterBuilders',
   'Telugu Experiments Family', 'BANJARA GMR', 'Low Level', 'Tyler & Snowi', 'TerrifyTee', 'Snarple', 'Pixden', 'Jeete Horror', 'YouTube',
   'FWFworks', 'JudeLowRussia', 'Henreee', 'UnstableTheory', 'Tayler', 'Navex', 'MangoSweat', 'babyjamie1'],
  'A9', 'not_minecraft_or_drama', 'medium', 'not Minecraft content, or creator-drama commentary (metadata)')
o(['Mumbo Jumbo', 'Mumbo but more Jumbo', 'RagePlaysGames', 'qarsan', 'Sbeev', 'WoodChuck', 'commonLuke', 'Element X', 'Purplers',
   'ECKOSOLDIER', 'Skizzle', 'Prism', 'Doodle', 'Mr.Lumpapa', 'KIAN', 'Daniel Krafft', 'Whimzee', 'CraftyMasterman', 'Skiddzie', 'DavidMC'],
  'A7', 'engineering', 'medium', 'known technical/redstone/experiment channel (metadata)')
o(['Joe Bartolozzi', 'The Game Theorists', 'Skip the Tutorial', 'Dialko', 'bubbybumble', 'liamvz', 'PlatoCat', 'Odyssey Central', 'Леоша',
   'acetwothree', 'sleepin', 'Phoenix SC', 'gerg', 'Jakka'], 'A8', 'lore_history', 'medium', 'documentary/lore/update channel (metadata)')
o(['ZolisterTV', 'jimdoga2', 'Parallax', 'j-gems', 'noblevox', 'Joost Joe', 'CloudyDreamzs', 'Namentix', 'Channy', 'Kiply'],
  'A6', 'mystery|arg|found_footage', 'medium', 'mystery/ARG/found-footage title pattern (metadata)')
o(['ohnepixel raw', 'CaseOh', 'steak', 'Vrumpo', 'Doni Bobes', 'Toxin', 'YokaSiri MC', '8-BitRyan', 'GOOBER GANG', 'Jynxzi Live', 'Wisp',
   'Tom', 'Chazington', 'JoeyShmoovin', 'LazarLazar', 'NotVixios', 'One Last Time', 'Vanilte', 'Shoco21', 'ShadowMech', 'Puff', 'CASTER',
   'kihec', 'Swayle', 'Vivilly', 'Karl', 'Ayu Playz', 'Pepper', 'ProVZzz', 'Vex Plays2', 'Krax plays', 'MinePush', 'S3ISMIC', 'Daiazal',
   'Kratzy', 'CheapPickle', 'al1'], 'A5', 'horror_mod', 'medium', 'horror/mod gameplay title pattern (metadata)')

o(['Syn Knows Games'], 'A9', 'fnaf_lore_not_minecraft', 'high', 'storyboard shows FNAF 2D/3D documentary, no Minecraft', 'STORYBOARD_SAMPLED')
o(['Stick It Out'], 'A3', 'zombie_survival|day_counter', 'medium', 'Day-N "Zombie Outbreak ... (Full Movie)" stick format (metadata; channel name)')
o(['Bionic', 'Flush', 'ScardJester', 'PixelNaut', 'TrainerDario', 'OwlOFC'], 'A5', 'horror_mod', 'medium', 'horror mod/entity title (metadata)')
o(['SSundeePlus'], 'A1', 'minigame|established_creator_spinoff', 'medium', 'SSundee spin-off channel name (metadata)')
o(['Caaligo', 'Freshi'], 'A6', 'arg_commentary', 'low', 'ARG/mystery title (metadata)')
o(['Xatrix', 'The Games Professor'], 'A8', 'lore', 'low', 'lore/theory title (metadata)')
o(['Uncharted Origin', 'What If Stickman', 'Hidden Truth Explained', 'Ras Mic', 'Slop Architect', 'Epsilon', 'MrOhhG', 'UrGunGirl', 'Oakley',
   'Bluer Pikmin'], 'A9', 'not_minecraft_or_drama', 'low', 'not Minecraft or drama/reaction (metadata)')

_ACC = re.compile(r"[áéíóúñãõçğşıäöüßạảấầẩậắằẳặẹẻẽếềểễệịọỏốồổỗộớờởỡợụủứừửữựỳỷỹđÁÉÍÓÚÑÃÕÇĞŞİÄÖÜĐ]")  # no re.I: 'ı' would fold to 'i'
_WORD = re.compile(r"\b(de|la|el|los|las|del|dias|hari|di|ich|und|aber|com|mas|pero|bir|ve|para|sobrevivi|yang|dan)\b", re.I)


class _Foreign:
    @staticmethod
    def search(t):
        return _ACC.search(t) or _WORD.search(t)


FOREIGN = _Foreign()
EN_C = {'US', 'GB', 'CA', 'AU', 'NZ', 'IE', '-', '', 'PH', 'IN', 'DE', 'KW', 'EG', 'KZ', 'TR', 'HR', 'CH', 'SE', 'AE', 'ZA', 'UG', 'SI', 'PL'}


def english(r):
    """ESTIMATED: YouTube audio-language tag when present, else channel country + title script/words."""
    lang = (r['lang'] or '').lower()
    if lang.startswith('en'):
        return not FOREIGN.search(r['title'])
    if lang and not lang.startswith('zx'):
        return False
    c = C.get(r['cid'], {}).get('snippet', {}).get('country', '-') or '-'
    odd = sum(1 for ch in r['title'] if ord(ch) > 0x24F and not 0x1F000 <= ord(ch) <= 0x1FFFF and not 0x2000 <= ord(ch) <= 0x2BFF)
    return c in EN_C and not FOREIGN.search(r['title']) and odd == 0


MC = re.compile(r"minecraft|\bmc\b|creeper|herobrine|verity|\bsmp\b|redstone|enderman|villager|nether|warden|hardcore|one block|skyblock|"
                r"\bjj\b|mikey|maizen|cobblemon", re.I)


NONMC = re.compile(r"roblox|\bgta\b|beamng|\bark\b|clash royale|fortnite|peppa|poppy|lego|software|pok[eé]mon fire|vintage story|"
                   r"oxide|build a boat|steal an egg|99 nights|subnautica|leviathan", re.I)


def rule(t):
    # every sampled video came from a Minecraft search: assume Minecraft unless the title names another game/topic
    if NONMC.search(t):
        return ('A9', 'other_game', 'low', 'title names a non-Minecraft game/topic (metadata)')
    if re.search(r"redstone|create mod|engineer|physics|experiment|machine|piston|computer|tnt|simulat", t, re.I):
        return ('A7', 'engineering', 'low', 'engineering keyword in title')
    if re.search(r"\barg\b|mystery|found footage|investigat|lost media|deleted|cursed|disturbing|exploring|world \d|seed", t, re.I):
        return ('A6', 'mystery', 'low', 'mystery keyword in title')
    if re.search(r"lore|history|explained|theory|origin|every .* (added|removed)|evolution of", t, re.I):
        return ('A8', 'lore', 'low', 'lore keyword in title')
    if re.search(r"horror|scary|scariest|terrif|phobia|creepy|haunted|entity|entities|jerry|godzilla|bloodbath|broken script|cave dweller|"
                 r"stalker|nightmare", t, re.I):
        return ('A5', 'horror', 'low', 'horror keyword in title')
    if re.search(r"animation|movie|cartoon|roleplay|story", t, re.I):
        return ('A2', 'machinima', 'low', 'animation/movie keyword in title')
    return ('A1', 'gameplay', 'low', 'Minecraft gameplay title (default rule)')


APOC = re.compile(r"apocalyp|outbreak|zombie|nuclear|wasteland|purge|infect|parasite|surviv|\d+ days|realistic|hardcore|lost at sea|deserted|"
                  r"island|wilderness", re.I)
out = {}
for r in R:
    if r['id'] in out:
        out[r['id']]['search_niches'] += r['n']
        continue
    ch = r['ch']
    p, tags, conf, ev, lvl = O[ch] if ch in O else (*rule(r['title']), MD)
    if p == 'A1' and APOC.search(r['title']):
        tags += '|apocalypse_survival'
    out[r['id']] = dict(
        video_id=r['id'], title=r['title'], channel=ch, channel_id=r['cid'], views=r['views'], published=r['pub'],
        video_age_days=round(r['age'], 2), duration_s=r['dur'], channel_subs=r['subs'], channel_age_days=round(r['chage'], 1),
        channel_age_at_publish_days=round(r['chage'] - r['age'], 1), made_for_kids=r['mfk'], audio_lang=r['lang'],
        english=english(r), search_niches=r['n'], primary_format=p, secondary_tags=tags, classification_confidence=conf,
        classification_evidence=ev, evidence_level=lvl)
rows = list(out.values())
with open(os.path.join(HERE, 'classified_videos.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)
json.dump(rows, open(os.path.join(HERE, 'classified_videos.json'), 'w'))
print('videos', len(rows), 'english', sum(r['english'] for r in rows))
print('primary', sorted(collections.Counter(r['primary_format'] for r in rows).items()))
print('evidence', collections.Counter(r['evidence_level'] for r in rows), collections.Counter(r['classification_confidence'] for r in rows))
miss = [n for n in O if n not in {r['channel'] for r in rows}]
print('override names not matched:', miss)
