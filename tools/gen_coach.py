#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从 war3-coach 的 opponents.json 生成静态战绩数据 coach-data.js。
博客/网站展示用: 汇总+每局(核心输点/趋势指标/12分钟时间轴/APM)。"""
import json
import os

SRC = os.path.expanduser('~/github/war3-coach/data/opponents.json')
DST = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'coach-data.js')

def main():
    src = json.load(open(SRC, encoding='utf-8'))
    games = []
    for g in sorted(src.get('games', []), key=lambda x: x.get('ts', 0)):
        me = next((p for p in g.get('players', []) if p['name'] == g.get('me')), {})
        opp = next((p for p in g.get('players', []) if p['name'] != g.get('me')), {})
        d = g.get('detail', {})
        games.append({
            'date': g.get('date', ''),
            'map': (g.get('map') or '').split('.')[0][:20],
            'me': g.get('me', ''),
            'meRace': me.get('race', ''),
            'opp': opp.get('name', ''),
            'oppRace': opp.get('race', ''),
            'result': me.get('result') or 'unknown',
            'guess': g.get('guess'),
            'core': g.get('core'),
            'length': g.get('length_s', 0),
            'heroes': me.get('heroes', []),
            'tech': me.get('tech', {}),
            'metrics': g.get('metrics'),
            'marks': g.get('marks') or [],
            'boMe': [e for e in (d.get(g.get('me', ''), {}) or {}).get('bo', [])][:160],
            'boOpp': [e for e in (d.get(opp.get('name', ''), {}) or {}).get('bo', [])][:160],
            'apm': (d.get(g.get('me', ''), {}) or {}).get('apm', []),
        })
    # ---- 总体诊断 (数据驱动: 核心输点分类 + 指标评级) ----
    from collections import Counter
    loss_cores = [g['core'] for g in games if g['core'] and g['result'] == 'loss']
    cats = Counter()
    for c in loss_cores:
        if '空军' in c or '蝙蝠' in c: cats['air'] += 1
        if '驱散' in c: cats['dispel'] += 1
        if '奶系' in c or '白牛' in c: cats['heal'] += 1
        if '节奏' in c or '时点' in c or '转型' in c: cats['tempo'] += 1
    gaps = [g['metrics']['gap_s'] for g in games if g.get('metrics')]
    diagnosis = {
        'cats': dict(cats),
        'gapAvg': round(sum(gaps)/len(gaps)) if gaps else None,
        'games': len(games),
        'advice': [],
    }
    # 建议按证据强度排
    if cats.get('air') or cats.get('dispel') or cats.get('heal'):
        n = cats.get('air', 0) + cats.get('dispel', 0) + cats.get('heal', 0)
        diagnosis['advice'].append([
            '建立「侦查→转型」反射 (本季最致命: 败局核心里 %d/%d 是对面成型兵种你没有应对单位)' % (
                n, len(loss_cores) or 1),
            '两个固定侦查节点: 点升二本的那一秒派苦工/狼探对面主基地看科技建筑; 对面升三本时再探一次。'
            '应对速查: 狮鹫笼/机场→3-4 蝙蝠; 神秘圣地(男女巫成型慢)→部队成型就压一波不给时间; '
            '蜘蛛海(中甲)→大 G 普通攻击150%克制,量要足; 十胜石雕像(重甲def4,猎头打它亏)→白牛驱锁链骷髅+科多吞兵。',
        ])
    if cats.get('tempo') or cats.get('dispel'):
        diagnosis['advice'].append([
            '二本转型期双线不停 (败局普遍在 15 分钟等级差 -2~-5: 升本的 150 秒+三本期你的练级和暴兵双双减速)',
            '升本命令下达后立即排好「练级点 A→B→C」既定路线, 部队队列保持有货。'
            '升本的钱从压人口里省, 不是从部队和练级里省。',
        ])
    if gaps and sum(gaps)/len(gaps) <= 30:
        diagnosis['advice'].append([
            '苦工生产空闲已达标 (均值 %ds < 30s 良好线) — 此项不用再投入, 保持即可' % round(sum(gaps)/len(gaps)),
            '把省下的注意力全部投给上面两条。',
        ])
    diagnosis = diagnosis

    wins = sum(1 for g in games if g['result'] == 'win')
    losses = sum(1 for g in games if g['result'] == 'loss')
    draws = sum(1 for g in games if g['result'] == 'draw')
    data = {'updated': games[-1]['date'] if games else '',
            'me': games[-1]['me'] if games else '',
            'total': len(games), 'wins': wins, 'losses': losses, 'draws': draws,
            'diagnosis': diagnosis,
            'games': games}
    with open(DST, 'w', encoding='utf-8') as f:
        f.write('const COACHDATA=')
        json.dump(data, f, ensure_ascii=False, separators=(',', ':'))
        f.write(';\n')
    print('coach-data.js:', os.path.getsize(DST) // 1024, 'KB,', len(games), 'games')

if __name__ == '__main__':
    main()
