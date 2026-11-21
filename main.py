import json,os,sys,urllib.request
U=os.environ['MAKEFUN_ENV_URL']
V={'p':100,'n':320,'b':330,'r':500,'q':900,'k':0}
B=(15,17,-15,-17);R=(1,-1,16,-16);N=(14,18,31,33,-14,-18,-31,-33);D=B+R
def post(p,d):
 q=urllib.request.Request(U+p,data=json.dumps(d).encode(),headers={'content-type':'application/json'})
 return json.load(urllib.request.urlopen(q,timeout=9))
def sq(s):return ord(s[0])-97+(ord(s[1])-49)*16
def nm(i):return 'abcdefgh'[i&7]+str((i>>4)+1)
def parse(f):
 q=f.split();b=['.']*128
 for y,row in enumerate(q[0].split('/')):
  x=0
  for c in row:
   if c.isdigit():x+=int(c)
   else:b[(7-y)*16+x]=c;x+=1
 return b,1 if q[1]=='w' else -1,q[2],-1 if q[3]=='-' else sq(q[3])
def atk(b,s,t):
 for d in ((15,17) if t==1 else (-15,-17)):
  a=s-d
  if not a&0x88 and b[a]==('P' if t==1 else 'p'):return 1
 for d in N:
  a=s+d
  if not a&0x88 and b[a].lower()=='n' and b[a].isupper()==(t==1):return 1
 for d in D:
  a=s+d;n=1
  while not a&0x88:
   p=b[a]
   if p!='.':
    if p.isupper()==(t==1):
     k=p.lower()
     if k=='q' or k=='r' and d in R or k=='b' and d in B or k=='k' and n==1:return 1
    break
   a+=d;n+=1
 return 0
def play(st,m):
 b,t,r,e=st;a,z=sq(m[:2]),sq(m[2:4]);p=b[a];c=b.copy();c[a]='.'
 if p.lower()=='p' and z==e:c[z-16*t]='.'
 if p.lower()=='k' and abs(z-a)==2:
  h=a+(3 if z>a else -4);c[a+(1 if z>a else -1)]=c[h];c[h]='.'
 c[z]=m[4].upper() if len(m)>4 and t==1 else m[4].lower() if len(m)>4 else p
 if p.lower()=='k':r=r.replace('K','').replace('Q','') if t==1 else r.replace('k','').replace('q','')
 rr={0:'Q',7:'K',112:'q',119:'k'}
 if p.lower()=='r' and a in rr:r=r.replace(rr[a],'')
 if b[z].lower()=='r' and z in rr:r=r.replace(rr[z],'')
 return c,-t,r,a+8*t if p.lower()=='p' and abs(z-a)==32 else -1
def gen(st):
 b,t,r,e=st;o=[]
 for a,p in enumerate(b):
  if p=='.' or p.isupper()!=(t==1):continue
  k=p.lower()
  if k=='p':
   d=16*t;z=a+d
   if not z&0x88 and b[z]=='.':
    o += [nm(a)+nm(z)+v for v in 'qrbn'] if z>>4 in (0,7) else [nm(a)+nm(z)]
    z+=d
    if a>>4==(1 if t==1 else 6) and b[z]=='.':o.append(nm(a)+nm(z))
   for z in (a+d-1,a+d+1):
    if not z&0x88 and ((b[z]!='.' and b[z].isupper()!=(t==1) and b[z].lower()!='k') or z==e):o += [nm(a)+nm(z)+v for v in 'qrbn'] if z>>4 in (0,7) else [nm(a)+nm(z)]
  else:
   ds=N if k=='n' else B if k=='b' else R if k=='r' else D
   for d in ds:
    z=a+d
    while not z&0x88:
     if b[z]!='.' and (b[z].isupper()==(t==1) or b[z].lower()=='k'):break
     o.append(nm(a)+nm(z))
     if b[z]!='.' or k in 'nk':break
     z+=d
 l=[]
 for m in o:
  c,u,rr,ee=play(st,m);k=next(i for i,p in enumerate(c) if p==('K' if t==1 else 'k'))
  if not atk(c,k,-t):l.append(m)
 return l
def ev(st):
 b,t,r,e=st;s=sum((V[p.lower()] if p.isupper() else -V[p.lower()]) for p in b if p!='.')
 return s*t
def order(st,ms):
 b,t,r,e=st
 def key(m):
  a,z=sq(m[:2]),sq(m[2:4]);p=b[a];v=V[b[z].lower()] if b[z]!='.' else V['p'] if p.lower()=='p' and z==e else 0
  return v*10-V[p.lower()] if v else V.get(m[4],0)*8 if len(m)>4 else 0
 return sorted(ms,key=key,reverse=True)
nodes=0
class Stop(Exception):pass
def search(st,d,lo,hi):
 global nodes
 nodes+=1
 if nodes>1000:raise Stop
 if not d:return ev(st)
 ms=order(st,gen(st))
 if not ms:
  b,t,r,e=st;k=next(i for i,p in enumerate(b) if p==('K' if t==1 else 'k'))
  return -30000 if atk(b,k,-t) else 0
 for m in ms:
  v=-search(play(st,m),d-1,-hi,-lo)
  if v>lo:lo=v
  if lo>=hi:break
 return lo
def choose(f,ms):
 st=parse(f);best=ms[0];lo=-32000
 global nodes
 nodes=0
 for m in order(st,ms):
  try:v=-search(play(st,m),2,-32000,-lo)
  except Stop:break
  if v>lo:lo=v;best=m
 return best
while 1:
 g=post('/game',{})
 if g['status']=='done':break
 while g['status']=='your_move':
  g=post('/move',{'game':g['game'],'move':choose(g['fen'],g['legal_moves'])})
 print('game',g['game'],g['outcome'],g['reason'],file=sys.stderr)
