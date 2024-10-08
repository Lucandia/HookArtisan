import cadquery as cq
import streamlit as st
import os
from streamlit_stl import stl_from_file
from models import *

if __name__ == "__main__":
    st.title('HookArtisan')
    st.write("Generate hooks and hang boxes for you personal shelves.  If you like the project put a like on [Printables](https://www.printables.com/it/model/714058-HookArtisan-custom-hanger-generator) or [support me with a coffee](https://www.paypal.com/donate/?hosted_button_id=V4LJ3Z3B3KXRY)!", unsafe_allow_html=True)

    with st.sidebar:
        model_type = st.selectbox('Model type', ["Door Hook", "Shelf Hook"])
        closet_size = st.number_input('Door/shelf thickness (mm)', value=20.0)
        hooks = st.number_input('N° hooks', min_value=1, value=1)
        out_format = st.selectbox("Output format", ['stl', 'step'])

    back_height = 0 
    back_angle = 0
    back_hanger_len = 0
    mirror = False 
    back_hooks = 1 
    shelf_arm = 0

    st.subheader("Hook parameters (mm):")
    if model_type == 'Door Hook':
        with st.sidebar:
            mirror = st.toggle('Mirror')
            back_hook = False
            if not mirror:
                col1, col2 = st.columns(2)
                with col1: back_hook = st.toggle("Back hook")
                if back_hook:
                    with col2: back_hooks = st.number_input('N° back hooks', min_value=1, value=1)
        col1, col2, col3 = st.columns(3)
        with col1: hanger_depth = st.slider('Width', min_value=5, max_value=100, value=10)
        with col2: front_height = st.slider('Length', min_value=2, max_value=500, value=50)
        with col3: angle = st.slider('Angle', min_value=10, max_value=90, value=45)
        col1, col2, col3 = st.columns(3)
        with col1: thick = st.slider('Thickness', min_value=1.0, max_value=50.0, value=4.0)
        with col2: hang_len = st.slider('Arm length', min_value=10, max_value=100, value=25)

        if not mirror:
            with col3: back_height = st.slider('Back length', min_value=2, max_value=500, value=25)
        col1, col2, col3 = st.columns(3)
        if back_hook:
            with col2: back_hanger_len = st.slider('Back arm length', min_value=10, max_value=100, value=25)
            with col3: back_angle = st.slider('Back angle', min_value=10, max_value=90, value=45) 

        
        # model = normal_hanger(closet_size, hanger_depth, front_height, thick, angle, hang_len, back_height, back_angle, back_hanger_len, mirror, hooks)
        
    if model_type == 'Shelf Hook':    
        col1, col2, col3 = st.columns(3)
        with col1: hanger_depth = st.slider('Width', min_value=5, max_value=100, value=10)
        with col2: front_height = st.slider('Length', min_value=2, max_value=500, value=50)
        with col3: angle = st.slider('Angle', min_value=10, max_value=90, value=45)
        col1, col2, col3 = st.columns(3)
        with col1: thick = st.slider('Thickness', min_value=1.0, max_value=50.0, value=4.0)
        with col2: hang_len = st.slider('Arm length', min_value=10, max_value=100, value=25)
        with col3: shelf_arm = st.slider('Shelf arm length', min_value=5, max_value=50, value=40)
        # model = shelves_hunger(closet_size, hanger_depth, front_height, thick, angle, hang_len, shelf_arm, hooks)

    try:
        model = hanger(closet_size, hanger_depth, front_height, thick, angle, hang_len, back_height, back_angle, back_hanger_len, mirror, hooks, back_hooks, shelf_arm)

        # EXPORT HANGER
        cq.exporters.export(model, "hook_artisan_display.stl")
        cq.exporters.export(model, f"HookArtisan.{out_format}")
        with st.sidebar:
            st.markdown("I am a student who enjoys 3D printing and programming. To support me with a coffee, just [click here!](https://www.paypal.com/donate/?hosted_button_id=V4LJ3Z3B3KXRY)", unsafe_allow_html=True)
            if f'HookArtisan.{out_format}' not in os.listdir():
                st.error('The program was not able to generate the mesh.', icon="🚨")
            else:
                with open(f'HookArtisan.{out_format}', "rb") as file:
                    btn = st.download_button(
                            label=f"Download {out_format}",
                            data=file,
                            file_name=f'HookArtisan_{"_".join(model_type.split())}.{out_format}',
                            mime=f"model/{out_format}"
                        )
        stl_from_file("hook_artisan_display.stl", color='#696969')
    except:
        st.error('The program was not able to generate the mesh. Try different parameters,', icon="🚨")

    # add the box
    with st.sidebar:
        add_box = st.toggle(':green[Create Hook Box]')
        if add_box:
            hex_base = st.toggle('Hex Holes')
    if add_box:
        st.subheader("Box parameters (mm):")
        col1, col2, col3 = st.columns(3)
        with col1: box_x = st.slider('Box x', min_value=5, max_value=500, value=100)
        with col2: box_y = st.slider('Box y', min_value=5, max_value=500, value=50)
        with col3: box_z = st.slider('Box z', min_value=5, max_value=200, value=40)
        col1, col2, col3 = st.columns(3)
        with col1: box_wall = st.slider('Wall thickness', min_value=1.0, max_value=20.0, value=4.0)
        honey_rad = 0
        if hex_base:
            with col2:
                honey_rad = st.slider('Hex diameter', min_value=5, max_value=30)

        try:
            box = box(box_x, box_y, box_z, box_wall, honey_rad, closet_size, hanger_depth, front_height, thick, angle, hang_len, hooks)
            # EXPORT BOX
            cq.exporters.export(box, "box_display.stl")
            cq.exporters.export(box, f"HookArtisan_box.{out_format}")
            with st.sidebar:
                if f'HookArtisan_box.{out_format}' not in os.listdir():
                    st.error('The program was not able to generate the box.', icon="🚨")
                else:
                    with open(f'HookArtisan_box.{out_format}', "rb") as file:
                        btn = st.download_button(
                                label=f"Download {out_format}",
                                data=file,
                                file_name=f'HookArtisan_box.{out_format}',
                                mime=f"model/{out_format}"
                            )
            stl_from_file("box_display.stl", color='#696969')
        except:
            st.error('The program was not able to generate the mesh. Try different parameters,', icon="🚨")
        
 
