from collections import OrderedDict
from enum import Enum

import customlogger as logger
from db import db

SKILL_BASE = {
    0: {"id": 0, "name": "", "keywords": [], "color": (255, 255, 255)},
    1: {"id": 1, "name": "SCORE Bonus", "keywords": ["su"], "color": (255, 101, 60)},
    2: {"id": 2, "name": "SCORE Bonus", "keywords": ["su"], "color": (255, 101, 60)},
    4: {"id": 4, "name": "COMBO Bonus", "keywords": ["cu"], "color": (248, 187, 0)},
    5: {"id": 5, "name": "PERFECT Support", "color": (33, 215, 174)},
    6: {"id": 6, "name": "PERFECT Support", "color": (33, 215, 174)},
    7: {"id": 7, "name": "PERFECT Support", "color": (33, 215, 174)},
    9: {"id": 9, "name": "COMBO Support", "color": (194, 194, 43)},
    12: {"id": 12, "name": "Damage Guard", "keywords": ["dg"], "color": (38, 201, 255)},
    14: {"id": 14, "name": "Overload", "keywords": ["ol"], "color": (200, 58, 140)},
    15: {"id": 15, "name": "Concentration", "keywords": ["cc"], "color": (148, 77, 255)},
    16: {"id": 16, "name": "Encore", "color": (255, 225, 255)},
    17: {"id": 17, "name": "Life Recovery", "keywords": ["healer"], "color": (78, 206, 49)},
    20: {"id": 20, "name": "Skill Boost", "keywords": ["sb"], "color": (253, 58, 54)},
    21: {"id": 21, "name": "Cute Focus", "keywords": ["focus"], "color": (242, 7, 99)},
    22: {"id": 22, "name": "Cool Focus", "keywords": ["focus"], "color": (15, 99, 255)},
    23: {"id": 23, "name": "Passion Focus", "keywords": ["focus"], "color": (248, 171, 7)},
    24: {"id": 24, "name": "All-round", "keywords": ["ar"], "color": (163, 197, 25)},
    25: {"id": 25, "name": "Life Sparkle", "keywords": ["ls"], "color": (255, 187, 96)},
    26: {"id": 26, "name": "Tricolor Synergy", "keywords": ["syn"], "color": (168, 92, 120)},
    27: {"id": 27, "name": "Coordinate", "color": (251, 153, 24)},
    28: {"id": 28, "name": "Long Act", "color": (255, 211, 119)},
    29: {"id": 29, "name": "Flick Act", "color": (119, 206, 222)},
    30: {"id": 30, "name": "Slide Act", "color": (234, 152, 255)},
    31: {"id": 31, "name": "Tuning", "color": (141, 201, 87)},
    32: {"id": 32, "name": "Cute Ensemble", "keywords": ["ens"], "color": (252, 104, 163)},
    33: {"id": 33, "name": "Cool Ensemble", "keywords": ["ens"], "color": (121, 168, 255)},
    34: {"id": 34, "name": "Passion Ensemble", "keywords": ["ens"], "color": (251, 201, 111)},
    35: {"id": 35, "name": "Vocal Motif", "color": (250, 80, 106)},
    36: {"id": 36, "name": "Dance Motif", "color": (77, 198, 217)},
    37: {"id": 37, "name": "Visual Motif", "color": (244, 162, 52)},
    38: {"id": 38, "name": "Tricolor Symphony", "keywords": ["sym"], "color": (205, 160, 177)},
    39: {"id": 39, "name": "Alternate", "keywords": ["alt"], "color": (127, 127, 127)},
    40: {"id": 40, "name": "Refrain", "keywords": ["ref"], "color": (218, 126, 3)},
    41: {"id": 41, "name": "Magic", "keywords": ["mag"], "color": (255, 200, 255)},
    42: {"id": 42, "name": "Mutual", "keywords": ["mut"], "color": (191, 191, 191)},
    43: {"id": 43, "name": "Overdrive", "keywords": ["od"], "color": (238, 187, 221)},
    44: {"id": 44, "name": "Tricolor Spike", "keywords": ["spk"], "color": (234, 115, 67)},
    45: {"id": 45, "name": "Dominant Harmony (CutexCool)", "keywords": ["dom", "har"], "color": (151, 44, 161)},
    46: {"id": 46, "name": "Dominant Harmony (CutexPassion)", "keywords": ["dom", "har"], "color": (244, 73, 62)},
    47: {"id": 47, "name": "Dominant Harmony (CoolxCute)", "keywords": ["dom", "har"], "color": (106, 62, 193)},
    48: {"id": 48, "name": "Dominant Harmony (CoolxPassion)", "keywords": ["dom", "har"], "color": (108, 128, 156)},
    49: {"id": 49, "name": "Dominant Harmony (PassionxCute)", "keywords": ["dom", "har"], "color": (246, 105, 44)},
    50: {"id": 50, "name": "Dominant Harmony (PassionxCool)", "keywords": ["dom", "har"], "color": (155, 142, 106)},
    51: {"id": 51, "name": "Crystal Heel", "keywords": ["cry"], "color": (78, 243, 253)}
}

