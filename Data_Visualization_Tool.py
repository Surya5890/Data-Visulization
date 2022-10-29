import streamlit as st
import matplotlib.pyplot as plt
from datetime import date, timedelta, datetime
import pandas as pd
import psycopg2 as psy
import altair as alt
import seaborn as sns
import numpy as np
import emoji
from st_aggrid import AgGrid

connection = psy.connect(user="postgres",
                                      password="12345",
                                      host="localhost",
                                      port="5432",
                                      database="postgres")
    
cursor = connection.cursor()


#datetime.datetime.strptime(d2['Date'],"%y-%m-%y")

def type_analysis(p1,p2, in1, in2):
    
    pi1=p1
    pi2=p2
    #st.pyplot(draw_pie(pi1, in1)|draw_pie(pi1, in1)
    
    draw_pie(pi1, in1)
    draw_pie(pi2, in2)
    
def draw_pie(pi1,in2):
    fig, ax = plt.subplots()
    patches, texts, pcts = ax.pie(
        pi1['Count'], labels=pi1['Type'],autopct='%1d%%',
        wedgeprops={'linewidth': 3.0, 'edgecolor': 'white'},
        textprops={'size': 'x-large'},
        startangle=90)
    # For each wedge, set the corresponding text label color to the wedge's
    # face color.
    for i, patch in enumerate(patches):
      texts[i].set_color(patch.get_facecolor())
    plt.setp(pcts, color='white')
    plt.setp(texts, fontweight=600)
    ax.set_title(in2+"'s case type analysis", fontsize=11)
    st.pyplot(fig)

def first_bar(s):
    st.markdown('**Number of Tickets worked on**.')
    fig, ax = plt.subplots()
    chart = sns.barplot(x = 'Date', y = 'Count', hue = 'Name', data = s,
            edgecolor = 'w', ci=None)
    plt.ylim(0,7)
    plt.show()
    for p in chart.patches:
                 chart.annotate("%.0f" % p.get_height(), (p.get_x() + p.get_width() / 2., p.get_height()),
                     ha='center', va='center', fontsize=10, color='black', xytext=(0, 5),
                     textcoords='offset points')
    x_dates = s['Date'].dt.strftime('%Y-%m-%d').sort_values().unique()
    ax.set_xticklabels(labels=x_dates, rotation=0, ha='right')
    st.pyplot(fig)
        
def line_chart(i1, d1, d2):
    q = """ select sum("Hours_worked"), "Owner_name", to_char("Status_changed_timestamp",'yyyy-mm-dd') 
from "Project"."All_Ticket" 
where "Owner_name" like %s
group by "Owner_name", to_char("Status_changed_timestamp",'yyyy-mm-dd')
order by 3,2;
"""
    cursor.execute(q, (i1,))
    l1 = pd.DataFrame(cursor.fetchall())
    l1.rename(columns = {0:'Hours',1:'Name', 2:'Date'}, inplace = True)
    l1['Date'] = pd.to_datetime(l1['Date']).dt.date
    l11 = (l1['Date'] >= np.datetime64(d1)) & (l1['Date'] <= np.datetime64(d2))
    l1=l1.loc[l11]
    l1['Hours'] = l1['Hours'].astype(float)
    chart = alt.Chart(l1, title = "Working Hours: "+i1).mark_line(point={
      "filled": False,
      "fill": "white"
    }).encode(
        x='Date',
        y=alt.Y('Hours'),
        #tooltip = 'Ticket',
        color=alt.Color('Name',
                scale=alt.Scale(
                    domain=l1.Name.unique())
                    )
    ).interactive()
    return chart

def sla_breach(in1, in2, s, e):
    st.write("SLA Breach Analysis")
    q3 = """select foo1."Ticket_number", foo1."Owner_name", foo1."Ticket_Status", foo2."Ticket_status",
    foo1."Status_changed_timestamp",
    to_char(foo1."Status_changed_timestamp", 'yyyy-mm-dd'), foo1."Due_date", foo3."boo"
    from "Project"."All_Ticket" foo1 
    left join (select count(distinct("Ticket_number")) "boo", to_char("Creation_timestamp", 'yyyy-mm-dd') "boo1"
    from "Project"."Ticket" where "Owner_name" like %s
    group by to_char("Creation_timestamp", 'yyyy-mm-dd')) foo3 
    on foo3."boo1" = to_char(foo1."Status_changed_timestamp", 'yyyy-mm-dd')
    join "Project"."Ticket" foo2 on foo1."Ticket_number" = foo2."Ticket_number" 
    where foo1."Owner_name" like %s;"""
    
    click = alt.selection_multi(encodings=['color'])
    cursor.execute(q3, (in1, in1))
    df = pd.DataFrame(cursor.fetchall())
    df.columns = ['Ticket', 'Name', 'Status', 'cur_sta','sta_tim','sta_date','Due', 'Count']
    df['Count'] = df['Count'].fillna(0)
    df['Count'] = df['Count'].astype(int)
    conditions = [df['sta_tim'] >= df['Due']]
    choices = ['Y']
    df['SLA'] = np.select(conditions, choices, default='N')
    df.sta_date= pd.to_datetime(df.sta_date)
    p11 = (df['sta_date'] >= np.datetime64(s)) & (df['sta_date'] <= np.datetime64(e))
    df=df.loc[p11]
    print(df.loc[df['SLA']=='Y'])
    scales = alt.selection_interval(bind='scales')
    print(df.loc[df['SLA']=='Y'])
    scales = alt.selection_interval(bind='scales')
    df1 = df.loc[df['SLA']=='Y']
    s1 = 'Null'
    s2 = 'Null'
    temp1 = 0
    temp2 = 0
    chart1 = None
    chart2 = None
    chart1 = alt.Chart(df, title = in1+" Queue").mark_circle().encode(
            x='sta_date',
            y='SLA',
            color='SLA',
            tooltip = ['Ticket','Status','cur_sta']
        ).interactive().properties(
            width=500,
            height=300
        )

    s1 = "No Tickets breached SLA for "+in1
    temp1 = 0

    #click = alt.selection_multi(encodings=['color'])
    cursor.execute(q3, (in2, in2))
    df3 = pd.DataFrame(cursor.fetchall())
    df3.columns = ['Ticket', 'Name', 'Status', 'cur_sta','sta_tim','sta_date','Due', 'Count']
    df3['Count'] = df3['Count'].fillna(0)
    df3['Count'] = df3['Count'].astype(int)
    conditions = [df3['sta_tim'] >= df3['Due']]
    choices = ['Y']
    df3['SLA'] = np.select(conditions, choices, default='N')
    df3.sta_date= pd.to_datetime(df3.sta_date)
    p11 = (df3['sta_date'] >= np.datetime64(s)) & (df3['sta_date'] <= np.datetime64(e))
    df3=df3.loc[p11]
    print(df3.loc[df3['SLA']=='Y'])
    scales = alt.selection_interval(bind='scales')
    print(df3.loc[df3['SLA']=='Y'])
    scales = alt.selection_interval(bind='scales')
    df2 = df3.loc[df3['SLA']=='Y']

    chart2 = alt.Chart(df3, title = in2+" Queue").mark_circle().encode(
            x='sta_date',
            y='SLA',
            color='SLA',
            tooltip = ['Ticket','Status','cur_sta']
        ).interactive().properties(
            width=500,
            height=300
        )

    s2 = "No Tickets breached SLA for "+in2
    
    if df1.empty == False:
        if df2.empty == False:
            st.altair_chart(chart1 | chart2)
        else:
            st.altair_chart(chart1)
            st.write(s2+(emoji.emojize(' Way to go thumbs_up:')))
    else:
        st.write(s1)
        if df2.empty == False:
            st.altair_chart(chart2)
        else:
            st.write(s2+(emoji.emojize(' Way to go :thumbs_up:')))
        

