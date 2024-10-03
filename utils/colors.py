from math import sqrt 

def rgb2lab(r, g, b):
  var_r = r/255
  var_g = g/255
  var_b = b/255
  
  if (var_r > 0.04045):
    var_r = pow(((var_r + 0.055) / 1.055), 2.4)
  else:
    var_r = var_r / 12.92
  if (var_g > 0.04045):
    var_g = pow(((var_g + 0.055) / 1.055), 2.4)
  else:
    var_g = var_g / 12.92
  if (var_b > 0.04045):
    var_b = pow(((var_b + 0.055) / 1.055), 2.4)
  else:
    var_b = var_b / 12.92

  var_r = var_r*100
  var_g = var_g*100
  var_b = var_b*100

  x = var_r * 0.4124 + var_g * 0.3576 + var_b * 0.1805
  y = var_r * 0.2126 + var_g * 0.7152 + var_b * 0.0722
  z = var_r * 0.0193 + var_g * 0.1192 + var_b * 0.9505
  
  var_x = x / 95.047
  var_y = y / 100
  var_z = z / 108.883
  
  if (var_x > 0.008856):
    var_x = pow(var_x, ( 1/3 ))
  else:
    var_x = ( 7.787 * var_x ) + (16 / 116)
  if (var_y > 0.008856):
    var_y = pow(var_y, ( 1/3 ))
  else:
    var_y = ( 7.787 * var_y ) + (16 / 116)
  if (var_z > 0.008856):
    var_z = pow(var_z, ( 1/3 ))
  else:
    var_z = ( 7.787 * var_z ) + (16 / 116)

  l_s = (116 * var_y) - 16
  a_s = 500 * (var_x - var_y)
  b_s = 200 * (var_y - var_z)
  
  return l_s, a_s, b_s

def h(a, b):
  return sqrt(a ** 2 + b ** 2)

def delta_E(l, l_0, a, a_0, b, b_0):
  return sqrt((l - l_0)**2 + (a - a_0) ** 2 + (b- b_0) ** 2)

def browning_index(l, a, b):
  x = (a + 1.75 * l) / (5.645*l + a - 3.012*b)
  return (100 * (x - 0.31)) / (0.17)

def normalize(x, x_0):
  return x / x_0


# Value from experiment
l_0 = 82.568
a_0 = 16.088
b_0 = 34.262
l = 70.820
a = 22.721
b = 43.251

print("Apple:")
print("Normalized L*: ", normalize(l, l_0))
print("Normalized Hue: ", normalize(h(a, b), h(a_0, b_0)))
print("Color Change: ", delta_E(l, l_0, a, a_0, b, b_0))
print("Normalized Browning Index: ", normalize(browning_index(l, a, b), browning_index(l_0, a_0, b_0)))


l_0 = 98.321
a_0 = -12.27
b_0 = 40.217
l = 97.939
a = -15.209
b = 53.256

print("Mango:")
print("Normalized L*: ", normalized_l(l, l_0))
print("Normalized Hue: ", normalize(h(a, b), h(a_0, b_0)))
print("Color Change: ", delta_E(l, l_0, a, a_0, b, b_0))
print("Normalized Browning Index: ", normalize(browning_index(l, a, b), browning_index(l_0, a_0, b_0)))
  
  
l_0 = 98.336
a_0 = -12.154
b_0 = 39.743
l = 35.476
a = 17.115
b = 25.024

print("Banana:")
print("Normalized L*: ", normalized_l(l, l_0))
print("Normalized Hue: ", normalize(h(a, b), h(a_0, b_0)))
print("Color Change: ", delta_E(l, l_0, a, a_0, b, b_0))
print("Normalized Browning Index: ", normalize(browning_index(l, a, b), browning_index(l_0, a_0, b_0)))