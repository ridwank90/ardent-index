import json,os,urllib.request as u
U=os.environ['MAKEFUN_ENV_URL']
V={'p':100,'n':320,'b':330,'r':500,'q':900,'k':0}
B=(15,17,-15,-17);R=(1,-1,16,-16);N=(14,18,31,33,-14,-18,-31,-33);D=B+R
class X(Exception):pass
def H(p,d):
 q=u.Request(U+p,data=json.dumps(d).encode(),headers={'content-type':'application/json'})
 return json.load(u.urlopen(q,timeout=9))
def sq(s):return ord(s[0])-97+(ord(s[1])-49)*16
def nm(i):return 'abcdefgh'[i&7]+str((i>>4)+1)
def P(f):
 q=f.split();b=['.']*128
 for y,row in enumerate(q[0].split('/')):
  x=0
  for c in row:
   if c.isdigit():x+=int(c)
   else:b[(7-y)*16+x]=c;x+=1
 return b,1 if q[1]=='w' else -1,q[2],-1 if q[3]=='-' else sq(q[3])
def A(b,s,t):
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
def M(st,m):
 b,t,r,e=st;a,z=sq(m[:2]),sq(m[2:4]);p=b[a];cap=b[z];c=b.copy();c[a]='.'
 if p.lower()=='p' and z==e and cap=='.':c[z-16*t]='.'
 if p.lower()=='k' and abs(z-a)==2:
  h=a+(3 if z>a else -4);c[a+(1 if z>a else -1)]=c[h];c[h]='.'
 c[z]=m[4].upper() if len(m)>4 and t==1 else m[4].lower() if len(m)>4 else p
 if p.lower()=='k':r=r.replace('K','').replace('Q','') if t==1 else r.replace('k','').replace('q','')
 rr={0:'Q',7:'K',112:'q',119:'k'}
 if p.lower()=='r' and a in rr:r=r.replace(rr[a],'')
 if cap.lower()=='r' and z in rr:r=r.replace(rr[z],'')
 return c,-t,r,a+8*t if p.lower()=='p' and abs(z-a)==32 else -1
def G(st):
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
    if not z&0x88 and ((b[z]!='.' and b[z].isupper()!=(t==1) and b[z].lower()!='k') or z==e and b[z]=='.' and b[z-16*t]==('p' if t==1 else 'P')):o += [nm(a)+nm(z)+v for v in 'qrbn'] if z>>4 in (0,7) else [nm(a)+nm(z)]
  else:
   ds=N if k=='n' else B if k=='b' else R if k=='r' else D
   for d in ds:
    z=a+d
    while not z&0x88:
     if b[z]!='.' and (b[z].isupper()==(t==1) or b[z].lower()=='k'):break
     o.append(nm(a)+nm(z))
     if b[z]!='.' or k in 'nk':break
     z+=d
   if k=='k':
    row=0 if t==1 else 112;rights='KQ' if t==1 else 'kq'
    if a==row+4
