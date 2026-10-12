import numpy as np, wave
SR=48000; DUR=23.2; N=int(SR*DUR); rng=np.random.default_rng(5)
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
mus=np.zeros(N); fx=np.zeros(N); amb=np.zeros(N)
BEAT=60/84
def rhodes(m,dur=1.6):
    n=int(dur*SR); t=np.arange(n)/SR; f=mtof(m)
    s=np.sin(2*np.pi*f*t+0.8*np.sin(2*np.pi*f*t)*np.exp(-t/0.3))*env(n,0.004,0.9)
    s+=0.25*np.sin(2*np.pi*f*7*t)*np.exp(-t/0.03); return s*(1+0.15*np.sin(2*np.pi*4.5*t))
def bassn(m,dur): n=int(dur*SR); t=np.arange(n)/SR; return np.tanh(1.4*np.sin(2*np.pi*mtof(m)*t))*env(n,0.01,0.35)
def kick(): n=int(0.3*SR); t=np.arange(n)/SR; f=48+60*np.exp(-t/0.03); return np.sin(2*np.pi*np.cumsum(f)/SR)*env(n,0.002,0.12)
def brush(d=0.09): n=int(0.3*SR); return filt(rng.standard_normal(n),lo=1500,hi=7000)*env(n,0.01,d)
def hat(): n=int(0.08*SR); return filt(rng.standard_normal(n),lo=6000)*env(n,0.001,0.02)
CH=[[53,57,60,64],[52,55,59,62],[50,53,57,60],[48,52,55,59]]  # Fmaj7 Em7 Dm7 Cmaj7
ROOT=[41,40,38,36]
def groove(t0,t1):
    b=0
    while True:
        tt=t0+b*BEAT
        if tt>=t1: break
        bar=b//4; ch=CH[bar%4]
        if b%4==0:
            for i,m in enumerate(ch): add(mus,rhodes(m+12,4*BEAT+0.3),tt+i*0.018,0.05)
            add(mus,bassn(ROOT[bar%4],BEAT*1.5),tt,0.20)
        if b%4==2: add(mus,bassn(ROOT[bar%4]+7,BEAT),tt,0.16)
        if b%4==3: add(mus,bassn(ROOT[bar%4]+5,BEAT*0.6),tt+BEAT*0.66,0.12)
        if b%2==0: add(mus,kick(),tt,0.30)
        else: add(mus,brush(),tt,0.10)
        add(mus,hat(),tt+BEAT*0.66,0.03); add(mus,hat(),tt,0.025)
        b+=1
def scratch(t0,dur=0.35,g=0.18):
    n=int(dur*SR); t=np.arange(n)/SR; sp=np.sin(2*np.pi*t/dur*1.5)
    ph=np.cumsum(300+900*np.abs(sp))/SR; s=filt(rng.standard_normal(n),lo=300,hi=3000)*np.sin(2*np.pi*ph)*np.hanning(n)
    add(fx,s,t0,g)
def bell(m,dur=1.2,d=0.4):
    n=int(dur*SR); t=np.arange(n)/SR; f=mtof(m)
    return (np.sin(2*np.pi*f*t)+0.3*np.sin(2*np.pi*2.76*f*t)*np.exp(-t/0.1))*env(n,0.002,d)
def clink(m):
    n=int(0.5*SR); t=np.arange(n)/SR; f=mtof(m)
    return sum(a*np.sin(2*np.pi*f*r*t)*np.exp(-t/d) for r,a,d in ((1,1,.12),(2.4,.6,.06),(4.1,.4,.04)))
def step(): n=int(0.15*SR); return filt(rng.standard_normal(n),hi=900)*env(n,0.002,0.03)
def whoosh(d,rev=False):
    n=int(d*SR); t=np.arange(n)/SR; e=(t/d)**2.5 if rev else np.sin(np.pi*t/d)**2
    return filt(rng.standard_normal(n),lo=300,hi=5000)*e
def thud():
    n=int(0.5*SR); t=np.arange(n)/SR; f=55+110*np.exp(-t/0.03)
    return np.tanh(2*np.sin(2*np.pi*np.cumsum(f)/SR)*env(n,0.001,0.12))+0.5*filt(rng.standard_normal(n),hi=1500)*env(n,0.001,0.04)
