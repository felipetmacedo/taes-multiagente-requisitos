"""Gera deck/TAES_Multiagente.html a partir do original, preenchendo os resultados reais."""
import base64, re
from pathlib import Path
import pandas as pd

R = Path("results"); SRC = Path("deck/TAES_Multiagente_original.html")
A = ["unambiguity", "verifiability", "singularity"]; K = ["repository", "issue_number"]
s = SRC.read_text(encoding="utf-8")

def img(name): return "data:image/png;base64," + base64.b64encode((R / "figures_deck" / name).read_bytes()).decode()
def f(x): return f"{x:.2f}".replace(".", ",")
def seg(start, end, new):
    global s
    a, b = s.index(start), s.index(end)
    s = s[:a] + new + s[b:]

# ---------- dados ----------
e = pd.read_csv(R / "hybrid_eval.csv"); fin = e[e.version == "final"].set_index(K)
j = pd.read_csv(R / "judged.csv"); j = j[(j.judge == "command-a-plus") & (j.generator == "deepseek-v4.1-flash")]
base = {p: j[j.prompt == p].set_index(K).reindex(fin.index) for p in ["naive", "fewshot", "expert"]}
m, sd = fin[A].mean(), fin[A].std()
allok = {n: (d[A] >= 4).all(axis=1).mean() * 100 for n, d in {**base, "multi": fin}.items()}
mean_all = {n: d[A].mean().mean() for n, d in {**base, "multi": fin}.items()}
hy = pd.read_csv(R / "hybrid.csv")
s5 = pd.read_csv(R / "specialists5.csv"); e5 = pd.read_csv(R / "specialists5_eval.csv"); f5 = e5[e5.version == "final"].set_index(K)
b30 = {p: j[j.prompt == p].set_index(K).reindex(f5.index) for p in ["naive", "fewshot", "expert"]}
h30 = e[e.version == "final"].set_index(K).reindex(f5.index)
ok5 = (f5[A] >= 4).all(axis=1).mean() * 100; okh = (h30[A] >= 4).all(axis=1).mean() * 100
terr = ("godotengine/godot-proposals", "6121")
t_it = int(hy[(hy.repository == terr[0]) & (hy.issue_number.astype(str) == terr[1])].iteracoes.iloc[0])
fb = {c: round((hy[c] < 4).mean() * 100) for c in ["first_u", "first_v", "first_s"]}

# ---------- slide 8: desenho ----------
s = s.replace("<li>Qwen QwQ-32b como avaliador</li>", "<li>Avaliador independente: Cohere command-a-plus (o Qwen guia o loop)</li>")
s = s.replace("<li>Mesmos testes estatísticos</li>", "<li>Testes não paramétricos (Wilcoxon pareado)</li>")
s = s.replace("<li>DeepSeek R1 × Ingênuo, Few-shot, Especialista (principal)</li><li>o3-mini × 3 prompts (referência)</li><li>Resultados do artigo, sem regerar</li>",
              "<li>DeepSeek v4.1 flash × Naive, Few-shot, Especialista, regerados nas 150 issues</li><li>Mesmo modelo, mesmas issues: comparação pareada</li><li>Valores do artigo só como referência</li>")

