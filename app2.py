import streamlit as st
from sqlalchemy import create_engine
from langchain.prompts import PromptTemplate
from langchain.llms import CTransformers
import pandas as pd


def getLLMresponse(question, col_names):
    llm = CTransformers(
        model='D:\QuerioLingua\Querio_Lingua-NL-to-SQL\Models\llama-2-7b.ggmlv3.q8_0.bin',
        model_type='llama',
        config={'max_new_tokens': 256, 'temperature': 0.01}
    )

    template = """ Sql column names for table project are given below:
    {col_names}. 
    ### Give me SQL code to retrieve: {question}\n"SELECT"
    """

    prompt = PromptTemplate(input_variables=['question', 'col_names'], template=template)
    response = llm(prompt.format(question=question, col_names=col_names))

    # Split the input text into individual code snippets
    code_snippets = [snippet.strip() for snippet in response.split("\n\n") if snippet.strip()]

    # Save each code snippet in a dictionary
    code_snippets_dict = {}
    for i, code_snippet in enumerate(code_snippets, start=1):
        cleaned_code = code_snippet.replace('"', '').strip()
        code_snippets_dict[f"code_snippet_{i}"] = cleaned_code

    return code_snippets_dict


# Page Configuration
st.set_page_config(page_title='Generate SQL Codes from NL 🦙',
                   page_icon= '🦙',
                   layout= 'centered', initial_sidebar_state='collapsed')

# Streamlit Header
st.header('Querio Lingua NL-to-SQL')

df = None
my_db = create_engine('sqlite:///:memory:')
with st.sidebar:
    st.title('Using Llama 2 🦙💬')
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    if uploaded_file is None:
        st.sidebar.warning("Upload a dataset")
    else:
        df = pd.read_csv(uploaded_file, index_col=0)
        data = df.to_sql(name = 'project',con = my_db, index=False)


col1,col2 = st.columns(2)
with col1:
    if df is None:
        st.warning('First Upload the Dataset in the sidebar')
    else:        
        st.dataframe(df.head(5))
        col_names = list(df.columns)


with col2:
    # Taking the querry input 
    question = st.text_input("Enter information you want to obtain:")
    if question is None:
        st.warning("Enter a query to obtain information")
    else:
        def create_table_prompt(df):
            pass
    submit = st.button('Generate')
    if submit:   
        code_snippets_dict = getLLMresponse(question, col_names)
        for key, value in code_snippets_dict.items():
            st.code(value, language='sql')

