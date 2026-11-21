"""Specs for the two HiDream jobs: character references, then every shot with its references."""
import json, sys
sys.path.insert(0, '.')
from art_prompts import SHOTS

STYLE = ("Painted fantasy storybook illustration, rich detailed digital painting with visible brushwork, warm cinematic "
         "lighting, deep crimson and gold accents, expressive comedic character acting. No text, no letters, no logos, "
         "no watermark, no border.")

C = {
 'thomas': "Thomas, a skinny fifteen-year-old wizard student with messy brown hair, freckles across his nose and a round face, wearing long dark navy-blue academy robes with a small crimson feather emblem on the chest and a brown leather belt",
 'helena': "Helena, a cheerful healer woman in her thirties with auburn hair in a neat bun, rosy cheeks and a huge friendly smile, wearing pristine white robes with crimson trim and wide sleeves",
 'professor': "the Professor, a stern elderly wizard with a very long grey beard, round half-moon spectacles and black robes with crimson lining",
 'headmaster': "a plump middle-aged headmaster with a shiny bald head, a clean-shaven chin and cheeks and only a big bushy brown handlebar mustache, purple robes and a heavy gold chain of office",
 'thorne': "Headmaster Aldric Thorne, a tall dignified man in his fifties with slicked-back silver hair and a sharp silver goatee, black-and-crimson robes with a black raven-feather collar",
 'owlbear': ("an owlbear: a huge four-legged beast built exactly like a massive grizzly bear, with a broad furry back, thick brown fur "
             "on its legs and belly, heavy bear paws with long curved black claws, a ruff of tawny feathers around its neck, and the head "
             "of a great horned owl with ear tufts, round glowing amber eyes and a sharp hooked beak"),
 'box': "an elegant dark wooden treasure chest reinforced with polished brass corners and bands, an engraved owlbear crest on the front, glowing crimson runes around the crest",
 'cub': "a small fluffy owlbear cub: a chubby bear-cub body with soft brown fur and little paws, the round head of a baby owl with downy feathers, huge amber eyes and a tiny beak",
 'malachar': "Malachar the Eternal, a gaunt pale sorcerer with glowing violet eyes and long straight black hair, wearing tattered dark spiked armor, his wrists bound in glowing red magical shackles",
}

REF_SHOTS = {
 'thomas': f"Full-body character reference of {C['thomas']}, standing relaxed facing the viewer in three-quarter view, whole figure from head to boots visible, plain soft light-grey studio background.",
 'helena': f"Full-body character reference of {C['helena']}, standing facing the viewer in three-quarter view, whole figure visible, plain soft light-grey studio background.",
 'professor': f"Full-body character reference of {C['professor']}, standing facing the viewer in three-quarter view holding a wand, whole figure visible, plain soft light-grey studio background.",
 'headmaster': f"Full-body character reference of {C['headmaster']}, standing facing the viewer in three-quarter view, whole figure visible, plain soft light-grey studio background.",
 'thorne': f"Full-body character reference of {C['thorne']}, standing proudly facing the viewer in three-quarter view, whole figure visible, plain soft light-grey studio background.",
 'owlbear': f"Full-body creature reference of {C['owlbear']}, standing on all fours in side three-quarter view, the whole animal visible from beak to hind paws, plain soft light-grey studio background.",
 'box': f"Product reference of {C['box']}, closed, three-quarter view, the whole chest visible, plain soft light-grey studio background.",
 'cub': f"Full-body creature reference of {C['cub']}, sitting and facing the viewer, whole body visible, plain soft light-grey studio background.",
 'malachar': f"Full-body character reference of {C['malachar']}, standing facing the viewer in three-quarter view, whole figure visible, plain soft light-grey studio background.",
}

# which references each shot uses
CAST = {
 'classroom_wide': ['thomas'], 'professor_class': ['professor'], 'thomas_bored': ['thomas'],
 'arena_wide': ['thomas', 'owlbear'], 'owlbear_claws': ['owlbear'], 'professor_arena': ['professor'],
 'thomas_eyes': ['thomas'], 'owlbear_charge': ['owlbear'], 'thomas_stretcher': ['thomas'],
 'box_hero': ['box'], 'box_label_base': ['box'], 'helena_box': ['helena', 'box'], 'owlbear_peek': ['box', 'owlbear'],
 'headmaster_lean': ['headmaster', 'box'], 'box_explode': ['box'], 'owlbear_tackle': ['owlbear', 'headmaster'],
 'helena_smile': ['helena'], 'montage_a': [], 'montage_b': ['owlbear'], 'montage_c': ['helena'],
 'montage_d': ['thomas', 'owlbear'], 'montage_e': ['thomas'], 'ward_bandaged': ['thomas'], 'helena_wand': ['helena'],
 'ward_restored': ['thomas'], 'owlbear_curtain': ['owlbear'], 'battlemages': [], 'healers_field': [], 'dragon_flag': [],
 'osric': [], 'malachar_wide': ['malachar'], 'malachar_close': ['malachar'], 'box_pedestal': ['box', 'owlbear'],
 'dragon_shield': ['thomas'], 'thorne_box': ['thorne', 'box'], 'thorne_down': ['thorne'], 'title_bg': [],
 'stinger_box': ['headmaster', 'box'], 'stinger_open': ['headmaster', 'box'], 'cub': ['cub', 'box'],
 'stinger_reach': ['headmaster', 'cub'], 'stinger_shadow': ['headmaster'],
}

# shot prompts: the FLUX ones, with the owlbear and cub described the new (bear-heavy) way
OLD_OWL = "a huge owlbear: a massive bear body covered in tawny brown owl feathers, the head of a great horned owl with round glowing amber eyes and a sharp hooked beak, enormous curved claws"
OLD_CUB = "a small fluffy owlbear cub with soft downy feathers, huge round amber eyes and a tiny beak, adorable"


def shot_prompt(name):
    p = SHOTS[name].replace(OLD_OWL, C['owlbear']).replace(OLD_CUB, C['cub']).replace('owlbear: a massive bear body covered in tawny brown owl feathers, the head of a great horned owl with round glowing amber eyes and a sharp hooked beak, enormous curved claws', 'owlbear (grizzly bear body, owl head)')
    p = p.replace('a plump middle-aged headmaster with a bald head, a bushy brown mustache, purple robes and a gold chain of office', 'a plump middle-aged headmaster with a shiny bald head, a big bushy brown beard and mustache, purple-and-gold robes and a heavy gold chain of office')
    who = CAST[name]
    lead = ('Wide cinematic 16:9 film still. ' + (f"The {' and the '.join(who)} must match the reference images exactly. " if who else ''))
    return lead + p + ' ' + STYLE


if __name__ == '__main__':
    stage = sys.argv[1]
    if stage == 'refs':
        spec = [{'name': k, 'prompt': v + ' ' + STYLE, 'w': 2048, 'h': 2048} for k, v in REF_SHOTS.items()]
    else:
        spec = []
        for n in SHOTS:
            refs = [f'refs/{c}.png' for c in CAST[n]]
            if len(refs) == 1: refs = refs * 2   # one ref = "edit this image" mode; two = place the subject in a new scene
            spec.append({'name': n, 'prompt': shot_prompt(n), 'refs': refs, 'w': 2560, 'h': 1440})
    json.dump(spec, open(f'hd_spec_{stage}.json', 'w'), indent=1)
    print(stage, len(spec), 'entries')
