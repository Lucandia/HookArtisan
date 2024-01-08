import cadquery as cq
import streamlit as st
import time
import os
from uuid import uuid4
from models import *

def stl_preview(text, color, render):
    # Load and embed the JavaScript file
    with open("js/three.min.js", "r") as js_file:
        three_js = js_file.read()

    with open("js/STLLoader.js", "r") as js_file:
        stl_loader = js_file.read()

    with open("js/OrbitControls.js", "r") as js_file:
        orbital_controls = js_file.read()

    with open("js/stl-viewer.js", "r") as js_file:
        stl_viewer_component = (
            js_file.read()
            .replace('{__REPLACE_COLOR__}',f'0x{color[1:]}')
            .replace('{__REPLACE_MATERIAL__}',render)
        )
    session_id = st.session_state['session_id']
    st.components.v1.html(
        r'<div style="height:500px">'+
        r'<script>'+
        three_js+' '+
        stl_loader+' '+
        orbital_controls+' '+
        stl_viewer_component+' '+
        r'</script>'+
        r'<stl-viewer model="./app/static/' + text + '_' + str(session_id) + '.stl?cache='+str(time.time())+r'"></stl-viewer>'+
        r'</div>',
        height = 500
        )

if __name__ == "__main__":
    # initialize session id
    if "session_id" not in st.session_state:
        st.session_state['session_id'] = uuid4()
    session_id = st.session_state['session_id']
    
    st.title('HangHub')
    st.write("Generate hang hooks and hang boxes for you personal shelves.  If you like the project put a like on [Printables](https://www.printables.com/it/model/520333-texttango-dual-letter-illusion) or [support me with a coffee](https://www.paypal.com/donate/?hosted_button_id=V4LJ3Z3B3KXRY)!", unsafe_allow_html=True)

    with st.sidebar:
        model_type = st.selectbox('Model type', ["Door Hanger", "Shelf Hanger"])
        closet_size = st.number_input('Door thickness (mm)', value=20.0)
        out_format = st.selectbox("Output format", ['stl', 'step'])

    if model_type == 'Door Hanger':
        with st.sidebar:
            mirror = st.toggle('Mirror')
            back_hook = False
            if not mirror:
                back_hook = st.toggle("Back hook")
        st.write("Hanger parameters (mm):")
        col1, col2, col3 = st.columns(3)
        with col1: hanger_depth = st.slider('Width', min_value=5, max_value=100, value=10)
        with col2: front_height = st.slider('Length', min_value=2, max_value=500, value=50)
        with col3: angle = st.slider('Angle', min_value=10, max_value=90, value=45)
        col1, col2, col3 = st.columns(3)
        with col1: thick = st.slider('Thickness', min_value=1.0, max_value=50.0, value=4.0)
        with col2: hang_len = st.slider('Arm length', min_value=10, max_value=100, value=25)

        back_height = 0
        if not mirror:
            with col3: back_height = st.slider('Back length', min_value=2, max_value=500, value=50)
        col1, col2, col3 = st.columns(3)
        back_angle = 0
        back_hanger_len = 0
        if back_hook:
            with col2: back_hanger_len = st.slider('Back arm length', min_value=10, max_value=100, value=25)
            with col3: back_angle = st.slider('Back angle', min_value=10, max_value=90, value=45) 
        model = normal_hanger(closet_size, hanger_depth, front_height, thick, angle, hang_len, back_height, back_angle, back_hanger_len, mirror)
        
    if model_type == 'Shelf Hanger':    
        st.write("Hanger parameters (mm):")
        col1, col2, col3 = st.columns(3)
        with col1: hanger_depth = st.slider('Width', min_value=5, max_value=100, value=10)
        with col2: front_height = st.slider('Length', min_value=2, max_value=500, value=50)
        with col3: angle = st.slider('Angle', min_value=10, max_value=90, value=45)
        col1, col2, col3 = st.columns(3)
        with col1: thick = st.slider('Thickness', min_value=1.0, max_value=50.0, value=4.0)
        with col2: hang_len = st.slider('Arm length', min_value=10, max_value=100, value=25)
        with col3: shelf_arm = st.slider('Shelf arm length', min_value=5, max_value=50, value=40)
        model = shelves_hunger(closet_size, hanger_depth, front_height, thick, angle, hang_len, shelf_arm)
    
    # EXPORT HANGER
    cq.exporters.export(model, f"./app/static/model_{session_id}.stl")
    cq.exporters.export(model, f"hanghub.{out_format}")
    with st.sidebar:
        st.markdown("I am a student who enjoys 3D printing and programming. To support me with a coffee, just [click here!](https://www.paypal.com/donate/?hosted_button_id=V4LJ3Z3B3KXRY)", unsafe_allow_html=True)
        if f'hanghub.{out_format}' not in os.listdir():
            st.error('The program was not able to generate the mesh.', icon="🚨")
        else:
            with open(f'hanghub.{out_format}', "rb") as file:
                btn = st.download_button(
                        label=f"Download {out_format}",
                        data=file,
                        file_name=f'HangHub_{"_".join(model_type.split())}.{out_format}',
                        mime=f"model/{out_format}"
                    )
    stl_preview('model', '#696969', "material")

    # add the box
    with st.sidebar:
        add_box = st.toggle(':green[Create Hanger Box]')
        if add_box:
            hex_base = st.toggle('Hex Holes')
    if add_box:
        col1, col2, col3 = st.columns(3)
        with col1: box_x = st.slider('Box x', min_value=5, max_value=500, value=100)
        with col2: box_y = st.slider('Box y', min_value=5, max_value=500, value=50)
        with col3: box_z = st.slider('Box z', min_value=5, max_value=200, value=40)
        col1, col2, col3 = st.columns(3)
        with col1: box_wall = st.slider('Box wall', min_value=1, max_value=20, value=4)
        honey_rad = 0
        if hex_base:
            with col2:
                honey_rad = st.slider('Hex diameter', min_value=5, max_value=30)
        box = box(box_x, box_y, box_z, box_wall, honey_rad, closet_size, hanger_depth, front_height, thick, angle, hang_len)


        # EXPORT BOX
        cq.exporters.export(box, f"./app/static/box_{session_id}.stl")
        cq.exporters.export(box, f"hanghub_box.{out_format}")
        with st.sidebar:
            if f'hanghub_box.{out_format}' not in os.listdir():
                st.error('The program was not able to generate the box.', icon="🚨")
            else:
                with open(f'hanghub_box.{out_format}', "rb") as file:
                    btn = st.download_button(
                            label=f"Download {out_format}",
                            data=file,
                            file_name=f'HangHub_box.{out_format}',
                            mime=f"model/{out_format}"
                        )
        stl_preview('box', '#696969', "material") 
        
 