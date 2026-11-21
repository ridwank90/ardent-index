import json,os,sys,urllib.request,urllib.error
U=os.environ.get('MAKEFUN_ENV_URL')
if not U:sys.exit('MAKEFUN_ENV_URL is not set')
V={'p':100,'n':320,'b':330,'r':500,'q':900,'k':0};B=(15,17,-15,-17);R=(1,-1,16,-16);N=(14,18,31,33,-14,-18,-31,-33);D=B+R
class Stop(Exception):pass
def post(p,d):
 r=urllib.request.Request(U+p,data=json.dumps(d).encode(),headers={'content-type':'application/json'})
 try:
  with urllib.request.urlopen(r,timeout=9) as x:return json.load(x)
 except urllib.error.HTTPError as e:sys.exit(str(e.code)+': '+e.read().decode())
def sq(s):return ord(s[0])-97+(ord(s[1])-49)*16
def name(i):return 'abcdefgh'[i&7]+str((i>>4)+1)
def parse(f):
 q=f.split();b=['.']*128
 for y,row in enumerate(q[0].split('/')):
  x=0
  for c in row:
   if c.isdigit():x+=int(c)
   else:b[(7-y)*16+x]=c;x+=1
 return b,1 if q[1]=='w' else -1,q[2],-1 if q[3]=='-' else sq(q[3])
def attacked(b,s,t):
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
 b,t,r,e=st;a,z=sq(m[:2]),sq(m[2:4]);p=b[a];cap=b[z];c=b.copy();c[a]='.'
 if p.lower()=='p' and z==e and cap=='.':c[z-16*t]='.'
 if p.lower()=='k' and abs(z-a)==2:
  h=a+(3 if z>a else -4);c[a+(1 if z>a else -1)]=c[h];c[h]='.'
 c[z]=(m[4].upper() if t==1 else m[4].lower()) if len(m)>4 else p
 if p.lower()=='k':r=r.replace('K','').replace('Q','') if t==1 else r.replace('k','').replace('q','')
 rights={0:'q',7:'k',112:'Q',119:'K'}
 if p.lower()=='r' and a in rights:r=r.replace(rights[a],'')
 if cap.lower()=='r' and z in rights:r=r.replace(rights[z],'')
 e=a+8*t if p.lower()=='p' and abs(z-a)==32 else -1
 return c,-t,r,e
def gen(st):
 b,t,r,e=st;out=[]
 for a,p in enumerate(b):
  if p=='.' or p.isupper()!=(t==1):continue
  k=p.lower()
  if k=='p':
   d=16*t;z=a+d
   if not z&0x88 and b[z]=='.':
    out += [name(a)+name(z)+v for v in 'qrbn'] if z>>4 in (0,7) else [name(a)+name(z)]
    z+=d
    if a>>4==(1 if t==1 else 6) and b[z]=='.':out.append(name(a)+name(z))
   for z in (a+d-1,a+d+1):
    if not z&0x88 and ((b[z]!='.' and b[z].isupper()!=(t==1) and b[z].lower()!='k') or z==e):out += [name(a)+name(z)+v for v in 'qrbn'] if z>>4 in (0,7) else [name(a)+name(z)]
  else:
   ds=N if k=='n' else B if k=='b' else R if k=='r' else D
   for d in ds:
    z=a+d
    while not z&0x88:
     if b[z]!='.' and (b[z].isupper()==(t==1) or b[z].lower()=='k'):break
     out.append(name(a)+name(z))
     if b[z]!='.' or k in 'nk':break
     z+=d
   if k=='k':
    row=0 if t==1 else 112;rights='KQ' if t==1 else 'kq'
    if a==row+4 and not attacked(b,a,-t):
     for side,flag,empty,through in ((1,rights[0],(row+5,row+6),row+5),(-1,rights[1],(row+1,row+2,row+3),row+3)):
      rook=row+(7 if side==1 else 0);dest=row+(6 if side==1 else 2);c=b.copy();c[a]='.';c[through]=p
      if flag in r and b[rook]==('R' if t==1 else 'r') and all(b[x]=='.' for x in empty) and not attacked(c,through,-t):out.append(name(a)+name(dest))
 legal=[]
 for m in out:
  c,u,rr,ee=play(st,m);king=next(i for i,p in enumerate(c) if p==('K' if t==1 else 'k'))
  if not attacked(c,king,-t):legal.append(m)
 return legal
def evaluate(st):
 b,t,r,e=st;s=0
 for i,p in enumerate(b):
  if p=='.':continue
  x=i&7;y=i>>4;k=p.lower();c=7-abs(3.5-x)-abs(3.5-y)
  v=V[k]+(9*(y if p.isupper() else 7-y)+2*c if k=='p' else 8*c if k in 'nb' else 2*c if k=='r' else c if k=='q' else 0);s+=v if p.isupper() else -v
 return s*t
def ordered(st,ms):
 b,t,r,e=st
 def key(m):
  a,z=sq(m[:2]),sq(m[2:4]);p=b[a];v=V[b[z].lower()] if b[z]!='.' else V['p'] if p.lower()=='p' and z==e else 0
  return (v*10-V[p.lower()] if v else 0)+(V.get(m[4],0)*8 if len(m)>4 else 0)
 return sorted(ms,key=key,reverse=True)
nodes=0
def search(st,d,lo,hi):
 global nodes
 nodes+=1
 if nodes>1200:raise Stop
 if d==0:return evaluate(st)
 ms=ordered(st,gen(st))
 if not ms:
  b,t,r,e=st;k=next(i for i,p in enumerate(b) if p==('K' if t==1 else 'k'))
  return -30000 if attacked(b,k,-t) else 0
 for m in ms:
  v=-search(play(st,m),d-1,-hi,-lo)
  if v>lo:lo=v
  if lo>=hi:break
 return lo
def choose(f,ms):
 if not ms:raise ValueError('empty legal_moves')
 st=parse(f);best=ms[0];lo=-32000
 global nodes
 nodes=0
 for m in ordered(st,ms):
  try:v=-search(play(st,m),2,-32000,-lo)
  except Stop:break
  if v>lo:lo=v;best=m
 return best
while 1:
 g=post('/game',{})
 if g['status']=='done':break
 while g['status']=='your_move':g=post('/move',{'game':g['game'],'move':choose(g['fen'],g['legal_moves'])})
 print('game',g['game'],g['outcome'],g['reason'],file=sys.stderr)
