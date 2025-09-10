import pandas as pd
from vector.plugins.linear_scorer import LinearScorer

def test_linear_scorer():
    users = pd.DataFrame([
        {"user_id":"1","handle":"a","followers":100},
        {"user_id":"2","handle":"b","followers":200},
    ])
    pagerank = {"1":0.2,"2":0.8}
    comms = {"1":0,"2":1}
    stats = {"1":{"x":{"count":3,"eng_sum":30.0}}, "2":{"x":{"count":3,"eng_sum":60.0}}}
    sc = LinearScorer()
    df = sc.score(users, pagerank, comms, stats)
    assert set(df["issue"]) == {"x"}
    assert len(df) == 2
