"""Prompts do artigo (Paiva et al., 2026) + prompts do pipeline multiagente."""

NAIVE = (
    "You are given a feature request from an open-source software project's issue tracker. "
    "Generate a clear, concise, and self-contained software requirement statement that captures "
    "the intended feature.\nOutput only the finalized requirement statement. "
    "Do not include explanations or commentary."
)

FEWSHOT = (
    "Here are examples of feature requests from an open-source software project's issue tracker "
    "along with their corresponding software requirements.\n"
    "Based on these examples, analyze new feature requests and generate the requirement.\n"
    "Output only the finalized requirement statement. Do not include explanations or commentary.\n"
    "Feature request: Limit GPU memory usage during prediction.\n"
    "Requirement: The system shall provide an option to limit GPU memory usage during prediction.\n"
    "Feature request: Reset password\n"
    "Requirement: The system must provide a functional \"forgot password\" link that allows users "
    "to reset their passwords securely.\n"
    "Feature request: Make the application use vector search.\n"
    "Requirement: The system shall use vector search to improve search performance."
)

EXPERT = (
    "You are a Software Requirements Engineer with deep expertise in analyzing feature requests "
    "in open-source software projects. Your task is to generate a clear, complete, and actionable "
    "software requirement from informal feature requests found in OSS issue trackers.\n"
    "Output only the finalized requirement statement. Do not include explanations or commentary."
)

PROMPTS = {"naive": NAIVE, "fewshot": FEWSHOT, "expert": EXPERT}

JUDGE = """As an experienced requirements engineer, your task is to evaluate the quality of a given software requirement based on the following criteria:
Unambiguity: The requirement is stated in such a way so that it can be interpreted in only one way. The requirement is stated simply and is easy to understand. Score 1 if the requirement is highly ambiguous and 5 if there is no room for multiple interpretations.
Verifiability: The requirement is structured and worded such that its realization can be proven (verified) to the customer's satisfaction at the level the requirements exists. Verifiability is enhanced when the requirement is measurable. Score 1 if the requirement is difficult to verify, and 5 if it is easily measurable.
Singularity: The requirement states a single capability, characteristic, constraint or quality factor. Score 1 if the requirement includes several needs or is unclear in its focus, and 5 if it is entirely singular in nature.
For each criterion, provide a score from 1 to 5, with 1 being the lowest (poor) and 5 being the highest (excellent). Structure your output as a JSON object containing the scores and a combined explanation for your ratings:
{"unambiguity": <1-5>, "verifiability": <1-5>, "singularity": <1-5>, "explanation": "<short text>"}
Output only the JSON object."""

# Extensão (não está no artigo): mede se o requisito ainda reflete o título da issue.
# Motivo: no baseline multiagente, a issue "General MPS op coverage tracking issue"
# virou "registrar % de cobertura de linhas de código a cada 5 min" — nota 5/5/5, mas infiel.
JUDGE_FIDELITY = """You compare a software requirement against the GitHub issue title it was derived from.
Score FIDELITY from 1 to 5: 5 = the requirement captures the intent of the title with no invented scope;
1 = the requirement is unrelated to the title or invents unrelated features/numbers.
Output only JSON: {"fidelity": <1-5>, "explanation": "<short text>"}"""

# Pipeline multiagente (gerador <-> juiz com feedback), como no notebook.
MA_GEN = (
    "You are a requirements engineer. Write ONE software requirement from the issue title.\n"
    "ISO/IEC/IEEE 29148: start with \"The system shall\"; unambiguous; singular (one capability, "
    "max 30 words); binary-verifiable. Do NOT invent numbers or scope absent from the title.\n"
    "Output only the requirement sentence."
)
MA_FEEDBACK = "\nFix the flaw pointed out by the judge: {feedback}\nKeep it focused and singular; do not invent scope."