def case_ana(in1, in2, s, e):
    
    q = """ select "Ticket_number", "Ticket_status","Sub-type","Creation_timestamp", 
    "Closed_timestamp", "Last_comment_updated","Age", "Hours_worked"
    from "Project"."Ticket" where "Owner_name" like %s;
    """
    cursor.execute(q, (in1,))
    l1= pd.DataFrame(cursor.fetchall())
    l1.columns = ['Ticket', 'status','Type','Creation', 'Closed', 'last','Age', 'Hours']
    l1['Hours'] = l1['Hours'].astype(float)
    l1['Age'] = l1['Age'].astype(float)
    print(l1.dtypes)
    
    l1.Creation= pd.to_datetime(l1.Creation).dt.date
    p11 = (l1['Creation'] >= np.datetime64(s)) & (l1['Creation'] <= np.datetime64(e))
    l1=l1.loc[p11]
    
    #click = alt.selection_multi(encodings=['color'])
    click = alt.selection_multi(encodings=['color'], toggle=False)
    # scatter plots of points
    scatter = alt.Chart(l1, title = "Analysing Resolution Hours: "+in1).mark_circle().encode(
        x='Creation',
        y='sum(Hours)',
        size=alt.Size('Age',
            scale=alt.Scale(range=(20,100))
        ),
        color=alt.Color('Type', legend=None),
        tooltip=['Ticket', 'Creation', 'Hours'],
    ).transform_filter(
        click
    ).interactive()
    
    # legend
    legend = alt.Chart(l1).mark_rect().encode(
        y=alt.Y('Type', axis=alt.Axis(title='Select Origin')),
        color=alt.condition(click, 'Type', 
                            alt.value('lightgray'), legend=None),
        size=alt.value(250)
    ).properties(
        selection=click
    )
    chart1 = (scatter | legend)
        
    cursor.execute(q, (in2,))
    l1= pd.DataFrame(cursor.fetchall())
    l1.columns = ['Ticket', 'status','Type','Creation', 'Closed', 'last','Age', 'Hours']
    l1['Hours'] = l1['Hours'].astype(float)
    l1['Age'] = l1['Age'].astype(float)
    print(l1.dtypes)
    
    l1.Creation= pd.to_datetime(l1.Creation).dt.date
    p11 = (l1['Creation'] >= np.datetime64(s)) & (l1['Creation'] <= np.datetime64(e))
    l1=l1.loc[p11]
    
    #click = alt.selection_multi(encodings=['color'])
    
    # scatter plots of points
    scatter = alt.Chart(l1, title = "Analysing Resolution Hours: "+in2).mark_circle().encode(
        x='Creation',
        y='sum(Hours)',
        size=alt.Size('Age',
            scale=alt.Scale(range=(20,100))
        ),
        color=alt.Color('Type', legend=None),
        tooltip=['Ticket', 'Creation', 'Hours'],
    ).transform_filter(
        click
    ).interactive()
    
    # legend
    legend = alt.Chart(l1).mark_rect().encode(
        y=alt.Y('Type', axis=alt.Axis(title='Select Origin')),
        color=alt.condition(click, 'Type', 
                            alt.value('lightgray'), legend=None),
        size=alt.value(250)
    ).properties(
        selection=click
    )
    
    chart2 = (scatter | legend)
    
    chart2 = (scatter | legend)
    st.altair_chart(chart1 | chart2)
    
