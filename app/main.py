import os
import re
import ipaddress
import requests
import datetime
from config import *
from netmiko import ConnectHandler
from flask import Flask
from flask_wtf import FlaskForm
from flask import render_template
from flask import request
from flask_bootstrap import Bootstrap
from wtforms import StringField
from wtforms import SelectField
from wtforms.validators import *

global device_list

class createForm(FlaskForm):
  
  device = SelectField('Urządzenie')
  command = SelectField('Polecenie')
  params = StringField('Parametry', validators=[Optional(), Regexp('([0-9]+)*(Gi[a-z]*[0-9]\/[0-9]+)*', message='Nieprawidłowy format.')])

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
  # This is not an exception!
  if str(status).startswith('5'):
    return render_template("error.html", error="Server error")

  command_list = [('show interfaces status', 'show interfaces status'), ('show mac address-table vlan', 'show mac address-table vlan'), ('show mac address-table interface', 'show mac address-table interface'), ('show vlan id', 'show vlan id'), ('show interface', 'show interface'), ('show logging', 'show logging'), ('show version', 'show version'), ('show interfaces transceiver', 'show interfaces transceiver')]
  device_list = []
  devices = r.json()['devices']
  for k,v in devices.items():
    t = (v['hostname'], v['hostname'])
    device_list.append(t)

  # How to sort a list of tuples?
  device_list = sorted(device_list, key=lambda x: x[0])
  form = createForm()   
  form.device.choices = device_list
  form.command.choices = command_list

  if form.validate_on_submit():
        
  	# Get all params 
    
    switch = request.form.get("device")
    command = request.form.get("command")
    params = request.form.get("params")

    # Validate user input
    if (switch in [i[0] for i in device_list]) and (command in [i[0] for i in command_list]):

      try:
        # Certain devices support telnet only, this is temporary workaround
        t1 = datetime.datetime.now()
        if switch in DEVICES_TELNET:
          conn = ConnectHandler(device_type='cisco_ios_telnet', host=switch,
              username=NET_USERNAME, password=NET_PASSWORD, timeout=5)
          output = conn.send_command(command + ' ' + params)
        else:
          conn = ConnectHandler(device_type='cisco_ios', host=switch,
              username=NET_USERNAME, password=NET_PASSWORD, timeout=5)
        output = conn.send_command(command + ' ' + params)

      except Exception as e:
        output = "Oops.. something went wrong when connecting to the device"
    else:

      return render_template("error.html", error="Input validation failed")
    t2 = datetime.datetime.now()
    duration = t2 - t1
    return render_template("home.html", form=form, result=output.strip(), time=duration)
  else:
    return render_template("home.html", form=form)

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=5000)