SKILL_COLOR_BY_NAME = {
    v['name']: v['color'] for v in SKILL_BASE.values()
}

logger.debug("Creating chihiro.skill_keywords...")

db.cachedb.execute(""" DROP TABLE IF EXISTS skill_keywords """)
db.cachedb.execute("""
    CREATE TABLE IF NOT EXISTS skill_keywords (
        "id" INTEGER UNIQUE PRIMARY KEY,
        "skill_name" TEXT,
        "keywords" TEXT
    )
""")
for skill_id, skill_data in SKILL_BASE.items():
    db.cachedb.execute("""
        INSERT OR IGNORE INTO skill_keywords ("id", "skill_name", "keywords")
        VALUES (?,?,?)
    """, [skill_id, skill_data['name'],
          skill_data['name'] + " " + " ".join(skill_data['keywords'])
          if 'keywords' in skill_data else skill_data['name']])
db.cachedb.commit()

logger.debug("chihiro.skill_keywords created.")

SPARKLE_BONUS_SSR = OrderedDict({_[0]: _[1] for idx, _ in enumerate(db.masterdb.execute_and_fetchall(
    "SELECT life_value / 10, type_01_value FROM skill_life_value ORDER BY life_value"))})
SPARKLE_BONUS_SR = OrderedDict({_[0]: _[1] for idx, _ in enumerate(db.masterdb.execute_and_fetchall(
    "SELECT life_value / 10, type_02_value FROM skill_life_value ORDER BY life_value"))})
SPARKLE_BONUS_SSR_GRAND = OrderedDict({_[0]: _[1] for idx, _ in enumerate(db.masterdb.execute_and_fetchall(
    "SELECT life_value / 10, type_01_value FROM skill_life_value_grand ORDER BY life_value"))})
SPARKLE_BONUS_SR_GRAND = OrderedDict({_[0]: _[1] for idx, _ in enumerate(db.masterdb.execute_and_fetchall(
    "SELECT life_value / 10, type_02_value FROM skill_life_value_grand ORDER BY life_value"))})

for d in [SPARKLE_BONUS_SSR, SPARKLE_BONUS_SR, SPARKLE_BONUS_SSR_GRAND, SPARKLE_BONUS_SR_GRAND]:
    c_v = 0
    for key, value in d.items():
        if value < c_v:
            d[key] = c_v
        if c_v < value:
            c_v = value

