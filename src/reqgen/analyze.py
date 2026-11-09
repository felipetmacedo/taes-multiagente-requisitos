"""Fase 3: estatística do artigo (descritiva, Kruskal-Wallis+Dunn, Mann-Whitney, Spearman)
+ concordância entre juízes e comparação multiagente x single-shot."""
import itertools
import pandas as pd
from scipy import stats

ATTR = ["unambiguity", "verifiability", "singularity"]


def load(path, judge=None):
    df = pd.read_csv(path)
    if judge:
        df = df[df["judge"] == judge]
    return df


def desc(df, by):
    g = df.groupby(by)[ATTR].agg(["mean", "median", "std"]).round(2)
    g["n"] = df.groupby(by).size()
    return g


def kruskal_by(df, col, attr):
    groups = [x[attr].values for _, x in df.groupby(col)]
    return stats.kruskal(*groups) if len(groups) > 1 else None


def mannwhitney_pairs(df, col, attr):
    out = []
    for a, b in itertools.combinations(sorted(df[col].unique()), 2):
        u, p = stats.mannwhitneyu(df[df[col] == a][attr], df[df[col] == b][attr])
        out.append((a, b, attr, round(p, 4)))
    return pd.DataFrame(out, columns=[col + "_a", col + "_b", "attr", "p"])


def spearman(df):
    rows = []
    for a, b in itertools.combinations(ATTR, 2):
        r, p = stats.spearmanr(df[a], df[b])
        rows.append((a, b, round(r, 2), round(p, 4)))
    return pd.DataFrame(rows, columns=["a", "b", "rho", "p"])


def judge_agreement(df):
    """Spearman + kappa ponderado quadrático entre pares de juízes, por atributo."""
    from sklearn.metrics import cohen_kappa_score  # opcional
    key = ["generator", "prompt", "repository", "issue_number"]
    rows = []
    for ja, jb in itertools.combinations(sorted(df["judge"].unique()), 2):
        m = df[df.judge == ja].merge(df[df.judge == jb], on=key, suffixes=("_a", "_b"))
        for at in ATTR:
            rho, _ = stats.spearmanr(m[at + "_a"], m[at + "_b"])
            k = cohen_kappa_score(m[at + "_a"], m[at + "_b"], weights="quadratic")
            rows.append((ja, jb, at, len(m), round(rho, 2), round(k, 2)))
    return pd.DataFrame(rows, columns=["judge_a", "judge_b", "attr", "n", "spearman", "wkappa"])


def report(gen_judged_csv, judge=None, ma_csv=None):
    df = load(gen_judged_csv, judge)
    out = ["# Resultados\n", f"N avaliações: {len(df)}\n"]
    out.append("## Por gerador\n" + desc(df, "generator").to_markdown())
    out.append("\n## Por prompt\n" + desc(df, "prompt").to_markdown())
    out.append("\n## Gerador x prompt\n" + desc(df, ["generator", "prompt"]).to_markdown())
    for col in ["generator", "prompt"]:
        out.append(f"\n## Kruskal-Wallis por {col}")
        for at in ATTR:
            k = kruskal_by(df, col, at)
            out.append(f"- {at}: H={k.statistic:.2f}, p={k.pvalue:.4g}" if k else f"- {at}: n/a")
    try:
        import scikit_posthocs as sp
        for at in ATTR:
            d = sp.posthoc_dunn(df, val_col=at, group_col="prompt", p_adjust="bonferroni")
            out.append(f"\n### Dunn (Bonferroni) prompt — {at}\n" + d.round(4).to_markdown())
    except ImportError:
        pass
    out.append("\n## Spearman entre atributos\n" + spearman(df).to_markdown(index=False))
    if "fidelity" in df and df["fidelity"].notna().any():
        out.append("\n## Fidelidade ao título (extensão)\n" + df.groupby("generator")["fidelity"].mean().round(2).to_markdown())
    full = load(gen_judged_csv)
    if full["judge"].nunique() > 1:
        out.append("\n## Concordância entre juízes\n" + judge_agreement(full).to_markdown(index=False))
        out.append("\n## Média por juiz (viés de severidade)\n" + full.groupby("judge")[ATTR].mean().round(2).to_markdown())
    if ma_csv:
        ma = pd.read_csv(ma_csv)
        out.append("\n## Multiagente (gerador<->juiz)\n" + ma.groupby("generator").agg(
            aprovados=("status", lambda s: (s == "APPROVE").mean().round(2)),
            iter_media=("iteracoes", "mean"), U=("unambiguity", "mean"),
            V=("verifiability", "mean"), S=("singularity", "mean")).round(2).to_markdown())
    return "\n".join(out)
