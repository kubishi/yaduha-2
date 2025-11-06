"""
Velar Language Vocabulary

A constructed language featuring:
- Gendered pronouns (masculine/feminine/neuter)
- Evidentiality markers (direct witness, hearsay, inference)
- Animacy distinctions (animate vs inanimate)
- VSO word order (Verb-Subject-Object)
"""

from yaduha.language import VocabEntry

# Animate Nouns (beings capable of independent movement)
ANIMATE_NOUNS = [
    VocabEntry("person", "renok"),
    VocabEntry("child", "kilos"),
    VocabEntry("woman", "femara"),
    VocabEntry("man", "maskel"),
    VocabEntry("dog", "kanir"),
    VocabEntry("cat", "miavor"),
    VocabEntry("bird", "avizel"),
    VocabEntry("fish", "peskol"),
    VocabEntry("horse", "kaval"),
    VocabEntry("bear", "ursak"),
    VocabEntry("wolf", "lupor"),
    VocabEntry("snake", "serpen"),
    VocabEntry("frog", "ranok"),
    VocabEntry("spider", "arachel"),
    VocabEntry("bee", "melif"),
]

# Inanimate Nouns (objects, places, concepts)
INANIMATE_NOUNS = [
    VocabEntry("water", "akvor"),
    VocabEntry("fire", "pyros"),
    VocabEntry("stone", "petra"),
    VocabEntry("tree", "arbos"),
    VocabEntry("mountain", "montak"),
    VocabEntry("river", "flumen"),
    VocabEntry("house", "domal"),
    VocabEntry("book", "librek"),
    VocabEntry("food", "sitor"),
    VocabEntry("bread", "panek"),
    VocabEntry("table", "mensal"),
    VocabEntry("chair", "sedek"),
    VocabEntry("door", "portal"),
    VocabEntry("window", "fenest"),
    VocabEntry("sky", "kelum"),
    VocabEntry("earth", "gerok"),
    VocabEntry("sun", "solum"),
    VocabEntry("moon", "lunak"),
    VocabEntry("star", "astrel"),
    VocabEntry("cloud", "nubel"),
    VocabEntry("wind", "vental"),
    VocabEntry("rain", "pluvik"),
]

# All nouns combined
NOUNS = ANIMATE_NOUNS + INANIMATE_NOUNS

# Transitive Verbs (require an object)
TRANSITIVE_VERBS = [
    VocabEntry("see", "viden"),
    VocabEntry("hear", "audir"),
    VocabEntry("eat", "manjan"),
    VocabEntry("drink", "biber"),
    VocabEntry("love", "amar"),
    VocabEntry("hate", "odiar"),
    VocabEntry("know", "saber"),
    VocabEntry("want", "volar"),
    VocabEntry("make", "fazer"),
    VocabEntry("break", "romper"),
    VocabEntry("find", "trovar"),
    VocabEntry("lose", "perder"),
    VocabEntry("give", "donar"),
    VocabEntry("take", "tomar"),
    VocabEntry("hold", "tener"),
    VocabEntry("throw", "jaktar"),
    VocabEntry("catch", "kaptar"),
    VocabEntry("kill", "mortar"),
    VocabEntry("read", "lektar"),
    VocabEntry("write", "skrivar"),
]

# Intransitive Verbs (no object)
INTRANSITIVE_VERBS = [
    VocabEntry("sleep", "dormir"),
    VocabEntry("wake", "desper"),
    VocabEntry("die", "morir"),
    VocabEntry("live", "vivir"),
    VocabEntry("run", "kurir"),
    VocabEntry("walk", "marchar"),
    VocabEntry("jump", "saltar"),
    VocabEntry("sit", "sedar"),
    VocabEntry("stand", "estar"),
    VocabEntry("fall", "kader"),
    VocabEntry("rise", "levar"),
    VocabEntry("swim", "natar"),
    VocabEntry("fly", "volar"),
    VocabEntry("sing", "kantar"),
    VocabEntry("laugh", "ridar"),
    VocabEntry("cry", "plorar"),
    VocabEntry("dance", "dansar"),
    VocabEntry("speak", "parlar"),
    VocabEntry("grow", "kresker"),
    VocabEntry("shine", "lumar"),
]