# ---------- novo slide: execução vs proposta ----------
diff = f'''<!-- 8b · Execução vs proposta -->
<section class="slide">
  <div class="kicker">Desenho experimental</div>
  <h1 class="t">Como a execução diferiu da proposta</h1>
  <div class="body">
    <table class="t" style="font-size:18px">
      <tr><th style="width:20%">Ponto</th><th style="width:38%">Proposta</th><th>O que executamos</th></tr>
      <tr><td>Fase 1</td><td>3 agentes especialistas, um por critério</td><td><b>Principal (150 issues):</b> reaproveita 3 propostas já geradas (few-shot, expert, naive). <b>Ablação (30 issues):</b> os 3 especialistas reais</td></tr>
      <tr><td>Gerador</td><td>DeepSeek</td><td>DeepSeek v4.1 flash (modelo mais novo e barato)</td></tr>
      <tr><td>Juiz</td><td>Qwen avalia e aprova</td><td>Qwen 3.8-27b guia o loop; Cohere command-a-plus avalia (independente)</td></tr>
      <tr><td>Linhas de base</td><td>Valores do artigo</td><td>Prompts regerados com o mesmo modelo e as mesmas issues</td></tr>
      <tr><td>Custo</td><td>Tokens, tempo, chamadas</td><td>Medidos por requisito</td></tr>
      <tr><td>Extra</td><td>—</td><td>Nota de fidelidade ao título da issue</td></tr>
    </table>
    <div class="cap" style="margin-top:14px;font-size:16px">Motivo: orçamento de API. Reaproveitar a Fase 1 evita ~3 chamadas por rodada; a ablação mede se a especialização muda o resultado.</div>
  </div>
</section>

'''
s = s.replace("<!-- 9 · Métricas -->", diff + "<!-- 9 · Métricas -->", 1)
s = s.replace("<b>Testes estatísticos:</b> <span class=\"muted\">Mann–Whitney (par a par) e Kruskal–Wallis (entre estratégias), como no artigo.</span>",
              "<b>Teste estatístico:</b> <span class=\"muted\">Wilcoxon pareado (mesmas issues) entre o multiagente e cada prompt único.</span>")
s = s.replace("Em andamento: os valores a seguir são placeholders", "DeepSeek v4.1 flash · 150 issues · avaliador independente")

# ---------- slide 11 ----------
def card(t, v, sdv, ref, who):
    return (f'<div class="card"><div class="h">{t}</div><div class="big" style="margin-top:10px">{f(v)}<small> /5</small></div>'
            f'<div class="cap">Multiagente · DP {f(sdv)}</div><div class="cap" style="margin-top:14px">Melhor prompt único: <b style="color:var(--dark)">{f(ref)}</b> ({who})</div></div>')
ov = ('<!-- 11 · Visão geral -->\n<section class="slide">\n  <div class="kicker">Resultados</div>\n  <h1 class="t">Visão geral: multiagente vs. melhor prompt</h1>\n  <div class="body">\n    <div class="grid g3">\n      '
      + card("Não Ambiguidade", m.unambiguity, sd.unambiguity, base["expert"].unambiguity.mean(), "Especialista")
      + card("Verificabilidade", m.verifiability, sd.verifiability, base["expert"].verifiability.mean(), "Especialista")
      + card("Singularidade", m.singularity, sd.singularity, base["fewshot"].singularity.mean(), "Few-shot")
      + f'''
    </div>
    <div class="card pink p" style="margin-top:22px"><b style="color:var(--red)">Mensagem principal:</b> o multiagente tem a <b>maior média</b> ({f(mean_all["multi"])} vs. {f(mean_all["expert"])} do melhor prompt, p &lt; 0,001) e <b>{allok["multi"]:.0f}%</b> dos requisitos com os três critérios ≥ 4 (prompts únicos: {allok["fewshot"]:.0f}–{allok["naive"]:.0f}%). Mas <b>não vence o melhor prompt em cada critério isolado</b>.</div>
  </div>
</section>

''')
seg("<!-- 11 · Visão geral -->", "<!-- 12 · Tabela -->", ov)

# ---------- slide 12 tabela + slides de gráficos ----------
def row(n, d, cls=""):
    mm = d[A].mean(); return f'<tr{cls}><td>{n}</td><td>{f(mm.unambiguity)}</td><td>{f(mm.verifiability)}</td><td>{f(mm.singularity)}</td><td>{f(mm.mean())}</td><td>{d[A].ge(4).all(axis=1).mean()*100:.0f}%</td></tr>'
