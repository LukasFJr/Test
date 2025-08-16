from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
from jinja2 import Environment, FileSystemLoader


def build_report(df: pd.DataFrame, out: Path) -> None:
    env = Environment(
        loader=FileSystemLoader(Path(__file__).resolve().parent / "templates")
    )
    tpl = env.get_template("report.html.j2")
    df["date"] = pd.to_datetime(df["date"])
    by_month = (
        df.groupby([pd.Grouper(key="date", freq="M"), "category"]).sum().reset_index()
    )
    fig = px.bar(by_month, x="date", y="amount", color="category")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(tpl.render(figure=fig.to_plotly_json()))
