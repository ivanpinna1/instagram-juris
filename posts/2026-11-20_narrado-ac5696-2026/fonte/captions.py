import json,re,unicodedata,difflib
T=json.load(open('transcr.json'))
W=[(s,e,w.strip()) for seg in T for (s,e,w) in seg['words']]
script="""O edital exige que você seja revendedor autorizado do fabricante? | Calma: o TCU disse que isso é irregular. ||
Imagina uma empresa que vende equipamentos há anos. | Tem estoque, | tem preço bom, | tem a documentação em dia. ||
Sai um edital perfeito pra ela. | Mas, lá na habilitação, | vem a exigência: | comprovar que é distribuidora credenciada do fabricante. ||
Ela compra de um distribuidor e revende. | Não tem esse credenciamento. | Resultado: | fica fora da disputa | antes mesmo de mostrar o preço. ||
Só que o TCU analisou | exatamente esse tipo de exigência. | E decidiu: | é irregular. ||
Primeiro motivo: | a Lei 14.133 diz o que pode ser exigido na habilitação, | nos artigos 62 a 70. | E vínculo com o fabricante | não está lá. ||
Segundo motivo: | essa exigência faz a sua participação depender | de um vínculo comercial com outra empresa. | Se o fabricante não te credenciar, | você está fora. ||
Então, se o edital trouxer essa exigência, | não espere a inabilitação: | impugne no prazo. | E, se você já foi inabilitado por isso, | recorra, | citando o Acórdão 5696 de 2026 | da Primeira Câmara do TCU. ||
Sua empresa perde tempo brigando com edital assim? | Comenta QUERO | que a gente cuida da sua área de licitações, | do edital ao recurso."""
def n(x): x=unicodedata.normalize('NFD',x.lower()); return re.sub(r'[^a-z0-9]','',''.join(c for c in x if not unicodedata.combining(c)))
toks=[];   # (word, chunk_id)
chunks=[]
for ch in re.split(r'\|\|?',script.replace('\n',' ')):
    ch=ch.strip()
    if not ch: continue
    chunks.append(ch)
    for w in ch.split(): toks.append((w,len(chunks)-1))
a=[n(w) for w,_ in toks]; b=[n(w) for _,_,w in W]
sm=difflib.SequenceMatcher(None,a,b,autojunk=False)
tm=[None]*len(a)
for i,j,k in sm.get_matching_blocks():
    for d in range(k): tm[i+d]=(W[j+d][0],W[j+d][1])
# interpolate missing
for i in range(len(tm)):
    if tm[i] is None:
        p=next((tm[k] for k in range(i-1,-1,-1) if tm[k]),(0,0)); q=next((tm[k] for k in range(i+1,len(tm)) if tm[k]),p)
        tm[i]=(p[1],q[0] if q[0]>p[1] else p[1]+0.3)
out=[]
for c,txt in enumerate(chunks):
    idx=[i for i,(_,cc) in enumerate(toks) if cc==c]
    out.append({'t0':round(tm[idx[0]][0],2),'t1':round(tm[idx[-1]][1],2),'text':txt,
      'words':[{'w':toks[i][0],'t':round(tm[i][0],2)} for i in idx]})
json.dump(out,open('captions.json','w'),ensure_ascii=False,indent=0)
for o in out: print(o['t0'],o['t1'],o['text'])
print('unmatched',sum(1 for i,j,k in [] ))