def img_slide(kick, title, name, side):
    return f'''<section class="slide">
  <div class="kicker">{kick}</div>
  <h1 class="t">{title}</h1>
  <div class="body" style="display:grid;grid-template-columns:1.7fr 1fr;gap:28px;align-items:center">
    <img src="{img(name)}" style="width:100%;border-radius:8px">
    <div class="card pink">{side}</div>
  </div>
</section>

'''
tab = ('<!-- 12 · Tabela -->\n<section class="slide">\n  <div class="kicker">Resultados · QP-MA1 e QP-MA2</div>\n  <h1 class="t">Comparação por estratégia</h1>\n  <div class="body">\n    <table class="t">\n'
       '      <tr><th style="width:30%">Estratégia (DeepSeek v4.1)</th><th>Não amb.</th><th>Verific.</th><th>Singul.</th><th>Média</th><th>3 critérios ≥ 4</th></tr>\n      '
       + row("Naive", base["naive"]) + row("Few-shot", base["fewshot"]) + row("Especialista", base["expert"]) + row("Multiagente (nosso)", fin, ' class="ours"') +
       '\n    </table>\n    <div class="cap" style="margin-top:14px;font-size:16px">150 issues, avaliador Cohere command-a-plus, mesmas issues em todas as linhas. Baselines regerados com o mesmo modelo (não são os valores do artigo). Multiagente = Fase 1 reaproveitada + consolidador + juiz Qwen.</div>\n'
       f'    <div class="p" style="margin-top:20px;font-size:19px"><b>Pareado vs. Especialista:</b> média +{f(mean_all["multi"]-mean_all["expert"])} (p &lt; 0,001) · verificabilidade −0,32 · não ambiguidade −0,23 (ambos p ≤ 0,001) · singularidade +1,27.</div>\n  </div>\n</section>\n\n')
tab += img_slide("Resultados · QP-MA1", "Nota média por critério", "d1_criterios.png",
                 '<div class="hr" style="font-size:20px">Leitura</div><p class="p" style="margin-top:10px;font-size:18px">Cada prompt único é forte em um critério e fraco em outro.</p><p class="p" style="margin-top:10px;font-size:18px">O multiagente fica <b>no meio-alto em todos</b>, sem o buraco de 2,5 a 3,0 dos prompts únicos.</p>')
tab += img_slide("Resultados · QP-MA2", "O trade-off diminui", "d2_tradeoff.png",
                 f'<div class="hr" style="font-size:20px">Leitura</div><p class="p" style="margin-top:10px;font-size:18px"><b>{allok["multi"]:.0f}%</b> dos requisitos passam de 4 nos três critérios ao mesmo tempo, contra {allok["fewshot"]:.0f}–{allok["naive"]:.0f}% dos prompts únicos.</p><p class="p" style="margin-top:10px;font-size:18px">A variância de Singularidade <b>não</b> caiu (DP {f(sd.singularity)}).</p>')
tab += img_slide("Resultados · origem do ganho", "O ganho vem do ciclo de revisão", "d3_efeito_loop.png",
                 '<div class="hr" style="font-size:20px">Leitura</div><p class="p" style="margin-top:10px;font-size:18px">Só consolidar as propostas <b>não</b> melhora a Singularidade.</p><p class="p" style="margin-top:10px;font-size:18px">É o feedback do juiz, em rodadas seguintes, que a leva de 2,85 para 3,83.</p>')
