import json, os, re, threading, time
from pathlib import Path
import yaml
from openai import OpenAI

ROOT = Path(__file__).resolve().parents[2]


def load_config(path=None):
    cfg = yaml.safe_load(open(path or ROOT / "config" / "models.yaml"))
    return cfg


def clean(text: str) -> str:
    text = re.sub(r"<think>.*?</think>", "", text or "", flags=re.DOTALL)
    return text.strip()


class Chat:
    """Cliente único p/ qualquer provedor compatível com OpenAI."""

    def __init__(self, cfg: dict, spec: dict):
        prov = cfg["providers"][spec["provider"]]
        key = os.environ.get(prov["key_env"])
        if not key:
            raise RuntimeError(f"Defina {prov['key_env']} (modelo {spec['id']})")
        self.client = OpenAI(base_url=prov["base_url"], api_key=key, timeout=120, max_retries=0)
        self.model, self.id = spec["model"], spec["id"]
        self.s = cfg["settings"]
        self._tl = threading.local()

    def usage(self):
        return getattr(self._tl, 'tokens', 0), getattr(self._tl, 'calls', 0)

    def __call__(self, system: str, user: str, temperature: float, json_mode=False) -> str:
        kw = dict(model=self.model, temperature=temperature,
                  messages=[{"role": "system", "content": system}, {"role": "user", "content": user}])
        if self.s.get("seed") is not None:
            kw["seed"] = self.s["seed"]
        if json_mode:
            kw["response_format"] = {"type": "json_object"}
        err = None
        for i in range(self.s["max_retries"]):
            try:
                out = self.client.chat.completions.create(**kw)
                self._tl.calls = getattr(self._tl, 'calls', 0) + 1
                self._tl.tokens = getattr(self._tl, 'tokens', 0) + (getattr(out.usage, 'total_tokens', 0) or 0)
                time.sleep(self.s.get("sleep_between_calls", 0))
                return clean(out.choices[0].message.content)
            except Exception as e:  # rate limit / instabilidade
                err = e
                # alguns provedores rejeitam json_mode/seed: tenta sem
                kw.pop("response_format", None) if json_mode and i == 0 else None
                time.sleep(30 if '429' in str(e) else 5 * (i + 1))
        raise RuntimeError(f"{self.id}: falhou após retries: {str(err)[:200]}")


def parse_json(text: str) -> dict:
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if not m:
        raise ValueError("sem JSON")
    return json.loads(m.group(0))
