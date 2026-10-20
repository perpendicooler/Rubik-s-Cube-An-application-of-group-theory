#!/usr/bin/env python3
"""Reproducible small-depth BFS for the 3x3 cube under U,R,F and inverses.

Representation uses arrays mapping new positions to old positions. Move tables
follow standard cubie-coordinate conventions. The exploration is an ORIGINAL
computational demonstration, not a new solution to the full cube diameter.
Python 3.10+, standard library only.
"""
from collections import deque
from math import factorial
from pathlib import Path
import json
import argparse

SOLVED = (tuple(range(8)), (0,)*8, tuple(range(12)), (0,)*12)

def move(cp,co,ep,eo):
    return (tuple(cp),tuple(co),tuple(ep),tuple(eo))

# Corner positions URF, UFL, ULB, UBR, DFR, DLF, DBL, DRB.
# Edge positions UR, UF, UL, UB, DR, DF, DL, DB, FR, FL, BL, BR.
MOVES = {
  'U': move((3,0,1,2,4,5,6,7),(0,)*8,
            (3,0,1,2,4,5,6,7,8,9,10,11),(0,)*12),
  'R': move((4,1,2,0,7,5,6,3),(2,0,0,1,1,0,0,2),
            (8,1,2,3,11,5,6,7,4,9,10,0),(0,)*12),
  'F': move((1,5,2,3,0,4,6,7),(1,2,0,0,2,1,0,0),
            (0,9,2,3,4,8,6,7,1,5,10,11),
            (0,1,0,0,0,1,0,0,1,1,0,0)),
}

def apply(state, operator):
    cp,co,ep,eo = state
    p,tw,e,fl=operator
    return (tuple(cp[p[k]] for k in range(8)),
            tuple((co[p[k]] + tw[k]) % 3 for k in range(8)),
            tuple(ep[e[k]] for k in range(12)),
            tuple((eo[e[k]] + fl[k]) % 2 for k in range(12)))

def power(g,k):
    state=SOLVED
    for _ in range(k): state=apply(state,g)
    return state

def sign(perm):
    inversions=sum(perm[i]>perm[j] for i in range(len(perm)) for j in range(i+1,len(perm)))
    return inversions%2

def invariant(state):
    cp,co,ep,eo=state
    return (sum(co)%3==0 and sum(eo)%2==0 and sign(cp)==sign(ep))

def execute(seq):
    s=SOLVED
    for symbol in seq:s=apply(s,MOVES[symbol])
    return s

def bfs(depth):
    seen={SOLVED}
    frontier={SOLVED}
    exact=[1]
    for d in range(1,depth+1):
        nxt=set()
        for s in frontier:
            for move_ in MOVES.values():
                v=apply(s,move_)
                if v not in seen:
                    nxt.add(v)
        seen.update(nxt)
        frontier=nxt
        exact.append(len(frontier))
        print(f'depth={d} new={len(frontier):,} cumulative={len(seen):,}',flush=True)
    return exact, seen

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--depth',type=int,default=6)
    parser.add_argument('--out',type=Path,default=Path('results.json'))
    args=parser.parse_args()
    for gname in list(MOVES):
        assert power(MOVES[gname],4)==SOLVED,gname
        MOVES[gname+"'"]=power(MOVES[gname],3)
    assert all(invariant(g) for g in MOVES.values())
    assert all(apply(MOVES[n],MOVES[n+"'"])==SOLVED for n in ('U','R','F'))
    assert execute(['R','U',"R'","U'"])!=SOLVED
    comm=execute(['R','U',"R'","U'"])
    moved_corners=sum(i!=p or t!=0 for i,(p,t) in enumerate(zip(comm[0],comm[1])))
    moved_edges=sum(i!=p or f!=0 for i,(p,f) in enumerate(zip(comm[2],comm[3])))
    layers, seen=bfs(args.depth)
    assert all(invariant(s) for s in seen), 'Invariant violated'
    order=factorial(8)*3**7*factorial(12)*2**11//2
    results={
        'model':'3x3 cubie group, exact quarter turns U,R,F and inverses',
        'exploration_scope':'BFS depth capped; not a full cube diameter computation',
        'generators':list(MOVES),
        'maximum_depth':args.depth,
        'exact_distance_counts':layers,
        'cumulative_counts':[sum(layers[:i+1]) for i in range(len(layers))],
        'invariants_passed':True,
        'inverse_and_order_four_checks_passed':True,
        'R_U_Rprime_Uprime':{'moved_corners':moved_corners,'moved_edges':moved_edges, 'state':comm},
        'legal_configurations':order,
        'unrestricted_cubie_arrangements':factorial(8)*3**8*factorial(12)*2**12,
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(results,indent=2)+'\n')
    print('ORDER:',order, 'COMMUTATOR:',moved_corners,moved_edges)
    print('RESULTS',args.out)
if __name__=='__main__':main()