SKILL_DESCRIPTION = {
    0: "",
    1: "{}% SCORE UP to PERFECT notes.",
    2: "{}% SCORE UP to PERFECT/GREAT notes.",
    4: "{}% COMBO BONUS UP.",
    5: "Set GREAT notes to PERFECT.",
    6: "Set GREAT/NICE notes to PERFECT.",
    7: "Set GREAT/NICE/BAD notes to PERFECT.",
    9: "Sustain combo on NICE.",
    12: "Prevents life decrease.",
    14: "Consuming {} life, {}% SCORE UP to PERFECT/GREAT notes and sustain combo on NICE/BAD.",
    15: "{}% SCORE UP to PERFECT notes, halves PERFECT timing window.",
    16: "Repeats the skill of other idols that was last activated.",
    17: "Heals {} life on PERFECT.",
    20: "Boosts SCORE UP/COMBO BONUS UP skill effects by {}%"
        " and boosts other skill effects of other idols.",
    21: "If only CUTE idols are in the unit, {}% SCORE UP to PERFECT notes, {}% COMBO BONUS UP.",
    22: "If only COOL idols are in the unit, {}% SCORE UP to PERFECT notes, {}% COMBO BONUS UP.",
    23: "If only PASSION idols are in the unit, {}% SCORE UP to PERFECT notes, {}% COMBO BONUS UP.",
    24: "{}% COMBO BONUS UP, heals {} life on PERFECT",
    25: "With the scale of the life value, COMBO BONUS UP.",
    26: "If idols of all 3 types are in the unit, {}% SCORE UP and {} life healing on PERFECT notes,"
        " {}% COMBO BONUS UP.",
    27: "{}% SCORE UP to PERFECT notes, {}% COMBO BONUS UP.",
    28: "{}% SCORE UP to PERFECT notes, {}% SCORE UP to PERFECT LONG notes.",
    29: "{}% SCORE UP to PERFECT notes, {}% SCORE UP to PERFECT FLICK notes.",
    30: "{}% SCORE UP to PERFECT notes, {}% SCORE UP to PERFECT SLIDE notes.",
    31: "{}% COMBO BONUS UP, set GREAT/NICE notes to PERFECT.",
    32: "Boosts SCORE UP/COMBO BONUS UP skill effects of other CUTE idols by {}%.",
    33: "Boosts SCORE UP/COMBO BONUS UP skill effects of other COOL idols by {}%.",
    34: "Boosts SCORE UP/COMBO BONUS UP skill effects of other PASSION idols by {}%.",
    35: "With the scale of the VOCAL value of the unit, SCORE UP to PERFECT notes.",
    36: "With the scale of the DANCE value of the unit, SCORE UP to PERFECT notes.",
    37: "With the scale of the VISUAL value of the unit, SCORE UP to PERFECT notes.",
    38: "If idols of all 3 types are in the unit, boosts SCORE UP/COMBO BONUS UP skill effects by {}%"
        " and boosts other skill effects of other idols.",
    39: "{}% COMBO BONUS DOWN, apply the highest SCORE UP effect activated during LIVE {}% boosted.",
    40: "Apply the highest SCORE UP/COMBO BONUS UP effect activated during LIVE.",
    41: "Activates the effects of all idols in the unit and applies the highest effect.",
    42: "{}% SCORE DOWN, apply the highest COMBO BONUS UP effect activated during LIVE {}% boosted.",
    43: "{}% COMBO BONUS UP, heals {} life on PERFECT and sustain combo only in PERFECT.",
    44: "If song is ALL type and idols of all 3 types are in the unit, consume {} life, {}% SCORE UP to PERFECT notes, {}% COMBO BONUS UP.",
    45: "If song is COOL type and only CUTE or COOL idols are in the unit, boosts SCORE UP skill effect of other CUTE idols and COMBO BONUS UP skill effect of other COOL idols scaling with each type's number.",
    46: "If song is PASSION type and only CUTE or PASSION idols are in the unit, boosts SCORE UP skill effect of other CUTE idols and COMBO BONUS UP skill effect of other PASSION idols scaling with each type's number.",
    47: "If song is CUTE type and only COOL or CUTE idols are in the unit, boosts SCORE UP skill effect of other COOL idols and COMBO BONUS UP skill effect of other CUTE idols scaling with each type's number.",
    48: "If song is PASSION type and only COOL or PASSION idols are in the unit, boosts SCORE UP skill effect of other COOL idols and COMBO BONUS UP skill effect of other PASSION idols scaling with each type's number.",
    49: "If song is CUTE type and only PASSION or CUTE idols are in the unit, boosts SCORE UP skill effect of other PASSION idols and COMBO BONUS UP skill effect of other CUTE idols scaling with each type's number.",
    50: "If song is COOL type and only PASSION or COOL idols are in the unit, boosts SCORE UP skill effect of other PASSION idols and COMBO BONUS UP skill effect of other COOL idols scaling with each type's number.",
    }


class SkillInact(Enum):
    LIFE_LOW = 1
    NOT_CU_ONLY = 2
    NOT_CO_ONLY = 3
    NOT_PA_ONLY = 4
    NOT_TRICOLOR = 5
    NO_ENCOREABLE = 6
    NO_SCORE_BONUS = 7
    NO_COMBO_BONUS = 8
    NO_SCORE_COMBO = 9
    NO_MAGIC_SKILL = 10
    NOT_ALL_SONG = 11
    NOT_CU_SONG = 12
    NOT_CO_SONG = 13
    NOT_PA_SONG = 14
    NOT_CUCO_ONLY = 15
    NOT_CUPA_ONLY = 16
    NOT_COPA_ONLY = 17


SKILL_INACTIVATION_REASON = {
    1: "Not enough life left.",
    2: "The unit does not consist of only CUTE idols.",
    3: "The unit does not consist of only COOL idols.",
    4: "The unit does not consist of only PASSION idols.",
    5: "The unit does not consist of all 3 type idols.",
    6: "There are no skills to encore.",
    7: "No SCORE UP skill effects have been activated.",
    8: "No COMBO BONUS UP skill effects have been activated.",
    9: "No SCORE UP nor COMBO BONUS UP skill effects have been activated.",
    10: "There are no skills that magic can activate.",
    11: "Song is not ALL type.",
    12: "Song is not CUTE type.",
    13: "Song is not COOL type.",
    14: "Song is not PASSION type.",
    15: "The unit does not consist of only CUTE or COOL idols.",
    16: "The unit does not consist of only CUTE or PASSION idols.",
    17: "The unit does not consist of only COOL or PASSION idols."
    }


def get_sparkle_bonus(rarity: int, grand: bool = False):
    if grand:
        if rarity > 6:
            return SPARKLE_BONUS_SSR_GRAND
        if rarity > 4:
            return SPARKLE_BONUS_SR_GRAND
    else:
        if rarity > 6:
            return SPARKLE_BONUS_SSR
        if rarity > 4:
            return SPARKLE_BONUS_SR