def rep_cases():
    in1 = st.selectbox("Select the team: ", ["Application-1","Application-2"])
    q = """select "Ticket_number", "Owner_name","Title","Type","Sub-type","Priority", "Creation_timestamp", 
    "Investigation_summary"
    from "Project"."Ticket" 
    where "Owner_name" in (select "Member_name" from "Project"."Team" where "Team_name" like %s); """
    da1 = st.date_input("Start Date")
    da2 = st.date_input("End Date")
    cursor.execute(q, (in1,))
    df = pd.DataFrame(cursor.fetchall())
    click = alt.selection_multi(encodings=['color'], on='mouseover', toggle=False, empty='none')
    df.columns = ['Ticket','Owner','Title','Type','Sub-Type','Priority','Created','Investigation Comments']
    df.Created = pd.to_datetime(df.Created)
    d22=(df['Created'] >= np.datetime64(da1)) & (df['Created'] <= np.datetime64(da2))
    df=df.loc[d22]
    submit = st.button("Submit", key = '99')
    dup1 = df[df.duplicated(subset = ['Title', 'Type', 'Sub-Type'], keep = False)]
    if submit:
        if dup1.empty== False:
        
            st.write("**Showing the cases that are requested again by Customer: **")
            st.write(dup1)
            scatter = alt.Chart(dup1, title = "Repeated Case Analysis: "+in1).mark_circle().encode(
            x='Created',
            y=alt.Y('Owner',scale=alt.Scale(domain=dup1.Owner.unique())),
            color=alt.Color('Type', legend=None),
            tooltip=['Ticket','Owner','Title','Type','Sub-Type','Priority','Created','Investigation Comments'],
        ).transform_filter(
            click
        ).interactive().properties( width=500, height=300)
        
        # legend
            legend = alt.Chart(dup1).mark_rect().encode(
                y=alt.Y('Type', axis=alt.Axis(title='Case Type')),
                color=alt.condition(click, 'Type', 
                                    alt.value('lightgray'), legend=None),
                size=alt.value(250)
            ).properties(
                selection=click
            )
            chart1 = (scatter | legend)
            st.altair_chart(chart1)
        else:
            st.write("No request was repeated either for this Team or for the entered timestamp")
            st.write("Anyhow the team ##**"+in1+"**## did resolve everything fine, **Kudos!!!**" +(emoji.emojize('Way to go team :thumbs_up:')))
 
def cmp_ach():
    q1 = """select "Member_name" from "Project"."Team" 
    where "Team_name" like %s; """
    
    q2 = """select count(distinct(foo1."Ticket_number")), foo1."Owner_name", 
    to_char(foo2."Creation_timestamp",'mm/dd/yyyy') 
    from "Project"."All_Ticket" foo1 
    join "Project"."Ticket" foo2 on foo1."Ticket_number"=foo2."Ticket_number"
    where foo1."Owner_name" like %s or foo1."Owner_name" like %s 
    or foo1."Owner_name" like %s or foo1."Owner_name" like %s
    group by foo1."Owner_name", to_char(foo2."Creation_timestamp",'mm/dd/yyyy') order by 3,2;"""
        
    q3="""select count(distinct(foo1."Ticket_number")), foo2."Type", 
    foo1."Owner_name", to_char(foo2."Creation_timestamp",'mm/dd/yyyy')  from "Project"."All_Ticket" foo1 
    join "Project"."Ticket" foo2 on foo1."Ticket_number"=foo2."Ticket_number"
    where foo1."Owner_name" like %s
    group by foo2."Type", foo1."Owner_name", to_char(foo2."Creation_timestamp",'mm/dd/yyyy')
    order by 2;"""      
    in1 = st.selectbox("Select first Team",["Application-1","Application-2"], key='1')
    cursor.execute(q1,(in1,))
    
    d1=pd.DataFrame(cursor.fetchall(), columns=['Name'])
    in2 = st.selectbox("Team Member : ", d1['Name'], key='2')            
    in3 = st.selectbox("Select second Team",["Application-1","Application-2"], key = '3')
    cursor.execute(q1,(in3,))
    d1=pd.DataFrame(cursor.fetchall(), columns=['Name'])
    in4 = st.selectbox("Team Member : ", d1['Name'], key='4')
    da1 = st.date_input('start date')
    da2 = st.date_input('end date')
    
    cursor.execute(q3,(in2,))
    p1 = pd.DataFrame(cursor.fetchall(), columns= ['Count', 'Type', 'Name','Date'])
    p1.Date= pd.to_datetime(p1.Date)
    p11 = (p1['Date'] >= np.datetime64(da1)) & (p1['Date'] <= np.datetime64(da2))
    p1=p1.loc[p11]
    p1 = p1.groupby('Type').agg({'Count':'sum'})
    p1['Type']=p1.index
    
    cursor.execute(q3,(in4,))
    p2 = pd.DataFrame(cursor.fetchall(), columns= ['Count', 'Type', 'Name','Date'])
    p2.Date= pd.to_datetime(p2.Date)
    p12 = (p2['Date'] >= np.datetime64(da1)) & (p2['Date'] <= np.datetime64(da2))
    p2=p2.loc[p12]
    p2 = p2.groupby('Type').agg({'Count':'sum'})
    p2['Type']=p2.index
    
    if in4 and in2:
        cursor.execute(q2, (in1, in2, in3, in4))
        d2=pd.DataFrame(cursor.fetchall(), columns=['Count','Name','Date'])
        d2.Date = pd.to_datetime(d2.Date)
        d22=(d2['Date'] >= np.datetime64(da1)) & (d2['Date'] <= np.datetime64(da2))
        d2=d2.loc[d22]
    st.write('Select Analysing Options: ')
    option_n = st.checkbox('Number of tickets', key = '30')
    option_u = st.checkbox('Case Type Analysis', key = '31')
    option_v = st.checkbox('Working Hours Analysis', key = '32')
    option_a = st.checkbox('SLA Breach Analysis', key = '33')
    option_t = st.checkbox('Ticket Efforts Analysis', key = '34')
    submit = st.button("Submit", key = '35')
    if submit:
        #st.write(d2)
        if option_n:
            if d2.empty == False:
                first_bar(d2)
            else:
                st.write("No data found for the mentioned time frame")
        if option_u:
            if p2.empty == False and p1.empty == False:
                type_analysis(p1,p2, in2, in4)
            else:
                st.write("No data found for the mentioned time frame")
        if option_v:
            st.altair_chart(line_chart(in2, da1, da2) | line_chart(in4, da1, da2))
        if option_a:
            sla_breach(in2, in4, da1, da2)
        if option_t:
            case_ana(in2, in4, da1, da2)

def case_type_analysis(p1, p2, in1):
    
    pi1=p1
    pi2=p2
    #st.pyplot(draw_pie(pi1, in1)|draw_pie(pi1, in1)
    
    pie_chart(pi1, in1)
    pie_chart(pi2, in1)
    
def pie_chart(pi1,in2):
    fig, ax = plt.subplots()
    patches, texts, pcts = ax.pie(
        pi1['Count'], labels=pi1['Type'],autopct='%1d%%',
        wedgeprops={'linewidth': 3.0, 'edgecolor': 'white'},
        textprops={'size': 'x-large'},
        startangle=90)
    # For each wedge, set the corresponding text label color to the wedge's
    # face color.
    for i, patch in enumerate(patches):
      texts[i].set_color(patch.get_facecolor())
    plt.setp(pcts, color='white')
    plt.setp(texts, fontweight=600)
    ax.set_title(in2+"'s case type analysis", fontsize=11)
    st.pyplot(fig)

