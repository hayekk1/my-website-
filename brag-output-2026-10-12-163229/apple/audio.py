import numpy as np, wave
SR=48000; DUR=14.5; N=int(SR*DUR); rng=np.random.default_rng(21)
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
mus=np.zeros(N); fx=np.zeros(N)
BPM=130; B=60/BPM; T0=1.0; T1=11.6
def pad(notes,dur,att=0.3):
    n=int(dur*SR); t=np.arange(n)/SR; s=np.zeros(n)
    for m in notes:
        for d in (-0.07,0.07): s+=np.sin(2*np.pi*mtof(m+d)*t)+0.3*np.sin(2*np.pi*2*mtof(m+d)*t)
    return s/len(notes)*np.minimum(1,np.minimum(t/att,(dur-t)/0.2))
def pluck(m,d=0.25): n=int(0.8*SR); t=np.arange(n)/SR; f=mtof(m); return (np.sin(2*np.pi*f*t)+0.4*np.sin(2*np.pi*3*f*t)*np.exp(-t/0.05))*env(n,0.002,d)
def kick(): n=int(0.3*SR); t=np.arange(n)/SR; f=45+70*np.exp(-t/0.03); return np.sin(2*np.pi*np.cumsum(f)/SR)*env(n,0.002,0.13)
def snap(): n=int(0.2*SR); return filt(rng.standard_normal(n),lo=1200,hi=6000)*env(n,0.001,0.05)
def hat(): n=int(0.06*SR); return filt(rng.standard_normal(n),lo=7000)*env(n,0.001,0.015)
CH=[[57,60,64,67],[53,57,60,64],[48,52,55,60],[55,59,62,67]]  # Am7 Fmaj7 C G
BAR=4*B; nb=int((T1-T0)/BAR)+1
for bi in range(nb):
    s0=T0+bi*BAR; ch=CH[bi%4]; d=min(BAR,T1-s0)
    if d<=0: break
    add(mus,pad(ch,d+0.02),s0,0.07)
    add(mus,np.tanh(1.5*np.sin(2*np.pi*mtof(ch[0]-24)*np.arange(int(d*SR))/SR))*np.minimum(1,(d-np.arange(int(d*SR))/SR)/0.05),s0,0.12)
    for k in range(8):
        tt=s0+k*B/2
        if tt>=T1: break
        add(mus,pluck(ch[[0,2,1,3,2,0,3,1][k]]+12),tt,0.045)
    if bi>=1:
        for k in range(4):
            tt=s0+k*B
            if tt>=T1: break
            add(mus,kick(),tt,0.35 if k%2==0 else 0.18)
            if k%2==1: add(mus,snap(),tt,0.12)
            add(mus,hat(),tt+B/2,0.05)
# swell into the intro
n=int(0.8*SR); t=np.arange(n)/SR; add(mus,filt(rng.standard_normal(n),lo=400,hi=5000)*(t/0.8)**2,0.25,0.04)
i=int(T1*SR); mus[i:]=0
# key click
n=int(0.06*SR); add(fx,filt(rng.standard_normal(n),lo=1500,hi=7000)*env(n,0.0005,0.006),0.62,0.25); add(fx,filt(rng.standard_normal(n),lo=600,hi=3000)*env(n,0.0005,0.01),0.70,0.15)
def whoosh(d): n=int(d*SR); t=np.arange(n)/SR; return filt(rng.standard_normal(n),lo=300,hi=5000)*np.sin(np.pi*t/d)**2
for x in (3.7,8.55,10.35): add(fx,whoosh(0.45),x,0.05)
def clink(m):
    n=int(0.5*SR); t=np.arange(n)/SR; f=mtof(m); return sum(a*np.sin(2*np.pi*f*r*t)*np.exp(-t/d) for r,a,d in ((1,1,.12),(2.4,.6,.06),(4.1,.4,.04)))
for k,x in enumerate([6.75,6.88,7.01,7.14]): add(fx,clink([93,96,100,98][k]),x,0.05)
n=int(0.4*SR); t=np.arange(n)/SR; f=60+90*np.exp(-t/0.03); add(fx,np.tanh(2*np.sin(2*np.pi*np.cumsum(f)/SR)*env(n,0.001,0.08)),10.95,0.25)
for k,x in enumerate([10.97,11.03,11.1]): add(fx,clink([96,91,98][k]),x,0.04)
def chime(m,d=1.5): n=int(2.5*SR); t=np.arange(n)/SR; f=mtof(m); return np.sin(2*np.pi*f*t)*env(n,0.004,d)+0.3*np.sin(2*np.pi*2*f*t)*env(n,0.004,d/3)
for i,m in enumerate([72,76,79]): add(fx,chime(m),11.9+i*0.04,0.05)
# phone-mic character: room verb, band-limit, room tone
irn=int(0.6*SR); ir=filt(rng.standard_normal(irn),hi=6000)*np.exp(-np.arange(irn)/SR/0.12); ir/=np.sqrt((ir**2).sum())
def verb(x,m): L=N+irn; return x+m*np.fft.irfft(np.fft.rfft(x,L)*np.fft.rfft(ir,L),L)[:N]
mix=verb(filt(mus,lo=140,hi=9000),0.35)+verb(fx,0.25)+filt(rng.standard_normal(N),lo=80,hi=600)*0.004
tt=np.arange(N)/SR; mix*=np.clip((DUR-tt)/0.4,0,1); mix=np.tanh(mix*1.5); mix/=np.abs(mix).max()*1.12
with wave.open('audio.wav','wb') as w: w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR);w.writeframes((np.stack([mix,mix],1)*32767).astype(np.int16).tobytes())
print(' '.join(f'{s/2:.1f}:{20*np.log10(np.sqrt((mix[int(s*SR/2):int((s+1)*SR/2)]**2).mean())+1e-9):.0f}' for s in range(29)))
