import numpy as np, wave
SR=48000; DUR=21.0; N=int(SR*DUR)
rng=np.random.default_rng(7)
def mtof(m): return 440*2**((m-69)/12)
def env(n,a,d):  # attack secs, exp decay time-const
    t=np.arange(n)/SR; return np.minimum(t/max(a,1e-4),1)*np.exp(-t/d)
def lp(x,fc):
    a=np.exp(-2*np.pi*fc/SR); y=np.empty_like(x); s=0.0
    for i in range(len(x)): s=(1-a)*x[i]+a*s; y[i]=s
    return y
def lp_fast(x,fc,passes=2):
    # FFT brickwall-ish smooth lowpass
    X=np.fft.rfft(x); f=np.fft.rfftfreq(len(x),1/SR); H=1/(1+(f/fc)**(2*passes)); return np.fft.irfft(X*H,len(x))
def hp_fast(x,fc):
    X=np.fft.rfft(x); f=np.fft.rfftfreq(len(x),1/SR); H=1/(1+(fc/np.maximum(f,1))**4); return np.fft.irfft(X*H,len(x))
def add(buf,sig,t0,g=1.0):
    i=int(t0*SR); j=min(N,i+len(sig)); 
    if i<N: buf[i:j]+=g*sig[:j-i]
music=np.zeros(N); sfx=np.zeros(N); drums=np.zeros(N)
T0=2.85; BEAT=0.5; BAR=2.0
# chords (midi) D, Bm, G, A
CH={'D':[50,57,62,66,69],'Bm':[47,54,59,62,66],'G':[43,55,59,62,67],'A':[45,52,57,61,64]}
prog=['D','Bm','G','A','D','Bm','G','A','D']
starts=[T0+i*BAR for i in range(8)]+[T0+16]
# intro pad (D add9) 0..T0
def pad(notes,dur,att=0.6,rel=1.0):
    n=int(dur*SR); t=np.arange(n)/SR; s=np.zeros(n)
    for m in notes:
        for det in (-0.08,0.0,0.08):
            f=mtof(m+det); s+=2*((t*f)%1)-1
    s=lp_fast(s/len(notes)/3,900)
    e=np.minimum(t/att,1)*np.minimum(1,(dur-t)/rel).clip(0,1); return s*e
add(music,pad([50,57,64,66,69],T0+0.5,att=1.2,rel=0.6),0,0.22)
for c,s0 in zip(prog,starts):
    d=BAR+0.3 if s0<T0+16 else DUR-s0
    add(music,pad(CH[c],d,att=0.25,rel=0.4 if s0<T0+16 else 2.0),s0,0.20)
# bass
for k,(c,s0) in enumerate(zip(prog[:8],starts[:8])):
    root=CH[c][0]-12 if CH[c][0]>=47 else CH[c][0]
    root=CH[c][0]-12
    for b in range(4):
        n=int(0.45*SR); t=np.arange(n)/SR; f=mtof(root)
        s=np.tanh(1.6*np.sin(2*np.pi*f*t))*env(n,0.005,0.22)
        add(music,s,s0+b*BEAT,0.32)
# final bass note
n=int(2.2*SR); t=np.arange(n)/SR; add(music,np.sin(2*np.pi*mtof(38)*t)*env(n,0.01,0.9),T0+16,0.3)
# pluck arp 8ths
for c,s0 in zip(prog[:8],starts[:8]):
    tones=[m+24 for m in CH[c][1:]]; pat=[0,1,2,3,2,1,3,2]
    for i in range(8):
        m=tones[pat[i]%len(tones)]; n=int(0.4*SR); t=np.arange(n)/SR; f=mtof(m)
        s=(np.sin(2*np.pi*f*t)+0.3*np.sin(4*np.pi*f*t))*env(n,0.003,0.12)
        add(music,s,s0+i*0.25,0.07)
# drums from T0 to T0+16
def kick():
    n=int(0.35*SR); t=np.arange(n)/SR; f=45+80*np.exp(-t/0.03); ph=2*np.pi*np.cumsum(f)/SR
    return np.sin(ph)*env(n,0.001,0.12)
