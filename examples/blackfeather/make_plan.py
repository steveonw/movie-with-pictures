"""Builds plan.json for Blackfeather Academy in a Box. Edit here, then rerun."""
import json

def sh(img, frm=(.5, .5, 1.0), to=(.5, .5, 1.2), tr='x', at=None, **kw):
    d = {'image': img, 'from': list(frm), 'to': list(to), 'tr': tr}
    if at: d['at'] = at
    d.update(kw); return d

def L(speaker, text, shot=None, display=None, shots=None, fx=None, sfx=None, bed=None, pause=None, lt=None):
    d = {'speaker': speaker, 'text': text}
    if display: d['display'] = display
    if shot: d['shot'] = shot
    if shots: d['shots'] = shots
    if fx: d['fx'] = fx
    if sfx: d['sfx'] = sfx
    if bed: d['bed'] = bed
    if pause is not None: d['pause_after'] = pause
    if lt: d['lower_third'] = lt
    return d

def cue(f, at=None, vol=1.0, **kw):
    d = {'file': f, 'vol': vol}
    if at: d['at'] = at
    d.update(kw); return d

scenes = [
 {'title': 'Is your academy good enough?', 'lines': [
  L('narrator', 'Is your magical academy still relying on outdated teaching methods?',
    sh('classroom_wide', (.5, .5, 1.0), (.62, .55, 1.25)),
    bed=[cue('amb_classroom', vol=.35, dur=9, fade=1.0), cue('music_calm', vol=.55, music=True)]),
  L('professor', 'Incorrect, Thomas. The answer is protective shielding.',
    sh('professor_class', (.45, .4, 1.1), (.5, .35, 1.3))),
  L('thomas', "Oh. I'll remember next time.",
    sh('thomas_bored', (.5, .45, 1.0), (.5, .4, 1.3)), pause=.5),
  L('narrator', 'Next time?', display='Next time?',
    shot=sh('thomas_bored', (.5, .4, 1.3), (.5, .4, 1.3), tr='cont'), pause=.7,
    bed=[cue('STOP_MUSIC')]),
  L('narrator', 'What if there is no next time?', display='What if there IS no next time?',
    shot=sh('black', tr='cut'), pause=.4),
 ]},
 {'title': 'The Blackfeather difference', 'lines': [
  L('narrator', 'At Blackfeather Academy, we believe every mistake should be a memorable learning experience!',
    sh('arena_wide', (.3, .5, 1.0), (.7, .5, 1.15), tr='cut'),
    shots=[sh('owlbear_claws', (.5, .7, 1.0), (.5, .4, 1.25), tr='cut', at='memorable')],
    bed=[cue('music_aspiration', vol=.5, music=True, start=0), cue('growl_mix', at='memorable', vol=.6)]),
  L('instructor', 'Incorrect answer! Pet the owlbear!',
    sh('professor_arena', (.5, .4, 1.0), (.5, .35, 1.25), tr='cut')),
  L('thomas', 'Wait, what?', display='WAIT, WHAT?',
    shot=sh('thomas_eyes', (.5, .5, 1.1), (.5, .5, 1.35), tr='cut'),
    shots=[sh('owlbear_charge', (.5, .5, 1.0), (.5, .45, 1.3), tr='cut', at='what+0.5'),
           sh('thomas_stretcher', (.3, .5, 1.2), (.5, .5, 1.0), tr='cut', at='what+1.5')],
    fx=[{'type': 'shake', 'at': 'what+0.5', 'dur': .8, 'amp': 14}, {'type': 'flash', 'at': 'what+0.5', 'dur': .3},
        {'type': 'shake', 'at': 'what+1.55', 'dur': .4, 'amp': 8}],
    bed=[cue('owlbear_roar', at='what+0.45', vol=1.0), cue('crash_mix', at='what+1.2', vol=.9),
         cue('body_fall', at='what+1.55', vol=.8), cue('DUCK', at='what+0.45', dur=2.0)], pause=2.0),
  L('narrator', "Now that's a lesson he'll never forget!", display="Now THAT'S a lesson he'll never forget!",
    shot=sh('thomas_stretcher', (.5, .5, 1.0), (.55, .5, 1.25), tr='cont')),
 ]},
 {'title': 'Introducing the box', 'lines': [
  L('narrator', 'Introducing Blackfeather Academy in a Box!', display='Introducing BLACKFEATHER ACADEMY IN A BOX!',
    shot=sh('box_hero', (.5, .6, 1.0), (.5, .5, 1.2), tr='flash'),
    bed=[cue('STOP_MUSIC'), cue('fanfare', vol=.75, music=True, start=0), cue('shimmer_hit', vol=.5)]),
  L('narrator', "The world's most effective magical training system, now delivered directly to your academy!",
    display="The world's most effective magical training system, now delivered directly to YOUR academy!",
    shot=sh('box_label', (.5, .5, 1.0), (.5, .5, 1.25), tr='cut'),
    shots=[sh('box_dimensions', (.5, .5, 1.0), (.5, .45, 1.05), tr='cut', at='delivered')], pause=.5),
 ]},
 {'title': "What's inside?", 'lines': [
  L('healer', "Hello! I'm Master Healer Helena Stitchwell, and I come with your box!",
    sh('helena_box', (.4, .4, 1.35), (.4, .38, 1.45), tr='cut'),
    lt=['MASTER HEALER HELENA STITCHWELL', 'Included with every box'],
    sfx=[{'type': 'tink', 'at': 'box'}], bed=[cue('STOP_MUSIC'), cue('music_aspiration', vol=.4, music=True, start=20)]),
  L('narrator', 'Every package includes a complete curriculum, advanced training facilities, certified instructional monsters, and your very own Blackfeather-trained healer!',
    sh('box_hero', (.2, .7, 1.5), (.3, .65, 1.5), tr='cut'),
    shots=[sh('owlbear_peek', (.5, .5, 1.0), (.5, .5, 1.25), tr='cut', at='monsters'),
           sh('helena_box', (.5, .5, 1.0), (.5, .5, 1.1), tr='cut', at='healer')],
    bed=[cue('growl_low', at='monsters+0.2', vol=.5)]),
  L('healer', 'Please stand back while I open the box.',
    sh('helena_box', (.6, .5, 1.1), (.6, .5, 1.2), tr='cont')),
  L('headmaster', 'How dangerous could', display='How dangerous could—',
    shot=sh('headmaster_lean', (.5, .45, 1.1), (.5, .4, 1.3), tr='cut'),
    shots=[sh('box_explode', (.5, .5, 1.25), (.5, .5, 1.0), tr='flash', at='could+0.2'),
           sh('owlbear_tackle', (.4, .5, 1.0), (.6, .5, 1.2), tr='cut', at='could+1.2')],
    fx=[{'type': 'shake', 'at': 'could+0.2', 'dur': 1.0, 'amp': 18}, {'type': 'debris', 'at': 'could+0.25', 'dur': 2.5, 'n': 50},
        {'type': 'shake', 'at': 'could+1.3', 'dur': .5, 'amp': 10}],
    bed=[cue('STOP_MUSIC', at='could'), cue('explosion_mix', at='could+0.12', vol=1.0),
         cue('owlbear_roar', at='could+1.1', vol=.9), cue('crash_mix', at='could+1.4', vol=.7)], pause=2.4),
  L('healer', "And that's why I'm included!",
    sh('helena_smile', (.5, .45, 1.0), (.5, .42, 1.15), tr='cut'),
    bed=[cue('music_aspiration', vol=.45, music=True, start=40)]),
 ]},
 {'title': 'Real training. Real results.', 'lines': [
  L('narrator', 'Why settle for theoretical knowledge when your students can develop real battlefield reflexes, real defensive skills, and real practical experience?',
    display='Why settle for theoretical knowledge when your students can develop REAL battlefield reflexes, REAL defensive skills, and REAL practical experience?',
    shot=sh('montage_a', (.3, .5, 1.0), (.7, .5, 1.2), tr='cut'),
    shots=[sh('montage_b', (.5, .5, 1.25), (.5, .5, 1.0), tr='cut', at='real#1'),
           sh('montage_c', (.5, .5, 1.0), (.5, .45, 1.25), tr='cut', at='real#2'),
           sh('montage_d', (.6, .5, 1.0), (.4, .5, 1.2), tr='cut', at='real#3')],
    bed=[cue('fireball', vol=.8), cue('amb_fire', vol=.3, dur=4, fade=1),
         cue('shield_hit', at='real#1', vol=.7), cue('heal_spell', at='real#2', vol=.6), cue('growl_mix', at='real#3', vol=.6)]),
  L('instructor', "What's the third principle of defensive spellcraft?", display="WHAT'S THE THIRD PRINCIPLE OF DEFENSIVE SPELLCRAFT?",
    shot=sh('professor_arena', (.45, .4, 1.3), (.45, .35, 1.45), tr='cut')),
  L('thomas', 'Adaptability!', display='ADAPTABILITY!',
    shot=sh('montage_d', (.7, .3, 1.5), (.7, .32, 1.5), tr='cut'),
    shots=[sh('montage_e', (.5, .5, 1.0), (.5, .5, 1.25), tr='cut', at='adaptability+0.8')],
    fx=[{'type': 'flash', 'at': 'adaptability+0.85', 'dur': .3}, {'type': 'shake', 'at': 'adaptability+0.85', 'dur': .5, 'amp': 10}],
    bed=[cue('shield_hit', at='adaptability+0.85', vol=.9), cue('demon_roar', at='adaptability+0.9', vol=.6, dur=1.6, fade=.5)], pause=.9),
  L('instructor', 'Excellent! Twenty points!', display='EXCELLENT! TWENTY POINTS!',
    shot=sh('professor_arena', (.55, .45, 1.0), (.55, .4, 1.15), tr='cut'),
    bed=[cue('points_ding', at='points+0.5', vol=.7)], pause=.6),
 ]},
 {'title': 'Our healers are the best', 'lines': [
  L('narrator', "Worried about injuries? Don't be! Every Blackfeather package includes professional medical supervision!",
    sh('ward_bandaged', (.4, .5, 1.0), (.55, .5, 1.2)),
    shots=[sh('helena_wand', (.5, .5, 1.0), (.5, .5, 1.05), tr='x', at='supervision')],
    bed=[cue('STOP_MUSIC'), cue('music_calm', vol=.45, music=True, start=30), cue('heal_spell', at='supervision+0.3', vol=.7)], pause=.5),
  L('thomas', 'I feel amazing!',
    sh('ward_restored', (.5, .5, 1.1), (.5, .45, 1.3), tr='flash'),
    shots=[sh('owlbear_curtain', (.5, .5, 1.3), (.5, .5, 1.0), tr='cut', at='amazing+0.8')],
    bed=[cue('STOP_MUSIC', at='amazing+0.5'), cue('curtain', at='amazing+0.8', vol=.6), cue('growl_low', at='amazing+0.9', vol=.9)], pause=1.4),
  L('thomas', 'Not again!', display='NOT AGAIN!',
    shot=sh('thomas_eyes', (.5, .5, 1.3), (.5, .5, 1.45), tr='cut')),
  L('healer', 'Wonderful! More practical experience!',
    sh('helena_wand', (.35, .35, 1.45), (.35, .35, 1.5), tr='cut'),
    bed=[cue('wand_cast', at='experience', vol=.6)], pause=.6),
 ]},
 {'title': 'Proven success', 'lines': [
  L('narrator', 'From the finest royal battlemages to the greatest healers in the multiverse, Blackfeather graduates deliver results!',
    sh('battlemages', (.2, .5, 1.1), (.8, .5, 1.1)),
    shots=[sh('healers_field', (.5, .5, 1.0), (.5, .5, 1.2), tr='cut', at='healers'),
           sh('dragon_flag', (.4, .5, 1.0), (.6, .45, 1.2), tr='cut', at='results')],
    bed=[cue('music_aspiration', vol=.55, music=True, start=84), cue('battle', vol=.4, dur=4.5, fade=1.5),
         cue('dragon_roar', at='results+0.1', vol=.45, dur=1.8, fade=.6)], pause=.8),
  L('osric', 'I ordered fifty boxes.',
    sh('osric', (.5, .45, 1.0), (.5, .42, 1.12), tr='cut'),
    lt=['KING OSRIC', 'Satisfied customer'], bed=[cue('STOP_MUSIC')]),
  L('osric', 'My battlemage corps has never been stronger.',
    sh('osric', (.5, .42, 1.12), (.5, .4, 1.22), tr='cont'), pause=1.0),
  L('osric', 'My insurance minister has resigned, but the results speak for themselves.',
    sh('osric', (.5, .35, 1.4), (.5, .35, 1.45), tr='cut'), pause=.6),
 ]},
 {'title': 'Even villains agree', 'lines': [
  L('malachar', 'I have conquered seven hundred dimensions.',
    sh('malachar_wide', (.5, .5, 1.0), (.5, .5, 1.15), tr='cut'),
    lt=['MALACHAR', 'Former interdimensional conqueror'], pause=.9),
  L('malachar', 'I invaded one Blackfeather world.', display='I invaded ONE Blackfeather world.',
    shot=sh('malachar_close', (.5, .45, 1.0), (.5, .42, 1.15), tr='cut'), pause=1.0),
  L('malachar', 'Never again.',
    sh('malachar_close', (.5, .25, 1.3), (.5, .22, 1.45), tr='cut'), pause=.9),
  L('narrator', 'Another satisfied educational outcome!',
    sh('malachar_wide', (.3, .5, 1.3), (.3, .5, 1.4), tr='cut'),
    bed=[cue('points_ding', vol=.4)], pause=.4),
 ]},
 {'title': 'Order today!', 'sting': True, 'lines': [
  L('narrator', 'Blackfeather Academy in a Box! Bringing centuries of magical excellence to your doorstep!',
    display='Blackfeather Academy in a Box! Bringing centuries of magical excellence to YOUR doorstep!',
    shot=sh('box_pedestal', (.5, .55, 1.0), (.5, .5, 1.15)),
    shots=[sh('box_pedestal_text', (.5, .5, 1.0), (.5, .5, 1.0), tr='cut', at='excellence')],
    bed=[cue('fanfare', vol=.7, music=True, start=100)]),
  L('narrator', "Because when disaster strikes, your students shouldn't ask what to do.",
    sh('box_pedestal_text', (.5, .5, 1.0), (.5, .5, 1.08), tr='cont'), pause=1.1,
    bed=[cue('dragon_roar', at='do+0.35', vol=.55, dur=1.4, fade=.4)]),
  L('narrator', 'They should already know!',
    sh('dragon_shield', (.5, .5, 1.0), (.5, .5, 1.2), tr='cut'),
    fx=[{'type': 'flash', 'at': 'know+0.45', 'dur': .3}],
    bed=[cue('shield_hit', at='know+0.45', vol=.9)], pause=.8),
 ]},
 {'title': 'The final disclaimer', 'lines': [
  L('thorne', "Blackfeather Academy. Where excellence isn't optional!",
    sh('thorne_box', (.5, .45, 1.0), (.5, .42, 1.15), tr='cut'),
    lt=['HEADMASTER ALDRIC THORNE', 'Blackfeather Academy'],
    bed=[cue('STOP_MUSIC', at='optional+0.3'), cue('growl_low', at='optional+0.5', vol=.8)], pause=1.1),
  L('thorne', 'Neither is the owlbear.',
    sh('thorne_down', (.5, .45, 1.15), (.5, .45, 1.3), tr='cut'),
    shots=[sh('black', tr='cut', at='owlbear+0.7')],
    fx=[{'type': 'shake', 'at': 'owlbear+0.35', 'dur': .4, 'amp': 16}],
    bed=[cue('owlbear_screech', at='owlbear+0.3', vol=1.0, dur=1.2, fade=.35)], pause=1.3),
  L('narrator_fast', 'Please open responsibly. Healer included. Limbs not guaranteed. Do not shake the box. Do not feed the owlbear raisins.',
    sh('final_title', (.5, .5, 1.0), (.5, .5, 1.04), tr='cut')),
  L('narrator_fast', 'Blackfeather Academy assumes no responsibility for emotional distress, broken furniture, or sudden improvements in survival instincts.',
    sh('final_title', (.5, .5, 1.04), (.5, .5, 1.08), tr='cont'),
    shots=[sh('black', tr='cut', at='instincts+1.6')], pause=3.2),
 ]},
 {'title': 'Post-credits', 'lines': [
  L('buyer', 'Surely the stories are exaggerated.',
    sh('stinger_box', (.5, .5, 1.0), (.5, .45, 1.15), tr='cut'),
    shots=[sh('stinger_open', (.5, .5, 1.0), (.5, .55, 1.15), tr='cut', at='exaggerated+0.5')],
    bed=[cue('chest_open', at='exaggerated+0.4', vol=.8, dur=1.9, fade=.5)], pause=2.2),
  L('buyer', 'See? Completely harmless.',
    sh('stinger_open', (.5, .55, 1.15), (.5, .58, 1.25), tr='cont'),
    shots=[sh('cub', (.5, .5, 1.0), (.5, .5, 1.2), tr='cut', at='harmless+0.6')],
    bed=[cue('cub_squeak', at='harmless+1.0', vol=.7)], pause=1.5),
  L('buyer', "Oh! You're actually rather cute!",
    sh('stinger_reach', (.5, .45, 1.0), (.5, .5, 1.15), tr='cut')),
  L('healer', "No! That's the mother's cub!", display="NO! THAT'S THE MOTHER'S CUB!",
    shot=sh('cub', (.5, .45, 1.5), (.5, .45, 1.5), tr='cut'),
    shots=[sh('stinger_shadow', (.5, .7, 1.0), (.5, .3, 1.15), tr='cut', at='cub+1.4'),
           sh('black', tr='cut', at='cub+4.0')],
    fx=[{'type': 'shake', 'at': 'cub+0.5', 'dur': .35, 'amp': 6, 'repeat': 4, 'every': 1.0}],
    bed=[cue('giant_steps', at='cub+0.4', vol=.9), cue('owlbear_roar_big', at='cub+4.3', vol=1.0)], pause=5.2),
  L('healer', 'Welcome to Blackfeather!',
    sh('black', tr='cont'), pause=1.5),
 ]},
]

