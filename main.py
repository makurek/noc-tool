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

# Fetch device list using Observium API

r = requests.get(OBSERVIUM_API_BASE_URL + OBSERVIUM_API_DEVICES_IOS, auth=(OBSERVIUM_USERNAME, OBSERVIUM_PASS))
device_list = []
devices = r.json()['devices']
for k,v in devices.items():
	t = (v['hostname'], v['hostname'])
	device_list.append(t)


class initForm(FlaskForm):
    
	device = SelectField('Device', choices=device_list)
	command = SelectField('Command', choices=[('show interfaces status', 'show interfaces status'), ('show mac address-table vlan', 'show mac address-table vlan')])
	params = StringField('Params', validators=[InputRequired()])
	

app = Flask(__name__)
app.config['SECRET_KEY'] = '443436456542'
Bootstrap(app)

@app.route("/", methods=["GET", "POST"])

def index():
    form = initForm()
    if form.validate_on_submit():
        
	# Get all params 
        switch = request.form.get("device")
        command = request.form.get("command")
        params = request.form.get("params")
        conn = ConnectHandler(device_type='cisco_ios', host=switch, username=NET_USERNAME, password=NET_PASSWORD)
        output = conn.send_command(command)
        
	# Initiate checks using data passed to web form
 
        return render_template("home.html", form=form, result=output)
    else:
        return render_template("home.html", form=form)


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
