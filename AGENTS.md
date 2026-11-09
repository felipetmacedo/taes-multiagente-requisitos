# reqgen — réplica e extensão de Paiva et al. (2026)

Gera requisitos ISO 29148 a partir de títulos de issues (150 issues, 5 repos OSS), avalia com LLM-as-a-Judge (unambiguity/verifiability/singularity 1-5) e compara vários modelos (o artigo só usou o3-mini e DeepSeek-R1).

- Código: `src/reqgen/` (generate, judge, multiagent, analyze, cli). Config de modelos: `config/models.yaml`.
- Dados: `data/issues.csv`. Saídas: `results/` (gitignored). Referências: `reference/` (artigo, baseline do notebook).
- Rodar: `PYTHONPATH=src .venv/bin/python -m reqgen.cli <generate|judge|multiagent|analyze>`. Testes: `PYTHONPATH=src .venv/bin/pytest`.
- Chaves em `.env` (ver `.env.example`). Nunca commitar.
- Prompts em inglês, idênticos ao artigo, p/ comparabilidade.