# --- 0-2.4 freeze hook
scratch(0.02,0.4,0.22)
add(fx,bell(72,2.4,1.2),0.3,0.03)
# vinyl crackle in freezes
cr=np.zeros(N)
for _ in range(220): add(cr,filt(rng.standard_normal(200),lo=2000),rng.uniform(0,DUR),rng.uniform(.02,.08))
# rewind 2.4-3.3
n=int(0.9*SR); t=np.arange(n)/SR
rw=filt(rng.standard_normal(n),lo=500,hi=6000)*(0.5+0.5*np.sin(2*np.pi*(8+30*t)*t))
ph=np.cumsum(400+1600*t/0.9)/SR; rw+=0.4*np.sin(2*np.pi*ph)*np.sin(2*np.pi*14*t)
add(fx,rw*np.hanning(n),2.4,0.12)
# --- cafe 3.3-11.2
add(fx,bell(84,1.2,.35),3.32,0.07); add(fx,bell(88,1.2,.35),3.45,0.06)
groove(3.3,11.2)
for k in range(8): add(fx,step(),3.45+k*0.17*2,0.10)
for k,tt in enumerate([6.84,7.02,7.2,7.33]): add(fx,clink([96,100,98,103][k]),tt,0.08)
# milk pour
n=int(0.95*SR); t=np.arange(n)/SR; mp=filt(rng.standard_normal(n),lo=200,hi=1400)*(0.6+0.4*np.sin(2*np.pi*11*t))*np.minimum(1,np.minimum(t/0.05,(0.95-t)/0.1))
add(fx,mp,7.48,0.09)
for k in range(6): add(fx,np.sin(2*np.pi*mtof(62+k)*np.arange(int(.08*SR))/SR)*env(int(.08*SR),.003,.02),7.6+k*0.13,0.04)
# espresso
n=int(0.7*SR); t=np.arange(n)/SR; ep=filt(rng.standard_normal(n),lo=1500,hi=5000)*np.minimum(1,np.minimum(t/0.05,(0.7-t)/0.1))
add(fx,ep,8.52,0.05)
for tt in (9.0,9.25): add(fx,clink(91)*0.5,tt,0.04)
n=int(0.25*SR); t=np.arange(n)/SR; add(fx,np.sin(2*np.pi*(300-200*t)*t)*env(n,0.002,0.05),9.62,0.10)  # straw plop
for k in range(5): add(fx,step(),10.35+k*0.18,0.08)
for k in range(6): add(fx,step(),10.4+k*0.13,0.07)
# --- bump
add(fx,thud(),11.2,0.45); scratch(11.25,0.45,0.25)
# freeze ambience 11.6-18
fz=np.zeros(N)
def pad(notes,dur):
    n=int(dur*SR); t=np.arange(n)/SR; s=sum(np.sin(2*np.pi*mtof(m)*t+0.3*np.sin(2*np.pi*0.3*t+m)) for m in notes)/len(notes)
    return s*np.minimum(1,np.minimum(t/1.0,(dur-t)/0.6))
add(fz,pad([60,64,67,71,74],6.4),11.6,0.10)
add(fz,pad([57,64,67,72],2.4),0.1,0.16); add(fz,pad([81,84,88],2.4)*0.5,0.1,0.06)
add(fz,pad([84,88,91],6.4)*0.5,11.6,0.05)
for k in range(6): n=int(0.05*SR); add(fx,filt(rng.standard_normal(n),lo=2500)*env(n,0.001,0.008),12.0+k*1.0,0.06)  # clock tick
for tt,m in zip([12.0,12.9,13.7,14.5,15.3,16.1],[72,76,79,83,84,88]): add(fx,bell(m,1.0,0.25),tt,0.045)
add(fx,whoosh(0.45,True),17.55,0.12)
# --- resume 18
groove(18.0,20.6)
add(fx,whoosh(0.3),18.4,0.08)
add(fx,bell(84,1.0,.3),18.92,0.07); add(fx,bell(91,1.0,.3),19.0,0.06)
for k in range(6): add(fx,step(),19.25+k*0.17,0.07)
add(fx,thud()*0.4,19.1,0.15)
# end
for i,m in enumerate([53,57,60,64,67]): add(mus,rhodes(m+12,2.6),20.6+i*0.03,0.06)
add(mus,bassn(41,2.6),20.6,0.2)
for i,m in enumerate([77,81,84]): add(fx,bell(m,1.6,0.6),20.8+i*0.1,0.035)
# ambience murmur during cafe scenes
n=N; t=np.arange(n)/SR; mur=filt(rng.standard_normal(n),lo=250,hi=1200)*(0.6+0.4*np.sin(2*np.pi*0.7*t)*np.sin(2*np.pi*0.23*t))
mask=((t>=3.3)&(t<6.6))|((t>=10.0)&(t<11.6))|((t>=18.0)&(t<20.6))
mk=np.convolve(mask.astype(float),np.ones(4800)/4800,'same'); amb+=mur*mk*0.02
crm=((t<2.4)|((t>=11.6)&(t<18.0))).astype(float); crm=np.convolve(crm,np.ones(4800)/4800,'same')
# reverb
irn=int(1.4*SR); ir=filt(rng.standard_normal(irn),hi=4500)*np.exp(-np.arange(irn)/SR/0.35); ir/=np.sqrt((ir**2).sum())
def verb(x,m): L=N+irn; return x+m*np.fft.irfft(np.fft.rfft(x,L)*np.fft.rfft(ir,L),L)[:N]
mix=verb(mus,0.2)+verb(fx,0.25)+verb(fz,0.5)+amb+cr*crm*0.6
mix*=np.clip((DUR-t)/0.6,0,1)
mix=np.tanh(mix*1.4); mix/=np.abs(mix).max()*1.12
R=np.concatenate([np.zeros(int(0.009*SR)),mix])[:N]
st=(np.stack([mix,0.5*mix+0.5*R],1)*32767).astype(np.int16)
with wave.open('music.wav','wb') as w: w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR);w.writeframes(st.tobytes())
for s in range(23):
    seg=mix[s*SR:(s+1)*SR]; print(s,round(20*np.log10(np.sqrt((seg**2).mean())+1e-9),1),end=' | ')