plan = {
 'title': 'Blackfeather Academy in a Box', 'width': 1280, 'fps': 24,
 'audio': 'narration_fx.wav', 'timestamps': 'labels_fx.txt', 'words': 'words.json',
 'cast': {'narrator': 'am_puck', 'narrator_fast': 'am_puck', 'professor': 'bf_emma', 'instructor': 'am_eric', 'buyer': 'bm_lewis', 'thomas': 'am_michael',
          'healer': 'af_bella', 'headmaster': 'bm_fable', 'osric': 'am_fenrir', 'malachar': 'am_fenrir',
          'thorne': 'bm_george'},
 'voice_fx': {'thomas': {'pitch': 2}, 'malachar': {'pitch': -3, 'echo': True}, 'thorne': {'pitch': -1.5}},
 'images': {},
 'music': {'file': 'bed.wav', 'volume': 8.333},
 'scenes': scenes,
}
names = set()
for sc in scenes:
    for ln in sc['lines']:
        for s in [ln.get('shot')] + ln.get('shots', []):
            if s: names.add(s['image'])
plan['images'] = {n: f'art/{n}.png' for n in sorted(names)}
json.dump(plan, open('plan.json', 'w'), indent=1, ensure_ascii=False)
print(len(names), 'images;', sum(len(s['lines']) for s in scenes), 'lines')
print(sorted(names))

