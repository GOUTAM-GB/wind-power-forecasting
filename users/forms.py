from django import forms

class WindInputForm(forms.Form):
    wind_speed = forms.FloatField(label="Wind Speed (m/s)")
    wind_direction = forms.FloatField(label="Wind Direction (°)")
    temperature = forms.FloatField(label="Temperature (°C)")
    rotor_speed = forms.FloatField(label="Rotor Speed (rpm)")
    pressure = forms.FloatField(label="Pressure (hPa)")
