import pandas as pd
import streamlit as st
from modules.scraper import fetch_main_tweet_dataframe, fetch_comments_dataframe
from modules.utils import (
    load_header,
    is_valid_twitter_url,
    apply_sentiment_pipeline
)
from modules.cache_functions import cache_sample_dataset


def update_dataframes(df_comments, df_author):
    # Mapping dictionary
    sentiment_map = {
        1: 'Positivo',
        0: 'Neutral',
        -1: 'Negativo'
    }

    with st.spinner("Analizando tweets..."):
        df_comments['predictedSentiment'] = df_comments['cleaned_text'].apply(lambda x: apply_sentiment_pipeline(x))
        # Assigning sentiment labels based on predictedSentiment values
        df_comments['sentiment_label'] = df_comments['predictedSentiment'].map(sentiment_map)

    st.session_state["master_df"] = df_comments
    st.session_state["original_tweet"] = df_author



def display_results(selected_actor):
    with st.expander("Tweet Original", expanded=True):
        st.dataframe(
            st.session_state["original_tweet"], height=1, use_container_width=True, key=selected_actor,
        )

    with st.expander("Comentarios", expanded=True):
        st.dataframe(
            st.session_state["master_df"], height=450, use_container_width=True, key=f'Comentarios para tweet de {selected_actor}',
        )

    st.write("<br>", unsafe_allow_html=True)

    st.download_button(
        label="Bajar archivo CSV",
        data=st.session_state["master_df"].to_csv(index=False).encode("utf-8"),
        file_name="comentarios_analizados.csv",
        use_container_width=True,
    )


def analyse_page():
    load_header("Analizar Tweet")

    cols = st.columns([5, 1])

    with cols[0]:
        twitter_url = st.text_input(
            "Pegar enlace aquí:",
            placeholder="https://x.com/Google/status/1790555395041472948",
            disabled=True
        ).strip()

    with cols[1]:
        st.write("<br>", unsafe_allow_html=True)
        submitted = st.button("Enviar", use_container_width=True, disabled=True)

    valid_twitter = is_valid_twitter_url(twitter_url)

    # If the input field is enabled
    if submitted and not valid_twitter:
        st.toast("⚠️ Enlace inválido")
    elif submitted and valid_twitter:
        with st.spinner("Obteniendo datos..."):
            df_author = fetch_main_tweet_dataframe(twitter_url)
            df_comments = fetch_comments_dataframe(twitter_url)
            update_dataframes(df_comments, df_author)
            display_results('Actor Seleccionado')

    # Using default datasets
    else:
        st.markdown("<p style='font-size: small;'>El campo está deshabilitado para la demostración, por favor use el menú para seleccionar un actor político</p>", unsafe_allow_html=True)

        datasets = cache_sample_dataset()

        options = list(datasets.keys())

        index = None if st.session_state["selected_actor"] is None else options.index(st.session_state["selected_actor"])

        selected_actor = st.selectbox("Seleccione un actor político", options, index=index, placeholder="Seleccione un actor político")

        if selected_actor and selected_actor != st.session_state["selected_actor"]:
            df_author = [value for dictionary in datasets[selected_actor] for key, value in dictionary.items() if 'comments' not in key][0]
            df_comments = [value for dictionary in datasets[selected_actor] for key, value in dictionary.items() if 'comments' in key][0]
            st.session_state["selected_actor"] = selected_actor
            index = options.index(selected_actor)
            update_dataframes(df_comments, df_author)
            display_results(selected_actor)
            st.rerun()
        elif selected_actor and selected_actor == st.session_state["selected_actor"]:
            display_results(st.session_state["selected_actor"])
