"""Action/emotion shots rerun WITHOUT references (references made HiDream copy the reference pose and calm face).
Characters are described exactly as in the reference images so they still match."""
import json, sys
sys.path.insert(0, '.')
from hd_specs import C, STYLE

C = dict(C)
C['headmaster'] = "a plump middle-aged headmaster with a shiny bald head, a big bushy brown beard and mustache, purple-and-gold robes and a heavy gold chain of office"
C['thomas'] = "Thomas, a skinny fifteen-year-old wizard student with big messy curly brown hair and a round face, wearing long dark navy-blue academy robes with a small crimson feather emblem and a brown leather belt"

A = {
 'thomas_bored': f"Medium close-up, eye level. {C['thomas']} slumps over a wooden school desk with his cheek squashed on his fist, heavy half-closed eyelids, mouth in a flat bored line, utterly uninterested. Sunlit academy classroom behind him.",
 'arena_wide': f"Wide low-angle shot of a vast stone training arena with crimson banners. On the left, small and nervous, {C['thomas']} takes a step back with his hands raised. On the right {C['owlbear']} rears up on its hind legs, front claws spread, beak wide open in a furious roar.",
 'owlbear_claws': f"Extreme low-angle close-up at ground level: two enormous furry bear paws with long curved black claws slam down into the sand of a stone arena, sand and dust exploding upward. Only the paws and lower legs of {C['owlbear']} are in frame.",
 'thomas_eyes': f"Extreme close-up of the face of {C['thomas']}: eyes stretched wide open in pure terror, tiny pupils, eyebrows shot up, mouth open in a silent scream, sweat drops flying, comic horror. Dark background.",
 'owlbear_charge': f"Dynamic action shot, low angle, strong perspective: {C['owlbear']} charges straight at the viewer at full speed, beak wide open in a roar, front claws reaching forward, sand and loose feathers flying behind it in a stone arena.",
 'thomas_stretcher': f"{C['thomas']} lies dazed and crumpled on a padded white medical stretcher at the edge of a training arena, eyes spiralled and unfocused, robes rumpled, a few cartoon stars circling his head, feathers drifting down. Slapstick.",
 'box_explode': f"The lid of {C['box']} blasts open in a huge explosion of golden light, wood splinters, smoke and feathers, a bright shockwave filling an elegant academy office, books and papers flying.",
 'owlbear_tackle': f"Slapstick action: {C['owlbear']} leaps out of a cloud of smoke and splinters and body-slams {C['headmaster']}, who is knocked off his feet with arms flailing and a shocked face, papers flying everywhere in an academy office.",
 'montage_b': f"Three students in dark navy-blue academy robes stand shoulder to shoulder, arms thrust forward, casting one combined glowing golden shield dome. {C['owlbear']} crashes into the dome mid-charge, sparks bursting where it hits.",
 'montage_d': f"{C['thomas']} screams and dives sideways as huge furry claws swipe just past his head, while a perfect glowing blue defensive rune blazes from his outstretched hand. Dynamic motion blur.",
 'montage_e': f"{C['thomas']}, now confident and battle-ready, stands firm on a smoky battlefield, holding up a brilliant blue magic shield that stops a charging red horned demon in its tracks.",
 'ward_restored': f"{C['thomas']} sits up on an infirmary bed fully healed, bandages flying off him, beaming with joy, both arms thrown up in the air, golden sparkles bursting around him.",
 'owlbear_curtain': f"Inside a bright infirmary, the huge dark silhouette of {C['owlbear']} looms behind a white hospital curtain, backlit, its glowing amber eyes visible through the fabric, menacing, claws curling around the curtain's edge.",
 'dragon_shield': f"{C['thomas']} calmly raises a glowing blue magic shield in front of a gigantic red dragon breathing a torrent of fire at him; the fire splashes harmlessly off the shield. Epic.",
 'stinger_shadow': f"{C['headmaster']} frozen mid-reach in his cozy office, slowly looking up in terror, sweating, as an enormous dark shadow with owl ear tufts falls over him and the whole room. Ominous.",
}

if __name__ == '__main__':
    only = sys.argv[1].split(',') if len(sys.argv) > 1 else list(A)
    spec = [{'name': f'{n}_act', 'prompt': 'Wide cinematic 16:9 film still. ' + A[n] + ' ' + STYLE, 'w': 2560, 'h': 1440} for n in only]
    json.dump(spec, open('hd_spec_action.json', 'w'), indent=1)
    print(len(spec), 'action shots')
