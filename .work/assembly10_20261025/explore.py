from itertools import product,combinations
from collections import Counter
from solver import *
T=tuple(product(range(3),range(2),range(2)))
catalog={}
for co in combinations(T,6):
 if connected(co) and is_3d(co):catalog[canonical(co)]=norm(co)
print('catalog',len(catalog))
for i,p in enumerate(catalog.values()):
 comps={canonical(set(T)-set(a)) for a in placements(p,T) if connected(set(T)-set(a))}
 if len(comps)<=2:
  print(i,'dims',dims(p),'edges',edges(p),'layers',layers(p),'comps',len(comps),'chiral',canonical(p)!=canonical(mirror(p)), 'poses',len(placements(p,T)))
