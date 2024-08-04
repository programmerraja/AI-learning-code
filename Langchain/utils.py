import umap
import altair as alt

from numba.core.errors import NumbaDeprecationWarning, NumbaPendingDeprecationWarning
import warnings

warnings.simplefilter("ignore", category=NumbaDeprecationWarning)
warnings.simplefilter("ignore", category=NumbaPendingDeprecationWarning)


def umap_plot(text, emb):

    cols = list(text.columns)
    reducer = umap.UMAP(n_neighbors=2)
    umap_embeds = reducer.fit_transform(emb)

    df_explore = text.copy()
    df_explore["x"] = umap_embeds[:, 0]
    df_explore["y"] = umap_embeds[:, 1]

    chart = (
        alt.Chart(df_explore)
        .mark_circle(size=60)
        .encode(
            x=alt.X("x", scale=alt.Scale(zero=False)),  
            y=alt.Y("y", scale=alt.Scale(zero=False)),
            tooltip=cols,
        )
        .properties(width=700, height=400)
    )
    return chart


def umap_plot_big(text, emb):

    cols = list(text.columns)
    reducer = umap.UMAP(n_neighbors=100)
    umap_embeds = reducer.fit_transform(emb)

    df_explore = text.copy()
    df_explore["x"] = umap_embeds[:, 0]
    df_explore["y"] = umap_embeds[:, 1]

    chart = (
        alt.Chart(df_explore)
        .mark_circle(size=60)
        .encode(
            x=alt.X("x", scale=alt.Scale(zero=False)),
            y=alt.Y("y", scale=alt.Scale(zero=False)),
            tooltip=cols,
            # tooltip=['text']
        )
        .properties(width=700, height=400)
    )
    return chart


def umap_plot_old(sentences, emb):
    reducer = umap.UMAP(n_neighbors=2)
    umap_embeds = reducer.fit_transform(emb)

    df_explore = sentences
    df_explore["x"] = umap_embeds[:, 0]
    df_explore["y"] = umap_embeds[:, 1]

    chart = (
        alt.Chart(df_explore)
        .mark_circle(size=60)
        .encode(
            x=alt.X("x", scale=alt.Scale(zero=False)),
            y=alt.Y("y", scale=alt.Scale(zero=False)),
            tooltip=["text"],
        )
        .properties(width=700, height=400)
    )
    return chart
