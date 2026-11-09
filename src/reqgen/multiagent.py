"""Experimento multiagente pareado.
Loop gerador<->juiz_loop (até 3 iterações). A iteração 1 = controle single-shot (mesmo prompt),
a final = tratamento. Depois `evaluate` re-julga AMBAS com um juiz independente (não-loop) + fidelidade."""
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
from .common import Appender, done_keys, read_issues
from .llm import Chat, parse_json
from .prompts import JUDGE, JUDGE_FIDELITY, MA_FEEDBACK, MA_GEN

FIELDS = ["generator", "loop_judge", "repository", "issue_number", "issue_title", "iteracoes", "status",
          "first_req", "first_u", "first_v", "first_s", "final_req", "final_u", "final_v", "final_s"]
EVAL = ["generator", "eval_judge", "repository", "issue_number", "version", "requirement",
        "unambiguity", "verifiability", "singularity", "fidelity"]


def sample_issues(path, n=50, seed=42):
    df = pd.DataFrame(read_issues(path))
    k = n // df["Repository"].nunique()
    return df.groupby("Repository", group_keys=False).sample(n=k, random_state=seed).to_dict("records")


def one(gen, jud, cfg, title, max_iter=3):
    jt = cfg["settings"]["judge_temperature"]
    fb, best, first = "", None, None
    for t in range(1, max_iter + 1):
        req = gen(MA_GEN, f"Issue: {title}" + (MA_FEEDBACK.format(feedback=fb) if fb else ""),
                  cfg["settings"]["temperature"]).replace("\n", " ")
        try:
            s = parse_json(jud(JUDGE, f"Requirement: {req}", jt, True))
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
    if not best:
        return None
    return dict(iteracoes=best["t"], status="APPROVE" if min(best["u"], best["v"], best["s"]) >= 4 else "REJECT",
                first_req=first["req"], first_u=first["u"], first_v=first["v"], first_s=first["s"],
                final_req=best["req"], final_u=best["u"], final_v=best["v"], final_s=best["s"])


def run(cfg, issues_path, out, gen_ids, loop_judge_id=None, n=50, workers=12):
    specs = {s["id"]: s for s in cfg["generators"] + [cfg["judge"]] + cfg.get("extra_judges", [])}
    jud = Chat(cfg, specs[loop_judge_id or cfg["judge"]["id"]])
    issues = sample_issues(issues_path, n)
    app = Appender(out, FIELDS)
    seen = done_keys(out, ["generator", "repository", "issue_number"])
    gens = {g: Chat(cfg, specs[g]) for g in gen_ids}
    jobs = [(g, it) for g in gen_ids for it in issues if (g, it["Repository"], it["Issue Number"]) not in seen]
    print(f"{len(jobs)} issues x loop")
    with ThreadPoolExecutor(workers) as ex:
        futs = {ex.submit(one, gens[g], jud, cfg, it["Issue Title"]): (g, it) for g, it in jobs}
        for k, f in enumerate(as_completed(futs), 1):
            g, it = futs[f]
            try:
                r = f.result()
            except Exception as e:
                print("  !", g, str(e)[:100]); continue
            if r:
                app.write(dict(generator=g, loop_judge=jud.id, repository=it["Repository"],
                               issue_number=it["Issue Number"], issue_title=it["Issue Title"], **r))
            if k % 20 == 0: print(f"{k}/{len(jobs)}")


def evaluate(cfg, ma_csv, out, eval_judge_id, workers=12):
    specs = {s["id"]: s for s in [cfg["judge"]] + cfg.get("extra_judges", [])}
    ch = Chat(cfg, specs[eval_judge_id])
    rows = list(csv.DictReader(open(ma_csv, encoding="utf-8")))
    seen = done_keys(out, ["generator", "repository", "issue_number", "version"])
    app = Appender(out, EVAL)

    def work(r, ver):
        req = r[f"{ver}_req"]
        s = parse_json(ch(JUDGE, f"Requirement: {req}", 0.0, True))
        f = parse_json(ch(JUDGE_FIDELITY, f"Issue title: {r['issue_title']}\nRequirement: {req}", 0.0, True))
        return r, ver, req, s, f

    jobs = [(r, v) for r in rows for v in ("first", "final")
            if (r["generator"], r["repository"], r["issue_number"], v) not in seen]
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
            if k % 50 == 0: print(f"{k}/{len(jobs)}")
