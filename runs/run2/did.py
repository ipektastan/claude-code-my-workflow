import pandas as pd, numpy as np, pyfixest as pf, warnings
warnings.filterwarnings('ignore')
d=pd.read_csv(r'C:/Users/ipekt/Documents/econ_workshop/claude-code-my-workflow/runs/run2/d_e4fd.csv').sort_values(['state','year'])
first=d[d.treated==1].groupby('state').year.min()
d['g']=d.state.map(first).fillna(0).astype(int)   # 0 = never treated
Y0=d.year.min()
# 1. TWFE
m=pf.feols('y ~ treated | state + year', d, vcov={'CRV1':'state'})
print('TWFE all states:', m.coef().values, m.se().values)
dn=d[d.g!=Y0]
m2=pf.feols('y ~ treated | state + year', dn, vcov={'CRV1':'state'})
print('TWFE drop always-treated:', m2.coef().values, m2.se().values)

# 2. Callaway-Sant'Anna (no covariates), long differences vs base g-1
W=d.pivot(index='state',columns='year',values='y'); G=d.groupby('state').g.first()
years=sorted(d.year.unique())
def attgt(W,G,ctrl):
    out=[]
    for g in sorted(G[(G>0)&(G>Y0)].unique()):
        for t in years:
            base=g-1 if t>=g else t-1   # varying base pre-period (CS default)
            if base<Y0: continue
            tr=G.index[G==g]
            if ctrl=='never': c=G.index[G==0]
            else: c=G.index[(G==0)|(G>max(t,base))]
            c=c[c.isin(G.index[G!=g])]
            if len(c)==0: continue
            dy=W[t]-W[base]
            out.append((g,t,dy[tr].mean()-dy[c].mean(),len(tr)))
    return pd.DataFrame(out,columns=['g','t','att','n'])
def agg(a):
    post=a[a.t>=a.g]; simple=np.average(post.att,weights=post.n)
    a=a.assign(e=a.t-a.g)
    es=a.groupby('e').apply(lambda x: np.average(x.att,weights=x.n))
    return simple, es
rng=np.random.default_rng(1)
for ctrl in ['never','notyet']:
    a=attgt(W,G,ctrl); s,es=agg(a)
    bs=[];bes=[]
    states=W.index.values
    for b in range(499):
        sm=rng.choice(states,len(states),replace=True)
        Wb=W.loc[sm].reset_index(drop=True); Gb=G.loc[sm].reset_index(drop=True)
        try:
            ab=attgt(Wb,Gb,ctrl); sb,esb=agg(ab); bs.append(sb); bes.append(esb)
        except Exception: pass
    bes=pd.DataFrame(bes)
    print(f'\nCS ({ctrl}-treated controls): overall ATT={s:.4f}  bootSE={np.std(bs):.4f}  95%CI=({np.percentile(bs,2.5):.4f},{np.percentile(bs,97.5):.4f})')
    tab=pd.DataFrame({'att':es,'se':bes.std()}).loc[-10:20]
    print(tab.round(3).to_string())
    pre=a[a.t<a.g]; print('pre-period placebo avg:',round(np.average(pre.att,weights=pre.n),4))
