import json,re,unicodedata,difflib
T=json.load(open('transcr.json'))
W=[(s,e,w.strip()) for seg in T for (s,e,w) in seg['words']]
script="""Perdeu o recurso na licitação | e ouviu que acabou, | que não cabe mais nada? | Não é bem assim. ||
Imagina: | sua empresa é desclassificada | por um erro da comissão. | Você recorre. | Dias depois, chega a resposta: | recurso negado. ||
E junto vem a frase: | a via administrativa está encerrada. ||
É verdade que a Lei 14.133 | não prevê um segundo recurso. | Decidiu a autoridade superior, | o recurso termina ali. ||
Mas o TCU deixou claro: | isso não impede a instância seguinte, | quando provocada, | de reconhecer e corrigir a irregularidade. ||
O nome disso é autotutela, | ou o princípio da autotutela. | A Administração pode rever os próprios atos | quando há ilegalidade. ||
Só tem um detalhe: | antes de mudar a decisão, | quem vai ser atingido precisa ser ouvido. | Se a prejudicada for a sua empresa, | você tem direito ao contraditório. ||
Então, para resumir: | recurso negado, | mas a ilegalidade é clara? | Leve o caso, por escrito, | à instância superior, | citando o Acórdão 2926 de 2026, | do Plenário do Tribunal de Contas da União. | E se quiserem rever uma decisão contra você | sem te ouvir, | exija ser ouvido. ||
Sua empresa já desistiu de uma licitação | depois de um recurso negado? | Comenta QUERO | ou mande um direct, | que a gente cuida da sua área de licitações, | do edital ao recurso."""
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
