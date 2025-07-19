import streamlit as st 
import math 
st.title("Hello,world") 

def circle(r):
     return math.pi * r**2 

r = st.number_input("Radius:") 
st.write("Circle area:", circle(r))