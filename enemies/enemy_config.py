# enemies/enemy_config.py
# DATA ONLY – KHÔNG LOAD ẢNH

ENEMY_CONFIG = {

# ================= PATROL =================
"AngryPig": {
    "hp": 2, "speed": 1,
    "animations": {
        "idle":  {"path": "assets/Enemies/AngryPig/Idle (36x30).png",  "w": 36, "h": 30},
        "run":   {"path": "assets/Enemies/AngryPig/Run (36x30).png",   "w": 36, "h": 30},
        "walk":  {"path": "assets/Enemies/AngryPig/Walk (36x30).png",  "w": 36, "h": 30},
        "hit":   {"path": "assets/Enemies/AngryPig/Hit (36x30).png",   "w": 36, "h": 30},
    }
},

"Chicken": {
    "hp": 1, "speed": 1,
    "animations": {
        "idle": {"path": "assets/Enemies/Chicken/Idle (32x34).png", "w": 32, "h": 34},
        "run":  {"path": "assets/Enemies/Chicken/Run (32x34).png",  "w": 32, "h": 34},
        "hit":  {"path": "assets/Enemies/Chicken/Hit (32x34).png",  "w": 32, "h": 34},
    }
},

"Radish": {
    "hp": 1, "speed": 1,
    "animations": {
        "idle1": {"path": "assets/Enemies/Radish/Idle 1 (30x38).png", "w": 30, "h": 38},
        "idle2": {"path": "assets/Enemies/Radish/Idle 2 (30x38).png", "w": 30, "h": 38},
        "run":   {"path": "assets/Enemies/Radish/Run (30x38).png",    "w": 30, "h": 38},
        "hit":   {"path": "assets/Enemies/Radish/Hit (30x38).png",    "w": 30, "h": 38},
    }
},

"Rino": {
    "hp": 3, "speed": 2,
    "animations": {
        "idle":     {"path": "assets/Enemies/Rino/Idle (52x34).png",      "w": 52, "h": 34},
        "run":      {"path": "assets/Enemies/Rino/Run (52x34).png",       "w": 52, "h": 34},
        "hit":      {"path": "assets/Enemies/Rino/Hit (52x34).png",       "w": 52, "h": 34},
        "hit_wall": {"path": "assets/Enemies/Rino/Hit Wall (52x34).png",  "w": 52, "h": 34},
    }
},

"Mushroom": {
    "hp": 1, "speed": 1,
    "animations": {
        "idle": {"path": "assets/Enemies/Mushroom/Idle (32x32).png", "w": 32, "h": 32},
        "run":  {"path": "assets/Enemies/Mushroom/Run (32x32).png",  "w": 32, "h": 32},
        "hit":  {"path": "assets/Enemies/Mushroom/Hit.png",          "w": 32, "h": 32},
    }
},

# ================= FLYING =================
"Bat": {
    "hp": 1, "speed": 1,
    "animations": {
        "idle":        {"path": "assets/Enemies/Bat/Flying (46x30).png",        "w": 46, "h": 30},
        "hit":         {"path": "assets/Enemies/Bat/Hit (46x30).png",           "w": 46, "h": 30},
        "ceiling_in":  {"path": "assets/Enemies/Bat/Ceiling In (46x30).png",    "w": 46, "h": 30},
        "ceiling_out": {"path": "assets/Enemies/Bat/Ceiling Out (46x30).png",   "w": 46, "h": 30},
    }
},

"Bee": {
    "hp": 1, "speed": 1,
    "animations": {
        "idle":   {"path": "assets/Enemies/Bee/Idle (36x34).png",   "w": 36, "h": 34},
        "attack": {"path": "assets/Enemies/Bee/Attack (36x34).png", "w": 36, "h": 34},
        "hit":    {"path": "assets/Enemies/Bee/Hit (36x34).png",    "w": 36, "h": 34},
    }
},

"BlueBird": {
    "hp": 1, "speed": 2,
    "animations": {
        "idle": {"path": "assets/Enemies/BlueBird/Flying (32x32).png", "w": 32, "h": 32},
        "hit":  {"path": "assets/Enemies/BlueBird/Hit (32x32).png",    "w": 32, "h": 32},
    }
},

# ================= JUMPER =================
"Bunny": {
    "hp": 1, "speed": 1,
    "animations": {
        "idle": {"path": "assets/Enemies/Bunny/Idle (34x44).png", "w": 34, "h": 44},
        "run":  {"path": "assets/Enemies/Bunny/Run (34x44).png",  "w": 34, "h": 44},
        "jump": {"path": "assets/Enemies/Bunny/Jump.png",         "w": 34, "h": 44},
        "fall": {"path": "assets/Enemies/Bunny/Fall.png",         "w": 34, "h": 44},
        "hit":  {"path": "assets/Enemies/Bunny/Hit (34x44).png",  "w": 34, "h": 44},
    }
},

"Slime": {
    "hp": 2, "speed": 1,
    "animations": {
        "idle": {"path": "assets/Enemies/Slime/Idle-Run (44x30).png", "w": 44, "h": 30},
        "hit":  {"path": "assets/Enemies/Slime/Hit (44x30).png",      "w": 44, "h": 30},
    }
},

# ================= STATIONARY / SHOOTER =================
"Plant": {
    "hp": 2, "speed": 0,
    "animations": {
        "idle":   {"path": "assets/Enemies/Plant/Idle (44x42).png",   "w": 44, "h": 42},
        "attack": {"path": "assets/Enemies/Plant/Attack (44x42).png", "w": 44, "h": 42},
        "hit":    {"path": "assets/Enemies/Plant/Hit (44x42).png",    "w": 44, "h": 42},
    }
},

"Trunk": {
    "hp": 2, "speed": 0,
    "animations": {
        "idle":   {"path": "assets/Enemies/Trunk/Idle (64x32).png",   "w": 64, "h": 32},
        "run":    {"path": "assets/Enemies/Trunk/Run (64x32).png",    "w": 64, "h": 32},
        "attack": {"path": "assets/Enemies/Trunk/Attack (64x32).png", "w": 64, "h": 32},
        "hit":    {"path": "assets/Enemies/Trunk/Hit (64x32).png",    "w": 64, "h": 32},
    }
},

# ================= SPECIAL =================
"Ghost": {
    "hp": 1, "speed": 0,
    "animations": {
        "idle":       {"path": "assets/Enemies/Ghost/Idle (44x30).png",       "w": 44, "h": 30},
        "appear":     {"path": "assets/Enemies/Ghost/Appear (44x30).png",     "w": 44, "h": 30},
        "disappear":  {"path": "assets/Enemies/Ghost/Desappear (44x30).png",  "w": 44, "h": 30},
        "hit":        {"path": "assets/Enemies/Ghost/Hit (44x30).png",         "w": 44, "h": 30},
    }
},

"Snail": {
    "hp": 2, "speed": 1,
    "animations": {
        "idle":  {"path": "assets/Enemies/Snail/Idle (38x24).png",            "w": 38, "h": 24},
        "walk":  {"path": "assets/Enemies/Snail/Walk (38x24).png",            "w": 38, "h": 24},
        "shell": {"path": "assets/Enemies/Snail/Shell Idle (38x24).png",      "w": 38, "h": 24},
        "hit":   {"path": "assets/Enemies/Snail/Hit (38x24).png",             "w": 38, "h": 24},
    }
},

"Turtle": {
    "hp": 3, "speed": 1,
    "animations": {
        "idle":   {"path": "assets/Enemies/Turtle/Idle 1 (44x26).png",    "w": 44, "h": 26},
        "shell":  {"path": "assets/Enemies/Turtle/Spikes in (44x26).png", "w": 44, "h": 26},
        "attack": {"path": "assets/Enemies/Turtle/Spikes out (44x26).png","w": 44, "h": 26},
        "hit":    {"path": "assets/Enemies/Turtle/Hit (44x26).png",       "w": 44, "h": 26},
    }
},
}
