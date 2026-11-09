"""Gráficos do deck: multiagente (híbrido / 5 agentes) vs prompts únicos do DeepSeek."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path

A = ["unambiguity", "verifiability", "singularity"]
LBL = ["Não ambiguidade", "Verificabilidade", "Singularidade"]
RED, DARK, GRAY, MID = "#DB1E2F", "#2B2B2B", "#5F5F5F", "#BFBFBF"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 13, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "axes.axisbelow": True, "grid.alpha": .25, "savefig.bbox": "tight", "figure.dpi": 150})
K = ["repository", "issue_number"]


def load(res):
    e = pd.read_csv(res / "hybrid_eval.csv")
    j = pd.read_csv(res / "judged.csv"); j = j[(j.judge == "command-a-plus") & (j.generator == "deepseek-v4.1-flash")]
    fin = e[e.version == "final"].set_index(K)
    rows = {"Naive": j[j.prompt == "naive"], "Few-shot": j[j.prompt == "fewshot"], "Expert": j[j.prompt == "expert"]}
    rows = {n: d.set_index(K).reindex(fin.index) for n, d in rows.items()}
    rows["Multiagente"] = fin
    return rows, fin, e, pd.read_csv(res / "hybrid.csv")


def make(res, out):
    res, out = Path(res), Path(out); out.mkdir(parents=True, exist_ok=True)
    rows, fin, e, h = load(res)
    colors = {"Naive": MID, "Few-shot": "#8A8A8A", "Expert": DARK, "Multiagente": RED}

    # 1 barras por critério
    fig, ax = plt.subplots(figsize=(10, 5.2)); w = .2; x = np.arange(3)
    for i, (n, d) in enumerate(rows.items()):
        m = d[A].mean(); ax.bar(x + (i - 1.5) * w, m, w, label=n, color=colors[n])
        for xi, v in zip(x + (i - 1.5) * w, m): ax.text(xi, v + .05, f"{v:.2f}".replace(".", ","), ha="center", fontsize=10)
    ax.set_xticks(x, LBL); ax.set_ylim(1, 5); ax.set_ylabel("Nota média (1-5)"); ax.legend(ncol=4, loc="upper center", bbox_to_anchor=(.5, 1.12), frameon=False)
    fig.savefig(out / "d1_criterios.png"); plt.close(fig)

    # 2 trade-off: % com os 3 criterios >= 4 e pior criterio
    fig, axs = plt.subplots(1, 2, figsize=(11, 4.6))
    ok = {n: (d[A] >= 4).all(axis=1).mean() * 100 for n, d in rows.items()}
    axs[0].bar(ok.keys(), ok.values(), color=[colors[n] for n in ok]); axs[0].set_title("% de requisitos com os 3 critérios ≥ 4"); axs[0].set_ylim(0, 58)
    for i, v in enumerate(ok.values()): axs[0].text(i, v + 1, f"{v:.0f}%", ha="center", fontweight="bold")
    mn = {n: d[A].min(axis=1).mean() for n, d in rows.items()}
    axs[1].bar(mn.keys(), mn.values(), color=[colors[n] for n in mn]); axs[1].set_title("Nota média do pior critério"); axs[1].set_ylim(1, 5)
    for i, v in enumerate(mn.values()): axs[1].text(i, v + .05, f"{v:.2f}".replace(".", ","), ha="center", fontweight="bold")
    fig.savefig(out / "d2_tradeoff.png"); plt.close(fig)

    # 3 efeito do loop: consolidado sem loop vs final
    first = e[e.version == "first"].set_index(K).reindex(fin.index)
    fig, ax = plt.subplots(figsize=(8.5, 4.8)); x = np.arange(3)
    ax.bar(x - .2, first[A].mean(), .4, color=MID, label="Consolidado, sem revisão do juiz")
    ax.bar(x + .2, fin[A].mean(), .4, color=RED, label="Após ciclo de revisão")
    for xi, v in zip(x - .2, first[A].mean()): ax.text(xi, v + .05, f"{v:.2f}".replace(".", ","), ha="center", fontsize=11)
    for xi, v in zip(x + .2, fin[A].mean()): ax.text(xi, v + .05, f"{v:.2f}".replace(".", ","), ha="center", fontsize=11)
    ax.set_xticks(x, LBL); ax.set_ylim(1, 5.6); ax.legend(frameon=False, loc="upper left", ncol=1); ax.set_ylabel("Nota média (1-5)")
    fig.savefig(out / "d3_efeito_loop.png"); plt.close(fig)

    # 4 distribuicao de singularidade
    fig, axs = plt.subplots(1, 4, figsize=(13, 3.6), sharey=True)
    for ax, (n, d) in zip(axs, rows.items()):
        c = d["singularity"].value_counts(normalize=True).reindex(range(1, 6), fill_value=0) * 100
        ax.bar(c.index, c.values, color=colors[n]); ax.set_title(n); ax.set_xlabel("Nota")
    axs[0].set_ylabel("% dos requisitos"); fig.suptitle("Distribuição da nota de Singularidade", y=1.04)
    fig.savefig(out / "d4_dist_singularidade.png"); plt.close(fig)

    # 5 por repositório
    t = pd.DataFrame({n: d[A].mean(axis=1).groupby(level=0).mean() for n, d in rows.items()})
    fig, ax = plt.subplots(figsize=(10, 4.8)); x = np.arange(len(t)); w = .2
    for i, n in enumerate(t.columns): ax.bar(x + (i - 1.5) * w, t[n], w, label=n, color=colors[n])
    ax.set_xticks(x, [r.split("/")[-1] for r in t.index]); ax.set_ylim(2.5, 4.5); ax.set_ylabel("Média dos 3 critérios"); ax.legend(ncol=4, frameon=False)
    fig.savefig(out / "d5_repositorios.png"); plt.close(fig)

    # 6 custo
    fig, axs = plt.subplots(1, 3, figsize=(12, 3.8))
    it = h.iteracoes.value_counts(normalize=True).sort_index() * 100
    axs[0].bar(it.index.astype(str), it.values, color=RED); axs[0].set_title("Iterações até o fim"); axs[0].set_ylabel("% das issues")
    axs[1].hist(h.tokens, bins=20, color=DARK); axs[1].set_title(f"Tokens/requisito (média {h.tokens.mean():,.0f})".replace(",", ".")); 
    axs[2].hist(h.seconds, bins=20, color=GRAY); axs[2].set_title(f"Tempo/requisito (média {h.seconds.mean():.0f} s)")
    fig.savefig(out / "d6_custo.png"); plt.close(fig)
    return sorted(p.name for p in out.glob("d*.png"))


def ablation(res, out):
    """Mesmas 30 issues: prompts únicos, híbrido (Fase 1 reaproveitada) e 5 agentes (arquitetura do deck)."""
    res, out = Path(res), Path(out)
    e5 = pd.read_csv(res / "specialists5_eval.csv"); f5 = e5[e5.version == "final"].set_index(K); idx = f5.index
    eh = pd.read_csv(res / "hybrid_eval.csv"); j = pd.read_csv(res / "judged.csv")
    j = j[(j.judge == "command-a-plus") & (j.generator == "deepseek-v4.1-flash")]
    rows = {"Naive": j[j.prompt == "naive"], "Few-shot": j[j.prompt == "fewshot"], "Expert": j[j.prompt == "expert"]}
    rows = {n: d.set_index(K).reindex(idx) for n, d in rows.items()}
    rows["Híbrido"] = eh[eh.version == "final"].set_index(K).reindex(idx); rows["5 agentes"] = f5
    col = {"Naive": MID, "Few-shot": "#8A8A8A", "Expert": DARK, "Híbrido": "#E8909A", "5 agentes": RED}
    fig, ax = plt.subplots(figsize=(11, 5.2)); w = .16; x = np.arange(3)
    for i, (n, d) in enumerate(rows.items()):
        m = d[A].mean(); ax.bar(x + (i - 2) * w, m, w, label=n, color=col[n])
        for xi, v in zip(x + (i - 2) * w, m): ax.text(xi, v + .05, f"{v:.2f}".replace(".", ","), ha="center", fontsize=9)
    ax.set_xticks(x, LBL); ax.set_ylim(1, 5.2); ax.set_ylabel("Nota média (1-5), 30 issues"); ax.legend(ncol=5, loc="upper center", bbox_to_anchor=(.5, 1.12), frameon=False)
    fig.savefig(out / "d7_ablacao_5agentes.png"); plt.close(fig)
