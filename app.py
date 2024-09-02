from flask import (
    Flask,
    render_template,
    request,
    redirect,
    flash,
    url_for,
    current_app
)
import urllib.request 
from urllib.parse import urlparse,urljoin
from bs4 import BeautifulSoup
import requests,validators,uuid,pathlib,os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import PassiveAggressiveClassifier
import pickle
import pandas as pd
from sklearn.model_selection import train_test_split


app = Flask(__name__)
app.secret_key = "secret-key"

tfvect = TfidfVectorizer(stop_words='english', max_df=0.7)
loaded_model = pickle.load(open('model.pkl', 'rb'))
dataframe = pd.read_csv('news.csv')
x = dataframe['text']
y = dataframe['label']
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=0)

def fake_news_det(news):
    tfid_x_train = tfvect.fit_transform(x_train)
    tfid_x_test = tfvect.transform(x_test)
    input_data = [news]
    vectorized_input_data = tfvect.transform(input_data)
    prediction = loaded_model.predict(vectorized_input_data)
    return prediction



@app.route("/")
def  index():
    return render_template("index.html")


@app.route("/link",methods=("GET", "POST"), strict_slashes=False)
def link():
   
    if request.method == "POST":

        try:
            global requested_url,specific_element,tag,text

            requested_url = request.form.get('urltext')
            tag = request.form.get('specificElement')

            source = requests.get(requested_url).text
            # parser library?
            soup = BeautifulSoup(source, "html.parser")
            
            specific_element = soup.find_all(class_=tag)
            
            text=""
            for res in specific_element:
                text= text+ res.get_text()
            
            

            counter = len(specific_element)

            return render_template("link.html",
                url = requested_url,
                counter=counter,
                text=text,
                results = specific_element
                )

        except Exception as e:
            flash(e, "danger")
            
    return render_template("link.html")

@app.route("/text",methods=("GET", "POST"), strict_slashes=False)
def text():
   
    if request.method == "POST":

        try:
            global text

            # requested_url = request.form.get('urltext')
            # tag = request.form.get('specificElement')

            # source = requests.get(requested_url).text
            # # parser library?
            # soup = BeautifulSoup(source, "html.parser")
            
            # specific_element = soup.find_all(class_=tag)
            
            # text=""
            # for res in specific_element:
            #     text= text+ res.get_text()
            
            text = request.form['message']

            # counter = len(specific_element)
            predict()
            # return render_template("text.html",
            #     results = specific_element
            #     )

        except Exception as e:
            flash(e, "danger")
            
    return render_template("text.html")


@app.route('/predict',methods=("GET", "POST"))
def predict():
    if request.method == "POST":
        # message = request.form['message']
        # specific_element="HIIIIIIII"
        # for result in specific_element:
        #     msg = result
        # msg="Trueeeekjadkjbakdbakj"
        text1 = request.form['message']
        pred = fake_news_det(text1)
        print(pred)
        return render_template('text.html', prediction=pred)
    else:
        pred = fake_news_det(text)
        print(pred)
        return render_template('link.html', prediction=pred)

if __name__ == "__main__":
    app.run(debug=True)