def bar_chart(s1):
    st.markdown('**Number of Tickets worked on**.')
    #st.markdown('**1. Number of Tickets worked on**.')
    fig, ax = plt.subplots()
    chart = sns.barplot(x = 'Date', y = 'Count', hue = 'Name', data = s1, edgecolor = 'w', ci=None)
    plt.ylim(0,7)
    plt.show()
    for p in chart.patches:
                 chart.annotate("%.0f" % p.get_height(), (p.get_x() + p.get_width() / 2., p.get_height()),
                     ha='center', va='center', fontsize=10, color='black', xytext=(0, 5),
                     textcoords='offset points')
    x_dates = s1['Date'].dt.strftime('%Y-%m-%d').sort_values().unique()
    ax.set_xticklabels(labels=x_dates, rotation=0, ha='right')
    st.pyplot(fig)
        
def chart_line(i1, d1, d2):
    q = """ select sum("Hours_worked"), "Owner_name", to_char("Status_changed_timestamp",'yyyy-mm-dd') 
from "Project"."All_Ticket" 
where "Owner_name" like %s
group by "Owner_name", to_char("Status_changed_timestamp",'yyyy-mm-dd')
order by 3,2;
"""
    cursor.execute(q, (i1,))
    l1 = pd.DataFrame(cursor.fetchall())
    l1.rename(columns = {0:'Hours',1:'Name', 2:'Date'}, inplace = True)
    l1['Date'] = pd.to_datetime(l1['Date']).dt.date
    l11 = (l1['Date'] >= np.datetime64(d1)) & (l1['Date'] <= np.datetime64(d2))
    l1=l1.loc[l11]
    l1['Hours'] = l1['Hours'].astype(float)
    chart = alt.Chart(l1, title = "Working Hours: "+i1).mark_line(point={
      "filled": False,
      "fill": "white"
    }).encode(
        x='Date',
        y=alt.Y('Hours'),
        tooltip = ['Date', 'Hours'],
        color=alt.Color('Name',
                scale=alt.Scale(
                    domain=l1.Name.unique())
                    )
    ).interactive()
    return chart

def sla_analysis(in1, in2, s1, e1, s2, e2):
    st.write("SLA Breach Analysis")
    q3 = """select foo1."Ticket_number", foo1."Owner_name", foo1."Ticket_Status", foo2."Ticket_status",
    foo1."Status_changed_timestamp",
    to_char(foo1."Status_changed_timestamp", 'yyyy-mm-dd'), foo1."Due_date", foo3."boo"
    from "Project"."All_Ticket" foo1 
    left join (select count(distinct("Ticket_number")) "boo", to_char("Creation_timestamp", 'yyyy-mm-dd') "boo1"
    from "Project"."Ticket" where "Owner_name" like %s
    group by to_char("Creation_timestamp", 'yyyy-mm-dd')) foo3 
    on foo3."boo1" = to_char(foo1."Status_changed_timestamp", 'yyyy-mm-dd')
    join "Project"."Ticket" foo2 on foo1."Ticket_number" = foo2."Ticket_number" 
    where foo1."Owner_name" like %s;"""
    
    click = alt.selection_multi(encodings=['color'])
    cursor.execute(q3, (in1, in1))
    df = pd.DataFrame(cursor.fetchall())
    df.columns = ['Ticket', 'Name', 'Status', 'cur_sta','sta_tim','sta_date','Due', 'Count']
    df['Count'] = df['Count'].fillna(0)
    df['Count'] = df['Count'].astype(int)
    conditions = [df['sta_tim'] >= df['Due']]
    choices = ['Y']
    df['SLA'] = np.select(conditions, choices, default='N')
    df.sta_date= pd.to_datetime(df.sta_date)
    p11 = (df['sta_date'] >= np.datetime64(s1)) & (df['sta_date'] <= np.datetime64(e1))
    df=df.loc[p11]
    print(df.loc[df['SLA']=='Y'])
    scales = alt.selection_interval(bind='scales')
    print(df.loc[df['SLA']=='Y'])
    scales = alt.selection_interval(bind='scales')
    df1 = df.loc[df['SLA']=='Y']
    temp1 = 0
    temp2 = 0
    chart1 = None
    chart2 = None
    chart1 = alt.Chart(df, title = in1+" Queue").mark_circle().encode(
            x='sta_date',
            y='SLA',
            color='SLA',
            tooltip = ['Ticket','Due','cur_sta']
        ).interactive().properties(
            width=500,
            height=300
        )

    s1 = "No Tickets breached SLA for "+in1
    temp1 = 0

    #click = alt.selection_multi(encodings=['color'])
    cursor.execute(q3, (in2, in2))
    df3 = pd.DataFrame(cursor.fetchall())
    df3.columns = ['Ticket', 'Name', 'Status', 'cur_sta','sta_tim','sta_date','Due', 'Count']
    df3['Count'] = df3['Count'].fillna(0)
    df3['Count'] = df3['Count'].astype(int)
    conditions = [df3['sta_tim'] >= df3['Due']]
    choices = ['Y']
    df3['SLA'] = np.select(conditions, choices, default='N')
    df3.sta_date= pd.to_datetime(df3.sta_date)
    p11 = (df3['sta_date'] >= np.datetime64(s2)) & (df3['sta_date'] <= np.datetime64(e2))
    df3=df3.loc[p11]
    print(df3.loc[df3['SLA']=='Y'])
    scales = alt.selection_interval(bind='scales')
    print(df3.loc[df3['SLA']=='Y'])
    scales = alt.selection_interval(bind='scales')
    df2 = df3.loc[df3['SLA']=='Y']

    chart2 = alt.Chart(df3, title = in2+" Queue").mark_circle().encode(
            x='sta_date',
            y='SLA',
            color='SLA',
            tooltip = ['Ticket','Due','cur_sta']
        ).interactive().properties(
            width=500,
            height=300
        )

    s2 = "No Tickets breached SLA for "+in2
    
    if df1.empty == False:
        if df2.empty == False:
            st.altair_chart(chart1 | chart2)
        else:
            st.altair_chart(chart1)
            st.write(s2+(emoji.emojize('... Way to go thumbs_up:')))
    else:
        st.write(s1)
        if df2.empty == False:
            st.altair_chart(chart2)
        else:
            st.write(s2+(emoji.emojize('... Way to go :thumbs_up:')))
        

