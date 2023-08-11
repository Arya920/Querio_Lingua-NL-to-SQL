![Landing Page](https://github.com/Arya920/Querio_Lingua-NL-to-SQL/blob/main/ss.png)
### QuerioLingua SQL Query Generator
QuerioLingua is a Streamlit web application that allows you to generate SQL queries for your datasets using natural language prompts & text-davinci-003 as a base model.

## Features

- Upload a CSV file to analyze data.
- Enter natural language queries to generate corresponding SQL queries.
- View SQL queries and their results.


## Getting Started

1. Clone this repository to your local machine:

   ```bash
      git clone https://github.com/yourusername/queriolingua-app.git

2. Install the Required Packages:
```bash
   pip install -r requirements.txt
```


set up your OpenAI API key:
- Go to the OpenAI Developer Platform: https://platform.openai.com/account/api-keys
- Copy your API key.
- Open app.py and replace "YOUR_OPENAI_API_KEY" with your actual API key.
streamlit run app.py

Usage
- Upload a CSV file using the sidebar.
- Enter a natural language query in the text input field.
- Click the "Generate SQL" button to generate SQL queries and view the results.

Customization
- You can customize the styling and appearance of the Streamlit app by modifying the custom_style in app.py.
-  Additionally, you can edit the config.toml file in the .streamlit directory to change the theme and appearance of your app.

Contributing
- Contributions are welcome! If you find a bug or want to add a new feature, feel free to open an issue or submit a pull request.
