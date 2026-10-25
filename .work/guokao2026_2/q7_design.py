"""Find four close top-view options with exactly one compatible cube stack."""
from itertools import combinations, product

FRONT = (2,3,1)
RIGHT = (2,3,2)
TOTAL = 12


def witnesses(mask):
    cells = sorted(mask)
    for values in product((1,2,3), repeat=len(cells)):
        if sum(values)!=TOTAL:continue
        matrix = dict(zip(cells,values))
        if tuple(max((matrix.get((r,c),0) for r in range(3)),default=0) for c in range(3))!=FRONT:continue
        if tuple(max((matrix.get((r,c),0) for c in range(3)),default=0) for r in range(3))!=RIGHT:continue
        yield matrix


MASKS=[set(combo) for combo in combinations(product(range(3), repeat=2),6)]
POSSIBLE=[(mask,next(witnesses(mask),None)) for mask in MASKS]

if __name__=="__main__":
    for index,(mask,witness) in enumerate(POSSIBLE):
        if all(any((r,c) in mask for c in range(3)) for r in range(3)) and all(any((r,c) in mask for r in range(3)) for c in range(3)):
            print(index,"YES" if witness else "NO",''.join(''.join('■' if (r,c) in mask else '□' for c in range(3)) for r in range(3)),witness)