def case_analysis(in1, in2, s1, e1, s2, e2):
    
    q = """ select "Ticket_number", "Ticket_status","Sub-type","Creation_timestamp", 
    "Closed_timestamp", "Last_comment_updated","Age", "Hours_worked"
    from "Project"."Ticket" where "Owner_name" like %s;
    """
    cursor.execute(q, (in1,))
    l1= pd.DataFrame(cursor.fetchall())
    l1.columns = ['Ticket', 'status','Type','Creation', 'Closed', 'last','Age', 'Hours']
    l1['Hours'] = l1['Hours'].astype(float)
    l1['Age'] = l1['Age'].astype(float)
    #print(l1.dtypes)
    
    l1.Creation= pd.to_datetime(l1.Creation).dt.date
    p11 = (l1['Creation'] >= np.datetime64(s1)) & (l1['Creation'] <= np.datetime64(e1))
    l1=l1.loc[p11]
    
    #click = alt.selection_multi(encodings=['color'])
    click = alt.selection_multi(encodings=['color'], toggle=False)
    # scatter plots of points
    scatter = alt.Chart(l1, title = "Analysing Resolution Hours: "+in1).mark_circle().encode(
        x='Creation',
        y='sum(Hours)',
        size=alt.Size('Age',
            scale=alt.Scale(range=(20,100))
        ),
        color=alt.Color('Type', legend=None),
        tooltip=['Ticket', 'Creation', 'Hours'],
    ).transform_filter(
        click
    ).interactive()
    
    # legend
    legend = alt.Chart(l1).mark_rect().encode(
        y=alt.Y('Type', axis=alt.Axis(title='Select Origin')),
        color=alt.condition(click, 'Type', 
                            alt.value('lightgray'), legend=None),
        size=alt.value(250)
    ).properties(
        selection=click
    )
    chart1 = (scatter | legend)
        
    cursor.execute(q, (in2,))
    l1= pd.DataFrame(cursor.fetchall())
    l1.columns = ['Ticket', 'status','Type','Creation', 'Closed', 'last','Age', 'Hours']
    l1['Hours'] = l1['Hours'].astype(float)
    l1['Age'] = l1['Age'].astype(float)
    #print(l1.dtypes)
    
    l1.Creation= pd.to_datetime(l1.Creation).dt.date
    p11 = (l1['Creation'] >= np.datetime64(s2)) & (l1['Creation'] <= np.datetime64(e2))
    l1=l1.loc[p11]
    
    #click = alt.selection_multi(encodings=['color'])
    
    # scatter plots of points
    scatter = alt.Chart(l1, title = "Analysing Resolution Hours: "+in2).mark_circle().encode(
        x='Creation',
        y='sum(Hours)',
        size=alt.Size('Age',
            scale=alt.Scale(range=(20,100))
        ),
        color=alt.Color('Type', legend=None),
        tooltip=['Ticket', 'Creation', 'Hours'],
    ).transform_filter(
        click
    ).interactive()
    
    # legend
    legend = alt.Chart(l1).mark_rect().encode(
        y=alt.Y('Type', axis=alt.Axis(title='Select Origin')),
        color=alt.condition(click, 'Type', 
                            alt.value('lightgray'), legend=None),
        size=alt.value(250)
    ).properties(
        selection=click
    )
    
    chart2 = (scatter | legend)
    
    chart2 = (scatter | legend)
    st.altair_chart(chart1 | chart2)
    
def self_cmp():
    q1 = """select "Member_name" from "Project"."Team" 
    where "Team_name" like %s; """
    
    q2 = """select count(distinct(foo1."Ticket_number")), foo1."Owner_name", 
    to_char(foo2."Creation_timestamp",'mm/dd/yyyy') 
    from "Project"."All_Ticket" foo1 
    join "Project"."Ticket" foo2 on foo1."Ticket_number"=foo2."Ticket_number"
    where foo1."Owner_name" like %s or foo1."Owner_name" like %s 
    group by foo1."Owner_name", to_char(foo2."Creation_timestamp",'mm/dd/yyyy') order by 3,2;"""
        
    q3="""select count(distinct(foo1."Ticket_number")), foo2."Type", 
    foo1."Owner_name", to_char(foo2."Creation_timestamp",'mm/dd/yyyy')  from "Project"."All_Ticket" foo1 
    join "Project"."Ticket" foo2 on foo1."Ticket_number"=foo2."Ticket_number"
    where foo1."Owner_name" like %s
    group by foo2."Type", foo1."Owner_name", to_char(foo2."Creation_timestamp",'mm/dd/yyyy')
    order by 2;"""      
    in1 = st.selectbox("Select first Team",["Application-1","Application-2"], key='119')
    cursor.execute(q1,(in1,))
    
    d1=pd.DataFrame(cursor.fetchall(), columns=['Name'])
    in2 = st.selectbox("Team Member : ", d1['Name'], key='122')            
    da1 = st.date_input('First start date', key = '10')
    da2 = st.date_input('First end date', key =  '11')
    da3 = st.date_input('Second Start date', key =  '12')
    da4 = st.date_input('Second end date', key =  '13')
    cursor.execute(q3,(in2,))
    p1 = pd.DataFrame(cursor.fetchall(), columns= ['Count', 'Type', 'Name','Date'])
    p1.Date= pd.to_datetime(p1.Date)
    p11 = (p1['Date'] >= np.datetime64(da1)) & (p1['Date'] <= np.datetime64(da2))
    p2=p1.loc[p11]
    p2 = p2.groupby('Type').agg({'Count':'sum'})
    p2['Type'] = p2.index
    
    cursor.execute(q3,(in2,))
    p4 = pd.DataFrame(cursor.fetchall(), columns= ['Count', 'Type', 'Name','Date'])
    p4.Date= pd.to_datetime(p4.Date)
    p11 = (p4['Date'] >= np.datetime64(da3)) & (p4['Date'] <= np.datetime64(da4))
    p3 = p4.loc[p11]
    p3 = p3.groupby('Type').agg({'Count':'sum'})
    p3['Type'] = p3.index
    
    #st.write(p2)
    #st.write(p3)    
    if in2:
        cursor.execute(q2, (in1, in2))
        d2=pd.DataFrame(cursor.fetchall(), columns=['Count','Name','Date'])
        d2.Date = pd.to_datetime(d2.Date)
        d22=(d2['Date'] >= np.datetime64(da1)) & (d2['Date'] <= np.datetime64(da2))
        d3=d2.loc[d22]
        #st.write(d3)
        
        d23=(d2['Date'] >= np.datetime64(da3)) & (d2['Date'] <= np.datetime64(da4))
        d4=d2.loc[d23]
        #st.write(d4)
        #st.write(d2)
        #st.write(d3)
        #st.write(d4)
    st.write('Select Analysing Options: ')
    option_n = st.checkbox('Number of tickets', key = '20')
    option_u = st.checkbox('Case Type Analysis', key = '21')
    option_v = st.checkbox('Working Hours Analysis', key = '22')
    option_a = st.checkbox('SLA Breach Analysis', key = '23')
    option_t = st.checkbox('Ticket Efforts Analysis', key = '24')
    submit = st.button("Submit",key = '189')
    if submit:
        #st.write(d2)
        if option_n:
            if d3.empty == False:
                bar_chart(d3)
            else:
                st.write("No Data found for the time period")
            if d4.empty == False:
                bar_chart(d4)
            else:
                st.write("No Data found for the time period")
        if option_u:
            if p3.empty == False and p4.empty == False:
                case_type_analysis(p2,p3, in2)
            else:
                st.write("No Data found for the time period")
                   
        if option_v:
            st.altair_chart(chart_line(in2, da1, da2) | chart_line(in2, da3, da4))
        if option_a:
            sla_analysis(in2, in2, da1, da2, da3, da4)
        if option_t:
            case_analysis(in2, in2, da1, da2, da3, da4)
            
