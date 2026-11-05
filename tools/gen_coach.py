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
            'boMe': [e for e in (d.get(g.get('me', ''), {}) or {}).get('bo', [])][:160],
            'boOpp': [e for e in (d.get(opp.get('name', ''), {}) or {}).get('bo', [])][:160],
            'apm': (d.get(g.get('me', ''), {}) or {}).get('apm', []),
        })
    wins = sum(1 for g in games if g['result'] == 'win')
    losses = sum(1 for g in games if g['result'] == 'loss')
    draws = sum(1 for g in games if g['result'] == 'draw')
    data = {'updated': games[-1]['date'] if games else '',
            'me': games[-1]['me'] if games else '',
            'total': len(games), 'wins': wins, 'losses': losses, 'draws': draws,
            'games': games}
    with open(DST, 'w', encoding='utf-8') as f:
        f.write('const COACHDATA=')
        json.dump(data, f, ensure_ascii=False, separators=(',', ':'))
        f.write(';\n')
    print('coach-data.js:', os.path.getsize(DST) // 1024, 'KB,', len(games), 'games')

if __name__ == '__main__':
    main()
