import numpy as np, wave
SR=48000; DUR=22.0; N=int(SR*DUR); rng=np.random.default_rng(11)
def mtof(m): return 440*2**((m-69)/12)
def env(n,a,d): t=np.arange(n)/SR; return np.minimum(t/max(a,1e-4),1)*np.exp(-t/d)
def filt(x,lo=None,hi=None,o=2):
    X=np.fft.rfft(x); f=np.fft.rfftfreq(len(x),1/SR); H=np.ones_like(f)
    if hi: H/=1+(f/hi)**(2*o)
    if lo: H/=1+(lo/np.maximum(f,1))**(2*o)
    return np.fft.irfft(X*H,len(x))
def add(buf,s,t0,g=1.0):
    i=int(t0*SR); j=min(N,i+len(s))
    if 0<=i<N: buf[i:j]+=g*s[:j-i]
mus=np.zeros(N); drm=np.zeros(N); fx=np.zeros(N); kenv=np.zeros(N)
BEAT=60/128; BAR=4*BEAT
def saw_pad(notes,dur,cut=1100,att=0.05,rel=0.3):
    n=int(dur*SR); t=np.arange(n)/SR; s=np.zeros(n)
    for m in notes:
        for d in (-0.1,0,0.1): f=mtof(m+d); s+=2*((t*f+rng.random())%1)-1
    s=filt(s/len(notes)/3,hi=cut); e=np.minimum(t/att,1)*np.clip((dur-t)/rel,0,1); return s*e
def kick(big=False):
    n=int(0.4*SR); t=np.arange(n)/SR; f=42+(140 if big else 90)*np.exp(-t/0.035)
    s=np.sin(2*np.pi*np.cumsum(f)/SR)*env(n,0.001,0.16 if big else 0.11); return np.tanh(s*1.5)
def clap():
    n=int(0.25*SR); s=filt(rng.standard_normal(n),lo=900,hi=3500); t=np.arange(n)/SR
    e=sum((t>=o)*np.exp(-np.maximum(t-o,0)/0.045) for o in (0,0.011,0.022)); return s*e/3
def hat(d=0.025): n=int(0.1*SR); return filt(rng.standard_normal(n),lo=7000)*env(n,0.001,d)
def boom():
    n=int(2.0*SR); t=np.arange(n)/SR; f=30+120*np.exp(-t/0.08)
    s=np.sin(2*np.pi*np.cumsum(f)/SR)*env(n,0.001,0.6)
    nz=filt(rng.standard_normal(n),hi=1800)*env(n,0.001,0.12); return np.tanh(1.4*s)+0.5*nz
def bell(m,dur=0.8,d=0.25):
    n=int(dur*SR); t=np.arange(n)/SR; f=mtof(m)
    return (np.sin(2*np.pi*f*t)+0.3*np.sin(2*np.pi*2*f*t)*np.exp(-t/0.08)+0.1*np.sin(2*np.pi*3*f*t)*np.exp(-t/0.04))*env(n,0.002,d)
def pluck(m,d=0.14):
    n=int(0.5*SR); t=np.arange(n)/SR; f=mtof(m)
    return (filt(2*((t*f)%1)-1,hi=2500)*0.5+np.sin(2*np.pi*f*t))*env(n,0.002,d)
def tick(): n=int(0.03*SR); return filt(rng.standard_normal(n),lo=1500,hi=6000)*env(n,0.0005,0.006)
def thud(): 
    n=int(0.5*SR); t=np.arange(n)/SR; f=60+120*np.exp(-t/0.03)
    return np.tanh(2*np.sin(2*np.pi*np.cumsum(f)/SR)*env(n,0.001,0.12))+0.4*filt(rng.standard_normal(n),hi=1200)*env(n,0.001,0.04)
def whoosh(d=0.35):
    n=int(d*SR); t=np.arange(n)/SR; return filt(rng.standard_normal(n),lo=400,hi=4000)*np.sin(np.pi*t/d)**2
