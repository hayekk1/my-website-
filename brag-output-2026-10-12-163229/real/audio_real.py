import numpy as np, wave
SR=48000; DUR=22.2; N=int(SR*DUR); rng=np.random.default_rng(5)
def mtof(m): return 440*2**((m-69)/12)
def env(n,a,d): t=np.arange(n)/SR; return np.minimum(t/max(a,1e-4),1)*np.exp(-t/d)
def filt(x,lo=None,hi=None,o=2):
    X=np.fft.rfft(x); f=np.fft.rfftfreq(len(x),1/SR); H=np.ones_like(f)
    if hi: H/=1+(f/hi)**(2*o)
    if lo: H/=1+(lo/np.maximum(f,1))**(2*o)
    return np.fft.irfft(X*H,len(x))
def add(b,s,t0,g=1.0):
    i=int(t0*SR); j=min(N,i+len(s))
    if 0<=i<N: b[i:j]+=g*s[:j-i]
mus=np.zeros(N); fx=np.zeros(N); fz=np.zeros(N)
BEAT=60/84
def rhodes(m,dur=1.6):
    n=int(dur*SR); t=np.arange(n)/SR; f=mtof(m)
    s=np.sin(2*np.pi*f*t+0.8*np.sin(2*np.pi*f*t)*np.exp(-t/0.3))*env(n,0.004,0.9)
    s+=0.25*np.sin(2*np.pi*f*7*t)*np.exp(-t/0.03); return s*(1+0.15*np.sin(2*np.pi*4.5*t))
def bassn(m,dur): n=int(dur*SR); t=np.arange(n)/SR; return np.tanh(1.4*np.sin(2*np.pi*mtof(m)*t))*env(n,0.01,0.35)
def kick(): n=int(0.3*SR); t=np.arange(n)/SR; f=48+60*np.exp(-t/0.03); return np.sin(2*np.pi*np.cumsum(f)/SR)*env(n,0.002,0.12)
def brush(d=0.09): n=int(0.3*SR); return filt(rng.standard_normal(n),lo=1500,hi=7000)*env(n,0.01,d)
def hat(): n=int(0.08*SR); return filt(rng.standard_normal(n),lo=6000)*env(n,0.001,0.02)
CH=[[53,57,60,64],[52,55,59,62],[50,53,57,60],[48,52,55,59]]; ROOT=[41,40,38,36]
def groove(t0,t1):
    b=0
    while t0+b*BEAT<t1:
        tt=t0+b*BEAT; bar=b//4; ch=CH[bar%4]
        if b%4==0:
            for i,m in enumerate(ch): add(mus,rhodes(m+12,4*BEAT+0.3),tt+i*0.018,0.05)
            add(mus,bassn(ROOT[bar%4],BEAT*1.5),tt,0.20)
        if b%4==2: add(mus,bassn(ROOT[bar%4]+7,BEAT),tt,0.16)
        if b%2==0: add(mus,kick(),tt,0.30)
        else: add(mus,brush(),tt,0.10)
        add(mus,hat(),tt+BEAT*0.66,0.03); add(mus,hat(),tt,0.025); b+=1
    # cut tails at t1
    i=int(t1*SR); mus[i:i+int(0.05*SR)]*=np.linspace(1,0,min(int(0.05*SR),N-i)); 
def scratch(t0,dur=0.35,g=0.18):
    n=int(dur*SR); t=np.arange(n)/SR; sp=np.sin(2*np.pi*t/dur*1.5)
    ph=np.cumsum(300+900*np.abs(sp))/SR; add(fx,filt(rng.standard_normal(n),lo=300,hi=3000)*np.sin(2*np.pi*ph)*np.hanning(n),t0,g)
def bell(m,dur=1.2,d=0.4):
    n=int(dur*SR); t=np.arange(n)/SR; f=mtof(m); return (np.sin(2*np.pi*f*t)+0.3*np.sin(2*np.pi*2.76*f*t)*np.exp(-t/0.1))*env(n,0.002,d)
def clink(m):
    n=int(0.5*SR); t=np.arange(n)/SR; f=mtof(m); return sum(a*np.sin(2*np.pi*f*r*t)*np.exp(-t/d) for r,a,d in ((1,1,.12),(2.4,.6,.06),(4.1,.4,.04)))
def whoosh(d,rev=False):
    n=int(d*SR); t=np.arange(n)/SR; e=(t/d)**2.5 if rev else np.sin(np.pi*t/d)**2; return filt(rng.standard_normal(n),lo=300,hi=5000)*e
def thud(f0=55):
    n=int(0.5*SR); t=np.arange(n)/SR; f=f0+110*np.exp(-t/0.03)
    return np.tanh(2*np.sin(2*np.pi*np.cumsum(f)/SR)*env(n,0.001,0.12))+0.5*filt(rng.standard_normal(n),hi=1500)*env(n,0.001,0.04)
def pad(notes,dur):
    n=int(dur*SR); t=np.arange(n)/SR; s=sum(np.sin(2*np.pi*mtof(m)*t+0.3*np.sin(2*np.pi*0.3*t+m)) for m in notes)/len(notes)
    return s*np.minimum(1,np.minimum(t/0.6,(dur-t)/0.4))
