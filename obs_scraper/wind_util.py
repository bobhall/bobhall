import math

def degrees_to_cardinal(degrees):
    cardinals = ['N','NNE','NE','ENE','E','ESE','SE','SSE','S',
                 'SSW','SW','WSW','W','WNW','NW','NNW']
    return cardinals[int(math.floor(((int(degrees)+11.25)%360)/22.25))]

def degrees_to_radians(degrees):
    return degrees * math.pi / 180

def radians_to_degrees(radians):
    return radians * 180 / math.pi


def calc_u(speed, direction):
    return math.sin(degrees_to_radians(direction+180)) * speed
    
def calc_v(speed, direction):
    return math.cos(degrees_to_radians(direction+180)) * speed


def wind_speed_and_direction_to_u_v(speed_and_direction):
    speed,direction = speed_and_direction
    return calc_u(speed, direction), calc_v(speed, direction)

def u_v_to_wind_speed_and_direction(u, v):
    speed = math.sqrt(u**2 + v**2)
    
    direction = math.atan2(-u,-v)
    direction = radians_to_degrees(direction)
    direction = direction % 360
    direction = (direction+360) % 360

    return speed, direction

#
# wind_speeds: [(4, 182),  # 4 kts, 182 degrees
#               (8, 270)   # 8 kts, 270 degrees
#
def get_average_wind_speeds(wind_speeds):
    u_v_components = map(wind_speed_and_direction_to_u_v, wind_speeds)

    u_list = [x[0] for x in u_v_components]
    v_list = [x[1] for x in u_v_components]

    u_avg = sum(u_list) / len(u_v_components)
    v_avg = sum(v_list) / len(u_v_components)

    return u_v_to_wind_speed_and_direction(u_avg, v_avg)
