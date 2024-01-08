import cadquery as cq
from math import cos, tan, sin, pi, sqrt
tollerance = 0.7

def points_hanger(closet_size, height, thick, angle, hanger_len = None, right=True):
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
        pts = [
            (0, 0),
            (x0, 0),
            (x0, y0),
            (x0 + sign * hanger_len*sin(angle_rad), y0 + hanger_len*cos(angle_rad)),
            (x0 + sign * (hanger_len*sin(angle_rad) + thick*cos(angle_rad)), y0 + hanger_len*cos(angle_rad) - thick*sin(angle_rad)),
            (x0 -sign * thick, y0 - (thick+thick/cos(angle_rad))/tan(angle_rad)),
            (x0 -sign * thick, -thick),
            (0, -thick),
            ]
    return pts

def normal_hanger(closet_size, hanger_depth, front_height, thick, angle, hanger_len, back_height, back_angle, back_hanger_len, mirror):
    pts = points_hanger(closet_size, front_height, thick, angle, hanger_len) 
    if not mirror:
        pts += points_hanger(closet_size, back_height, thick, back_angle, back_hanger_len, right=False)[::-1][1:]
    hanger = (cq.Workplane("XY")
            .polyline(pts)
            .close()
            .extrude(hanger_depth))
    if mirror:
        hanger =  hanger.mirror('YZ', union=True)
    hanger = hanger.edges("|Z").fillet(thick/5)
    return hanger

        
def shelves_hunger(closet_size, hanger_depth, front_height, thick, angle, hang_len, shelves_hang):
    def points_hanger_shelves(height, thick, angle, hanger_len, shelves_hang):
        angle_rad = angle/180*pi
        y0 = - height - closet_size - thick * 2  
        pts = [
            (-shelves_hang - thick, 0),
            (0, 0),
            (0, y0),
            (0 + hanger_len*sin(angle_rad), y0 + hanger_len*cos(angle_rad)),
            (hanger_len*sin(angle_rad) + thick*cos(angle_rad), y0 + hanger_len*cos(angle_rad) - thick*sin(angle_rad)),
            (-thick, y0 - (thick+thick/cos(angle_rad))/tan(angle_rad)),
            (-thick, - closet_size - thick * 2),
            (-thick -  shelves_hang, - closet_size - thick * 2),
            (-thick -  shelves_hang, - closet_size - thick),
            (-thick, - closet_size - thick),
            (-thick, -thick),
            (-thick -  shelves_hang, -thick),
            ]
        return pts
    pts_shelv = points_hanger_shelves(front_height, thick, angle, hang_len, shelves_hang)
    hanger_shelv = (cq.Workplane("XY")
            .polyline(pts_shelv)
            .close()
            .extrude(hanger_depth)
            .edges("|Z")
            .fillet(thick/5)
            )
    return hanger_shelv

def box(box_x, box_y, box_z, box_wall, honey_rad, closet_size, hanger_depth, front_height, thick, angle, hang_len):
    pts_diff = points_hanger(closet_size, front_height, thick + tollerance, angle, hang_len+tollerance)
    hanger_diff = (cq.Workplane("XY")
                    .polyline(pts_diff)
                    .close()
                    .extrude(hanger_depth+tollerance)
                    .edges("|Z")
                    .fillet(thick/5)
                    )

    box = ( cq.Workplane()
            .box(box_y-box_wall*2, box_z-box_wall, box_x-box_wall*2)
            .translate((closet_size/2 + thick + box_y/2 + tollerance, -front_height + -thick + box_z/2 - box_wall, 0))
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

