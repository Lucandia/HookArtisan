import cadquery as cq
from math import cos, tan, sin, pi, sqrt
tollerance = 0.6

def points_hanger(closet_size, height, thick, angle, hanger_len = None, hooks = 0, right=True, shelves_hang = None):
    angle_rad = angle/180*pi
    if right: sign = 1
    else: sign = -1
    x0 = sign * (closet_size/2 +thick)
    y0 = - height - thick
    if not hanger_len:
        pts = [
            (0, 0),
            (x0, 0),
            (x0, y0),
            (x0 -sign * thick, y0),
            (x0 -sign * thick, -thick),
            (0, -thick),
            ]      
    else:
        if shelves_hang:
            y0 = - height - closet_size - thick * 2
            x0 = 0
            sign = +1
            start = [
                    (-shelves_hang - thick, 0),
                    (0, 0),
                    ]
            end = [
                    (-thick, - closet_size - thick * 2),
                    (-thick -  shelves_hang, - closet_size - thick * 2),
                    (-thick -  shelves_hang, - closet_size - thick),
                    (-thick, - closet_size - thick),
                    (-thick, - thick),
                    (-thick -  shelves_hang, - thick),
                    ]
        else:
            start = [
                (0, 0),
                (x0, 0),
                ]
            end = [ 
                    (x0 -sign * thick, -thick),
                    (0, -thick)
                    ]
        for _ in range(hooks-1):
            start += [
                    (x0, y0),
                    (x0 + sign * hanger_len*sin(angle_rad), y0 + hanger_len*cos(angle_rad)),
                    (x0 + sign * (hanger_len*sin(angle_rad) + thick*cos(angle_rad)), y0 + hanger_len*cos(angle_rad) - thick*sin(angle_rad)),
                    (x0, y0 - (thick/cos(angle_rad))/tan(angle_rad)),
                    ]
            y0 -= height
        middle = [
            (x0, y0),
            (x0 + sign * hanger_len*sin(angle_rad), y0 + hanger_len*cos(angle_rad)),
            (x0 + sign * (hanger_len*sin(angle_rad) + thick*cos(angle_rad)), y0 + hanger_len*cos(angle_rad) - thick*sin(angle_rad)),
            (x0 -sign * thick, y0 - (thick+thick/cos(angle_rad))/tan(angle_rad)),
            ]
        pts = start + middle + end
    return pts

def hanger(closet_size, hanger_depth, front_height, thick, angle, hanger_len, back_height, back_angle, back_hanger_len, mirror, hooks, back_hooks, shelves_hang):
    pts = points_hanger(closet_size, front_height, thick, angle, hanger_len, hooks, right=True, shelves_hang=shelves_hang) 
    if not mirror and not shelves_hang:
        pts += points_hanger(closet_size, back_height, thick, back_angle, back_hanger_len, back_hooks, right=False)[::-1][1:]
    hanger = (cq.Workplane("XY")
            .polyline(pts)
            .close()
            .extrude(hanger_depth))
    if mirror and not shelves_hang:
        hanger =  hanger.mirror('YZ', union=True)
    hanger = hanger.edges("|Z").fillet(thick/5)
    return hanger


def box(box_x, box_y, box_z, box_wall, honey_rad, closet_size, hanger_depth, front_height, thick, angle, hang_len, hooks):
    pts_diff = points_hanger(closet_size, front_height, thick + tollerance, angle, hang_len+tollerance, hooks)
    hanger_diff = (cq.Workplane("XY")
                    .polyline(pts_diff)
                    .close()
                    .extrude(hanger_depth+tollerance)
                    .edges("|Z")
                    .fillet(thick/5)
                    )

    box = ( cq.Workplane()
            .box(box_y-box_wall*2, box_z-box_wall, box_x-box_wall*2)
            .translate((closet_size/2 + thick + box_y/2 + tollerance, -front_height*hooks + -thick + box_z/2 - box_wall, 0))
            .faces('>Y')
            .shell(box_wall)
            )
    
    box -= hanger_diff.translate(((0,0, box_x/2 - box_wall/2 - (hanger_depth+tollerance)))) + hanger_diff.translate(((0,0,  - box_x/2 + box_wall/2 ))) 
    box = box.rotate((1,0,0), (0,0,0), -90)

    if honey_rad:
        honeycomb = (cq.Sketch('XZ')
                        .regularPolygon(honey_rad, 6)
                        .vertices()
                        .fillet(honey_rad/4)
                            )
        n_y = int(box_y // (honey_rad*sqrt(3) + honey_rad))
        n_x = int(box_x // 2 // (honey_rad*2))
        box = (box
            .faces("<Z")
            .workplane(centerOption="CenterOfMass")
            .rarray(honey_rad*sqrt(3) + honey_rad, honey_rad*4, n_y, n_x)
            .placeSketch(honeycomb) 
            .cutThruAll()
            )
    return box