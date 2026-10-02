exec(open('did.py').read().split('# 2.')[0])
exec('# 2.'+open('did.py').read().split('# 2.')[1].split('rng=')[0])
a=attgt(W,G,'never').assign(e=lambda x:x.t-x.g)
# balanced: cohorts observed for e in 0..12
gs=a[a.e==12].g.unique(); b=a[a.g.isin(gs)&(a.e.between(0,12))]
print('balanced cohorts',gs, 'n states',G[G.isin(gs)].size)
print('balanced e0-12 avg ATT', b.groupby('e').apply(lambda x:np.average(x.att,weights=x.n)).mean().round(4))
post=a[a.e>=0]; print('dynamic (equal weight e=0..20):', post[post.e<=20].groupby('e').apply(lambda x:np.average(x.att,weights=x.n)).mean().round(4))
# Sun-Abraham style via interaction-weighted: saturated cohort x rel-time with never-treated as control
dn=d[d.g!=Y0].copy()
fit=pf.event_study(data=dn,yname='y',idname='state',tname='year',gname='g',estimator='twfe') if False else None
# simple dynamic TWFE (binned) to show contrast
dn['e']=np.where(dn.g>0,(dn.year-dn.g).clip(-10,20),-1000)
r=pf.feols('y ~ i(e, ref=-1) | state + year', dn[dn.e!=-1000].pipe(lambda x:x) if False else dn.assign(e=dn.e.replace(-1000,-1)), vcov={'CRV1':'state'})
print(r.tidy().iloc[[10,15,20,25,29]][['Estimate','Std. Error']].round(3))
# Did2s (Gardner) via pyfixest
try:
    from pyfixest.did.estimation import did2s
    g2=did2s(dn.assign(treat=dn.treated.astype(bool)),yname='y',first_stage='~0|state+year',second_stage='~treat',treatment='treat',cluster='state')
    print('did2s:',g2.coef().values,g2.se().values)
except Exception as ex: print('did2s err',ex)
