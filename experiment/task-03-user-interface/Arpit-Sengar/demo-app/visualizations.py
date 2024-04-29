import streamlit as st
import streamlit_highcharts as hct


def visualization_page():
    st.write("""
        <div style='text-align:center;'>
            <h1 style='text-align:center; font-size: 300%;'>Visualizations</h1>
            <p style=' color: #9c9d9f'>Lorem ipsum dolor sit amet consectetur adipisicing elit. Quasi, asperiores./p>
            <hr>
        </div>
            """
    , unsafe_allow_html=True)
    
    chart_def={
    "title":{
        "text":"Sales of petroleum products March, Norway",
        "align":"left"
    },
    "xAxis":{
        "categories":["Jet fuel","Duty-free diesel"]
    },
    "yAxis":{
        "title":{"text":"Million liter"}
    },
    "series":[
            {"type":"column",
                "name":"2020",
                "data":[59,83]},
            {"type":"column",
                "name":"2021",
                "data":[24,79]
            },
            {"type":"column",
                "name":"2022",
                "data":[58,88]
            },
            {"type":"spline",
                "name":"Average",
                "data":[47,83.33],
                "marker":{
                    "lineWidth":2,
                    "fillColor":"black",
                }
            }
        ]
    }

    st.write("## Example")
    selSample=st.selectbox("Choose a sample",[hct.SAMPLE11,hct.SAMPLE,hct.SAMPLE2,hct.SAMPLE3,hct.SAMPLE5,hct.SAMPLE7,hct.SAMPLE8],format_func=lambda x: str(x["title"]["text"])
    )
    hct.streamlit_highcharts(selSample, 640)