def cta_type_analysis(in1,in2, da1, da2):
    q3="""select count(distinct(foo1."Ticket_number")), foo2."Type", 
    foo1."Owner_name", to_char(foo2."Creation_timestamp",'mm/dd/yyyy')  from "Project"."All_Ticket" foo1 
    join "Project"."Ticket" foo2 on foo1."Ticket_number"=foo2."Ticket_number"
    where foo1."Owner_name" like %s
    group by foo2."Type", foo1."Owner_name", to_char(foo2."Creation_timestamp",'mm/dd/yyyy')
    order by 2;"""      
    cursor.execute(q3,(in1,))
    p1 = pd.DataFrame(cursor.fetchall(), columns= ['Count', 'Type', 'Name','Date'])
    
    
    p1.Date= pd.to_datetime(p1.Date)
    p11 = (p1['Date'] >= np.datetime64(da1)) & (p1['Date'] <= np.datetime64(da2))
    p1=p1.loc[p11]
    p4 = p1.groupby('Type').agg({'Count':'sum'})
    p4['Type']=p4.index
    #st.write(p4)
    
    cursor.execute(q3,(in2,))
    
    p2 = pd.DataFrame(cursor.fetchall(), columns= ['Count', 'Type', 'Name','Date'])
    p2.Date= pd.to_datetime(p2.Date)
    p21 = (p2['Date'] >= np.datetime64(da1)) & (p2['Date'] <= np.datetime64(da2))
    p2=p2.loc[p21]
    p3 = p2.groupby('Type').agg({'Count':'sum'})
    p3['Type']=p3.index
    #st.write(p3)
    
    cta_draw_pie(p4, in1)
    cta_draw_pie(p3, in2)
    
def cta_draw_pie(pi1,in2):
    
    fig, ax = plt.subplots()
    patches, texts, pcts = ax.pie(
        pi1['Count'], labels=pi1['Type'],autopct='%1d%%',
        wedgeprops={'linewidth': 3.0, 'edgecolor': 'white'},
        textprops={'size': 'x-large'},
        startangle=90)
    # For each wedge, set the corresponding text label color to the wedge's
    # face color.
    for i, patch in enumerate(patches):
      texts[i].set_color(patch.get_facecolor())
    plt.setp(pcts, color='white')
    plt.setp(texts, fontweight=600)
    ax.set_title(in2+"'s case type analysis", fontsize=11)
    st.pyplot(fig)

def cta():
    q1 = """select "Member_name" from "Project"."Team" 
    where "Team_name" like %s; """
    in1 = st.selectbox("Select first Team",["Application-1","Application-2"], key='40')
    cursor.execute(q1,(in1,))
    d1=pd.DataFrame(cursor.fetchall(), columns=['Name'])
    in2 = st.selectbox("Team Member : ", d1['Name'], key='41')  
    st.write("** Case Type Analysis **")
    s = st.date_input('start date')
    e = st.date_input('end date')
    submit = st.button("Submit")
    if submit:
        cta_type_analysis(in1, in2, s,e)

def sla():
    q1 = """select "Member_name" from "Project"."Team" 
    where "Team_name" like %s; """
    #st.markdown("## **SLA Analysis**")
    in1 = st.selectbox("Select first Team",["Application-1","Application-2"], key='40')
    cursor.execute(q1,(in1,))
    d1=pd.DataFrame(cursor.fetchall(), columns=['Name'])
    in2 = st.selectbox("Team Member : ", d1['Name'], key='41')  
    #st.write("** Case Type Analysis **")
    s = st.date_input('start date')
    e = st.date_input('end date')
    submit = st.button("Submit")
    if submit:
        sla_analysis(in1, in2, s, e, s, e)
    
