import statistics as st
v=[59.29,21.51,20.42,15.19,14.13,12.51,11.66,8.77,8.43,8.06,7.62,7.46,7.46,7.34,7.12,6.45,6.35,6.22,5.61,5.08,4.95,4.73,4.58,4.48,4.46,4.45,4.37,4.36,4.31,4.31,4.27,3.98,3.90,3.89,3.88,3.87,3.82,3.79,3.77,3.64,3.38,3.34,3.26,3.25,3.17,3.17,3.15,3.02,2.92,2.92,2.90,2.85,2.73,2.71,2.68,2.59,2.59,2.55,2.50,2.49,2.49,2.49,2.29,2.26,2.24,2.17,2.13,2.12,2.12,2.09,2.05,2.02,1.99,1.96,1.96,1.93,1.73,1.60,1.28,1.26,1.13,1.02,1.01,0.94,0.94,0.92,0.79,0.61,0.57,0.54,0.54,0.53,0.51,0.49,0.37]
lab="D A D A A D D D D A D D A A F A A A B B B D F E F A B F C B B A A A E S D A A A B A A A B A D A S A A E A B A B A A A A F C A A A C A B S C A A B A B A A A A S S A S A A F A E S A F S A A A".split()
assert len(v)==95==len(lab),(len(v),len(lab))
name={'A':'Skin Minecraft đơn giản cổ điển','B':'Skin dễ thương/anime trên thân khối chuẩn','C':'Nhân vật cầu kỳ (giáp phát sáng/anime chi tiết)','S':'Người que 2D cực đơn giản','E':'Thế giới Minecraft render thật, không anh hùng','D':'Không phải Minecraft','F':'Quay mặt thật / game khác'}
for k in 'ABCSE DF'.split()[0]+'DF':
    xs=[x for x,l in zip(v,lab) if l==k]
    print(f"{k} {name[k]:48s} n={len(xs):2d} tong={sum(xs):6.1f}M median={st.median(xs):.2f}M")
mc=[(x,l) for x,l in zip(v,lab) if l in 'ABCSE']
tot=sum(x for x,_ in mc)
print('MC-story pool n',len(mc),'tot',round(tot,1))
for k in 'ABCSE': print(k, f"{100*sum(x for x,l in mc if l==k)/tot:.0f}% views", f"{100*sum(1 for _,l in mc if l==k)/len(mc):.0f}% videos")
