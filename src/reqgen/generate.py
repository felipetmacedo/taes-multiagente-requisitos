"""Fase 1 (réplica do artigo): gera requisitos = modelos x prompts x issues."""
from .common import Appender, done_keys, read_issues
from .llm import Chat
from .prompts import PROMPTS

FIELDS = ["generator", "prompt", "repository", "issue_number", "issue_title", "requirement"]


def run(cfg, issues_path, out, models=None, prompts=None, limit=None, workers=16):
    from concurrent.futures import ThreadPoolExecutor, as_completed
    issues = read_issues(issues_path, limit)
    gens = [g for g in cfg["generators"] if not models or g["id"] in models]
    seen = done_keys(out, ["generator", "prompt", "repository", "issue_number"])
    app = Appender(out, FIELDS)
    temp = cfg["settings"]["temperature"]
    chats = {g["id"]: Chat(cfg, g) for g in gens}

    def work(gid, pname, it):
        return gid, pname, it, chats[gid](PROMPTS[pname], it["Issue Title"], temp)

    jobs = [(g["id"], p, it) for g in gens for p in (prompts or PROMPTS) for it in issues
            if (g["id"], p, it["Repository"], it["Issue Number"]) not in seen]
    import random; random.Random(0).shuffle(jobs)  # intercala modelos: um com rate limit não trava os outros
    print(f"{len(jobs)} chamadas")
    with ThreadPoolExecutor(workers) as ex:
        futs = {ex.submit(work, *j): j for j in jobs}
        for n, f in enumerate(as_completed(futs), 1):
            try:
                gid, pname, it, req = f.result()
            except Exception as e:
                print("  !", futs[f][:2], str(e)[:100]); continue
            app.write(dict(generator=gid, prompt=pname, repository=it["Repository"],
                           issue_number=it["Issue Number"], issue_title=it["Issue Title"],
                           requirement=req.replace("\n", " ")))
            if n % 100 == 0: print(f"{n}/{len(jobs)}")
