# USAGE
# run venv
# source bin/activate
# Start the server:
# 	python3 run_front_server.py

import json

from flask import Flask, render_template, redirect, url_for, request
from flask_wtf import FlaskForm
from requests.exceptions import ConnectionError
from wtforms import IntegerField, SelectField, StringField
from wtforms.validators import DataRequired

import urllib.request
import json

class ClientDataForm(FlaskForm):


    workclass_choices = ['Federal-gov', 'Local-gov', 'Never-worked', 'Private', 'Self-emp-inc',
     'Self-emp-not-inc', 'State-gov', 'Without-pay']

    education_choices = ['10th', '11th','12th', '1st-4th', '5th-6th', '7th-8th' '9th', 'Assoc-acdm', 
        'Assoc-voc', 'Bachelors', 'Doctorate', 'HS-grad', 'Masters', 'Preschool', 'Prof-school', 'Some-college']
    education_num_choices = ['1.0', '2.0', '3.0', '4.0', '5.0', '6.0', '7.0', '8.0', 
        '9.0', '10.0', '11.0', '12.0', '13.0', '14.0', '15.0', '16.0']
    marital_status_choices = ['Divorced', 'Married-AF-spouse', 'Married-civ-spouse', 'Married-spouse-absent', 
        'Never-married', 'Separated', 'Widowed']
    occupation_choices = ['Adm-clerical', 'Armed-Forces', 'Craft-repair', 'Exec-managerial', 'Farming-fishing', 
        'Handlers-cleaners', 'Machine-op-inspct', 'Other-service', 'Priv-house-serv', 'Prof-specialty', 
        'Protective-serv', 'Sales', 'Tech-support', 'Transport-moving']
    relationship_choices = ['Husband', 'Not-in-family', 'Other-relative', 'Own-child', 'Unmarried', 'Wife']

					


    age = StringField('age', validators=[DataRequired()])
    workclass = SelectField('workclass', choices=workclass_choices, validators=[DataRequired()])
    education = SelectField('education', choices=education_choices, validators=[DataRequired()])
    education_num = SelectField('education_num', choices=education_num_choices, validators=[DataRequired()])
    marital_status = SelectField('marital_status', choices=marital_status_choices, validators=[DataRequired()])
    occupation = SelectField('occupation', choices=occupation_choices, validators=[DataRequired()])
    relationship = SelectField('relationship', choices=relationship_choices, validators=[DataRequired()])
    capital_gain = StringField('capital_gain', validators=[DataRequired()])
    capital_loss = StringField('capital_loss', validators=[DataRequired()])
    hours_per_week = StringField('hours_per_week', validators=[DataRequired()])

    


app = Flask(__name__)
app.config.update(
    CSRF_ENABLED=True,
    SECRET_KEY='you-will-never-guess',
)

def get_prediction(age, workclass, education, education_num, marital_status, occupation, relationship, capital_gain, capital_loss, hours_per_week):
    # body = {'age':age,
    #         'workclass':workclass, 
    #         'education':education, 
    #         'education-num':education_num, 
    #         'marital-status':marital_status, 
    #         'occupation':occupation, 
    #         'relationship':relationship,
    #         'capital-gain':capital_gain, 
    #         'capital-loss':capital_loss, 
    #         'hours-per-week':hours_per_week,}
    body = {'age':age,
            'workclass':workclass, 
            'education':education, 
            'education_num':education_num, 
            'marital_status':marital_status, 
            'occupation':occupation, 
            'relationship':relationship,
            'capital_gain':capital_gain, 
            'capital_loss':capital_loss, 
            'hours_per_week':hours_per_week, } 

    myurl = "http://0.0.0.0:8180/predict"
    req = urllib.request.Request(myurl)
    req.add_header('Content-Type', 'application/json; charset=utf-8')
    jsondata = json.dumps(body)
    jsondataasbytes = jsondata.encode('utf-8')   # needs to be bytes
    req.add_header('Content-Length', len(jsondataasbytes))
    #print (jsondataasbytes)
    response = urllib.request.urlopen(req, jsondataasbytes)
    return json.loads(response.read())['predictions']

@app.route("/")
def index():
    return render_template('index.html')


@app.route('/predicted/<response>')
def predicted(response):
    response = json.loads(response)
    print(response)
    return render_template('predicted.html', response=response)


@app.route('/predict_form', methods=['GET', 'POST'])
def predict_form():
    form = ClientDataForm()
    data = dict()
    if request.method == 'POST':
        # age, workclass, education, education_num, marital_status, occupation, relationship, capital_gain, capital_loss, hours_per_week
        data['age'] = request.form.get('age')
        data['workclass'] = request.form.get('workclass')
        data['education'] = request.form.get('education')
        data['education_num'] = request.form.get('education_num')
        data['marital_status'] = request.form.get('marital_status')
        data['occupation'] = request.form.get('occupation')
        data['relationship'] = request.form.get('relationship')
        data['capital_gain'] = request.form.get('capital_gain')
        data['capital_loss'] = request.form.get('capital_loss')
        data['hours_per_week'] = request.form.get('hours_per_week')

        print('have post data = ',data)


        try:
            response = str(get_prediction(data['age'],
                                      data['workclass'],
                                      data['education'],
                                      data['education_num'],
                                      data['marital_status'],
                                      data['occupation'],
                                      data['relationship'],
                                      data['capital_gain'],
                                      data['capital_loss'],
                                      data['hours_per_week']))
            print(response)
        except ConnectionError:
            response = json.dumps({"error": "ConnectionError"})
        return redirect(url_for('predicted', response=response))
    return render_template('form.html', form=form)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8181, debug=True)
