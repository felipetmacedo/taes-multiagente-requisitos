"""Arquitetura do deck: 3 agentes especialistas -> consolidador -> juiz (pode rejeitar), até 3 rodadas.
Registra iterações, tokens, tempo, chamadas e motivos de rejeição por requisito."""
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from .common import Appender, done_keys, read_issues
from .llm import Chat, parse_json
from .prompts import JUDGE

OUT = "Output only one requirement sentence starting with \"The system shall\". No explanations. Do not invent features, numbers or scope that the issue title does not imply."
AG_U = ("You are a requirements engineer specialised in UNAMBIGUITY (ISO/IEC/IEEE 29148). Rewrite the issue as a requirement "
        "that has a single possible interpretation: replace vague terms with precise, concrete wording. " + OUT)
AG_S = ("You are a requirements engineer specialised in SINGULARITY (ISO/IEC/IEEE 29148). Rewrite the issue as a requirement "
        "that states exactly ONE capability: cut extra scope and anything not central. " + OUT)
AG_V = ("You are a requirements engineer specialised in VERIFIABILITY (ISO/IEC/IEEE 29148). Rewrite the issue as a requirement "
        "that can be tested: make the condition, the criterion and the expected result explicit. " + OUT)
CONSOL = ("You consolidate three proposals (unambiguity, singularity, verifiability) for the same issue into ONE requirement. "
          "Resolve conflicts between them; prioritise a single capability that is unambiguous and testable. " + OUT)

CONSOL_REUSE = ("You consolidate three candidate requirements (A, B, C) for the same issue into ONE requirement. "
                "Keep the focus of A (one capability) and the testability/precision of B; resolve conflicts. " + OUT)

FIELDS = ["generator", "loop_judge", "repository", "issue_number", "issue_title", "iteracoes", "status",
          "first_round_approved", "tokens", "calls", "seconds", "requirement", "unambiguity", "verifiability",
          "singularity", "first_requirement", "first_u", "first_v", "first_s", "rejection_reasons"]


def one(gen, jud, cfg, title, max_iter=3, reuse=None):
    t0 = time.time()
    tg0, cg0 = gen.usage(); tj0, cj0 = jud.usage()
    T, J = cfg["settings"]["temperature"], cfg["settings"]["judge_temperature"]
    fb, best, first, reasons = "", None, None, []
    for t in range(1, max_iter + 1):
        extra = f"\nJudge feedback to fix: {fb}" if fb else ""
        user = f"Issue title: {title}{extra}"
        if reuse:  # híbrido: Fase 1 reaproveitada (propostas já geradas), só consolidador+juiz são novos
            req = gen(CONSOL_REUSE, f"Issue title: {title}\nProposal A (few-shot prompt, strong on singularity): {reuse['fewshot']}\n"
                                    f"Proposal B (expert prompt, strong on verifiability/unambiguity): {reuse['expert']}\n"
                                    f"Proposal C (naive prompt): {reuse['naive']}{extra}", T).replace("\n", " ")
        else:
            props = [gen(a, user, T).replace("\n", " ") for a in (AG_U, AG_S, AG_V)]
            req = gen(CONSOL, f"Issue title: {title}\nUnambiguity proposal: {props[0]}\nSingularity proposal: {props[1]}\n"
                              f"Verifiability proposal: {props[2]}{extra}", T).replace("\n", " ")
        try:
            s = parse_json(jud(JUDGE, f"Requirement: {req}", J, True))
            u, v, g = int(s["unambiguity"]), int(s["verifiability"]), int(s["singularity"])
        except Exception:
            fb = "Make it shorter, simpler and easier to test."
            continue
        cur = dict(req=req, u=u, v=v, s=g, t=t)
        first = first or cur
        if best is None or u + v + g >= best["u"] + best["v"] + best["s"]:
            best = cur
        if min(u, v, g) >= 4:
            break
        fb = str(s.get("explanation", ""))
        reasons.append(fb.replace("\n", " "))
    if not best:
        return None
    tg1, cg1 = gen.usage(); tj1, cj1 = jud.usage()
    ok = min(best["u"], best["v"], best["s"]) >= 4
    return dict(iteracoes=best["t"], status="APPROVE" if ok else "REJECT",
                first_round_approved=int(min(first["u"], first["v"], first["s"]) >= 4),
                tokens=(tg1 - tg0) + (tj1 - tj0), calls=(cg1 - cg0) + (cj1 - cj0), seconds=round(time.time() - t0, 1),
                requirement=best["req"], unambiguity=best["u"], verifiability=best["v"], singularity=best["s"],
                first_requirement=first["req"], first_u=first["u"], first_v=first["v"], first_s=first["s"],
                rejection_reasons=" || ".join(reasons))


