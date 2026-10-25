#!/usr/bin/env python3
# 从博客 tools/war3-preview-data.json + 图脚本路线生成 data.js（含营地基础经验与待核清零）
import json, re, os
BLOG = '/Users/luxiaopeng/github/blog'
HERE = os.path.dirname(os.path.abspath(__file__))
L={"Forest Troll":2,"Forest Troll Trapper":3,"Forest Troll Berserker":4,"Forest Troll High Priest":4,
"Forest Troll Warlord":6,"Forest Troll Shadow Priest":2,"Ice Troll":2,"Ice Troll Priest":2,"Ice Troll Berserker":4,
"Ice Troll High Priest":4,"Ice Troll Warlord":6,"Ice Troll Trapper":3,"Ogre Warrior":3,"Ogre Mauler":5,
"Ogre Magi":5,"Ogre Lord":7,"Gnoll":1,"Gnoll Warden":3,"Gnoll Brute":3,"Gnoll Overseer":5,"Gnoll Assassin":3,
"Gnoll Poacher":1,"Kobold":1,"Kobold Tunneler":3,"Kobold Geomancer":3,"Kobold Taskmaster":5,
"Murloc Tiderunner":1,"Murloc Huntsman":2,"Murloc Flesheater":3,"Murloc Nightcrawler":3,"Murloc Plaguebearer":2,
"Murloc Mutant":6,"Rock Golem":6,"Mud Golem":2,"Granite Golem":9,"Sea Turtle":2,"Giant Sea Turtle":4,
"Gargantuan Sea Turtle":7,"Dragon Turtle":10,"Tuskarr Warrior":4,"Tuskarr Trapper":4,"Tuskarr Sorcerer":5,
"Tuskarr Spearman":2,"Tuskarr Fighter":2,"Tuskarr Healer":3,"Tuskarr Chieftain":7,"Polar Furbolg Shaman":4,
"Polar Furbolg Tracker":6,"Magnataur Reaver":8,"Nerubian Webspinner":3,"Crystal Arachnathid":1,
"Barbed Arachnathid (Creep)":1,"Warrior Arachnathid":3,"Arachnathid Earth-borer":4,"Overlord Arachnathid":5,
"Renegade Wizard":5,"Apprentice Wizard":1,"Rogue":3,"Rogue Wizard":3,"Rogue Wizard (creep)":3,"Brigand":2,"Enforcer":5,"Assassin":4,"Bandit Lord":7,
"Timber Wolf":2,"Frost Wolf":2,"Dire Wolf":6,"Dire Frost Wolf":6,"Hydra Hatchling":3,"Hydra":6,"Elder Hydra":7,
"Mammoth":3,"Icetusk Mammoth":5,"Dire Mammoth":8,"Mur'gul Snarecaster":4,"Mur'gul Tidewarrior":3,
"Mur'gul Blood-Gill":2,"Mur'gul Marauder":6,"Red Dragon Whelp":3,"Red Drake":6,"Red Dragon":10,"Black Drake":6,"Sea Turtle Hatchling":1,
"Sasquatch":5,"Elder Sasquatch":6,"Enraged Wildkin":6,"Wildkin":4,"Berserk Wildkin":8,
"Spider Crab Limbripper":3,"Spider Crab Shorecrawler":1,"Spider Crab Behemoth":5,
"Furbolg":4,"Furbolg Shaman":4,"Furbolg Tracker":6,"Furbolg Champion":7,"Furbolg Elder Shaman":7,
"Makrura Tidecaller":2,"Makrura Snapper":5,"Makrura Prawn":1,"Makrura Pooldweller":2,"Makrura Deepseer":5,"Makrura Tidal Lord":7,
"Reef Elemental":2,"Enraged Elemental":4,"Sea Elemental":5,"Berserk Elemental":8,
"Skeleton Archer":1,"Giant Skeleton Warrior":3,"Skeletal Marksman":3,"Burning Archer":3,"Skeleton Warrior":1,
"Stormreaver Apprentice":1,"Stormreaver Hermit":3,"Stormreaver Necrolyte":6,"Stormreaver Warlock":9,
"Sea Giant":3,"Sea Giant Hunter":5,"Sea Giant Behemoth":8,"Sludge Flinger":3,"Sludge Minion":1,"Sludge Monstrosity":5,
"Voidwalker":3,"Greater Voidwalker":6,"Polar Bear":4,"Giant Polar Bear":6,"Skeletal Orc":3}
BX={1:25,2:40,3:60,4:85,5:115,6:150,7:190,8:235,9:285,10:340}
d=json.load(open(os.path.join(BLOG,'tools','war3-preview-data.json')))
NAME={"ei":"Echo Isles","ch":"Concealed Hill","am":"Amazonia","tm":"Twisted Meadows","al":"Autumn Leaves",
"st":"Springtime","hf":"HammerFall","th":"TideHunter3","ni":"Northern Isles","lr":"Last Refuge","tr2":"Turtle Rock","lt2":"Lost Temple"}
src=open(os.path.join(BLOG,'tools','war3-figures.py')).read()
routes={}
for key in NAME:
    m=re.search(r'draw_data\("%s",.*?routes=\[(.*?)\],\s*(?:legend_loc="[^"]*",\s*)*note='%key, src, re.S)
    if not m: continue
    pts=[]
    for rm in re.finditer(r'\[([\d\.,\s()]+?)\],\s*(\w+),\s*"[^"]*",\s*\n?\s*"([^"]*)"', m.group(1)):
        nums=re.findall(r'\(([\d.]+),\s*([\d.]+)\)', rm.group(1))
        pts.append({"style":rm.group(2),"label":rm.group(3),"path":[[float(a),float(b)] for a,b in nums]})
    if pts: routes[key]=pts
msrc=re.search(r'CN = \{(.*?)\n    \}', src, re.S)
CN={k:v for k,v in re.findall(r'"([^"]+)":\s*"([^"]+)"', msrc.group(1))}
ITEM={"Permanent":"永久","Charged":"充能","Power Up":"强化"}
out={"maps":[]}
miss={}
for key in NAME:
    md=d[key]; spots=[]
    for s in md["spots"]:
        xp=0; ok=True
        for c in s["creeps"]:
            lv=L.get(c["name"])
            if lv is None: ok=False; miss[c["name"]]=1; continue
            xp+=BX[lv]*c["count"]
        comp="、".join(f"{CN.get(c['name'],c['name'])}{'×'+str(c['count']) if c['count']>1 else ''}" for c in s["creeps"])
        drops=" / ".join(f"{ITEM.get(c['item'],c['item'])}{c['ilvl']}" for c in s["creeps"] if c["item"])
        spots.append({"x":s["x"],"y":s["y"],"level":s["level"],"xp":xp if ok else None,"comp":comp,"drops":drops})
    out["maps"].append({"key":key,"name":NAME[key],"img":f"assets/preview-{key}.jpg",
        "objects":md["objects"],"spots":spots,"routes":routes.get(key,[])})
with open(os.path.join(HERE,'..','data.js'),'w') as f:
    f.write('const MAPDATA='+json.dumps(out,ensure_ascii=False))
print('camps:',sum(len(m['spots']) for m in out['maps']),'| routes:',sorted(routes.keys()),'| missing:',miss or '无')
