# USAGE
# Start the server:
# 	python3 run_server.py


# import the necessary packages
import dill
import pandas as pd
import os
dill._dill._reverse_typemap['ClassType'] = type
#import cloudpickle
import flask
import logging
from logging.handlers import RotatingFileHandler
from time import strftime

# initialize our Flask application and the model
app = flask.Flask(__name__)
model = None

handler = RotatingFileHandler(filename='app.log', maxBytes=100000, backupCount=10)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(handler)

def load_model(model_path):
	# load the pre-trained model
	global model
	with open(model_path, 'rb') as f:
		model = dill.load(f)
	print(model)

modelpath = "./models/xgboost_pipeline.dill"
load_model(modelpath)

@app.route("/", methods=["GET"])
def general():
	return """Welcome to fraudelent prediction process. Please use 'http://<address>/predict' to POST"""

@app.route("/predict", methods=["POST"])
def predict():
	# initialize the data dictionary that will be returned from the
	# view
	data = {"success": False}
	dt = strftime("[%Y-%b-%d %H:%M:%S]")
	# ensure an image was properly uploaded to our endpoint
	if flask.request.method == "POST":

		# description, company_profile, benefits = "", "", ""
		age, workclass, education, education_num, marital_status = "", "", "", "", ""
		occupation, relationship, capital_gain, capital_loss, hours_per_week = "", "", "", "", "" 
		request_json = flask.request.get_json()
		print('request_json', request_json)
		if request_json["age"]:
			age = request_json['age']

		if request_json["workclass"]:
			workclass = request_json['workclass']

		if request_json["education"]:
			education = request_json['education']
			
		if request_json["education_num"]:
			education_num = request_json['education_num']

		if request_json["marital_status"]:
			marital_status = request_json['marital_status']

		if request_json["occupation"]:
			occupation = request_json['occupation']

		if request_json["relationship"]:
			relationship = request_json['relationship']

		if request_json["capital_gain"]:
			capital_gain = request_json['capital_gain']

		if request_json["capital_loss"]:
			capital_loss = request_json['capital_loss']

		if request_json["hours_per_week"]:
			hours_per_week = request_json['hours_per_week']
		
		

		
		logger.info(f'{dt} Data: age={age}, workclass={workclass}, education={education}, education_num={education_num}, marital_status={marital_status}, occupation={occupation}, relationship={relationship}, capital_gain={capital_gain}, capital_loss={capital_loss}, hours_per_week={hours_per_week}')
		try:
			preds = model.predict_proba(pd.DataFrame({'age':[age],
													'workclass':[workclass], 
													'education':[education], 
													'education-num':[education_num], 
													'marital-status':[marital_status], 
													'occupation':[occupation], 
													'relationship':[relationship],
													'capital-gain':[capital_gain], 
													'capital-loss':[capital_loss], 
													'hours-per-week':[hours_per_week],}))
		except AttributeError as e:
			logger.warning(f'{dt} Exception: {str(e)}')
			data['predictions'] = str(e)
			data['success'] = False
			return flask.jsonify(data)

		data["predictions"] = str(preds[:, 1][0])
		# data["predictions"] = str(preds)
		# indicate that the request was a success
		data["success"] = True

	# return the data dictionary as a JSON response
	return flask.jsonify(data)

# if this is the main thread of execution first load the model and
# then start the server
if __name__ == "__main__":
	print(("* Loading the model and Flask starting server..."
		"please wait until server has fully started"))
	port = int(os.environ.get('PORT', 8180))
	app.run(host='0.0.0.0', debug=True, port=port)
