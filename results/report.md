# Resultados

N avaliações: 408

## Por gerador
| generator           |   ('unambiguity', 'mean') |   ('unambiguity', 'median') |   ('unambiguity', 'std') |   ('verifiability', 'mean') |   ('verifiability', 'median') |   ('verifiability', 'std') |   ('singularity', 'mean') |   ('singularity', 'median') |   ('singularity', 'std') |   ('n', '') |
|:--------------------|--------------------------:|----------------------------:|-------------------------:|----------------------------:|------------------------------:|---------------------------:|--------------------------:|----------------------------:|-------------------------:|------------:|
| claude-haiku-5.5    |                      4.16 |                           4 |                     0.5  |                        4.16 |                             4 |                       0.86 |                      2.88 |                           2 |                     1.41 |          51 |
| deepseek-v4.1-flash |                      3.78 |                           4 |                     0.83 |                        3.73 |                             4 |                       1.3  |                      3.08 |                           2 |                     1.43 |          51 |
| gemini-3.8-flash    |                      3.51 |                           4 |                     0.81 |                        3.27 |                             3 |                       1.3  |                      3.41 |                           3 |                     1.42 |          51 |
| glm-5.3-flash       |                      3.88 |                           4 |                     0.84 |                        3.94 |                             5 |                       1.32 |                      3.18 |                           2 |                     1.37 |          51 |
| gpt-6-luna          |                      3.63 |                           4 |                     0.8  |                        3.35 |                             3 |                       1.23 |                      3.96 |                           5 |                     1.43 |          51 |
| minimax-m3.1-flash  |                      3.96 |                           4 |                     0.8  |                        4.08 |                             5 |                       1.2  |                      3.16 |                           2 |                     1.47 |          51 |
| mistral-large-4     |                      3.82 |                           4 |                     0.82 |                        3.88 |                             4 |                       1.21 |                      3.45 |                           3 |                     1.42 |          51 |
| qwen3.8-flash       |                      3.51 |                           4 |                     0.92 |                        3.31 |                             3 |                       1.3  |                      3.94 |                           5 |                     1.38 |          51 |

## Por prompt
| prompt   |   ('unambiguity', 'mean') |   ('unambiguity', 'median') |   ('unambiguity', 'std') |   ('verifiability', 'mean') |   ('verifiability', 'median') |   ('verifiability', 'std') |   ('singularity', 'mean') |   ('singularity', 'median') |   ('singularity', 'std') |   ('n', '') |
|:---------|--------------------------:|----------------------------:|-------------------------:|----------------------------:|------------------------------:|---------------------------:|--------------------------:|----------------------------:|-------------------------:|------------:|
| expert   |                      4.15 |                           4 |                     0.59 |                        4.39 |                             5 |                       0.77 |                      2.82 |                           2 |                     1.24 |         136 |
| fewshot  |                      3.22 |                           3 |                     0.83 |                        2.79 |                             2 |                       1.29 |                      4.26 |                           5 |                     1.25 |         136 |
| naive    |                      3.98 |                           4 |                     0.7  |                        3.96 |                             4 |                       1.06 |                      3.07 |                           2 |                     1.43 |         136 |

