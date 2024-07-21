import random
import pandas as pd
from PIL import Image
import streamlit as st
from wordcloud import WordCloud
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from nltk.tokenize import word_tokenize
from modules.utils import get_top_ngram
from modules.cache_functions import cache_stopwords


def process_texts(texts):
    stop_words = cache_stopwords()
    
    tokenized_texts = texts.apply(word_tokenize)
    tokenized_texts = tokenized_texts.apply(
        lambda x: [word.lower() for word in x if word.lower() not in stop_words]
    )
    texts_cleaned = tokenized_texts.apply(lambda x: " ".join(x))
    return texts_cleaned


def custom_color_func(word, font_size, position, orientation, font_path, random_state):
    color_palette = ["#ff2b2b", "#83c9ff", "#0068c9"]
    return random.choice(color_palette)


def display_word_cloud(dataframe):
    all_text = " ".join(dataframe["cleaned_text"])
    stop_words = cache_stopwords()
    wordcloud = WordCloud(
        background_color="#fff", 
        colormap="autumn", 
        color_func=custom_color_func,
        stopwords=stop_words,
    ).generate(all_text)
    wordcloud_image = wordcloud.to_array()

    fig = go.Figure()
    fig.add_layout_image(
        dict(
            source=Image.fromarray(wordcloud_image),
            x=0,
            y=1,
            sizex=1,
            sizey=1.3,
            opacity=1,
            xref="paper",
            yref="paper"
        )
    )
    fig.update_layout(
        autosize=True,
        height=340,
        width=500,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
    )

    return fig


def most_common_trigrams(df, pdf=False):
    colors = ["#ff2b2b", "#83c9ff", "#0068c9"]
    fig = make_subplots(rows=1, cols=3)

    sentiment_list = ["Positive", "Neutral", "Negative"]

    for i, sentiment_label in enumerate(sentiment_list):
        texts = df[df['sentiment_label'] == sentiment_label]["cleaned_text"]
        if texts.empty:
            continue
        texts_cleaned = process_texts(texts)
        top_n_bigrams = get_top_ngram(texts_cleaned, 2)[:15]

        if not top_n_bigrams:
            continue

        x, y = map(list, zip(*top_n_bigrams))

        fig.add_trace(
            go.Bar(
                x=y,
                orientation="h",
                type="bar",
                name=sentiment_label,
                marker=dict(color=colors[i]),
                text=x,
                textposition="inside",
                hovertemplate="%{text}: %{y}",
            ),
            1,
            i + 1,
        )

    fig.update_layout(
        title_text="Bigramas más frecuentes",
        title_y=1,
        title_font=dict(color="#808495", size=15),
        autosize=False,
        margin=dict(t=0, b=0, l=0, r=0),
        height=250,
    )

    return fig


def display_target_count(df):
    colors = ["#83c9ff", "#ff2b2b", "#0068c9"]
    
    fig = go.Figure()
    
    fig.add_trace(
        go.Pie(
            labels=df.sentiment_label.value_counts().index,
            values=df.sentiment_label.value_counts().values,
            name="Distribución Sentimiento",
            text=df.sentiment_label.value_counts().values,
            textinfo='label+percent',
            textfont=dict(size=12, color='white'),
            marker=dict(colors=colors, line=dict(color="#fff", width=1))
        )
    )
    
    fig.update_layout(
        title_text="Distribución de Sentimiento",
        title_y=1,
        title_font=dict(color="#808495", size=15),
        autosize=True,
        height=250,
        margin=dict(l=0, r=0, t=25, b=10),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
    )

    return fig


def sentiment_over_date(df):
    grouped = df.groupby(["createdAt", "sentiment_label"]).size().unstack(fill_value=0)

    fig = go.Figure()

    colors = ["#ff2b2b", "#83c9ff", "#0068c9"][::-1]
    for idx, sentiment_label in enumerate(grouped.columns):
        fig.add_trace(
            go.Scatter(
                x=grouped.index,
                y=grouped[sentiment_label],
                mode="lines",
                name=sentiment_label,
                stackgroup="one",
                line=dict(width=2, color=colors[idx]),
                fillcolor=colors[idx],
                hoverinfo="y+name",
            )
        )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)
    fig.update_layout(
        title_text= "Sentimiento vs. Tiempo transcurrido",
        title_y=1,
        title_font=dict(color="#808495", size=15),
        xaxis_title="Fecha",
        yaxis_title="Total de Sentimiento",
        hovermode="x",
        showlegend=True,
        autosize=False,
        height=250,
        width=500,
        margin=dict(l=0, r=0, t=40, b=0),
        plot_bgcolor="white",
        paper_bgcolor="white",
    )

    return fig


