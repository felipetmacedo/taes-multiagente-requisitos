"""Gráficos para avaliação/apresentação -> results/figures/*.png"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path

ATTR = ["unambiguity", "verifiability", "singularity"]
LBL = {"unambiguity": "Unambiguity", "verifiability": "Verifiability", "singularity": "Singularity"}
COL = {"unambiguity": "#2a6fdb", "verifiability": "#e08a1e", "singularity": "#2a9d6f"}
plt.rcParams.update({"font.size": 11, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "grid.alpha": .25, "figure.dpi": 130, "savefig.bbox": "tight"})


def _ci(x):
    return 1.96 * x.std(ddof=1) / np.sqrt(len(x)) if len(x) > 1 else 0


def _save(fig, d, name):
    fig.savefig(Path(d) / f"{name}.png"); plt.close(fig)


def make_all(judged_csv, gen_csv, out_dir, judge, ma_csv=None):
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    full = pd.read_csv(judged_csv)
    df = full[full.judge == judge].copy()
    df["overall"] = df[ATTR].mean(axis=1)
    gen = pd.read_csv(gen_csv)
    gen["words"] = gen.requirement.fillna("").str.split().str.len()
    gen["markdown"] = gen.requirement.fillna("").str.contains(r"\*\*|##|Requirement:", regex=True)
    order = df.groupby("generator").overall.mean().sort_values(ascending=False).index.tolist()

    # 1 ranking geral por atributo
    fig, ax = plt.subplots(figsize=(10, 5)); w = .27; x = np.arange(len(order))
    for i, a in enumerate(ATTR):
        g = df.groupby("generator")[a]
        ax.bar(x + (i - 1) * w, g.mean()[order], w, yerr=g.apply(_ci)[order], label=LBL[a], color=COL[a], capsize=2)
    ax.set_xticks(x, order, rotation=30, ha="right"); ax.set_ylim(1, 5); ax.set_ylabel("Nota média (1-5, IC 95%)")
    ax.set_title(f"Qualidade ISO 29148 por modelo (juiz: {judge})"); ax.legend(ncol=3)
    _save(fig, out, "01_ranking_modelos")

    # 2 heatmap modelo x prompt
    pv = df.pivot_table(index="generator", columns="prompt", values="overall").loc[order]
    fig, ax = plt.subplots(figsize=(6.5, 5)); im = ax.imshow(pv.values, cmap="YlGn", vmin=2.5, vmax=5, aspect="auto")
    ax.set_xticks(range(pv.shape[1]), pv.columns); ax.set_yticks(range(pv.shape[0]), pv.index); ax.grid(False)
    for i in range(pv.shape[0]):
        for j in range(pv.shape[1]): ax.text(j, i, f"{pv.values[i, j]:.2f}", ha="center", va="center")
    ax.set_title("Nota média: modelo × estratégia de prompt"); fig.colorbar(im)
    _save(fig, out, "02_heatmap_modelo_prompt")

    # 3 efeito do prompt por atributo
    fig, ax = plt.subplots(figsize=(8, 4.5)); pr = ["naive", "fewshot", "expert"]; x = np.arange(3)
    for i, a in enumerate(ATTR):
        g = df.groupby("prompt")[a]
        ax.bar(x + (i - 1) * w, g.mean()[pr], w, yerr=g.apply(_ci)[pr], label=LBL[a], color=COL[a], capsize=3)
    ax.set_xticks(x, ["Naive", "Few-shot", "Expert"]); ax.set_ylim(1, 5); ax.legend(ncol=3)
    ax.set_title("Efeito da estratégia de prompt (todos os modelos)"); ax.set_ylabel("Nota média")
    _save(fig, out, "03_efeito_prompt")

    # 4 prompt x modelo: singularity (principal achado do artigo)
    fig, axs = plt.subplots(1, 3, figsize=(14, 4.5), sharey=True)
    for ax, a in zip(axs, ATTR):
        for p, m in zip(pr, ["o", "s", "^"]):
            ax.plot(order, df[df.prompt == p].groupby("generator")[a].mean()[order], marker=m, label=p)
        ax.set_title(LBL[a]); ax.tick_params(axis="x", rotation=60)
    axs[0].set_ylabel("Nota média"); axs[0].legend()
    fig.suptitle("Prompt × modelo por atributo"); _save(fig, out, "04_prompt_por_atributo")

    # 5 distribuição de notas de singularity (empilhado)
    fig, axs = plt.subplots(1, 3, figsize=(14, 4.5), sharey=True)
    cmap = plt.cm.RdYlGn(np.linspace(.1, .9, 5))
    for ax, a in zip(axs, ATTR):
        dist = df.groupby("generator")[a].value_counts(normalize=True).unstack(fill_value=0).reindex(columns=range(1, 6), fill_value=0).loc[order[::-1]]
        left = np.zeros(len(dist))
        for k in range(1, 6):
            ax.barh(dist.index, dist[k], left=left, color=cmap[k - 1], label=str(k)); left += dist[k].values
        ax.set_title(LBL[a]); ax.set_xlim(0, 1)
    axs[-1].legend(title="Nota", bbox_to_anchor=(1, 1))
    fig.suptitle("Distribuição das notas (1-5)"); _save(fig, out, "05_distribuicao_notas")

    # 6 correlação entre atributos
    c = df[ATTR].corr(method="spearman")
    fig, ax = plt.subplots(figsize=(4.8, 4)); ax.imshow(c, cmap="Blues", vmin=-.2, vmax=1); ax.grid(False)
    ax.set_xticks(range(3), [LBL[a] for a in ATTR], rotation=20); ax.set_yticks(range(3), [LBL[a] for a in ATTR])
    for i in range(3):
        for j in range(3): ax.text(j, i, f"{c.values[i, j]:.2f}", ha="center", va="center")
    ax.set_title("Spearman entre atributos"); _save(fig, out, "06_spearman")

    # 7 juízes: severidade e concordância
    if full.judge.nunique() > 1:
        fig, ax = plt.subplots(figsize=(7, 4.5)); js = sorted(full.judge.unique()); x = np.arange(3); ww = .8 / len(js)
        for i, j in enumerate(js):
            ax.bar(x + i * ww, full[full.judge == j][ATTR].mean(), ww, label=j)
        ax.set_xticks(x + ww * (len(js) - 1) / 2, [LBL[a] for a in ATTR]); ax.set_ylim(1, 5); ax.legend()
        ax.set_title("Severidade por juiz (média das notas)"); _save(fig, out, "07_severidade_juizes")

        key = ["generator", "prompt", "repository", "issue_number"]
        ja, jb = js[0], js[1]
        m = full[full.judge == ja].merge(full[full.judge == jb], on=key, suffixes=("_a", "_b"))
        fig, axs = plt.subplots(1, 3, figsize=(12, 4))
        rng = np.random.default_rng(0)
        for ax, a in zip(axs, ATTR):
            ax.scatter(m[a + "_a"] + rng.normal(0, .08, len(m)), m[a + "_b"] + rng.normal(0, .08, len(m)), s=6, alpha=.25, color=COL[a])
            ax.plot([1, 5], [1, 5], "k--", lw=1); rho = m[[a + "_a", a + "_b"]].corr("spearman").iloc[0, 1]
            ax.set_title(f"{LBL[a]} (ρ={rho:.2f})"); ax.set_xlabel(ja); ax.set_ylabel(jb)
        fig.suptitle("Concordância entre juízes"); _save(fig, out, "08_concordancia_juizes")

        # ranking de modelos muda com o juiz?
        fig, ax = plt.subplots(figsize=(9, 4.5)); x = np.arange(len(order))
        for i, j in enumerate(js):
            t = full[full.judge == j].assign(o=lambda d: d[ATTR].mean(axis=1)).groupby("generator").o.mean()[order]
            ax.bar(x + i * ww, t, ww, label=j)
        ax.set_xticks(x + ww * (len(js) - 1) / 2, order, rotation=30, ha="right"); ax.set_ylim(1, 5); ax.legend()
        ax.set_title("Ranking de modelos por juiz (robustez)"); _save(fig, out, "09_ranking_por_juiz")

    # 10 fidelidade
    if "fidelity" in df and df.fidelity.notna().any():
        f = df.groupby("generator").agg(q=("overall", "mean"), fid=("fidelity", "mean"))
        fig, ax = plt.subplots(figsize=(7, 5.5)); ax.scatter(f.q, f.fid, s=90, color="#7a4fd1")
        for k, (n, r) in enumerate(f.sort_values("q").iterrows()):
            ax.annotate(n, (r.q, r.fid), xytext=(6, 8 + 11 * (k % 3)), textcoords="offset points", fontsize=9)
        ax.set_ylim(1, 5.4); ax.set_xlim(3.2, 4.0)
        ax.set_xlabel("Qualidade ISO média (U,V,S)"); ax.set_ylabel("Fidelidade ao título (1-5)")
        ax.set_title("Qualidade × fidelidade: requisito bom ≠ requisito fiel"); _save(fig, out, "10_qualidade_vs_fidelidade")

    # 11 tamanho e formatação
    fig, axs = plt.subplots(1, 2, figsize=(12, 4.5))
    axs[0].boxplot([gen[gen.generator == g].words for g in order], tick_labels=order, showfliers=False)
    axs[0].tick_params(axis="x", rotation=40); axs[0].set_ylabel("Palavras"); axs[0].set_title("Tamanho do requisito")
    mk = gen.groupby("generator").markdown.mean()[order] * 100
    axs[1].bar(order, mk, color="#c0392b"); axs[1].tick_params(axis="x", rotation=40)
    axs[1].set_ylabel("% de saídas"); axs[1].set_title('Violam "só o requisito" (markdown/título)')
    _save(fig, out, "11_tamanho_formato")

    # 12 multiagente vs single-shot
    if ma_csv and Path(ma_csv).exists():
        ma = pd.read_csv(ma_csv); ma["overall"] = ma[ATTR].mean(axis=1)
        ids = [g for g in order if g in set(ma.generator)]
        if ids:
            single = df[df.prompt == "naive"].groupby("generator").overall.mean()[ids]
            multi = ma.groupby("generator").overall.mean()[ids]
            x = np.arange(len(ids)); fig, ax = plt.subplots(figsize=(7, 4.5))
            ax.bar(x - .2, single, .4, label="Single-shot (naive)"); ax.bar(x + .2, multi, .4, label="Multiagente (gerador↔juiz)")
            ax.set_xticks(x, ids); ax.set_ylim(1, 5); ax.legend(); ax.set_title("Multiagente × geração direta")
            ax.set_ylabel("Nota média (juiz principal)"); _save(fig, out, "12_multiagente_vs_single")
    return sorted(p.name for p in out.glob("*.png"))