tab += f'''<section class="slide">
  <div class="kicker">Resultados · ablação</div>
  <h1 class="t">Com os 5 agentes reais (30 issues)</h1>
  <div class="body" style="display:grid;grid-template-columns:1.7fr 1fr;gap:28px;align-items:center">
    <img src="{img("d7_ablacao_5agentes.png")}" style="width:100%;border-radius:8px">
    <div class="card pink"><div class="hr" style="font-size:20px">Leitura</div>
      <p class="p" style="margin-top:10px;font-size:18px">Média <b>{f(f5[A].mean().mean())}</b> (híbrido {f(h30[A].mean().mean())}); <b>{ok5:.0f}%</b> com os 3 critérios ≥ 4 (híbrido {okh:.0f}%).</p>
      <p class="p" style="margin-top:10px;font-size:18px">Diferença para o híbrido <b>não significativa</b> (p = 0,18, n = 30). Contra o Especialista, +0,54 (p = 0,001).</p>
      <p class="p" style="margin-top:10px;font-size:18px">Custo: ~{s5.tokens.mean()/1000:.1f} mil tokens e {s5.seconds.mean():.0f} s por requisito.</p></div>
  </div>
</section>

'''
seg("<!-- 12 · Tabela -->", "<!-- 13 · Custo -->", tab)

# ---------- slide 13 custo ----------
cost = f'''<!-- 13 · Custo -->
<section class="slide">
  <div class="kicker">Resultados · QP-MA4</div>
  <h1 class="t">Quanto custa a melhora</h1>
  <div class="body">
    <div class="grid g4">
      <div class="card"><div class="big" style="font-size:50px">{f(hy.iteracoes.mean()).replace(",", ",")[:3]}</div><div class="lbl">iterações médias</div><div class="cap" style="font-size:16px">até o fim do ciclo</div></div>
      <div class="card"><div class="big" style="font-size:50px">{hy.first_round_approved.mean()*100:.0f}%</div><div class="lbl">aprovados na 1ª</div><div class="cap" style="font-size:16px">sem nenhum retorno</div></div>
      <div class="card"><div class="big" style="font-size:50px">{hy.tokens.mean()/1000:.1f} mil</div><div class="lbl">tokens/requisito</div><div class="cap" style="font-size:16px">{s5.tokens.mean()/1000:.1f} mil nos 5 agentes reais</div></div>
      <div class="card"><div class="big" style="font-size:50px">{hy.seconds.mean():.0f} s</div><div class="lbl">tempo/requisito</div><div class="cap" style="font-size:16px">{s5.seconds.mean():.0f} s nos 5 agentes reais</div></div>
    </div>
    <div class="card out" style="margin-top:22px;box-shadow:none">
      <div class="h" style="font-size:20px">Critério abaixo de 4 na 1ª rodada (juiz Qwen)</div>
      <div class="p" style="margin-top:10px;font-size:18px">Singularidade <b>{fb["first_s"]}%</b> · Não ambiguidade <b>{fb["first_u"]}%</b> · Verificabilidade <b>{fb["first_v"]}%</b></div>
      <div class="cap" style="margin-top:8px;font-size:16px">{hy.status.eq("APPROVE").mean()*100:.0f}% das issues são aprovadas ao fim de 3 rodadas; as demais saem com a melhor versão. Custo do prompt único não medido (1 chamada por requisito).</div>
    </div>
  </div>
</section>

'''
seg("<!-- 13 · Custo -->", "<!-- 14 · Exemplo -->", cost)

# ---------- slide 14 exemplo Terrain ----------
ex = f'''<!-- 14 · Exemplo -->
<section class="slide">
  <div class="kicker">Resultados · QP-MA3</div>
  <h1 class="t">Caso do artigo, refeito: “Implement Terrain”</h1>
  <div class="body" style="display:grid;grid-template-columns:1fr 50px 1fr;align-items:stretch">
    <div class="card" style="display:flex;flex-direction:column">
      <div class="tag" style="color:var(--gray)">DeepSeek v4.1 · prompt Especialista</div>
      <p class="p" style="margin-top:14px">Requisito de 9 itens (heightmap, ruído procedural, LOD, edição com undo, APIs, formatos, testes, desempenho…) mais critérios de aceitação.</p>
      <div style="margin-top:auto"><div class="big" style="color:var(--dark);font-size:52px">4 <small>/</small> 4 <small>/</small> <span style="color:var(--red)">2</span></div><div class="cap" style="font-size:16px">Não amb. / Verific. / Singul.</div></div>
    </div>
    <div style="display:flex;align-items:center;justify-content:center;font-size:40px;color:var(--red)">→</div>
    <div class="card pink" style="display:flex;flex-direction:column">
      <div class="tag">Multiagente · {t_it} iterações</div>
      <p class="p" style="margin-top:14px">“The system shall implement a heightmap-based terrain subsystem with configurable width, depth, height scale, resolution, and materials.”</p>
      <div style="margin-top:auto"><div class="big" style="font-size:52px">4 / 3 / 2</div><div class="cap" style="font-size:16px">Não amb. / Verific. / Singul. · mais curto e focado, mas Singularidade segue 2: título vago demais</div></div>
    </div>
  </div>
</section>

'''
seg("<!-- 14 · Exemplo -->", "<!-- 15 · Ameaças -->", ex)