def run(cfg, issues_path, out, gen_id, judge_id, limit=None, workers=12, reuse_csv=None):
    specs = {s["id"]: s for s in cfg["generators"] + [cfg["judge"]] + cfg.get("extra_judges", [])}
    gen, jud = Chat(cfg, specs[gen_id]), Chat(cfg, specs[judge_id])
    issues = read_issues(issues_path)
    if limit:  # amostra estratificada por repositório (mesma semente => mesmas issues sempre)
        import pandas as pd
        df = pd.DataFrame(issues); k = max(1, limit // df["Repository"].nunique())
        issues = df.groupby("Repository", group_keys=False).sample(n=k, random_state=42).to_dict("records")
    app = Appender(out, FIELDS)
    seen = done_keys(out, ["repository", "issue_number"])
    jobs = [it for it in issues if (it["Repository"], it["Issue Number"]) not in seen]
    R = {}
    if reuse_csv:
        import csv
        for r in csv.DictReader(open(reuse_csv, encoding="utf-8")):
            if r["generator"] == gen_id:
                R.setdefault((r["repository"], r["issue_number"]), {})[r["prompt"]] = r["requirement"]
        jobs = [it for it in jobs if len(R.get((it["Repository"], it["Issue Number"]), {})) == 3]
    print(f"{len(jobs)} issues ({'híbrido: Fase 1 reaproveitada' if reuse_csv else '5 agentes'})")
    with ThreadPoolExecutor(workers) as ex:
        futs = {ex.submit(one, gen, jud, cfg, it["Issue Title"], 3, R.get((it["Repository"], it["Issue Number"]))): it for it in jobs}
        for k, f in enumerate(as_completed(futs), 1):
            it = futs[f]
            try:
                r = f.result()
            except Exception as e:
                print("  !", str(e)[:100]); continue
            if r:
                app.write(dict(generator=gen_id, loop_judge=jud.id, repository=it["Repository"],
                               issue_number=it["Issue Number"], issue_title=it["Issue Title"], **r))
            if k % 10 == 0: print(f"{k}/{len(jobs)}")


EVAL = ["generator", "eval_judge", "repository", "issue_number", "version", "requirement",
        "unambiguity", "verifiability", "singularity", "fidelity"]


def evaluate(cfg, in_csv, out, eval_judge_id, workers=12):
    """Juiz INDEPENDENTE (não é o do loop) avalia a saída final e a 1ª consolidação (sem loop)."""
    import csv
    from .prompts import JUDGE_FIDELITY
    specs = {s["id"]: s for s in [cfg["judge"]] + cfg.get("extra_judges", [])}
    ch = Chat(cfg, specs[eval_judge_id])
    rows = list(csv.DictReader(open(in_csv, encoding="utf-8")))
    seen = done_keys(out, ["repository", "issue_number", "version"])
    app = Appender(out, EVAL)

    def work(r, ver, col):
        req = r[col]
        s = parse_json(ch(JUDGE, f"Requirement: {req}", 0.0, True))
        f = parse_json(ch(JUDGE_FIDELITY, f"Issue title: {r['issue_title']}\nRequirement: {req}", 0.0, True))
        return r, ver, req, s, f

    jobs = [(r, v, c) for r in rows for v, c in (("final", "requirement"), ("first", "first_requirement"))
            if (r["repository"], r["issue_number"], v) not in seen]
    print(f"{len(jobs)} avaliações independentes")
    with ThreadPoolExecutor(workers) as ex:
        futs = [ex.submit(work, *j) for j in jobs]
        for k, f in enumerate(as_completed(futs), 1):
            try:
                r, ver, req, s, fi = f.result()
                app.write(dict(generator=r["generator"], eval_judge=ch.id, repository=r["repository"],
                               issue_number=r["issue_number"], version=ver, requirement=req,
                               unambiguity=s["unambiguity"], verifiability=s["verifiability"],
                               singularity=s["singularity"], fidelity=fi.get("fidelity", "")))
            except Exception as e:
                print("  !", str(e)[:100])
