import json,os,sys,urllib.request,urllib.error
U=os.environ.get('MAKEFUN_ENV_URL')
if not U: sys.exit('MAKEFUN_ENV_URL is not set')
V={'p':100,'n':320,'b':330,'r':500,'q':900,'k':0}
def post(p,d):
 r=urllib.request.Request(U+p,data=json.dumps(d).encode(),headers={'content-type':'application/json'})
 try:
  with urllib.request.urlopen(r,timeout=9) as x:return json.load(x)
 except urllib.error.HTTPError as e:sys.exit(str(e.code)+': '+e.read().decode())
def board(f):
 b={}
 for y,row in enumerate(f.split()[0].split('/')):
  x=0
  for c in row:
   if c.isdigit():x+=int(c)
   else:b["abcdefgh"[x]+str(8-y)]=c;x+=1
 return b
def sq(s):return ord(s[0])-97,int(s[1])-1
def choose(f,ms):
 b=board(f)
 def rank(m):
  a,z=m[:2],m[2:4];p=b[a];t=b.get(z);v=p.lower();x,y=sq(z);cx,cy=abs(3.5-x),abs(3.5-y)
  center=int(14-2*(cx+cy));advance=y if p.isupper() else 7-y
  positional=0
  if v in 'nb':positional=center*5
  elif v=='p':positional=advance*7+center*2
  elif v=='q':positional=center
  elif v=='r':positional=advance*2
  if v=='k' and a[0]=='e' and z[0] in 'cg':positional+=45
  taken=V[t.lower()] if t else (100 if v=='p' and a[0]!=z[0] else 0)
  promo=V.get(m[4],0)*2 if len(m)>4 else 0
  return (-(taken*10+promo+positional),V[v],m)
 return min(ms,key=rank)
while 1:
 g=post('/game',{})
 if g['status']=='done':break
 while g['status']=='your_move':g=post('/move',{'game':g['game'],'move':choose(g['fen'],g['legal_moves'])})
 print('game',g['game'],g['outcome'],g['reason'],file=sys.stderr)
