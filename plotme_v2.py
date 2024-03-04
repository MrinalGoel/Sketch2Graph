
import streamlit as st
import base64
import requests
import json
import pandas as pd
import ast
import plotly.express as px


def generate_plot_details(plot_image):
    
    # OpenAI API Key
    api_key = ""

    # Function to encode the image
    def encode_image(image_path):
      with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

    # Path to your image
    image_path =plot_image.name

    # Getting the base64 string
    base64_image = encode_image(image_path)

    headers = {
      "Content-Type": "application/json",
      "Authorization": f"Bearer {api_key}"
    }

    payload = {
      "model": "gpt-4-vision-preview",
      "messages": [
        {
          "role": "user",
          "content": [
            {
              "type": "text",
              "text" : "You are a helpful assistant that analyzes the different types of graphs present in the uploaded image. Provide your answer in JSON structure like this {\"SerialNumber\": \"<Serial Number of identified graph>\", \"Type\": \"<What type of graph have you identified? Example : Bar or pie>\", \"Title\": \"<What is the title of the graph?>\", \"X_Label\": \"<What is the X-Label of the graph? In case of pie chart, return NA for this field.>\", \"Y_Label\": \"<What is the Y-Label of the graph? In case of pie chart, return NA for this field.>\", \"Color\": \"<Return list containing hex code for major color used in the graph>\",\"Location\": <Location of this graph in [Row,Column] format relative to other graphs present, for example if there is a single graph detected the location will be [1,1]>}. Do not generate any other explanation and do not add new line characters in the JSON, But separate details of each graph identified by a new line character."

            },
            {
              "type": "image_url",
              "image_url": {
                "url": f"data:image/png;base64,{base64_image}"
              }
            }
          ]
        }
      ],
      "max_tokens": 300
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

    json_data = json.loads(response.text)
    jdata =json_data['choices'][0]['message']['content']
    NumberOfGraphs = len(jdata.split('\n'))
    st.write("Number of graphs identified : "+str(NumberOfGraphs))
    return jdata
    

def format_gpt_out(jdata):

  listOfGraphs = jdata.split('\n')
  return listOfGraphs


def generate_pandas_plots(data_file,listOfGraphs):

    data = pd.read_csv(data_file.name)
    for graph in listOfGraphs:
      graph_dict = ast.literal_eval(graph)
      print(graph_dict)
      if graph_dict['Type'] == "Bar":
        st.write(graph_dict['SerialNumber']+'.'+' A '+graph_dict['Type']+' titled '+graph_dict['Title']+' and Labels '+graph_dict['X_Label']+','+graph_dict['Y_Label'])
        fig = px.bar(data, x=graph_dict['X_Label'], y=graph_dict['Y_Label'],title=graph_dict['Title'])
        st.plotly_chart(fig, use_container_width=True)

      elif graph_dict['Type'] == "Pie":
        st.write(graph_dict['SerialNumber']+'.'+' A '+graph_dict['Type']+' titled '+graph_dict['Title'])
        df = data.groupby([graph_dict['Title']])[graph_dict['Title']].count().reset_index(name='count')
        fig = px.pie(df, values='count', names=graph_dict['Title'], title=graph_dict['Title'])
        st.plotly_chart(fig, use_container_width=True)


def main():
    st.set_page_config("Sketch2Graph")
    st.header("Sketch2Graph ✎ : Transform your Doodles into powerful visuals!")
    flag = False

    with st.sidebar:
        st.title("Upload your Sketches and Data here - ")
        plot_image = st.file_uploader("Upload your Sketch")
        data_file = st.file_uploader("Upload your Data")
        if st.button("Process"):
            with st.spinner("Processing..."):
                flag = True
                #call_funcs()
                #st.success("Done")


    if flag == True:
        jdata = generate_plot_details(plot_image)
        listOfGraphs = format_gpt_out(jdata)
        generate_pandas_plots(data_file,listOfGraphs)
                #st.success("Done")



if __name__ == "__main__":
    main()