# HiDream version: same plan, art from art_hd/, a few crops where HiDream doubled a character
import os
if os.environ.get('ART') == 'art_hd':
    BOX = {'professor_class': [0.42, 0.0, 1.0, 1.0], 'montage_c': [0.35, 0.0, 1.0, 1.0],
           'owlbear_curtain': [0.0, 0.08, 0.55, 0.92], 'malachar_close': [0.2, 0.0, 0.7, 0.5]}
    for sc in plan['scenes']:
        for ln in sc['lines']:
            for s in [ln.get('shot')] + ln.get('shots', []):
                if s and s['image'] in BOX:
                    s['box'] = BOX[s['image']]
                    if s['image'] == 'malachar_close':
                        s['from'][1] = s['to'][1] = 0.35
                    if s['image'] == 'professor_class':
                        s['from'][1] = s['to'][1] = 0.12
    for sc in plan['scenes']:
        for ln in sc['lines']:
            for s in [ln.get('shot')] + ln.get('shots', []):
                if s and s['image'] == 'box_hero' and s['from'][2] >= 1.45:
                    s['from'] = [.85, .65, 1.5]; s['to'] = [.8, .6, 1.5]
    plan['images'] = {n: f'art_hd/{n}.png' for n in plan['images']}
    json.dump(plan, open('plan_hd.json', 'w'), indent=1, ensure_ascii=False)
    print('wrote plan_hd.json')

