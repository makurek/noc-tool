import os
import re
import ipaddress
import requests
from config import *
from netmiko import ConnectHandler
from flask import Flask
from flask_wtf import FlaskForm
from flask import render_template
from flask import request
from flask_bootstrap import Bootstrap
from wtforms import StringField
from wtforms import SelectField
from wtforms.validators import InputRequired

global device_list

class createForm(FlaskForm):
  
  device = SelectField('Urządzenie')
  command = SelectField('Polecenie', choices=[('show interfaces status', 'show interfaces status'), ('show mac address-table vlan', 'show mac address-table vlan'), ('show mac address-table interface', 'show mac address-table interface'), ('show vlan id', 'show vlan id')])
  params = StringField('Parametry', validators=[InputRequired()])

app = Flask(__name__)
app.config['SECRET_KEY'] = '443436456542'
Bootstrap(app)

@app.route("/", methods=["GET", "POST"])

def index():

# Fetch device list using Observium API

  try:
    r = requests.get(OBSERVIUM_API_BASE_URL + OBSERVIUM_API_DEVICES_IOS, auth=(OBSERVIUM_USERNAME, OBSERVIUM_PASS))
  except requests.exceptions.ConnectionError:
    error = "Unable to connect to Observium API, check your network"
    return render_template("error.html", error)
  except requests.exceptions.Timeouts:
    error = "Unable to fetch device list from Observium API, request timed out"
    return render_template("error.html", error)
  except:
    return render_template("error.html", error="Caught generic exception while connecting to Observium API")

  status = r.status_code
  if str(status).startswith('5'):
    return render_template("error.html", error="Server error")

  device_list = []
  devices = r.json()['devices']
  for k,v in devices.items():
    t = (v['hostname'], v['hostname'])
    device_list.append(t)


  form = createForm()   
  form.device.choices = device_list

  if form.validate_on_submit():
        
  	# Get all params 
    switch = request.form.get("device")
    command = request.form.get("command")
    params = request.form.get("params")
    # TODO: Validate all inputs
    try:
      # TODO: timeout should be 5 seconds max
      conn = ConnectHandler(device_type='cisco_ios', host=switch, username=NET_USERNAME, password=NET_PASSWORD)
      output = conn.send_command(command)
    except:
      output = "Oops.. something went wrong when connecting to the device"

    
    return render_template("home.html", form=form, result=output.strip())
  else:
    return render_template("home.html", form=form)

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
