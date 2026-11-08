import os
import sys

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Add src to path so we can import our graph logic
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from src.simulation.graph import build_dependency_graph, simulate_cascade

load_dotenv(".env")

st.set_page_config(page_title="Scenario Simulator", layout="wide")
st.title("Resilience Scenario Simulator")
st.markdown("**Work Package 6** — Cascading Failure Analysis")


@st.cache_resource
def get_engine():
    return create_engine(
        f"postgresql+psycopg://{os.getenv('POSTGRES_USER', 'bri')}:{os.getenv('POSTGRES_PASSWORD', 'change_me')}@"
        f"{os.getenv('POSTGRES_HOST', 'localhost')}:{os.getenv('POSTGRES_PORT', '5432')}/{os.getenv('POSTGRES_DB', 'bri')}"
    )


@st.cache_data
def load_dependencies():
    engine = get_engine()
    with engine.connect() as conn:
        df = pd.read_sql(text("SELECT * FROM sector_dependencies"), conn)
    return df.to_dict("records")


deps = load_dependencies()
graph = build_dependency_graph(deps)

st.sidebar.header("Simulation Parameters")
failed_sector = st.sidebar.selectbox("Select a starting disruption:", ["electricity", "telecommunications", "water"])

if st.button("Run Simulation"):
    impacted = simulate_cascade(graph, failed_sector)

    st.subheader("Cascading Impact Results")
    st.write(f"If **{failed_sector}** fails, the following essential services are impacted:")

    cols = st.columns(len(impacted))
    for idx, sector in enumerate(impacted):
        if idx == 0:
            cols[idx].error(f"🔴 **{sector.capitalize()}** (Initial Failure)")
        else:
            cols[idx].warning(f"🟠 **{sector.capitalize()}** (Cascaded)")

    st.markdown("---")
    st.subheader("Dependency Graph")
    st.write("Electricity acts as the root dependency for most other sectors.")

    # Safely build the graphviz string
    edges_str = ""
    for d in deps:
        edges_str += f'"{d["source_sector"]}" -> "{d["dependent_sector"]}"; '

    graphviz_dot = f"digraph G {{ rankdir=LR; node [shape=box, style=filled, color=lightblue]; {edges_str} }}"
    st.graphviz_chart(graphviz_dot)
