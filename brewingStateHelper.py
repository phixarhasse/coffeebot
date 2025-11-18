import json 

class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj,'reprJSON'):
            return obj.reprJSON()
        else:
            return json.JSONEncoder.default(self, obj)

class Dimming:
    def __init__(self, dimmingPercent):
        self.brightness = 78.66 if dimmingPercent is None else dimmingPercent

    def reprJSON(self):
        return dict(brightness = self.brightness) 


class XY:    
    def __init__(self, x, y):
        self.X = x
        self.Y = y

    def reprJSON(self):
        return dict(x = self.X, y = self.Y) 
        
        
class Color:    
    def __init__(self, x, y):
        self.XY = XY(x, y)

    def reprJSON(self):
        return dict(xy = self.XY) 


class ColorTemperature:
    def __init__(self, mirek, valid):
        self.Mirek = mirek
        self.Mirek_valid = False if valid is None else valid

    def reprJSON(self):
        return dict(mirek = self.Mirek, mirek_valid = self.Mirek_valid) 
    

class Parameters:
    def __init__(self, color, colorTemperature, speed = None):
        self.Color = color
        self.ColorTemperature = colorTemperature
        self.Speed = 0.0 if speed is None else speed

    def reprJSON(self):
        return dict(color = self.Color, color_temperature = self.ColorTemperature, speed = self.Speed) 


class Action:
    def __init__(self, effect = None, parameters = None):
        self.Effect = "no_effect" if effect is None else effect
        self.Parameters = parameters 

    def reprJSON(self):
        return dict(effect = self.Effect, parameters = self.Parameters) 


class Effects_v2:
    def __init__(self, effect = None, parameters = None):
        self.Action = Action(effect, parameters)
        self.Action.Effect = effect 
        self.Action.Parameters = parameters 

    def reprJSON(self):
        return dict(action = self.Action) 


class BrewingState:
   
	def __init__(self, dimming = None, color = None, effect = None, parameters = None):
		self.Dimming = Dimming(100.0) if dimming is None else dimming 
		self.Color = color 
		self.Effects_v2 = None if effect is None else Effects_v2(effect, parameters)

	def reprJSON(self):
		return dict(dimming = self.Dimming, color = self.Color, effects_v2 = self.Effects_v2) 