## Gerador x prompt
|                                    |   ('unambiguity', 'mean') |   ('unambiguity', 'median') |   ('unambiguity', 'std') |   ('verifiability', 'mean') |   ('verifiability', 'median') |   ('verifiability', 'std') |   ('singularity', 'mean') |   ('singularity', 'median') |   ('singularity', 'std') |   ('n', '') |
|:-----------------------------------|--------------------------:|----------------------------:|-------------------------:|----------------------------:|------------------------------:|---------------------------:|--------------------------:|----------------------------:|-------------------------:|------------:|
| ('claude-haiku-5.5', 'expert')     |                      4.24 |                           4 |                     0.56 |                        4.41 |                             4 |                       0.62 |                      1.94 |                           2 |                     0.24 |          17 |
| ('claude-haiku-5.5', 'fewshot')    |                      3.88 |                           4 |                     0.33 |                        3.65 |                             4 |                       1    |                      4.41 |                           5 |                     1.06 |          17 |
| ('claude-haiku-5.5', 'naive')      |                      4.35 |                           4 |                     0.49 |                        4.41 |                             5 |                       0.71 |                      2.29 |                           2 |                     1.1  |          17 |
| ('deepseek-v4.1-flash', 'expert')  |                      4.35 |                           4 |                     0.49 |                        4.71 |                             5 |                       0.47 |                      2.41 |                           2 |                     1    |          17 |
| ('deepseek-v4.1-flash', 'fewshot') |                      3.24 |                           3 |                     0.83 |                        2.71 |                             2 |                       1.31 |                      4.41 |                           5 |                     1.18 |          17 |
| ('deepseek-v4.1-flash', 'naive')   |                      3.76 |                           4 |                     0.75 |                        3.76 |                             4 |                       1.09 |                      2.41 |                           2 |                     1.06 |          17 |
| ('gemini-3.8-flash', 'expert')     |                      3.76 |                           4 |                     0.56 |                        4    |                             4 |                       0.94 |                      2.82 |                           2 |                     1.07 |          17 |
| ('gemini-3.8-flash', 'fewshot')    |                      2.88 |                           3 |                     0.78 |                        2.29 |                             2 |                       1.26 |                      4.12 |                           5 |                     1.41 |          17 |
| ('gemini-3.8-flash', 'naive')      |                      3.88 |                           4 |                     0.7  |                        3.53 |                             3 |                       1.07 |                      3.29 |                           2 |                     1.49 |          17 |
| ('glm-5.3-flash', 'expert')        |                      4.29 |                           4 |                     0.47 |                        4.71 |                             5 |                       0.69 |                      2.59 |                           2 |                     0.94 |          17 |
| ('glm-5.3-flash', 'fewshot')       |                      3.12 |                           3 |                     0.86 |                        2.71 |                             2 |                       1.36 |                      4    |                           5 |                     1.37 |          17 |
| ('glm-5.3-flash', 'naive')         |                      4.24 |                           4 |                     0.56 |                        4.41 |                             5 |                       0.8  |                      2.94 |                           2 |                     1.39 |          17 |
| ('gpt-6-luna', 'expert')           |                      4.12 |                           4 |                     0.6  |                        4.12 |                             4 |                       0.78 |                      3.65 |                           4 |                     1.41 |          17 |
| ('gpt-6-luna', 'fewshot')          |                      3.29 |                           3 |                     0.77 |                        2.71 |                             2 |                       1.21 |                      4.59 |                           5 |                     1.18 |          17 |
| ('gpt-6-luna', 'naive')            |                      3.47 |                           4 |                     0.8  |                        3.24 |                             3 |                       1.25 |                      3.65 |                           5 |                     1.54 |          17 |
| ('minimax-m3.1-flash', 'expert')   |                      4.41 |                           4 |                     0.62 |                        4.71 |                             5 |                       0.47 |                      2.82 |                           2 |                     1.38 |          17 |
| ('minimax-m3.1-flash', 'fewshot')  |                      3.41 |                           4 |                     0.87 |                        3.06 |                             3 |                       1.48 |                      3.94 |                           5 |                     1.48 |          17 |
| ('minimax-m3.1-flash', 'naive')    |                      4.06 |                           4 |                     0.56 |                        4.47 |                             5 |                       0.62 |                      2.71 |                           2 |                     1.31 |          17 |
| ('mistral-large-4', 'expert')      |                      4.18 |                           4 |                     0.53 |                        4.59 |                             5 |                       0.62 |                      2.65 |                           2 |                     1.17 |          17 |
| ('mistral-large-4', 'fewshot')     |                      3.12 |                           3 |                     0.86 |                        2.82 |                             2 |                       1.29 |                      4.53 |                           5 |                     0.94 |          17 |
| ('mistral-large-4', 'naive')       |                      4.18 |                           4 |                     0.53 |                        4.24 |                             4 |                       0.83 |                      3.18 |                           2 |                     1.42 |          17 |
| ('qwen3.8-flash', 'expert')        |                      3.82 |                           4 |                     0.64 |                        3.88 |                             4 |                       0.99 |                      3.65 |                           4 |                     1.41 |          17 |
| ('qwen3.8-flash', 'fewshot')       |                      2.82 |                           3 |                     0.88 |                        2.41 |                             2 |                       1.18 |                      4.12 |                           5 |                     1.36 |          17 |
| ('qwen3.8-flash', 'naive')         |                      3.88 |                           4 |                     0.86 |                        3.65 |                             4 |                       1.27 |                      4.06 |                           5 |                     1.39 |          17 |

## Kruskal-Wallis por generator
- unambiguity: H=28.32, p=0.0001927
- verifiability: H=29.46, p=0.000119
- singularity: H=27.20, p=0.000307

## Kruskal-Wallis por prompt
- unambiguity: H=95.40, p=1.927e-21
- verifiability: H=106.10, p=9.138e-24
- singularity: H=73.33, p=1.19e-16

### Dunn (Bonferroni) prompt — unambiguity
|         |   expert |   fewshot |   naive |
|:--------|---------:|----------:|--------:|
| expert  |   1      |         0 |  0.2932 |
| fewshot |   0      |         1 |  0      |
| naive   |   0.2932 |         0 |  1      |

### Dunn (Bonferroni) prompt — verifiability
|         |   expert |   fewshot |   naive |
|:--------|---------:|----------:|--------:|
| expert  |   1      |         0 |  0.0096 |
| fewshot |   0      |         1 |  0      |
| naive   |   0.0096 |         0 |  1      |

### Dunn (Bonferroni) prompt — singularity
|         |   expert |   fewshot |   naive |
|:--------|---------:|----------:|--------:|
| expert  |   1      |         0 |  0.5305 |
| fewshot |   0      |         1 |  0      |
| naive   |   0.5305 |         0 |  1      |

## Spearman entre atributos
| a             | b             |   rho |      p |
|:--------------|:--------------|------:|-------:|
| unambiguity   | verifiability |  0.69 | 0      |
| unambiguity   | singularity   | -0.03 | 0.6084 |
| verifiability | singularity   | -0.08 | 0.0979 |

## Fidelidade ao título (extensão)
| generator           |   fidelity |
|:--------------------|-----------:|
| claude-haiku-5.5    |       4.96 |
| deepseek-v4.1-flash |       5    |
| gemini-3.8-flash    |       4.96 |
| glm-5.3-flash       |       4.94 |
| gpt-6-luna          |       5    |
| minimax-m3.1-flash  |       5    |
| mistral-large-4     |       4.96 |
| qwen3.8-flash       |       5    |