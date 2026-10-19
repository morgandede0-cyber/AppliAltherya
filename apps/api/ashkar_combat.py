"""Pure combat rules extracted from the historical Tower; no bot initialization."""
import random,json
from pathlib import Path
from dataclasses import dataclass
from arena_engine import CLASSES,arena_player_skills
FLOORS={int(k):v for k,v in json.loads(Path(__file__).with_name('ashkar_catalog.json').read_text()).items()}
@dataclass
class BattleState:
    owner_id: int
    floor: int
    class_key: str
    player_name: str
    player_level: int
    player_hp: int
    player_max_hp: int
    player_atk: int
    player_def: int
    player_speed: int
    equipment_def_pct: float
    enemy_hp: int
    enemy_max_hp: int
    enemy_atk: int
    enemy_def: int
    enemy_speed: int
    ultimate_cd: int = 0
    guarding: bool = False
    guard_reduction: float = 0.0
    temp_evade: float = 0.0
    next_damage_bonus: float = 0.0
    ravager_light_stacks: int = 0
    enemy_bleed: int = 0
    enemy_shaken: bool = False
    evaded_last_attack: bool = False
    enemy_enraged: bool = False
    log: str = "Le combat commence !"

    @property
    def class_cfg(self):
        return {**CLASSES["arena_fighter"], "skills": arena_player_skills(self.player_level)}

def _enemy_damage(atk: int, defense: int, reduction: float = 0.0, *, power=1.0):
    mitigation = 100 / (100 + max(0, defense))
    raw = atk * mitigation * power * random.uniform(.90, 1.10)
    raw *= max(0.05, 1.0 - reduction)
    crit = random.random() < .06
    if crit:
        raw *= 1.5
    return max(1, round(raw)), crit

def _player_damage(state: BattleState, action: str):
    cfg = state.class_cfg
    skill = cfg["skills"][action]
    # Conversion des puissances de l'Arène vers l'échelle de la Tour.
    skill_mult = skill["power"] / 14.0
    mult = skill_mult
    if state.next_damage_bonus:
        mult *= 1 + state.next_damage_bonus
        state.next_damage_bonus = 0.0
    mitigation = 100 / (100 + max(0, state.enemy_def))
    raw = state.player_atk * mitigation * mult * random.uniform(.94, 1.06)
    crit = action == "ultimate" and random.random() < .50
    if crit:
        raw *= 1.60
    return max(1, round(raw)), crit

def _enemy_dodges(state: BattleState, action: str):
    if action == "light":
        return False
    skill = state.class_cfg["skills"][action]
    if random.random() > skill.get("accuracy", 1.0):
        return True
    speed_gap = max(0, state.enemy_speed - state.player_speed)
    chance = min(.14, .02 + speed_gap * .0025)
    return random.random() < chance

def _player_dodges(state: BattleState):
    cfg = state.class_cfg
    speed_gap = max(0, state.player_speed - state.enemy_speed)
    equip_evade = min(.05, max(0.0, (state.player_speed - 100) / 2000.0))
    chance = min(.15, cfg["evade"] + state.temp_evade + equip_evade + speed_gap * .0015)
    dodged = random.random() < chance
    state.evaded_last_attack = dodged
    return dodged

def enemy_turn(s):
    if s.enemy_hp <= 0:
        return ''
    bleed_line = ''
    if s.enemy_bleed > 0:
        bleed = s.enemy_bleed
        s.enemy_bleed = 0
        s.enemy_hp = max(0, s.enemy_hp - bleed)
        bleed_line = f"🩸 {FLOORS[s.floor]['name']} subit **{bleed}** dégâts de saignement. "
        if s.enemy_hp <= 0:
            return bleed_line
    if _player_dodges(s):
        s.guarding = False
        s.guard_reduction = 0.0
        s.temp_evade = 0.0
        return bleed_line + f'💨 {s.player_name} esquive la riposte !'
    power = 0.9 if s.enemy_shaken else 1.0
    s.enemy_shaken = False
    if s.floor == 10 and s.enemy_hp <= s.enemy_max_hp // 2:
        if not s.enemy_enraged:
            s.enemy_enraged = True
        power *= 1.22
    class_reduction = s.class_cfg['passive_reduction']
    equip_reduction = min(0.1, s.equipment_def_pct / 100.0)
    total_reduction = 1 - (1 - class_reduction) * (1 - equip_reduction)
    if s.guarding:
        total_reduction = 1 - (1 - total_reduction) * (1 - s.guard_reduction)
    dmg, crit = _enemy_damage(s.enemy_atk, s.player_def, total_reduction, power=power)
    s.player_hp = max(0, s.player_hp - dmg)
    prefix = '💥 CRITIQUE ! ' if crit else ''
    rage = " 🔥 Varkhaz entre en **Rage d'Obsidienne** !" if s.enemy_enraged and s.floor == 10 else ''
    s.guarding = False
    s.guard_reduction = 0.0
    s.temp_evade = 0.0
    return bleed_line + f"{prefix}{FLOORS[s.floor]['name']} inflige **{dmg}** dégâts.{rage}"