def clang(m):
    n=int(0.9*SR); t=np.arange(n)/SR; f=mtof(m)
    return sum(a*np.sin(2*np.pi*f*r*t)*np.exp(-t/dd) for r,a,dd in ((1,1,.3),(2.76,.6,.15),(5.4,.4,.08),(8.9,.25,.05)))*0.5
def put_kick(tt,g=0.6,big=False):
    add(drm,kick(big),tt,g); n=int(0.35*SR); add(kenv,np.exp(-np.arange(n)/SR/0.09),tt,1.0)
# --- intro tension (B minor) 0.36 -> 5.45
T1=0.36
for b in range(int((5.45-T1)/BEAT)+1):
    tt=T1+b*BEAT
    if tt>=5.45: break
    put_kick(tt,0.55)
    add(drm,hat(),tt+BEAT/2,0.07)
    for h in (0.25,0.75): 
        if tt+h*BEAT<5.45: add(drm,hat(0.012),tt+h*BEAT,0.03)
    if b%2==1: add(drm,clap(),tt,0.18)
    for e in range(2):  # pulsing bass 8ths
        n=int(BEAT/2*SR*0.9); t=np.arange(n)/SR; f=mtof(35)
        add(mus,np.tanh(2*np.sin(2*np.pi*f*t))*env(n,0.003,0.12),tt+e*BEAT/2,0.30)
add(mus,saw_pad([47,54,59,62],5.45-T1,cut=700,att=0.4,rel=0.05),T1,0.13)
# riser into drop
n=int(0.6*SR); t=np.arange(n)/SR; r=filt(rng.standard_normal(n),lo=300,hi=6000)*(t/0.6)**2.5
f=200*2**(t/0.6*2.5); r+=0.25*np.sin(2*np.pi*np.cumsum(f)/SR)*(t/0.6)**2
add(fx,r,4.85,0.14)
# --- drop (D major) 5.6 -> 19.4
T2=5.6; prog=[[50,57,62,66,69],[47,54,59,62,66],[43,55,59,62,67],[45,52,57,61,64]]
nb=int((19.4-T2)/BAR+0.999)
for bi in range(nb):
    s0=T2+bi*BAR; ch=prog[bi%4]; d=min(BAR,19.4-s0)
    if d<=0: break
    add(mus,saw_pad(ch,d+0.05,cut=1500,att=0.01,rel=0.05),s0,0.16)
    for b in range(4):
        tt=s0+b*BEAT
        if tt>=19.4: break
        put_kick(tt,0.62)
        if b%2==1: add(drm,clap(),tt,0.24)
        add(drm,hat(),tt+BEAT/2,0.09)
        add(drm,hat(0.01),tt+BEAT*0.25,0.035);add(drm,hat(0.01),tt+BEAT*0.75,0.035)
        for e in range(2):
            n=int(BEAT/2*SR*0.9); t=np.arange(n)/SR; f=mtof(ch[0]-12)
            add(mus,np.tanh(2.2*np.sin(2*np.pi*f*t))*env(n,0.003,0.11),tt+e*BEAT/2,0.30)
    pat=[0,2,1,3,2,4,3,1]; tones=[m+24 for m in ch]
    for i in range(8):
        tt=s0+i*BEAT/2
        if tt<19.4: add(mus,pluck(tones[pat[i]%5]),tt,0.06)
