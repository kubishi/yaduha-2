"""
Kethara Language Vocabulary

An agglutinative constructed language featuring:
- Noun classes (human/animal/plant/object/abstract) instead of gender
- Agglutinative morphology (suffixes stack on roots)
- SOV word order
- Vowel harmony in suffixes
- Directional/spatial case system
- No articles
"""

from yaduha.language import VocabEntry

# HUMAN nouns (people, professions)
HUMAN_NOUNS = [
    VocabEntry("person", "zhen"),
    VocabEntry("child", "pelki"),
    VocabEntry("woman", "thera"),
    VocabEntry("man", "kodan"),
    VocabEntry("friend", "miru"),
    VocabEntry("teacher", "saveth"),
    VocabEntry("student", "nolki"),
    VocabEntry("warrior", "dakhen"),
]

# ANIMAL nouns (creatures, living beings)
ANIMAL_NOUNS = [
    VocabEntry("dog", "kurma"),
    VocabEntry("cat", "shiva"),
    VocabEntry("bird", "telun"),
    VocabEntry("fish", "nakos"),
    VocabEntry("horse", "vareth"),
    VocabEntry("bear", "gormak"),
    VocabEntry("wolf", "ulven"),
    VocabEntry("deer", "serka"),
    VocabEntry("snake", "zhilak"),
    VocabEntry("frog", "popeth"),
]

# PLANT nouns (vegetation)
PLANT_NOUNS = [
    VocabEntry("tree", "korvan"),
    VocabEntry("flower", "lumi"),
    VocabEntry("grass", "veltha"),
    VocabEntry("fruit", "merka"),
    VocabEntry("seed", "pinja"),
]

# OBJECT nouns (inanimate physical things)
OBJECT_NOUNS = [
    VocabEntry("house", "talo"),
    VocabEntry("book", "kirja"),
    VocabEntry("table", "poyda"),
    VocabEntry("chair", "istuva"),
    VocabEntry("door", "verko"),
    VocabEntry("window", "ikuna"),
    VocabEntry("food", "mato"),
    VocabEntry("water", "vesik"),
    VocabEntry("stone", "kiva"),
    VocabEntry("wood", "puva"),
    VocabEntry("fire", "tulka"),
    VocabEntry("cup", "malka"),
    VocabEntry("bread", "leipu"),
]

# ABSTRACT nouns (concepts, places, natural phenomena)
ABSTRACT_NOUNS = [
    VocabEntry("sky", "taiva"),
    VocabEntry("earth", "manu"),
    VocabEntry("sun", "aurik"),
    VocabEntry("moon", "kuma"),
    VocabEntry("star", "tahti"),
    VocabEntry("mountain", "vuora"),
    VocabEntry("river", "jova"),
    VocabEntry("wind", "tuva"),
    VocabEntry("rain", "sade"),
    VocabEntry("time", "aika"),
    VocabEntry("love", "rakka"),
    VocabEntry("truth", "tosi"),
]

# All nouns combined
NOUNS = HUMAN_NOUNS + ANIMAL_NOUNS + PLANT_NOUNS + OBJECT_NOUNS + ABSTRACT_NOUNS

# Transitive Verbs (take an object)
TRANSITIVE_VERBS = [
    VocabEntry("see", "nakh"),
    VocabEntry("hear", "kulv"),
    VocabEntry("eat", "syo"),
    VocabEntry("drink", "juo"),
    VocabEntry("love", "rakast"),
    VocabEntry("know", "tied"),
    VocabEntry("want", "halut"),
    VocabEntry("make", "teh"),
    VocabEntry("break", "rikk"),
    VocabEntry("find", "loyt"),
    VocabEntry("give", "anna"),
    VocabEntry("take", "otta"),
    VocabEntry("hold", "pida"),
    VocabEntry("throw", "heit"),
    VocabEntry("catch", "nappa"),
    VocabEntry("read", "luk"),
    VocabEntry("write", "kirjoit"),
    VocabEntry("help", "auta"),
    VocabEntry("teach", "opet"),
    VocabEntry("learn", "oppi"),
]

# Intransitive Verbs (no object)
INTRANSITIVE_VERBS = [
    VocabEntry("sleep", "nuku"),
    VocabEntry("wake", "herata"),
    VocabEntry("die", "kuol"),
    VocabEntry("live", "ela"),
    VocabEntry("run", "juoks"),
    VocabEntry("walk", "kavele"),
    VocabEntry("jump", "hyppa"),
    VocabEntry("sit", "istu"),
    VocabEntry("stand", "seiso"),
    VocabEntry("fall", "putoa"),
    VocabEntry("rise", "nous"),
    VocabEntry("swim", "ui"),
    VocabEntry("fly", "lenna"),
    VocabEntry("sing", "laula"),
    VocabEntry("laugh", "naura"),
    VocabEntry("cry", "itke"),
    VocabEntry("dance", "tans"),
    VocabEntry("speak", "puhu"),
    VocabEntry("grow", "kasva"),
    VocabEntry("shine", "loista"),
]
