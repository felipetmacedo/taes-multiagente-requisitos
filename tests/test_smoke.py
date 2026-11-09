import pandas as pd
from reqgen import analyze
from reqgen.llm import clean, parse_json


def test_clean_parse():
    assert clean("<think>x</think> ok") == "ok"
    assert parse_json('blah {"a": 1} x') == {"a": 1}


def test_spearman():
    df = pd.DataFrame({"unambiguity": [1, 2, 3, 4], "verifiability": [1, 2, 3, 4], "singularity": [4, 3, 2, 1]})
    assert analyze.spearman(df).loc[0, "rho"] == 1.0
