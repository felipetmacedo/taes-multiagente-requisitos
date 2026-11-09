import argparse, sys
from pathlib import Path
from dotenv import load_dotenv
from . import specialists, analyze, plots, generate, judge, multiagent
from .llm import ROOT, load_config

R = ROOT / "results"
ISS = ROOT / "data" / "issues.csv"


def main():
    load_dotenv(ROOT / ".env")
    p = argparse.ArgumentParser(prog="reqgen")
    sub = p.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("generate"); g.add_argument("--models", nargs="*"); g.add_argument("--prompts", nargs="*"); g.add_argument("--limit", type=int)
    j = sub.add_parser("judge"); j.add_argument("--judges", nargs="*"); j.add_argument("--fidelity", action="store_true"); j.add_argument("--limit", type=int); j.add_argument("--only")
    m = sub.add_parser("multiagent"); m.add_argument("--gens", nargs="+", required=True); m.add_argument("--judge"); m.add_argument("--n", type=int, default=50)
    me = sub.add_parser("ma-eval"); me.add_argument("--judge", required=True)
    a = sub.add_parser("analyze"); a.add_argument("--file", default="judged.csv"); a.add_argument("--judge"); a.add_argument("--ma", action="store_true")
    b = sub.add_parser("balance"); b.add_argument("--n", type=int)
    sp = sub.add_parser("specialists"); sp.add_argument("--gen", default="deepseek-v4.1-flash"); sp.add_argument("--judge", default="qwen-judge"); sp.add_argument("--limit", type=int); sp.add_argument("--reuse", action="store_true"); sp.add_argument("--out", default="specialists.csv")
    se = sub.add_parser("sp-eval"); se.add_argument("--inp", required=True); se.add_argument("--out", required=True); se.add_argument("--judge", default="command-a-plus")
    pl = sub.add_parser("plots"); pl.add_argument("--file", default="judged.csv")
    p.add_argument("--config")
    x = p.parse_args()
    cfg = load_config(x.config)
    if x.cmd == "generate":
        generate.run(cfg, ISS, R / "generated.csv", x.models, x.prompts, x.limit)
    elif x.cmd == "judge":
        judge.run(cfg, R / "generated.csv", R / "judged.csv", x.judges, x.fidelity, x.limit, only_csv=(R / x.only if x.only else None))
    elif x.cmd == "multiagent":
        multiagent.run(cfg, ISS, R / "multiagent.csv", x.gens, x.judge, x.n)
    elif x.cmd == "specialists":
        specialists.run(cfg, ISS, R / x.out, x.gen, x.judge, x.limit, reuse_csv=(R / "generated.csv" if x.reuse else None))
    elif x.cmd == "sp-eval":
        specialists.evaluate(cfg, R / x.inp, R / x.out, x.judge)
    elif x.cmd == "ma-eval":
        multiagent.evaluate(cfg, R / "multiagent.csv", R / "multiagent_eval.csv", x.judge)
    elif x.cmd == "balance":
        import pandas as pd
        d = pd.read_csv(R / "judged.csv"); d = d[d.judge == cfg["judge"]["id"]]
        n = x.n or int(d.groupby(["generator", "prompt"]).size().min())
        d = d.groupby(["generator", "prompt"], group_keys=False).sample(n=n, random_state=42)
        d.to_csv(R / "judged_balanced.csv", index=False); print(f"n={n} por célula, {len(d)} linhas")
    elif x.cmd == "plots":
        print(plots.make_all(R / x.file, R / "generated.csv", R / "figures", cfg["judge"]["id"], R / "multiagent.csv"))
    elif x.cmd == "analyze":
        txt = analyze.report(R / x.file, x.judge or cfg["judge"]["id"], R / "multiagent.csv" if x.ma else None)
        (R / "report.md").write_text(txt, encoding="utf-8"); print(txt)


if __name__ == "__main__":
    main()