# ---------- slide 15 ameaças ----------
s = s.replace("A arquitetura pode aprender a agradar o Qwen. Mitigar com um 2º juiz de outra família e amostra humana.",
              "Mitigado: o Qwen guia o loop e o Cohere avalia. Falta ainda amostra humana.")
s = s.replace("Juiz no ciclo = avaliador final", "Juiz no ciclo ≠ avaliador final")
s = s.replace("O ganho pode ser do pipeline ou do modelo. Comparar com o DeepSeek R1 do artigo isola parte disso.",
              "Medimos só com o DeepSeek v4.1 flash. Outros geradores ainda não foram testados na arquitetura.")
s = s.replace("Várias chamadas por requisito. A melhora precisa compensar o custo (QP-MA4).",
              f"Cerca de {hy.calls.mean():.0f} chamadas e {hy.tokens.mean()/1000:.1f} mil tokens por requisito ({s5.tokens.mean()/1000:.1f} mil nos 5 agentes reais).")
s = s.replace("Não determinismo", "Fase 1 híbrida e amostra pequena")
s = s.replace("A mesma semente não garante a mesma saída. Repetir uma amostra para medir a variação.",
              "Os 5 agentes reais só rodaram em 30 issues: a diferença para o híbrido não é significativa (p = 0,18).")

# ---------- slide 16 conclusões ----------
concl = [
    f"<b>Melhor média e menos trade-off:</b> {f(mean_all['multi'])} vs. {f(mean_all['expert'])} do melhor prompt único (p &lt; 0,001); {allok['multi']:.0f}% dos requisitos com os 3 critérios ≥ 4 (vs. {allok['fewshot']:.0f}–{allok['naive']:.0f}%).",
    "<b>Mas não vence cada critério:</b> o Especialista segue melhor em verificabilidade e não ambiguidade; o Few-shot, em singularidade. O ganho vem do ciclo de revisão do juiz.",
    f"<b>5 agentes reais (30 issues):</b> média {f(f5[A].mean().mean())} e {ok5:.0f}% com os 3 critérios ≥ 4, a ~{f(s5.tokens.mean()/hy.tokens.mean())[:3]}× os tokens do híbrido. Ganho sobre o híbrido não significativo.",
]
for i, c in enumerate(concl, 1):
    s = s.replace(f'<div class="card ph p" style="flex:1;display:flex;align-items:center">[Conclusão {i}]</div>',
                  f'<div class="card" style="flex:1;display:flex;align-items:center;font-size:17px;line-height:1.35"><div>{c}</div></div>')

s = s.replace("[link do repositório do grupo]", "github.com/felipetmacedo/taes-multiagente-requisitos")
out = Path("deck/TAES_Multiagente.html"); out.write_text(s, encoding="utf-8")
left = re.findall(r"\[[^\]<]{1,40}\]", re.sub(r"data:[^\"']+", "", s))
print("ok", len(s) // 1024, "KB; slides:", s.count('<section class="slide'), "; colchetes restantes:", left)