t=np.arange(N)/SR
# hook freeze
scratch(0.02,0.4,0.24); add(fz,pad([57,64,67,72],2.5),0.1,0.16); add(fz,pad([81,84,88],2.5)*.5,0.1,0.05)
n=int(0.7*SR); tt=np.arange(n)/SR; rw=filt(rng.standard_normal(n),lo=500,hi=6000)*(0.5+0.5*np.sin(2*np.pi*(8+30*tt)*tt))
rw+=0.4*np.sin(2*np.pi*np.cumsum(400+1600*tt/0.7)/SR)*np.sin(2*np.pi*14*tt); add(fx,rw*np.hanning(n),2.6,0.13)
# cafe
add(fx,bell(84,1.2,.35),3.32,0.07); add(fx,bell(88,1.2,.35),3.45,0.06)
groove(3.3,9.78)
for k,x in enumerate([3.5,3.62,3.71]): add(fx,clink([96,100,98][k]),x,0.05)
n=int(1.25*SR); tt=np.arange(n)/SR; add(fx,filt(rng.standard_normal(n),lo=200,hi=1400)*(0.6+0.4*np.sin(2*np.pi*11*tt))*np.minimum(1,np.minimum(tt/0.05,(1.25-tt)/0.1)),5.9,0.10)
n=int(0.85*SR); tt=np.arange(n)/SR; add(fx,filt(rng.standard_normal(n),lo=1500,hi=5000)*np.minimum(1,np.minimum(tt/0.05,(0.85-tt)/0.1)),7.2,0.06)
for x in (7.5,7.8,8.1): add(fx,clink(91)*0.5,x,0.04)
n=int(0.25*SR); tt=np.arange(n)/SR; add(fx,np.sin(2*np.pi*(300-200*tt)*tt)*env(n,0.002,0.05),8.25,0.10)
# bump
add(fx,whoosh(0.35),9.5,0.10); add(fx,thud(),9.8,0.5); scratch(9.85,0.45,0.25)
# freeze description
add(fz,pad([60,64,67,71,74],6.8),10.3,0.11); add(fz,pad([84,88,91],6.8)*0.5,10.3,0.05)
for k in range(7):
    n=int(0.05*SR); add(fx,filt(rng.standard_normal(n),lo=2500)*env(n,0.001,0.008),10.5+k*0.9,0.06)
for x,m in zip([10.5,11.0,12.2,13.4,14.6,15.8],[72,76,79,83,84,88]): add(fx,bell(m,1.0,0.25),x,0.05)
add(fx,whoosh(0.45,True),16.55,0.13)
# land
add(fx,whoosh(0.5),17.1,0.08); add(fx,thud(90)*0.8,17.95,0.35)
for k,x in enumerate([17.97,18.03,18.1,18.2]): add(fx,clink([98,95,100,93][k]),x,0.06)
groove(18.1,22.2)
add(fx,bell(84,1.0,.3),18.2,0.06)
for i,m in enumerate([53,57,60,64,67]): add(mus,rhodes(m+12,2.6),19.6+i*0.03,0.06)
for i,m in enumerate([77,81,84]): add(fx,bell(m,1.6,0.6),19.8+i*0.1,0.035)
# ambience: cafe murmur + vinyl crackle in freezes
mur=filt(rng.standard_normal(N),lo=250,hi=1200)*(0.6+0.4*np.sin(2*np.pi*0.7*t)*np.sin(2*np.pi*0.23*t))
mask=((t>=3.3)&(t<9.8))|((t>=17.0)); mk=np.convolve(mask.astype(float),np.ones(4800)/4800,'same')
cr=np.zeros(N)
for _ in range(220): add(cr,filt(rng.standard_normal(200),lo=2000),rng.uniform(0,DUR),rng.uniform(.02,.08))
crm=np.convolve(((t<2.6)|((t>=10.3)&(t<17.0))).astype(float),np.ones(4800)/4800,'same')
irn=int(1.4*SR); ir=filt(rng.standard_normal(irn),hi=4500)*np.exp(-np.arange(irn)/SR/0.35); ir/=np.sqrt((ir**2).sum())
def verb(x,m): L=N+irn; return x+m*np.fft.irfft(np.fft.rfft(x,L)*np.fft.rfft(ir,L),L)[:N]
mix=verb(mus,0.2)+verb(fx,0.25)+verb(fz,0.5)+mur*mk*0.02+cr*crm*0.6
mix*=np.clip((DUR-t)/0.6,0,1); mix=np.tanh(mix*1.4); mix/=np.abs(mix).max()*1.12
R=np.concatenate([np.zeros(int(0.009*SR)),mix])[:N]
with wave.open('audio.wav','wb') as w: w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR);w.writeframes((np.stack([mix,0.5*mix+0.5*R],1)*32767).astype(np.int16).tobytes())
print(' | '.join(f'{s}:{20*np.log10(np.sqrt((mix[s*SR:(s+1)*SR]**2).mean())+1e-9):.0f}' for s in range(22)))
