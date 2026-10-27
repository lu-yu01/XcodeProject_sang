from itertools import product,combinations
from collections import Counter

def g1():
 out=[]
 for bits in product([0,1],repeat=8):
  a,b,c,d,e,f,g,h=bits
  if sum(bits)!=4 or not(a or b):continue
  if a and not c or b and d:continue
  if f != (a!=e):continue
  if g and not b:continue
  out.append(bits)
 return out
def g2():
 pairs=list(combinations(range(5),2));out=[]
 for rows in product(pairs,repeat=4):
  counts=Counter(x for row in rows for x in row)
  if any(not 1<=counts[x]<=2 for x in range(5)):continue
  if any(0 in row and 1 in row for row in rows):continue
  if (0 in rows[0])+(2 in rows[0])!=1:continue
  if 4 in rows[0]:continue
  if (3 in rows[1]) != (1 in rows[3]):continue
  if not any(2 in row and 4 in row for row in rows):continue
  out.append(rows)
 return out
DUR=[2,1,2,1,1]
def nonoverlap(m,a,b):return m[a]+DUR[a]<=m[b] or m[b]+DUR[b]<=m[a]
def g3():
 out=[]
 for m in product(range(1,7),repeat=5):
  if any(m[i]+DUR[i]>7 for i in range(5)):continue
  if not all(nonoverlap(m,a,b) for a,b in combinations([0,2,4],2)):continue
  if not nonoverlap(m,1,3):continue
  if m[0]+2>m[1] or m[2]+2>m[3] or m[1]+1>m[4]:continue
  out.append(m)
 return out
if __name__=='__main__':
 for key,models in [('G1',g1()),('G2',g2()),('G3',g3())]:
  print(key,len(models));print(models[:35])
  if key=='G1':
   for i,name in enumerate('甲乙丙丁戊己庚'):print(name,sum(m[i] for m in models))
   for i,j in combinations(range(7),2):
    count=sum(m[i] and m[j] for m in models)
    if count in [0,1,len(models)]:print('pair',i,j,count)
  if key=='G2':
   for i in range(4):print('paper',i,Counter(m[i] for m in models))
   for i in range(5):print('counts',i,Counter(sum(i in row for row in m) for m in models))
  if key=='G3':
   for i in range(5):print('start',i,Counter(m[i] for m in models))
   print('finish',Counter(max(m[i]+DUR[i]-1 for i in range(5)) for m in models))
