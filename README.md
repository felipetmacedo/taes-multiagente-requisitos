# reqgen

Validação multi-modelo do artigo *From issue titles to requirements* (Paiva et al., 2026).

## Setup
```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
cp .env.example .env   # preencha as chaves (OpenRouter cobre quase todos os modelos)
export PYTHONPATH=src
```
Edite `config/models.yaml` (modelos, juízes). Confira os slugs no provedor.

## Fluxo
```bash
python -m reqgen.cli generate --limit 5                 # teste barato
python -m reqgen.cli generate                           # modelos x 3 prompts x 150 issues
python -m reqgen.cli judge --fidelity                   # juiz principal (+ fidelidade ao título)
python -m reqgen.cli judge --judges gpt-oss-120b-judge gemini-judge   # juízes extras
python -m reqgen.cli multiagent --gen gpt-oss-120b      # pipeline gerador<->juiz do notebook
python -m reqgen.cli analyze --ma                       # results/report.md
```
Todas as etapas são retomáveis (pulam o que já está no CSV).

## Resultados principais (DeepSeek v4.1 flash, 150 issues, juiz independente Cohere)
| | Média | 3 critérios ≥ 4 |
|---|---|---|
| Melhor prompt único (Expert) | 3,80 | 17% |
| Multiagente híbrido (150 issues) | 4,04 | 49% |
| 5 agentes reais (30 issues) | 4,30 | 67% |

Multiagente vence na média (p < 0,001) e reduz o trade-off, mas **não** vence o melhor prompt em cada critério isolado; o ganho vem do ciclo de revisão do juiz. Híbrido = Fase 1 reaproveitada (propostas naive/few-shot/expert já geradas) + consolidador + juiz Qwen. Detalhes em `deck/TAES_Multiagente.html`.

```bash
python -m reqgen.cli specialists --reuse --out hybrid.csv             # híbrido (150 issues)
python -m reqgen.cli sp-eval --inp hybrid.csv --out hybrid_eval.csv   # avaliação independente (Cohere)
python -m reqgen.cli specialists --out specialists5.csv --limit 30    # 5 agentes reais
python deck/build_deck.py                                             # regera o deck com os números
```
`multiagent`/`ma-eval` = ablação de loop simples gerador↔juiz (8 modelos, `results/ablation_loop_simples*.csv`).

## O que é novo vs. artigo
1. Mais geradores (config), não só DeepSeek/o3-mini.
2. Vários juízes + concordância (Spearman, kappa ponderado) → testa viés do juiz.
3. Métrica de fidelidade ao título: o baseline multiagente tirou 5/5/5 em requisitos inventados (ex.: issue #77764 "MPS op coverage" virou "% cobertura de linhas a cada 5 min").
4. Pipeline multiagente comparável a single-shot.

Custo: 8 geradores x 3 prompts x 150 = 3600 gerações + 3600 julgamentos por juiz.
