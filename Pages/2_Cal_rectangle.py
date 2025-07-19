import streamlit as st



def cal_rectangle_area(w,h):
    return w * h

area = cal_rectangle_area(10,2)

print ("the area is " + str(area))
print (f"the area is {area}" )

def cal_circle_area(r):
    return 3.14*r*r

st.title("Shape calculator")
st.write("this is the calculator app.")

radius = st.number_input("Enter radius")
submit_btn = st.button("submit")
if submit_btn:
    area = cal_circle_area(radius)
    st.write(f"the area is {area}")



circle_area = cal_circle_area(4)

print ("the area is " + str(circle_area))
print (f"the area is {circle_area}" )
