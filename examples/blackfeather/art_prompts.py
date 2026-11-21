"""Shot prompts for Blackfeather. Characters are described the same way every time so they stay on-model."""
import json

STYLE = ("Painted fantasy storybook illustration, rich detailed digital painting, warm cinematic lighting, "
         "deep crimson and gold accents, comedic and expressive, wide 16:9 film still, no text, no letters, no watermark, no border")

C = {
 'thomas': "Thomas, a skinny fifteen-year-old wizard student with messy brown hair, freckles and a round face, wearing dark blue academy robes with a small crimson feather emblem",
 'professor': "the Professor, a stern elderly wizard with a long grey beard, half-moon spectacles and black-and-crimson robes",
 'helena': "Helena, a cheerful healer woman in her thirties with a neat auburn hair bun, rosy cheeks and a huge friendly smile, wearing pristine white robes with crimson trim",
 'owlbear': "a huge owlbear: a massive bear body covered in tawny brown owl feathers, the head of a great horned owl with round glowing amber eyes and a sharp hooked beak, enormous curved claws",
 'box': "an elegant dark wooden chest reinforced with polished brass, an engraved owlbear crest on the front, glowing crimson runes around the crest",
 'headmaster': "a plump middle-aged headmaster with a bald head, a bushy brown mustache, purple robes and a gold chain of office",
 'thorne': "Headmaster Aldric Thorne, a tall dignified man in his fifties with a sharp silver goatee and slicked-back silver hair, black-and-crimson robes with a raven-feather collar",
 'osric': "King Osric, a portly smug middle-aged king with a bushy ginger beard, a golden crown and ermine-trimmed red robes",
 'malachar': "Malachar the Eternal, a gaunt pale sorcerer with glowing violet eyes and long black hair, wearing tattered dark armor, his wrists in glowing magical shackles",
 'cub': "a small fluffy owlbear cub with soft downy feathers, huge round amber eyes and a tiny beak, adorable",
}