def crear_grafico_dispersion(df):
    sentiment_colors = {
        "Positivo": "#83c9ff",
        "Negativo": "#ff2b2b",
        "Neutral": "#0068c9"
    }

    fig = px.scatter(
        df,
        x="likeCount",
        y="sentiment_label",
        size="likeCount",  # Bubble size based on number of likes
        color="sentiment_label",
        labels={
            "likeCount": "Número de Likes",
            "sentiment_label": "Etiqueta de Sentimiento",
        },
        title="Relación entre Número de Likes y Etiquetas de Sentimiento",
        color_discrete_map=sentiment_colors
    )

    fig.update_layout(
        title_y=1,
        title_font=dict(color="#808495", size=15),
        autosize=True,
        height=250,
        margin=dict(l=0, r=0, t=20, b=0),
    )

    return fig


def stacked_bar_fig(df):
    sentiment_colors = {
        "Positivo": "#83c9ff",
        "Negativo": "#ff2b2b",
        "Neutral": "#0068c9"
    }

    fig = px.histogram(
        df,
        x="account_creation_time",
        color="sentiment_label",
        title="Distribución del Tiempo de <br>Creación de Cuenta por Sentimiento de Comentario",
        labels={
            "sentiment_label": "Sentimiento",
        },
        barmode="stack",
        nbins=25,
        color_discrete_map=sentiment_colors
    )

    fig.update_layout(
        title_y=0.95,
        title_font=dict(color="#808495", size=15),
        yaxis_title="Número de Usuarios",
        xaxis_title="Tiempo de Creación de Cuenta (meses)",
    )

    return fig

def metrics_bar(tweet_data, df):
    st.write(
        """
    <style>
    div[data-testid="stMetric"]
    {
        background-color: #00000005;
        color: black;
        padding: 10px 0 0 10px;
        border-radius: 5px;
    }
    </style>
            
    """,
        unsafe_allow_html=True,
    )

    avg_time = df["account_creation_time"].mean()
    min_time = df["account_creation_time"].min()
    max_time = df["account_creation_time"].max()

    left, right = st.columns([2, 2])

    with left:
        with st.container(border=True):
            st.write("Antigüedad de las Cuentas de los Usuarios que comentaron")
            col1, col2, col3 = st.columns(3)
            col1.metric("Tiempo Promedio", f"{round(avg_time/12)} años")
            col2.metric("Tiempo Mínimo", f"{min_time} meses")
            col3.metric("Tiempo Máximo", f"{round(max_time/12)} años")

    with right:
        with st.container(border=True):
            st.write("Distribución Sentimiento Comentarios")
            pos, neu, neg = st.columns(3)
            pos.metric(label=":green[Positivo]", value=tweet_data["positive"])
            neu.metric(label=":gray[Neutral]", value=tweet_data["neutral"])
            neg.metric(label=":red[Negativo]", value=tweet_data["negative"])


def clean_and_plot_locations(df):
    """"
    Cleans the dataframe and generates the locations graphic
    """

    # Groups by country
    def map_to_country(location):
        location = location.lower()
        if 'salvador' in location:
            return 'El Salvador'
        else:
            return 'Otro'


    # Group by country
    df['country'] = df['author__location'].apply(map_to_country)

    # Count ocurrences
    country_counts = df['country'].value_counts().reset_index()
    country_counts.columns = ['Country', 'Count']

    color_discrete_map = {
        'El Salvador': "#ff2b2b",
        'Otro': "#83c9ff"
    }

    # Graphic
    fig = px.bar(country_counts, 
                 x='Country', 
                 y='Count', 
                 title='Ubicación usuarios', 
                 labels={'Country': 'País', 'Count': 'Conteo'}, 
                 color='Country', 
                color_discrete_map=color_discrete_map,
                category_orders={'Country': ['El Salvador', 'Otro']}
                )

    fig.add_annotation(
        x=1.2,
        y=0,
        xref="paper",
        yref="paper",
        text=f"Total: {df['author__location'].notna().sum()}",
        showarrow=False,
        font=dict(size=14, color="red"),
        align="center"
    )

    fig.update_layout(
        title_y=1,
        title_font=dict(color="#808495", size=15),
    )

    return fig
