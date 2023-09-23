import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy import text
import replicate
import pandas as pd
import re
import os


st.set_page_config(page_title='🗣️ to 💬 using 🦙')

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




# Uploading the file 
with st.sidebar:
    st.title('Using Llama 2 13B version model 🦙💬')

    replicate_api = st.text_input('Enter Replicate API token:', type='password')
    if not (replicate_api.startswith('r8_') and len(replicate_api)==40):
        st.warning('Please enter your credentials!', icon='⚠️')
    else:
        st.success('Proceed to entering your prompt message!', icon='👉')
    os.environ['REPLICATE_API_TOKEN'] = replicate_api

    # For uploading the CSV file
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

    st.subheader('Models and parameters')
    selected_model = st.sidebar.selectbox('Choose a Llama2 model', ['Llama2-7B', 'Llama2-13B'], key='selected_model')
    if selected_model == 'Llama2-7B':
        llm = 'a16z-infra/llama7b-v2-chat:4f0a4744c7295c024a1de15e1a63c880d3da035fa1f49bfd344fe076074c8eea'
    elif selected_model == 'Llama2-13B':
        llm = 'a16z-infra/llama13b-v2-chat:df7690f1994d94e96ad9d568eac121aecf50684a0b0963b25a41cc40061269e5'
    temperature = st.sidebar.slider('temperature', min_value=0.01, max_value=5.0, value=0.1, step=0.01)
    top_p = st.sidebar.slider('top_p', min_value=0.01, max_value=1.0, value=0.9, step=0.01)
    max_length = st.sidebar.slider('max_length', min_value=32, max_value=128, value=120, step=8)
    st.markdown('📖 Learn how to build this app in this [blog](https://blog.streamlit.io/how-to-build-a-llama-2-chatbot/)!')


    

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
    

    # Taking the querry input 
    nlp_text = st.text_input("Enter information you want to obtain:")

    if nlp_text is None:
        st.warning("Enter a query to obtain information")
    else:
        def create_table_prompt(df):

            prompt = '''Sql column names for table project are given below:
            {}
            '''.format(list(df.columns))
            return prompt
        
        def combine_prompts(df, query_prompt):
            defination = create_table_prompt(df)
            query_init_string = f'''###Give me SQL code to retrieve: {query_prompt}\n'''
            return defination+query_init_string

        
        # Function for generating LLaMA2 response. Refactored from https://github.com/a16z-infra/llama2-chatbot
        def generate_llama2_response(x):
            output = replicate.run('a16z-infra/llama13b-v2-chat:df7690f1994d94e96ad9d568eac121aecf50684a0b0963b25a41cc40061269e5', 
                                input={"prompt": f"{combine_prompts(df, x)}",
                                        "temperature":temperature, "top_p":top_p, "max_length":max_length, "repetition_penalty":1})
            
            return output 
        
        def handle_response(y):   
            predictions = list(y)        
            # Filter out non-empty and non-whitespace fragments
            cleaned_fragments = [fragment.strip() for fragment in predictions if fragment.strip()]
            
            # Join cleaned fragments into a single string
            cleaned_query = ' '.join(cleaned_fragments)
            
            # Remove double quotes from the query
            cleaned_query = cleaned_query.replace('"', '')
            
            # Extract the SQL query
            sql_query = cleaned_query.split('Answer: ')[0].strip()
            
            return sql_query

            
        
        output = generate_llama2_response(nlp_text)        
        respond = handle_response(output)

        st.markdown(respond)
       
        '''  with my_db.connect() as conn:
            results = conn.execute(respond)

        # Desigining the Output
        col1, col2 = st.columns(2)
        if st.button("Show The SQL Querry and the Output"):
            
            with col1: 
                    st.markdown('**:green[SQL Query]**')
                    response_output = output
                    st.code(response_output)
                
            with col2:
                st.markdown('**:green[Query Output]**')
                if nlp_text.strip():  # Only display if nlp_text is not empty
                        for result in results.all():
                            st.write(result)



'''