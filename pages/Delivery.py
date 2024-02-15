import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime
from pushbullet import Pushbullet


st.title("Delivery Management")
st.markdown("Select option from below")
Push_API="o.YsbcZIdI3a94aC3bnXT4Znf4FQz2f77d"
pb=Pushbullet(Push_API)

OUTLETS=["Residency Road","Koramangala","Jayanagar","Bellandur","Whitefield","Marathahalli","Kalyan Nagar","SahakarNagar","E City","Domlur","Arekere"]
conn=st.connection("gsheets", type=GSheetsConnection)
existing_data=conn.read(worksheet="Requests",usecols=list(range(7)),ttl=5)

action = st.selectbox(
    "Choose an Action",
    [
        "Place an Order",
        "View and Update Existing Orders",
    ],
)

if action == "Place an Order":
    st.markdown("Enter Details of the Order Below")
    orderdate=datetime.date.today()
    ordernumber=max(existing_data["Entry Number"])+1
    with st.form(key="order_form"):
        outletname=st.selectbox("Outlet Name",options=OUTLETS,index=None)
        ordertype=st.selectbox("Order Type",["Emergency Order","Regular Delivery"])
        productlist=st.text_input(label="Product List")
        submit_button=st.form_submit_button(label="Submit Order")
        if submit_button:
            if not outletname or not productlist or not ordertype:
                st.warning("Ensure all mandatory fields are filled.")
            else:
                order_data=pd.DataFrame(
                     [
                          {
                               "Date":orderdate,
                               "Type":ordertype,
                               "Outlet":outletname,
                               "Items":productlist,
                               "Status":"Not Sent",
                               "Entry Number":ordernumber
                          }
                     ]
                )
                updated_df=pd.concat([existing_data,order_data],ignore_index=True)
                conn.update(worksheet="Requests",data=updated_df)
                
                st.success("You submitted the order")
                push=pb.push_note('New Order Received',outletname)

elif action=="View and Update Existing Orders":
    sql = '''
    SELECT
        "Entry Number",
        "Date",
        "Type",
        "Outlet",
        "Items",
        "Status",
        "Reason"
    FROM
        Requests
    WHERE
        "Status"='Not Sent'

'''

    mydata=conn.query(sql=sql,ttl=5)
    st.dataframe(mydata)
    st.markdown("Select the order which you want to mark as sent")
    orderselect=st.selectbox("Entry Number",options=mydata["Entry Number"].tolist())
    updateorderdata=existing_data[existing_data["Entry Number"]==orderselect].iloc[0]
    with st.form("Update Order"):
        status=st.selectbox("Updated Status",options=["Sent","Ignored"])
        reason=st.text_input("Enter reason for ignoring:")
        update_button=st.form_submit_button(label="Update Status")
        if update_button:
            existing_data.drop(existing_data[existing_data["Entry Number"] == orderselect].index,inplace=True,)
            outletname=updateorderdata["Outlet"]
            ordertype=updateorderdata["Type"]
            orderdate=updateorderdata["Date"]
            productlist=updateorderdata["Items"]
            ordernumber=updateorderdata["Entry Number"]
            order_data=pd.DataFrame(
                     [
                          {
                               "Date":orderdate,
                               "Type":ordertype,
                               "Outlet":outletname,
                               "Items":productlist,
                               "Status":status,
                               "Entry Number":ordernumber,
                               "Reason":reason
                          }
                     ]
                )
            updated_df=pd.concat([existing_data,order_data],ignore_index=True)
            conn.update(worksheet="Requests",data=updated_df)
            st.success("You submitted the order")
            