# Version built from the user's own painted art (11 scenes + 21 inserts), see compose_user.py
if os.environ.get('ART') == 'art_user':
    for sc in plan['scenes']:
        for ln in sc['lines']:
            if ln.get('lower_third', [''])[0] == 'MALACHAR':
                del ln['lower_third']          # already painted into scene 08
            for s in [ln.get('shot')] + ln.get('shots', []):
                if s and s['image'] == 'box_hero' and s['from'][2] >= 1.45:
                    s['from'] = [.3, .75, 1.5]; s['to'] = [.38, .72, 1.5]
    # stinger: no "peering into an empty box" image, so the lid-open beat stays on the buyer
    st = plan['scenes'][-1]['lines']
    st[0]['shots'] = [sh('stinger_open', (.35, .4, 1.0), (.35, .38, 1.12), tr='cut', at='exaggerated+0.5')]
    mal = plan['scenes'][7]['lines']
    mal[0]['shot'].update({'from': [.5, .5, 1.0], 'to': [.5, .52, 1.06]})
    mal[1]['shot'].update({'from': [.5, .4, 1.0], 'to': [.5, .38, 1.1]})
    mal[2]['shot'].update({'from': [.5, .3, 1.25], 'to': [.5, .28, 1.35]})
    mal[3]['shot'].update({'from': [.5, .33, 1.4], 'to': [.5, .32, 1.45]})
    st[1]['shot'].update({'from': [.35, .38, 1.12], 'to': [.35, .36, 1.2]})
    mal[2]['shot'].update({'from': [.5, .28, 1.3], 'to': [.5, .26, 1.4]})
    s1 = plan['scenes'][0]['lines']
    s1[1]['shot'].update({'from': [.5, .4, 1.0], 'to': [.5, .38, 1.08]})          # professor_class
    s1[2]['shot'].update({'from': [.5, .45, 1.0], 'to': [.5, .42, 1.12]})         # thomas_bored push
    s1[3]['shot'].update({'from': [.5, .42, 1.12], 'to': [.5, .42, 1.12]})        # freeze frame
    plan['scenes'][2]['lines'][1]['shot'].update({'from': [.5, .5, 1.0], 'to': [.5, .5, 1.08]})   # box_label
    plan['scenes'][5]['lines'][3]['shot'].update({'from': [.35, .35, 1.3], 'to': [.35, .35, 1.35]})  # helena_wand
    st[1]['shots'][0].update({'from': [.5, .55, 1.0], 'to': [.5, .55, 1.08]})
    st[3]['shot'] = sh('stinger_shadow', (.35, .6, 1.5), (.35, .6, 1.5), tr='cut')
    plan['images'] = {n: f'art_user/{n}.png' for n in plan['images']}
    json.dump(plan, open('plan_user.json', 'w'), indent=1, ensure_ascii=False)
    print('wrote plan_user.json')