def clap():
    n=int(0.25*SR); s=rng.standard_normal(n); s=hp_fast(lp_fast(s,3000),900)
    e=np.zeros(n); t=np.arange(n)/SR
    for o in (0,0.012,0.024): e+=(t>=o)*np.exp(-np.maximum(t-o,0)/0.05)
    return s*e/3
def hat():
    n=int(0.08*SR); return hp_fast(rng.standard_normal(n),7000)*env(n,0.001,0.02)
K,C=kick(),clap()
for b in range(32):
    tb=T0+b*BEAT
    add(drums,K,tb,0.55)
    if b%2==1: add(drums,C,tb,0.22)
    add(drums,hat(),tb+0.25,0.06)
# ---- SFX (key of D, pentatonic) ----
def bell(m,dur=1.0,d=0.35):
    n=int(dur*SR); t=np.arange(n)/SR; f=mtof(m)
    return (np.sin(2*np.pi*f*t)+0.25*np.sin(2*np.pi*f*2.0*t)*np.exp(-t/0.1))*env(n,0.002,d)
def tick():
    n=int(0.03*SR); return lp_fast(hp_fast(rng.standard_normal(n),1500),5000)*env(n,0.0005,0.006)
# drip
n=int(0.5*SR); t=np.arange(n)/SR; f=mtof(86)*(1+0.5*np.exp(-t/0.02)); 
add(sfx,np.sin(2*np.pi*np.cumsum(f)/SR)*env(n,0.001,0.09),0.70,0.35)
n=int(1.2*SR); t=np.arange(n)/SR; add(sfx,np.sin(2*np.pi*mtof(38)*t)*env(n,0.01,0.4),0.72,0.30)  # low bloom on impact
# whoosh into reveal
n=int(0.6*SR); t=np.arange(n)/SR; w=lp_fast(rng.standard_normal(n),2500)*(t/0.6)**2
add(sfx,w,2.25,0.10)
for m in (74,78,81): add(sfx,bell(m,2.0,0.6),T0,0.10)
# clicks
for c in [6.9,8.85,12.25]: add(sfx,tick(),c,0.10); add(sfx,bell(81,0.3,0.05),c,0.04)
# typing
tt=7.05
while tt<8.05: add(sfx,tick(),tt,0.025*rng.uniform(.6,1)); tt+=rng.uniform(0.035,0.06)
add(sfx,bell(81,0.8,0.2),8.95,0.09); add(sfx,bell(86,0.8,0.25),9.07,0.09)
for tt,m in [(10.05,74),(10.4,78),(10.75,81)]: add(sfx,bell(m,0.6,0.12),tt,0.11)
add(sfx,tick(),12.25,0.1); add(sfx,bell(86,1.0,0.3),12.27,0.11); add(sfx,bell(93,1.0,0.3),12.27,0.05)
for tt,m in zip([13.95,14.45,14.95,15.45],[74,76,78,81]): add(sfx,bell(m,0.7,0.18),tt,0.10)
for tt,m in zip([15.8,15.9,16.0,16.1,16.25],[83,86,88,90,93]): add(sfx,bell(m,0.5,0.1),tt,0.06)
add(sfx,bell(86,1.2,0.4),16.45,0.08)
for m in (62,69,74,78): add(sfx,bell(m,3.0,0.9),17.95,0.07)
# reverb (shared space)
irn=int(1.8*SR); ir=rng.standard_normal(irn)*np.exp(-np.arange(irn)/SR/0.45); ir=lp_fast(ir,5000); ir/=np.sqrt((ir**2).sum())
def verb(x,mix):
    L=N+irn; y=np.fft.irfft(np.fft.rfft(x,L)*np.fft.rfft(ir,L),L)[:N]; return x+mix*y
mix=verb(music,0.25)+verb(sfx,0.35)+verb(drums,0.08)
# fades & master
t=np.arange(N)/SR; mix*=np.minimum(1,(DUR-t)/0.6).clip(0,1)
mix=np.tanh(mix*1.2); mix/=np.abs(mix).max()*1.12
# stereo widen: small delay on R for pads
L=mix; R=np.concatenate([np.zeros(int(0.008*SR)),mix])[:N]*0.5+mix*0.5
st=np.stack([L,R],1); st=(st*32767).astype(np.int16)
with wave.open('music.wav','wb') as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(st.tobytes())
print('ok')