def on_hold():
    q1 = """select "Member_name" from "Project"."Team" 
    where "Team_name" like %s; """
    in2 = st.selectbox("Select first Team",["Application-1","Application-2"], key='50')
    add = {'Name':['Whole Team']}
    add = pd.DataFrame(add)
    q2 = """select "Member_name" from "Project"."Team" 
    where "Team_name" like %s; """
    cursor.execute(q2,(in2,))
    u = pd.DataFrame(cursor.fetchall(), columns = {'Name'})
    u = pd.concat([u, add], ignore_index = True)
    in1 = st.selectbox("Team Member : ", u['Name'])
    submit = st.button("Submit")
    if submit:
        if in1 == "Whole Team":
            q = """select "Ticket_number", to_char("Creation_timestamp",'yyyy-mm-dd'),"Owner_name","Title", "Type","Sub-type","Priority","Last_comment_updated",
            "Environment","Investigation_summary" 
            from "Project"."Ticket" 
            where "Ticket_status" like 'On Hold'
            and "Application" like %s;"""
            cursor.execute(q,(str(in2),))
        
        else:
            q = """select "Ticket_number", to_char("Creation_timestamp",'yyyy-mm-dd'),"Owner_name","Title", "Type","Sub-type","Priority","Last_comment_updated",
            "Environment","Investigation_summary" 
            from "Project"."Ticket" 
            where "Ticket_status" like 'On Hold'
            and "Owner_name" like %s
            and "Application" like %s;"""
            cursor.execute(q,(str(in1),str(in2)))
        
        
        df = pd.DataFrame(cursor.fetchall())
        df.columns = ['Ticket','Creation_Timestamp','Owner','Subject','Type','Sub-type','Priority','Last Comment Added','Environment','Investigation']
        st.dataframe(data=df)
        #AgGrid(df, height=500, fit_columns_on_grid_load=True)
        #df.Creation_timestamp = pd.DateTime(df['Creation_timestamp']).dt.date
        chart = alt.Chart(df).mark_circle(size=60).encode(
            x='Creation_Timestamp',
            y='Priority',
            color='Type',
            tooltip=['Ticket','Owner','Subject','Type','Sub-type','Priority','Last Comment Added','Environment','Investigation']
        ).interactive().properties(
                width=500,
                height=300
            )
    
        st.altair_chart(chart)

def outage_analysis():
    qu1 = """select "Member_name" from "Project"."Team" 
    where "Team_name" like %s; """
    in2 = st.selectbox("Select first Team",["Application-1","Application-2"], key='50')
    add = {'Name':['Whole Team']}
    add = pd.DataFrame(add)
    qu2 = """select "Member_name" from "Project"."Team" 
    where "Team_name" like %s; """
    cursor.execute(qu2,(in2,))
    u = pd.DataFrame(cursor.fetchall(), columns = {'Name'})
    u = pd.concat([u, add], ignore_index = True)
    in1 = st.selectbox("Team Member : ", u['Name'])
    print("Outage Analysis")
    q = """select "Ticket_number","Owner_name","Title","Type","Sub-type","Ticket_status","Priority",
    to_char("Creation_timestamp",'yyyy-mm-dd'),"Due_date","Closed_timestamp","Last_comment_updated",
    "Application","Environment","Hours_worked","Closed_reason","Complaint","Age",
    "Outage_start","Outage_end","Outage_severity","Investigation_summary"  
    from "Project"."Ticket" 
    where "Type" like 'Outage'
    and "Owner_name" like %s;"""
    q2 = """select "Ticket_number","Owner_name","Title","Type","Sub-type","Ticket_status","Priority",
    to_char("Creation_timestamp",'yyyy-mm-dd'),"Due_date","Closed_timestamp","Last_comment_updated",
    "Application","Environment","Hours_worked","Closed_reason","Complaint","Age",
    "Outage_start","Outage_end","Outage_severity","Investigation_summary"  
    from "Project"."Ticket" 
    where "Type" like 'Outage'
    and "Application" like %s;"""
    q1 = """select "Ticket_number","Owner_name","Title","Type","Sub-type","Ticket_status","Priority",
    to_char("Creation_timestamp",'yyyy-mm-dd'),"Due_date","Closed_timestamp","Last_comment_updated",
    "Application","Environment","Hours_worked","Closed_reason","Complaint","Age",
    "Outage_start","Outage_end","Outage_severity","Investigation_summary"  
    from "Project"."Ticket"
    where "Type" like 'Code'
    and "Sub-type" like 'Code Fix';"""
    submit = st.button("Submit")
    if submit:
        if in1=="Whole Team":
             cursor.execute(q2,(in2,))
             df = pd.DataFrame(cursor.fetchall())
        else:
            cursor.execute(q,(in1,))
            df = pd.DataFrame(cursor.fetchall())
        if df.empty== False:
            df.columns = ['Ticket','Owner','Subject','Type','Sub-type','Status','Priority','Creation_time',
                          'Due_date','Closed_time','Last_comment_added','Application','Environment','Hours_worked',
                          'Closed_reason','Complaint','Age','Outage_start','Outage_end','Outage_severity',
                          'Investigation-summary']
            df['Creation_time'] = pd.to_datetime(df.Creation_time)
            #print(df.dtypes)
            
            cursor.execute(q1)
            df1 = pd.DataFrame(cursor.fetchall())
            df1.columns = ['Ticket','Owner','Subject','Type','Sub-type','Status','Priority','Creation_time',
                          'Due_date','Closed_time','Last_comment_added','Application','Environment','Hours_worked',
                          'Closed_reason','Complaint','Age','Outage_start','Outage_end','Outage_severity',
                          'Investigation-summary']
            
            df1['Creation_time'] = pd.to_datetime(df1.Creation_time)
            temp_df = df1.loc[(df1['Type']=='Code') & (df1['Sub-type']=='Code Fix'), ['Ticket','Owner','Creation_time']]
            df['T'] = ""
            df_test = df
            for x in df['Creation_time']:
                x = x-timedelta(days = 7)
                #print(x)
                df.loc[len(df.index)-1, 'range']  = x
            df_dup = pd.DataFrame()
            for x in df['Ticket']:
                    s = (df['range'].loc[df['Ticket']== x])
                    e = (df['Creation_time'].loc[df['Ticket']== x])
                    mask = (df1['Creation_time'] >np.datetime64(s[0])) & (df1['Creation_time'] <= np.datetime64(e[0]))
                    df2=df1.loc[mask]
                    df2['Link'] = x
            st.write("Outage Tickets are: ")      
            st.write(df)
            st.write("The possible tickets that might have caused this outage: ")
            st.write(df2)
            chart = alt.Chart(df, title = "Outage Tickets").mark_point(point={
              "filled": False,
              "fill": "white"
            },size=60).encode(
                    x='Creation_time',
                    y='Owner',
                    color='Environment',
                    tooltip=['Ticket','Owner','Subject','Type','Sub-type','Outage_severity','Last_comment_added','Environment','Investigation-summary','Outage_start','Outage_end']
                ).interactive().properties(
                        width=500,
                        height=300
                    )
            chart1 = alt.Chart(df2, title = "Outage Tickets").mark_point(point={
              "filled": False,
              "fill": "white"
            },size=60).encode(
                    x='Creation_time',
                    y='Owner',
                    color='Environment',
                    tooltip=['Ticket','Owner','Subject','Type','Sub-type','Last_comment_added','Environment','Investigation-summary','Closed_time']
                ).interactive().properties(
                        width=500,
                        height=300
                    )
            st.altair_chart(chart | chart1)
        else:
            st.write("No Outage Tickets Found under the selected user queue")
    
