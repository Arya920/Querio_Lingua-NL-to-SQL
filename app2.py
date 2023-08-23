import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy import text
import pandas as pd
import re
import openai
from secret_key import openai_key

openai.api_key = openai_key

import streamlit as st

# Custom CSS style
custom_style = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Curlz+MT&display=swap');
    .center-top-container {
        text-align: center;
        padding-top: 15vh; /* Adjust the top padding as needed */
    }
    .custom-title {
        font-family: 'Showcard Gothic', cursive;
        font-size: 5em;
        font-style: italic;
        font-weight: bold;
        margin: 0; /* Remove default margin */
    }
    .custom-title .pink-q {
        color: pink; /* Make the Q pink */
    }
    .custom-title .pink-l {
        color: pink; /* Make the L pink */
    }
</style>
"""

st.markdown(custom_style, unsafe_allow_html=True)
# Display the centered title at the top
st.markdown('<div class="center-top-container"><p class="custom-title"> <span class="pink-q">Q</span>uerio<span class="pink-l"> L</span>ingua</p></div>', unsafe_allow_html=True)


def create_table_prompt(df):
    """
    This Function returns a prompt informs GPT that we want to work with SQL Tables    
    """
    prompt = '''Sql column names for table project are given below:
    {}
    '''.format(list(df.columns))
    return prompt

# Uploading the file 
with st.sidebar:
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is None:
    st.sidebar.warning("Upload a dataset")

else:
    df = pd.read_csv(uploaded_file, index_col=0)
    st.write("Uploaded Data:")
    my_db = create_engine('sqlite:///:memory:')
    data = df.to_sql(name = 'project',con = my_db, index=False)

    st.write("Showing only the 10 rows ~")
    st.table(df.head(10))
    col1,col2,col3 = st.columns(3)
    cat_col=[]
    num_col=[]
    for i in df.columns:
        if df[i].dtype == "object":
            cat_col.append(i)
        else:
            num_col.append(i)

    # Description 
    if st.button("Show Descriptions"):
        with col1:
            st.write("Number of Columns ~", len(df.columns))
            st.write("Number of Rows ~", len(df))
        with col2:
            if len(cat_col) ==0 :
                st.write("No Catagorical Columns")
            else:
                st.write("Catagorical Columns", cat_col)
        with col3:
            if len(num_col) ==0:
                st.write("No Catagorical Columns")
            else:
                st.write("Numerical Columns", num_col)
    
    # Column wise Description
    

            

    # Taking the querry input 
    nlp_text = st.text_input("Enter information you want to obtain:")

    if nlp_text is None:
        st.warning("Enter a query to obtain information")
    else:
        def combine_prompts(df, query_prompt):
            defination = create_table_prompt(df)
            query_init_string = f'### Give me SQL code to retrieve: {query_prompt}\n"SELECT"'
            return defination+query_init_string

        response = openai.Completion.create(
            model = "text-davinci-003",
            prompt = combine_prompts(df, nlp_text),
            temperature = 1,
            max_tokens =150,
            top_p =1.0,
            frequency_penalty =0.0,
            presence_penalty = 0.0,
            stop =["#", ";"]
            )

        def handle_response(response):
            query = response["choices"][0]["text"]
            query = re.sub(r'"', '', query)

            if query.startswith(" "):
                query = "Select"+ query
            return query

        with my_db.connect() as conn:
            results = conn.execute(text(handle_response(response)))

        # Desigining the Output
        col1, col2 = st.columns(2)
        if st.button("Show The SQL Querry and the Output"):
            
            with col1: 
                    st.markdown('**:green[SQL Query]**')
                    response_output = handle_response(response)
                    st.code(response_output)
                
            with col2:
                st.markdown('**:green[Query Output]**')
                if nlp_text.strip():  # Only display if nlp_text is not empty
                        for result in results.all():
                            st.write(result)



