"""Fase 2: LLM-as-a-Judge (U/V/S 1-5) + fidelidade opcional. Aceita vários juízes."""
import csv
from .common import Appender, done_keys
from .llm import Chat, parse_json
from .prompts import JUDGE, JUDGE_FIDELITY

FIELDS = ["judge", "generator", "prompt", "repository", "issue_number", "requirement",
          "unambiguity", "verifiability", "singularity", "fidelity", "explanation"]


def run(cfg, gen_csv, out, judge_ids=None, fidelity=False, limit=None, workers=16, only_csv=None):
    from concurrent.futures import ThreadPoolExecutor, as_completed
    specs = [cfg["judge"]] + cfg.get("extra_judges", [])
    specs = [s for s in specs if not judge_ids or s["id"] in judge_ids]
    rows = list(csv.DictReader(open(gen_csv, encoding="utf-8")))
    rows = rows[:limit] if limit else rows
    if only_csv:  # restringe às linhas já presentes em outro CSV (ex.: amostra balanceada)
        keep = {(r["generator"], r["prompt"], r["repository"], r["issue_number"]) for r in csv.DictReader(open(only_csv, encoding="utf-8"))}
        rows = [r for r in rows if (r["generator"], r["prompt"], r["repository"], r["issue_number"]) in keep]
    seen = done_keys(out, ["judge", "generator", "prompt", "repository", "issue_number"])
    app = Appender(out, FIELDS)
    chats = {s["id"]: Chat(cfg, s) for s in specs}
    jt = cfg["settings"]["judge_temperature"]

    def work(jid, r):
        chat = chats[jid]
        s = parse_json(chat(JUDGE, f"Requirement: {r['requirement']}", jt, True))
        fid = ""
        if fidelity:
            fid = parse_json(chat(JUDGE_FIDELITY, f"Issue title: {r['issue_title']}\nRequirement: {r['requirement']}",
                                  0.0, True)).get("fidelity", "")
        return jid, r, s, fid

    jobs = [(sp["id"], r) for sp in specs for r in rows if r["requirement"] and
            (sp["id"], r["generator"], r["prompt"], r["repository"], r["issue_number"]) not in seen]
    print(f"{len(jobs)} julgamentos")
    with ThreadPoolExecutor(workers) as ex:
        futs = {ex.submit(work, *j): j for j in jobs}
        for n, f in enumerate(as_completed(futs), 1):
            try:
                jid, r, s, fid = f.result()
                app.write(dict(judge=jid, generator=r["generator"], prompt=r["prompt"],
                               repository=r["repository"], issue_number=r["issue_number"],
                               requirement=r["requirement"], unambiguity=s["unambiguity"],
                               verifiability=s["verifiability"], singularity=s["singularity"],
                               fidelity=fid, explanation=str(s.get("explanation", "")).replace("\n", " ")))
            except Exception as e:
                print("  !", str(e)[:100])
            if n % 100 == 0: print(f"{n}/{len(jobs)}")