def idle_hours():
    qu1 = """select "Member_name" from "Project"."Team" 
    where "Team_name" like %s; """
    in2 = st.selectbox("Select first Team",["Application-1","Application-2"], key='50')
    add = {'Name':['Whole Team']}
    add = pd.DataFrame(add)
    qu2 = """select "Member_name" from "Project"."Team" 
    where "Team_name" like %s; """
    cursor.execute(qu2,(in2,))
    u = pd.DataFrame(cursor.fetchall(), columns = {'Name'})
    u = pd.concat([u, add], ignore_index = True)
    in1 = st.selectbox("Team Member : ", u['Name'])
    q="""select round(avg(foo1."Age_in_current_queue")*24,3), round(avg(foo1."Hours_worked"),3), to_char(foo2."Creation_timestamp",'yyyy-mm-dd'),
    foo1."Owner_name", foo1."Ticket_Status"
    from "Project"."All_Ticket" foo1
    join "Project"."Ticket" foo2 on foo1."Ticket_number" = foo2."Ticket_number"
    where foo2."Owner_name" like %s
    and foo1."Ticket_Status" in ('Evaluate','In Progress')
    group by foo1."Ticket_Status", foo1."Owner_name", to_char(foo2."Creation_timestamp",'yyyy-mm-dd')
    order by to_char(foo2."Creation_timestamp",'yyyy-mm-dd'),foo1."Ticket_Status";"""
    q1="""select round(avg(foo1."Age_in_current_queue")*24,3), round(avg(foo1."Hours_worked"),3), to_char(foo2."Creation_timestamp",'yyyy-mm-dd'),
    foo1."Owner_name", foo1."Ticket_Status"
    from "Project"."All_Ticket" foo1
    join "Project"."Ticket" foo2 on foo1."Ticket_number" = foo2."Ticket_number"
    where foo2."Application" like %s
    and foo1."Ticket_Status" in ('Evaluate','In Progress')
    group by foo1."Ticket_Status", foo1."Owner_name", to_char(foo2."Creation_timestamp",'yyyy-mm-dd')
    order by to_char(foo2."Creation_timestamp",'yyyy-mm-dd'),foo1."Ticket_Status";
    """
    df = pd.DataFrame()
    if in1 == "Whole Team":
        cursor.execute(q1,(in2,))
        df = pd.DataFrame(cursor.fetchall())
    else:
        cursor.execute(q,(in1,))
        df = pd.DataFrame(cursor.fetchall())
    submit = st.button("Submit")
    if submit:
        if df.empty == False:
            df.columns = ['Age','Hours','Created_time','Owner','Status']    
            df['Age'] = df['Age'].astype(float)
            df['Hours'] = df['Hours'].astype(float)
            selection = alt.selection_multi(fields=['Type'], bind='legend')
        
            chart1 = alt.Chart(df, title = "Avg of Ticket Old Days: "+in1).mark_line(point={
              "filled": False,
              "fill": "white"
            }).encode(
                x='Created_time',
                y=alt.Y('Age'),
                #tooltip = 'Ticket',
                color=alt.Color('Status'),
                tooltip = ['Age','Hours','Status','Created_time']
            ).interactive().properties(
                    width=500,
                    height=500
                )
            chart2 = alt.Chart(df, title = "Avg of Working hours: "+in1).mark_line(point={
              "filled": False,
              "fill": "white"
            }).encode(
                x='Created_time',
                y=alt.Y('Hours', scale=alt.Scale(domain=[0, 5])),
                #tooltip = 'Ticket',
                color=alt.Color('Status'),
                tooltip = ['Age','Hours','Status','Created_time']
            ).interactive().properties(
                    width=500,
                    height=500
                )
        
            st.altair_chart(chart1 | chart2)

def application():
    
    st.sidebar.title('Lets analyze')
    in1 = st.sidebar.selectbox("What do you want to analyze ", ["Compare Achievements", "Self Achievement compare", "Repeated Tickets Analysis", "Case Type Analysis","SLA Breach Analysis","On Hold Analysis","Outage Analysis", "Idle Analysis"])
    st.success(in1)
    if in1 == 'Compare Achievements':
        st.title("**Compare Achivements**")
        cmp_ach()
    if in1 == 'Self Achievement compare':
        st.title("**Comparing Self Achievements**")
        self_cmp()
    if in1 == 'Repeated Tickets Analysis':
        st.title("**Repeated Tickets Analysis**")
        rep_cases()
    if in1 == 'Case Type Analysis':
        st.title("**Case Type Analysis**")
        cta()
    if in1 == 'SLA Breach Analysis':
        st.title("**SLA Analysis**")
        sla()
    if in1 == 'On Hold Analysis':
        st.title("**On Hold Analysis**")
        on_hold()
    if in1 == 'Outage Analysis':
        st.title("**Outage Analysis**")
        outage_analysis()
    if in1 == 'Idle Analysis':
        st.title("**Idle Analysis**")
        idle_hours()

if __name__ == '__main__':
    application()
    