SHOTS = {
 'classroom_wide': f"Wide shot of a beautiful magical academy classroom, sunlight streaming through tall stained-glass windows, rows of students in dark blue robes calmly taking notes with quills, peaceful and ordinary. In the middle row, {C['thomas']}, looking bored, chin on hand.",
 'professor_class': f"Medium shot of {C['professor']} standing at a chalkboard in a sunlit academy classroom, pointing his wand at a student off-screen with a disapproving frown.",
 'thomas_bored': f"Close-up of {C['thomas']} slouching at a wooden desk, half-lidded bored eyes, shrugging, sunlit classroom behind him.",
 'arena_wide': f"Wide low-angle shot of a vast stone training arena with crimson Blackfeather banners. {C['thomas']} stands small and nervous on the left facing {C['owlbear']} on the right, which rears up roaring.",
 'owlbear_claws': f"Extreme low-angle close-up of the giant feathered claws of {C['owlbear']}, slamming into the sand of a stone arena, dust flying, dramatic.",
 'professor_arena': f"{C['professor']} standing on a stone balcony above a training arena, shouting down with one hand cupped to his mouth, crimson banners behind him.",
 'thomas_eyes': f"Extreme close-up of the terrified wide eyes and pale freckled face of {C['thomas']}, sweat drops, comedic horror, dark background.",
 'owlbear_charge': f"Dynamic action shot of {C['owlbear']} roaring with its beak wide open, charging straight toward the viewer in a stone arena, sand and feathers flying.",
 'thomas_stretcher': f"{C['thomas']} lying dazed flat on a padded white medical stretcher at the edge of a training arena, robes rumpled, stars around his head, feathers drifting down, comedic.",
 'box_hero': f"Dramatic product shot of {C['box']}, resting on a red velvet platform, golden god-rays pouring down through clouds behind it, sparkles, heroic and luxurious.",
 'box_label_base': f"Close-up of the side of {C['box']}, a large blank cream parchment label nailed to the wood with brass tacks, the label is completely empty, warm light.",
 'helena_box': f"{C['helena']} standing on the left beside {C['box']} on the right, giving a cheerful thumbs-up to the viewer, bright clean academy hall.",
 'owlbear_peek': f"Close-up of {C['box']} with its lid open just a crack, two glowing amber owl eyes peering out from the darkness inside, ominous and funny.",
 'headmaster_lean': f"{C['headmaster']} leaning forward curiously toward {C['box']}, raising an eyebrow, in an elegant academy office.",
 'box_explode': f"The lid of {C['box']} blasting upward in a huge explosion of light, splinters and feathers, shockwave of dust filling an elegant academy office.",
 'owlbear_tackle': f"{C['owlbear']} leaping through a cloud of smoke and splinters to tackle {C['headmaster']}, both tumbling out of frame to the right, papers flying, slapstick.",
 'helena_smile': f"{C['helena']} standing perfectly calm and still smiling sweetly in a smoky ruined academy office, her face lightly smudged with soot, feathers drifting around her.",
 'montage_a': f"A young battlemage in dark blue robes sprinting through a burning obstacle course, blocking a huge fireball with a shimmering blue magic shield, flames everywhere, action shot.",
 'montage_b': f"Three students in dark blue academy robes standing shoulder to shoulder, casting one combined glowing golden shield dome as {C['owlbear']} charges into it, sparks flying.",
 'montage_c': f"{C['helena']} healing a wincing student's broken arm with a bright flash of golden magic light, in a training arena, sparkles.",
 'montage_d': f"{C['thomas']} screaming and diving aside as giant owlbear claws swipe past him, a perfect glowing blue defensive rune shining from his outstretched hand, dynamic motion.",
 'montage_e': f"{C['thomas']}, older and confident, standing firm on a real smoky battlefield, blocking a charging red horned demon with a brilliant blue magic shield.",
 'ward_bandaged': f"A peaceful bright infirmary ward with white curtains. {C['thomas']} sits on a bed wrapped head to toe in bandages like a mummy, surrounded by three smiling healers in white-and-crimson robes.",
 'helena_wand': f"{C['helena']} waving her wand over a patient's bed in a bright infirmary ward, golden sparkles spiraling, cheerful.",
 'ward_restored': f"{C['thomas']} sitting up on an infirmary bed fully healed, bandages falling away, beaming with joy, both arms raised, golden sparkles around him.",
 'owlbear_curtain': f"The huge silhouette of {C['owlbear']} looming behind a white infirmary curtain, backlit, its glowing amber eyes visible through the fabric, menacing.",
 'battlemages': f"Sweeping wide shot of a disciplined formation of elite battlemages in crimson-and-black armor on a grand plaza, staffs raised, glowing spells ready, a huge crimson Blackfeather banner.",
 'healers_field': f"Healers in white-and-crimson robes kneeling to stabilize wounded adventurers on a misty battlefield, glowing golden healing magic.",
 'dragon_flag': f"A huge green dragon flinching back and retreating in fear from a crimson Blackfeather flag planted on a rocky cliff, epic sunset sky.",
 'osric': f"{C['osric']} sitting in a luxurious golden throne in a palace, facing the viewer directly like a satisfied customer in a testimonial, smug proud smile, hands folded.",
 'malachar_wide': f"{C['malachar']} sitting stiffly on a small wooden chair at a plain table in a grey magical prison interview room, glowing runes on the walls, awkward.",
 'malachar_close': f"Close-up of {C['malachar']} staring straight at the viewer, dead serious, haunted expression, dim cold light.",
 'box_pedestal': f"{C['box']} on a magnificent white marble pedestal in a grand hall, behind it happy students in dark blue robes, smiling healers in white robes, and a calm well-behaved {C['owlbear'].replace('a huge owlbear', 'owlbear')} wearing a big blue prize ribbon, triumphant golden light.",
 'dragon_shield': f"{C['thomas']} calmly raising a glowing blue magic shield in front of a gigantic red dragon breathing fire at him, the fire splashing harmlessly off the shield, epic.",
 'thorne_box': f"{C['thorne']} standing proudly beside {C['box']} in a grand academy hall, smiling at the viewer.",
 'thorne_down': f"Close-up of {C['thorne']} glancing down to the side with a slightly nervous smile, the corner of the chest beside him faintly glowing red.",
 'title_bg': "A large ornate golden owlbear crest emblem centered on dark crimson velvet, soft rim light, elegant, lots of empty space around it.",
 'stinger_box': f"{C['headmaster']} standing confidently in front of {C['box']} just delivered in his cozy office, hands on hips.",
 'stinger_open': f"{C['headmaster']} peering down into the open {C['box']}, the inside dark and empty, puzzled.",
 'cub': f"{C['cub']} climbing out of the open {C['box']}, tilting its head adorably at the viewer.",
 'stinger_reach': f"{C['headmaster']} smiling and reaching down to pet {C['cub']} on the office floor.",
 'stinger_shadow': f"{C['headmaster']} frozen mid-reach, slowly looking up in terror as an enormous dark shadow of a giant owlbear falls over him and the whole office, ominous.",
}

if __name__ == '__main__':
    json.dump({'style': STYLE, 'shots': SHOTS}, open('art_prompts.json', 'w'), indent=1)
    print(len(SHOTS), 'shots')