add(drm,boom(),5.6,0.55); put_kick(5.6,0.0)
# outro
add(fx,whoosh(0.45),19.4,0.12)
add(drm,boom(),19.85,0.40)
add(mus,saw_pad([50,57,62,66,69,74],2.15,cut=1800,att=0.01,rel=1.4),19.85,0.18)
n=int(2.2*SR); t=np.arange(n)/SR; add(mus,np.sin(2*np.pi*mtof(38)*t)*env(n,0.01,0.8),19.85,0.35)
for i,m in enumerate([74,78,81,86]): add(fx,bell(m,1.6,0.6),19.85+i*0.06,0.07)
# --- SFX
n=int(0.35*SR); t=np.arange(n)/SR; f=mtof(95)*np.exp(-t/0.25)
add(fx,np.sin(2*np.pi*np.cumsum(f)/SR)*np.minimum(t/0.02,1)*np.clip((0.36-t)/0.05,0,1),0.0,0.10)  # falling whistle
add(drm,boom(),0.36,0.6)
for x in (1.5,3.1,7.8,10.0,12.8,15.2,16.8): add(fx,whoosh(0.25),x-0.12,0.07)
for x in (1.55,1.7,1.85,2.0): add(drm,thud(),x,0.30)
add(drm,boom(),2.25,0.35); add(mus,saw_pad([47,54,59,62,66],0.5,cut=2500,rel=0.3),2.25,0.12)
for x,m in [(3.3,71),(3.85,66),(4.4,71),(4.85,62)]: add(fx,bell(m,0.4,0.07),x,0.10)   # chat pops (B minor)
add(fx,tick(),8.05,0.1)
tt=8.15
while tt<8.95: add(fx,tick(),tt,0.03*rng.uniform(.6,1)); tt+=rng.uniform(0.03,0.05)
add(fx,tick(),9.3,0.14); add(drm,thud(),9.3,0.18)
for i in range(10): add(fx,bell(86+[0,2,4,7,9][i%5],0.4,0.06),9.32+i*0.035,0.035)
for x,m in [(10.15,74),(10.45,78),(10.75,81)]: add(fx,bell(m,0.6,0.12),x,0.10)
add(fx,tick(),11.6,0.12)
add(drm,thud(),11.8,0.5); add(drm,boom(),11.8,0.25)
for x,m in [(12.95,74),(13.35,76),(13.85,78),(14.25,81)]: add(fx,bell(m,0.6,0.15),x,0.09)
for x in (13.42,13.62): add(fx,clang(78),x,0.10)
for i,m in enumerate([86,90,93,98]): add(fx,bell(m,0.6,0.15),13.95+i*0.05,0.04)
for i,m in enumerate([74,76,78,81,86]): add(fx,bell(m,0.5,0.1),15.35+i*0.15,0.08); add(drm,thud(),15.35+i*0.15,0.08)
add(fx,bell(86,0.9,0.3),16.1,0.08)
for x,m in [(17.0,69),(17.75,74),(18.4,66)]: add(fx,bell(m,0.4,0.07),x,0.10)
# sidechain music
duck=1-0.55*np.clip(kenv,0,1); mus*=duck
# reverb
irn=int(1.6*SR); ir=filt(rng.standard_normal(irn),hi=5000)*np.exp(-np.arange(irn)/SR/0.4); ir/=np.sqrt((ir**2).sum())
def verb(x,m): L=N+irn; return x+m*np.fft.irfft(np.fft.rfft(x,L)*np.fft.rfft(ir,L),L)[:N]
mix=verb(mus,0.22)+verb(fx,0.3)+verb(drm,0.06)
# silence gap before drop (keep nothing from 5.45-5.6 except tails faded)
t=np.arange(N)/SR; g=np.ones(N); g[(t>=5.45)&(t<5.6)]=0.05; mix*=g
mix*=np.clip((DUR-t)/0.5,0,1)
mix=np.tanh(mix*1.3); mix/=np.abs(mix).max()*1.1
R=np.concatenate([np.zeros(int(0.007*SR)),mix])[:N]
st=(np.stack([mix,0.5*mix+0.5*R],1)*32767).astype(np.int16)
with wave.open('music2.wav','wb') as w: w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR);w.writeframes(st.tobytes())
for s in range(22):
    seg=mix[s*SR:(s+1)*SR]; print(s,round(20*np.log10(np.sqrt((seg**2).mean())+1e-9),1),end=' | ')
