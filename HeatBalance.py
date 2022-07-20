#Lines 2-18 import the necessary LIBRARIES.
import json
import math
import requests
import numpy as np
import array as arr
import pandas as pd
import seaborn as sns
import scipy.constants
import streamlit as st
from scipy import linalg
from st_aggrid import AgGrid          #Library used for creating interactive tables.
import matplotlib.pyplot as plt
from pandas import DataFrame, Series 
from streamlit_lottie import st_lottie
from annotated_text import annotated_text
from streamlit_option_menu import option_menu
import base64
#The base64 libarary helps with the data download for the csv file because it is going to encode the ASCII to byte conversion.

#Declaring the required GLOBAL CONSTANT(s). Line 22.
REFERENCE_TEMPERATURE_NTP = 20 
                                                            

#Lines 26-32 hide the HAMBURGER MENU and the "MADE WITH STREAMLIT FOOTER" footer.
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""" 
st.markdown(hide_streamlit_style, unsafe_allow_html=True)  


#FUNCTION for LOTTIE GIF's to be used in the web application. Lines 36-41.
@st.cache(allow_output_mutation=True)
def load_lottieurl(url:str):
    r = requests.get(url)
    if r.status_code != 200:
       return None
    return r.json()

#FUNCTION used for generating DOWNLOAD LINKS. Lines 44-51.
def df_to_link(df, title='Download csv', filename='download.csv'):
    """Generates a link allowing the data in a given pandas dataframe to be downloaded.
    input:  dataframe
    output: href string
    """
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
    return f'<a href="data:file/csv;base64,{b64}" download="{filename}">{title}</a>'




#CLASS containing all the function definitions required for calculating Kiln Surface Radiation. Lines 57-93.
class Kiln():
    def __init__(self, diameter, ambient_velocity, ambient_temp, temp_unit, emissivity, interval, df):
        self.diameter = diameter # meter
        self.ambient_velocity = ambient_velocity # m/s
        self.ambient_temp = ambient_air_temperature + 273
        self.emissivity = emissivity
        self.interval = interval # meter
        self.section_area = math.pi * diameter * interval
        columns_count = len(df.columns)
        rows_count = len(df.index)
        self.length = interval * rows_count

        #To AUTO-GENERATE names for the columns in input excel (dfKilnRadTemps in this case).
        df.columns = [f'Input {i}' for i in range(1, columns_count+1)]
        
        #Compute average of temperatures in input columns.
        average = df[list(df.columns)].sum(axis=1)/columns_count
        df['Temp'] = average if temp_unit=='Kelvin' else average + 273

        #AUTO-GENERATE lengths at which readings were taken based on the interval and the number of readings.
        length = [i for i in range(interval, self.length+1, interval)]
        df.insert(0, 'Length', length)

        self.df = df # Pandas DF with temp readings in Kelvin.

    def radiation(self, tempcol='Temp'):
        """Calculate radiation heat loss (kcal/hr) from each section of kiln"""
        return self.emissivity * self.section_area * scipy.constants.Stefan_Boltzmann * (self.df[tempcol]**4 - self.ambient_temp**4)

    def convection(self, tempcol='Temp'):
        """ Calculate convection heat loss (kcal/hr) from each section of kiln """
        if self.ambient_velocity < 3:
            #Natural Convection.
            return 80.33 * (((self.df[tempcol] + self.ambient_temp)/2)**-0.724 * (self.df[tempcol] - self.ambient_temp)**1.333) * self.section_area
        else:
            #Forced Convection.
            return 28.03 * (self.df[tempcol] * self.ambient_temp)**-0.351 * self.ambient_velocity**0.805 * self.diameter**-0.195 * (self.df[tempcol] - self.ambient_temp) * self.section_area
    
    

    
#SIDEBAR. Lines 99-122.
with st.sidebar:
    url1 = "https://assets8.lottiefiles.com/private_files/lf30_nhg4au0e.json"
    res1_json = load_lottieurl(url1)
    st_lottie(res1_json)
    options = option_menu(
        menu_title = "Navigation",
        options = ["Introduction", "User Notes", "Average Values", "Split DataFrames", "Fan Flows", "Cooler Fans", "Blowers/PA Fans", "Cooler Heat Balance", "Kiln Radiation", "Kiln Heat Balance", "Dashboard Reset"],
        icons = ["info-circle-fill", "journal-check", "calculator-fill", "bar-chart-fill", "fan", "wind", "layout-three-columns", "cloud-snow", "radioactive", "bricks", "yin-yang"],
        menu_icon = "cast",
        default_index = 0)
        #orientation = "horizontal")                                      #Bootstrap icons used for navigation bar.                 
st.sidebar.write("***")
st.sidebar.title('Excel Uploads')
input_excel = st.sidebar.file_uploader('Upload the Dynamic Pressures and Velocities Sheet.', type=['xls','xlsx','xlsm','xlsb','odf'])
input_excel_kilnsurftemps = st.sidebar.file_uploader('Upload the Kiln Surface Temperatures.', type=['xls', 'xlsx', 'xlsm', 'xlsb', 'odf'])
with st.sidebar:
     url2 = "https://assets9.lottiefiles.com/packages/lf20_jkdsmf9r.json"
     res2_json = load_lottieurl(url2)
     st_lottie(res2_json) 
st.sidebar.write("***")
st.sidebar.title('Video')
st.sidebar.info("For a demo of the Web Application, you may refer to the following video:") 
st.sidebar.markdown("[Web Application Demo](https://drive.google.com/file/d/1KaUQNLd_f8AdbMpj0oOvebPf1QEiXgzo/view?usp=sharing)")
st.sidebar.write("***")    




#Code for the "INTRODUCTION" section. Lines 128-151.     
if(options == 'Introduction'):
    st.title("PYRO HEAT BALANCE WEB APP")
    annotated_text(
    ("Well", ",", "#8cff66"),
    ("Hello there", "!", "#8cff66"),    #8ef: Blue,     #faa: Red,     #afa: Green
    )    
    st.markdown("""
This tool will help you with Pyro Heat Balance. Don't scroll down yet...
""")
#To display the "COOLER" animation via LOTTIE Library.        
    url3 = "https://assets3.lottiefiles.com/packages/lf20_vhnlnxlf.json"
    res3_json = load_lottieurl(url3)
    st_lottie(res3_json)
    annotated_text(
    "Umm, you did anyways...Click on the ",
    (" 'User Notes' ", "", "#faa"),
    "checkbox under", 
    (" 'Navigation' ", "", "#faa"),
    "to see how to use this app and what features are available."    
    )
#To display the "LEFT ARROW" animation via LOTTIE Library.    
    url4 = "https://assets5.lottiefiles.com/packages/lf20_0krOal.json"
    res4_json = load_lottieurl(url4)
    st_lottie(res4_json)

  


#Code for the "USER NOTES" section. Lines 157-224.
elif(options == 'User Notes'):
    st.title("NOTES")
   
    url5 = "https://assets2.lottiefiles.com/packages/lf20_kzfwp1ef.json" #Code to display the NOTES GIF from Lottie Library.
    res5_json = load_lottieurl(url5)
    st_lottie(res5_json)
   
    st.write("""
Let's walk you through the web application!
1. The first thing you need to get familiar with is the **'NAVIGATION'** section in the sidebar to your left. You have already seen the **'INTRODUCTION'** of the web app and right now you are in the **'USER NOTES'** section. By clicking on the respective checkboxes the relevant results will be displayed. For eg: the next option is that of **'AVERAGE VALUES'**. Here you can download the excel sheet with the average values (columnwise) of your data. 
2. Now, of course you might be wondering where to upload your file. Go to the **'EXCEL UPLOADS'** section in the sidebar. There you can see two boxes. One is for the **'Dynamic Pressures and Velocities Sheet'** and the other for the **'Kiln Surface Temperatures'**. Click on respective **'BROWSE FILES'** button and upload your excel. You are now all set to go (or maybe not...),
3. In the excel file that you are going to upload (for the 'Dynamic Pressures and Velocities'), make sure that the data is in the order as given below (columnwise).
**Dynamic Pressure** Values of:
* Preheater Downcomer Ducts
* Tertiary Air Ducts
* Cooler Mid Air Ducts
* Cooler Vent Air Ducts
* ESP Stack Duct
then the **Velocities** of:
* Cooler Fans 
and finally the **Dynamic Pressure** Values of,
* Kiln Blowers
* Calciner Blowers
* PA Fans
""")
    st.write("If you have any doubt, you may click on the **'EXCEL FILE EXAMPLE'** link to see how your input excel should look like.")
    st.markdown("[EXCEL FILE EXAMPLE](https://drive.google.com/file/d/1CNGLBLcFnylBkYjmMGMORRFZBh01sH5i/view?usp=sharing)")  #Pic showing a sample "INPUT EXCEL SHEET".
    st.write("If you want, then you can fill in the information in the **'GENERAL INFORMATION ABOUT YOUR DATA'** section. A template excel will be automatically generated. You can fill up the generated excel sheet and upload it here for further use.")
    st.write("""
4. Whereas, for the other excel file (containing the 'Kiln Surface Temperatures') you are going to upload, keep in mind the following details:
* The first meter starts from the kiln outlet side.
* "Interval" is the distance between consecutive temperature readings. For example, when surface temperature was measured every 3 meters, the interval would be 3.
* Multiple temperature readings can be provided at each point by putting them in separate excel columns. In such a case, the **average** of the readings will be automatically computed.
* Fill the columns in the Input Excel starting from column A and use columns B,C,D,... as required. Columns should contain only the temperature readings in numbers and nothing else, not even column headers!
""")
    st.write("***")
    st.write("""
5. The reference temperature (NTP) considered for the calculations is **20 degree celsius**.
6. You can always use the **'DASHBOARD RESET'** button to unclutter the dashboard and work only with the input columns. It will not reset your data to the default values in the input columns though. Go ahead... give it a shot! If you want to come back here, then you know what to do. A few more tips and you are good to go.
7. Next, what are the input columns? Scroll down below where you can see the **'GENERAL INFORMATION ABOUT YOUR DATA'** section. Before you download any of the excel sheets or view any of the dataframes, make sure to fill in the right information. Below that you will be able to see the **'FAN FLOWS'**, **'COOLER FANS'**, **'COOLER HB'**, **'BLOWERS/PA FANS'** and **'KILN HB'** columns. You can enter data in these expanders by clicking on them.
Finally if you want to see the Python Libraries used for creating this web app, then select 'YES' below (in the dropdown). 
""")
    
    
    libraries = st.selectbox(
             'Would you like to see the Python Libraries used to make this app?',
              ('No', 'Yes'))
    if (libraries == 'Yes'):
          st.write("1. streamlit")
          st.write("2. base64")
          st.write("3. json")
          st.write("4. requests")
          st.write("5. numpy")  
          st.write("6. array")
          st.write("7. pandas") 
          st.write("8. math")
          st.write("9. scipy")  
          st.write("10. streamlit-aggrid")
          st.write("11. streamlit-lottie")
          st.write("12. annotated_text")
          st.write("13. streamlit-option-menu") 
          st.write("14. matplotlib")  
        
    st.write("You are all set to use this app now. If you have any doubt regarding the functionalities of the web application, then you may watch the demo. The link for it has been provided at the bottom of the sidebar.") 
    st.write("Now go ahead and upload your excel files!!!")
    url6 = "https://assets2.lottiefiles.com/packages/lf20_4m0f2coq.json"  #"BLUE LINE" animation from Lottie. To separate the 2 sections.
    res6_json = load_lottieurl(url6)
    st_lottie(res6_json)
    
    


#EXPANDER to input the GENERAL INFORMATION required for further computation. Lines 230-257.  
st.header("GENERAL INFORMATION ABOUT YOUR DATA")
with st.expander("GENERAL INFO"):
     number_of_preheater_downcomer_ducts = st.number_input('How many Preheater Downcomer Ducts are to be considered?', 1, 3, 3, 1)
     number_of_tertiaryair_ducts = st.number_input('How many Tertiary Air Ducts are to be considered?', 0, 2, 2, 1)
     number_of_coolermidair = st.number_input('How many Cooler Mid Air Ducts are to be considered?', 0, 2, 2, 1)
     number_of_cooler_ventair_ducts = st.number_input('How many Cooler Vent Air Ducts are to be considered?', 0, 1, 1, 1)
     st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html = True)
     backcalcordirectorindirect = st.radio(
                     "How do you want to calculate the CVA flow?",
                      ('Direct', 'Back Calculate', 'Indirect (ESP Stack Flow - MidAir Flow)'))
     number_of_cooler_fans = st.number_input('How many Cooler Fans are to be considered?', 0, 15, 7, 1)
     number_of_kiln_blowers = st.number_input('How many Kiln Blowers are to be considered?', 1, 2, 1, 1)
     number_of_calciner_blowers = st.number_input('How many Calciner Blowers are to be considered?', 0, 2, 1, 1)
     number_of_PA_fans = st.number_input('How many PA Fans are to be considered?', 1, 2, 1, 1)
     mean_sea_level = st.number_input('Mean Sea Level (in Meters):', 0.000, 1000.000, 432.000, 10.000, format = "%.3f")
     datum_pressure = 10336*(math.e)**(-0.0001255*mean_sea_level) 
     st.write('The datum pressure is:') 
     st.write(datum_pressure)
     ambient_air_temperature = st.number_input('Ambient Air Temperature (in Celsius):', 0.00, 2000.00, 30.00, 10.00) 
     cooler_air_density = st.number_input('Enter the Cooler Air Density:', 0.000, 5.000, 1.293, 0.001, format="%.3f")
     kilnfeed_factor = st.number_input('Enter the Kiln Feed Factor:', 0.000, 5.000, 1.615, 0.001, format="%.3f")
     kilnfeed = st.number_input('Enter the Kiln Feed (tph):', 0.00, 2000.00, 689.00, 10.00)
     clinker_capacity = kilnfeed/kilnfeed_factor
     st.write("The Clinker Capacity is (tph):")
     st.write(clinker_capacity)
     st.write("The Clinker Capacity is (tpd):")
     st.write(clinker_capacity*24)
     st.write("***")    



#Code for the template excel that will be generated via link. Lines 262-295.       
dftemplatePH = pd.DataFrame(columns = range(1, int(number_of_preheater_downcomer_ducts)+1))
dftemplatePH.columns = ['PH' + str(i+1) for i in range (int(number_of_preheater_downcomer_ducts))]

dftemplateTAD = pd.DataFrame(columns = range(1, int(number_of_tertiaryair_ducts)+1))
dftemplateTAD.columns = ['TAD' + str(i+1) for i in range (int(number_of_tertiaryair_ducts))]

dftemplateCMA = pd.DataFrame(columns = range(1, int(number_of_coolermidair)+1))
dftemplateCMA.columns = ['CMA' + str(i+1) for i in range (int(number_of_coolermidair))]

if ( (number_of_cooler_ventair_ducts > 0 and backcalcordirectorindirect == 'Direct') ):
  dftemplateCVA = pd.DataFrame(columns = range(1, int(number_of_cooler_ventair_ducts)+1))
  dftemplateCVA.columns = ['CVA' + str(i+1) for i in range (int(number_of_cooler_ventair_ducts))]
elif ( (number_of_cooler_ventair_ducts > 0 and backcalcordirectorindirect == 'Back Calculate') or (number_of_cooler_ventair_ducts == 0) or (number_of_cooler_ventair_ducts > 0 and backcalcordirectorindirect == 'Indirect (ESP Stack Flow - MidAir Flow)') ):
  dftemplateCVA = pd.DataFrame(columns = range(1,1))
    
dftemplateESP = pd.DataFrame(columns = range(1, 2))
dftemplateESP.columns = ['ESP Stack']

dftemplateCF = pd.DataFrame(columns = range(1, int(number_of_cooler_fans)+1))
dftemplateCF.columns = ['Cooler Fan' + str(i+1) for i in range (int(number_of_cooler_fans))]

dftemplateKB = pd.DataFrame(columns = range(1, int(number_of_kiln_blowers)+1))
dftemplateKB.columns = ['Kiln Blower' + str(i+1) for i in range (int(number_of_kiln_blowers))]

dftemplateCB = pd.DataFrame(columns = range(1, int(number_of_calciner_blowers)+1))
dftemplateCB.columns = ['Calciner Blower' + str(i+1) for i in range (int(number_of_calciner_blowers))]

dftemplatePA = pd.DataFrame(columns  = range(1, int(number_of_PA_fans)+1))
dftemplatePA.columns = ['PA Fan' + str(i+1) for i in range (int(number_of_PA_fans))]

dftemplate = pd.concat([dftemplatePH, dftemplateTAD, dftemplateCMA, dftemplateCVA, dftemplateESP, dftemplateCF, dftemplateKB, dftemplateCB, dftemplatePA]  , axis = 1)
download_link = df_to_link(dftemplate, title='Template for Dp Values and Velocities', filename='Template.csv')
st.markdown(download_link, unsafe_allow_html=True)
st.write("***") 



#Lines 300-303 take care of the first output of the program, that is the appended excel with average values (columnwise).
if input_excel is not None:
   dfinputexcel = pd.read_excel(input_excel)
   dfmeanexcel = dfinputexcel.mean(axis = 0) #dfmeanexcel variable stores the average values of the input excel columns in a dataframe.
   dfappendedoriginalandaverages = dfinputexcel.append(dfmeanexcel, ignore_index=True) #Original+Average Values Sheet (appended).



#Splitting the original dataframe for further usage. Did the splitting using .T feature for transpose and the iloc function for accessing specific rows. Lines 308-356.
   dfinputexceltranspose = dfinputexcel.T 

   #Variable holding the transposed data of preheater downcomer ducts columns.
   dfpreheater_downcomerducts_rowsintransposedframe = dfinputexceltranspose.iloc[0:int(number_of_preheater_downcomer_ducts)]
   dfpreheatercolumns = dfpreheater_downcomerducts_rowsintransposedframe.T

   df_tertiary_airducts_rowsintransposedframe = dfinputexceltranspose.iloc[int(number_of_preheater_downcomer_ducts):int(number_of_tertiaryair_ducts+number_of_preheater_downcomer_ducts)]
   dfTADcolumns = df_tertiary_airducts_rowsintransposedframe.T

   df_cooler_midairs_rowsintransposedframe = dfinputexceltranspose.iloc[int(number_of_preheater_downcomer_ducts+number_of_tertiaryair_ducts):int(number_of_tertiaryair_ducts+number_of_preheater_downcomer_ducts+number_of_coolermidair)]
   dfCMAcolumns = df_cooler_midairs_rowsintransposedframe.T
   
   if (backcalcordirectorindirect == 'Direct'):                                       
     df_cooler_ventair_rowsintransposedframe = dfinputexceltranspose.iloc[int(number_of_tertiaryair_ducts+number_of_preheater_downcomer_ducts+number_of_coolermidair):int(number_of_tertiaryair_ducts+number_of_preheater_downcomer_ducts+number_of_coolermidair+number_of_cooler_ventair_ducts)]
     dfCVAcolumns = df_cooler_ventair_rowsintransposedframe.T
     
     df_cooler_ESPstack_rowsintransposedframe = dfinputexceltranspose.iloc[int(number_of_tertiaryair_ducts+number_of_preheater_downcomer_ducts+number_of_coolermidair+number_of_cooler_ventair_ducts):int(number_of_tertiaryair_ducts+number_of_preheater_downcomer_ducts+number_of_coolermidair+number_of_cooler_ventair_ducts+1)]
     dfESPcolumns = df_cooler_ESPstack_rowsintransposedframe.T   
        
     df_cooler_coolerfans_rowsintransposedframe = dfinputexceltranspose.iloc[int(number_of_tertiaryair_ducts+number_of_preheater_downcomer_ducts+number_of_coolermidair+number_of_cooler_ventair_ducts+1):int(number_of_tertiaryair_ducts+number_of_preheater_downcomer_ducts+number_of_coolermidair+number_of_cooler_ventair_ducts+number_of_cooler_fans+1)]
     dfcoolerfancolumns = df_cooler_coolerfans_rowsintransposedframe.T   
        
     df_cooler_kilnblowersintransposedframe = dfinputexceltranspose.iloc[int(number_of_tertiaryair_ducts+number_of_preheater_downcomer_ducts+number_of_coolermidair+number_of_cooler_ventair_ducts+number_of_cooler_fans+1):int(number_of_tertiaryair_ducts+number_of_preheater_downcomer_ducts+number_of_coolermidair+number_of_cooler_ventair_ducts+number_of_cooler_fans+1+number_of_kiln_blowers)]
     dfkilnblowerscolumns = df_cooler_kilnblowersintransposedframe.T 
        
     df_cooler_calcinerblowersintransposedframe = dfinputexceltranspose.iloc[int(number_of_tertiaryair_ducts+number_of_preheater_downcomer_ducts+number_of_coolermidair+number_of_cooler_ventair_ducts+number_of_cooler_fans+1+number_of_kiln_blowers):int(number_of_tertiaryair_ducts+number_of_preheater_downcomer_ducts+number_of_coolermidair+number_of_cooler_ventair_ducts+number_of_cooler_fans+1+number_of_kiln_blowers+number_of_calciner_blowers)]
     dfcalcinerblowerscolumns = df_cooler_calcinerblowersintransposedframe.T  
        
     df_cooler_PAfansintransposedframe = dfinputexceltranspose.iloc[int(number_of_tertiaryair_ducts+number_of_preheater_downcomer_ducts+number_of_coolermidair+number_of_cooler_ventair_ducts+number_of_cooler_fans+1+number_of_kiln_blowers+number_of_calciner_blowers):int(number_of_tertiaryair_ducts+number_of_preheater_downcomer_ducts+number_of_coolermidair+number_of_cooler_ventair_ducts+number_of_cooler_fans+1+number_of_kiln_blowers+number_of_calciner_blowers+number_of_PA_fans)]   
     dfPAfanscolumns = df_cooler_PAfansintransposedframe.T 
        
   elif (backcalcordirectorindirect == 'Back Calculate' or backcalcordirectorindirect == 'Indirect (ESP Stack Flow - MidAir Flow)'):
       df_cooler_ventair_rowsintransposedframe = dfinputexceltranspose.iloc[int(number_of_tertiaryair_ducts+number_of_preheater_downcomer_ducts+number_of_coolermidair):int(number_of_tertiaryair_ducts+number_of_preheater_downcomer_ducts+number_of_coolermidair)]
       dfCVAcolumns = df_cooler_ventair_rowsintransposedframe.T 
    
       df_cooler_ESPstack_rowsintransposedframe = dfinputexceltranspose.iloc[int(number_of_tertiaryair_ducts+number_of_preheater_downcomer_ducts+number_of_coolermidair):int(number_of_tertiaryair_ducts+number_of_preheater_downcomer_ducts+number_of_coolermidair+1)]
       dfESPcolumns = df_cooler_ESPstack_rowsintransposedframe.T

       df_cooler_coolerfans_rowsintransposedframe = dfinputexceltranspose.iloc[int(number_of_tertiaryair_ducts+number_of_preheater_downcomer_ducts+number_of_coolermidair+1):int(number_of_tertiaryair_ducts+number_of_preheater_downcomer_ducts+number_of_coolermidair+1+number_of_cooler_fans)]
       dfcoolerfancolumns = df_cooler_coolerfans_rowsintransposedframe.T
    
       df_cooler_kilnblowersintransposedframe = dfinputexceltranspose.iloc[int(number_of_tertiaryair_ducts+number_of_preheater_downcomer_ducts+number_of_coolermidair+number_of_cooler_fans+1):int(number_of_tertiaryair_ducts+number_of_preheater_downcomer_ducts+number_of_coolermidair+number_of_cooler_fans+1+number_of_kiln_blowers)]
       dfkilnblowerscolumns = df_cooler_kilnblowersintransposedframe.T
    
       df_cooler_calcinerblowersintransposedframe = dfinputexceltranspose.iloc[int(number_of_tertiaryair_ducts+number_of_preheater_downcomer_ducts+number_of_coolermidair+number_of_cooler_fans+1+number_of_kiln_blowers):int(number_of_tertiaryair_ducts+number_of_preheater_downcomer_ducts+number_of_coolermidair+number_of_cooler_fans+1+number_of_kiln_blowers+number_of_calciner_blowers)]
       dfcalcinerblowerscolumns = df_cooler_calcinerblowersintransposedframe.T
    
       df_cooler_PAfansintransposedframe = dfinputexceltranspose.iloc[int(number_of_tertiaryair_ducts+number_of_preheater_downcomer_ducts+number_of_coolermidair+number_of_cooler_fans+1+number_of_kiln_blowers+number_of_calciner_blowers):int(number_of_tertiaryair_ducts+number_of_preheater_downcomer_ducts+number_of_coolermidair+number_of_cooler_fans+1+number_of_kiln_blowers+number_of_calciner_blowers+number_of_PA_fans)]   
       dfPAfanscolumns = df_cooler_PAfansintransposedframe.T

  
  

#Code for the COLUMNS OF THE DASHBOARD (excluding the CONTAINER). Lines 362-984.    
col1, col2, col3 = st.columns(3)  


#Code for COLUMN 1, taking care of the FAN FLOWS. Lines 366-746 as of now.
with col1:
    st.header("FAN FLOWS")
    CountColumn1Expander1PH = 1
    CountColumn1Expander1TAD = 1
    CountColumn1Expander1CoolerMidair = 1
    np.arraypreheaterdowncomerductstemperatures = []      #Array to store the temperatures of preheater downcomer ducts. 
    np.arrayTADtemperatures = []                          #Array to store the temperatures of TAD's. (Tertiary Air Ducts).
    np.arrayCoolerMidAirtemperatures = []                 #Array to store the temperatures of Cooler Mid Air Ducts.
    
    CountColumn1Expander2PH = 1
    CountColumn1Expander2TAD = 1
    CountColumn1Expander2CoolerMidair = 1
    np.arraypreheaterdowncomerductsdiameters = []          #Array to store the diameters of preheater downcomer ducts. 
    np.arrayTADdiameters = []                              #Array to store the diameters of TAD's. (Tertiary Air Ducts).
    np.arrayCoolerMidAirdiameters = []                     #Array to store the diameters of Cooler Mid Air Ducts.
                                                           #CMA: Cooler Mid Air, TAD: Tertiary Air Duct.
    CountColumn1Expander3PH = 1
    CountColumn1Expander3TAD = 1
    CountColumn1Expander3CoolerMidair = 1
    np.arraypreheaterdowncomerductsstaticpressures = []     #Array to store the static pressures of preheater downcomer ducts. 
    np.arrayTADstaticpressures = []                         #Array to store the static pressures of TAD's. (Tertiary Air Ducts).
    np.arrayCoolerMidAirstaticpressures = []                #Array to store the static pressures of Cooler Mid Air Ducts.
    
    CountColumn1Expander4PH = 1
    np.arraypreheaterdowncomerductsO2 = []
    np.arraypreheaterdowncomerductsCO2 = []
    np.arraypreheaterdowncomerductsCO = []
    np.arraypreheaterdowncomerductsH2O = []
    
    np.arraydensitiesPH = []
    
    CountColumn1Expander5PH = 1
    CountColumn1Expander5TAD = 1
    CountColumn1Expander5CoolerMidair = 1
    np.arraypreheaterdowncomerductspitotconstants = []     #Array to store the pitot constants of preheater downcomer ducts. 
    np.arrayTADpitotconstants = []                         #Array to store the pitot constants of TAD's. (Tertiary Air Ducts).
    np.arrayCoolerMidAirpitotconstants = []                #Array to store the pitot constants of Cooler Mid Air Ducts.
    
    CountColumn1Expander6PH = 1
    np.arraypreheaterdowncomerductspower = []
    
    CountColumn1Expander7PH = 1
    np.arraypreheaterdowncomerductsfanoutletpressure = []
    
    
    with st.expander("TEMPERATURES"):                                          #EXPANDER 1 for TEMPERATURES.
         st.write("Enter the temperatures in **celsius**:") 
         cooler_ESPstack_temperature = st.number_input("Temperature of the Cooler ESP Stack:", 0.00, 1000.00, 151.00, 1.00)   
         while (CountColumn1Expander1PH <= number_of_preheater_downcomer_ducts):
                temperaturePH = st.number_input('Temperature of Preheater Downcomer Duct %d:' %CountColumn1Expander1PH, 0.00, 1000.00, 264.00, 1.00, key = CountColumn1Expander1PH)
                np.arraypreheaterdowncomerductstemperatures.append(temperaturePH)
                CountColumn1Expander1PH += 1
         while ( (CountColumn1Expander1TAD <= number_of_tertiaryair_ducts) and (number_of_tertiaryair_ducts > 0) ):
                temperatureTAD = st.number_input('Temperature of Tertiary Air Duct %d:' %CountColumn1Expander1TAD, 0.00, 1000.00, 912.00, 1.00, key = CountColumn1Expander1TAD)
                np.arrayTADtemperatures.append(temperatureTAD)
                CountColumn1Expander1TAD += 1 
         while ( (CountColumn1Expander1CoolerMidair <= number_of_coolermidair) and (number_of_coolermidair > 0) ):
                temperatureCMA = st.number_input('Temperature of Cooler Mid Air Duct %d:' %CountColumn1Expander1CoolerMidair, 0.00, 1000.00, 161.50, 1.00, key = CountColumn1Expander1CoolerMidair)
                np.arrayCoolerMidAirtemperatures.append(temperatureCMA)
                CountColumn1Expander1CoolerMidair += 1       
         if ( (backcalcordirectorindirect == 'Direct' and number_of_cooler_ventair_ducts > 0) or (backcalcordirectorindirect == 'Indirect (ESP Stack Flow - MidAir Flow)' and number_of_cooler_ventair_ducts > 0) ):
            tempCVAdirect = st.number_input("Temperature of Cooler Vent Air:", 0.00, 1000.00, 320.0, 1.00)
    
    
    
    with st.expander("DIAMETERS"):                                           #EXPANDER 2 for DIAMETERS.
         st.write("Enter the diameters in **meters (m)**:")
         cooler_ESPstack_diameter = st.number_input("Diameter of the Cooler ESP Stack:", 0.00, 100.00, 6.00, 1.0)
         while (CountColumn1Expander2PH <= number_of_preheater_downcomer_ducts):
                diameterPH = st.number_input('Diameter of Preheater Downcomer Duct %d:' %CountColumn1Expander2PH, 0.00, 20.00, 3.55, 0.10, key = CountColumn1Expander2PH)
                np.arraypreheaterdowncomerductsdiameters.append(diameterPH)
                CountColumn1Expander2PH += 1
         while ( (CountColumn1Expander2TAD <= number_of_tertiaryair_ducts) and (number_of_tertiaryair_ducts > 0) ):
                diameterTAD = st.number_input('Diameter of Tertiary Air Duct %d:' %CountColumn1Expander2TAD, 0.00, 20.00, 2.50, 0.10, key = CountColumn1Expander2TAD)
                np.arrayTADdiameters.append(diameterTAD)
                CountColumn1Expander2TAD += 1 
         while ( (CountColumn1Expander2CoolerMidair <= number_of_coolermidair) and (number_of_coolermidair > 0) ):
                diameterCMA = st.number_input('Diameter of Cooler Mid Air Duct %d:' %CountColumn1Expander2CoolerMidair, 0.00, 20.00, 3.20, 0.10, key = CountColumn1Expander2CoolerMidair)
                np.arrayCoolerMidAirdiameters.append(diameterCMA)
                CountColumn1Expander2CoolerMidair += 1
         if ( (backcalcordirectorindirect == 'Direct' and number_of_cooler_ventair_ducts > 0) or (backcalcordirectorindirect == 'Indirect (ESP Stack Flow - MidAir Flow)' and number_of_cooler_ventair_ducts > 0) ):
            diamCVAdirect = st.number_input("Diameter of Cooler Vent Air:", 0.00, 20.00, 1.50, 0.01)        
    
    
    
    with st.expander("STATIC PRESSURES"):                                    #EXPANDER 3 for STATIC PRESSURES.
         st.write("Just enter the **magnitude** of the static pressures in **Millimeters of Water Gauge (mmWg)**:")    
         cooler_ESPstack_staticpressure = st.number_input("Enter the Static Pressure of the Cooler ESP Stack:", 0.00, 1000.00, 146.00, 1.00)          
         while (CountColumn1Expander3PH <= number_of_preheater_downcomer_ducts):
                staticpressurePH = st.number_input('Static Pressure of Preheater Downcomer Duct %d:' %CountColumn1Expander3PH, 0.00, 2000.00, 835.00, 10.00, key = CountColumn1Expander3PH)
                np.arraypreheaterdowncomerductsstaticpressures.append(-staticpressurePH)
                CountColumn1Expander3PH += 1
         while ( (CountColumn1Expander3TAD <= number_of_tertiaryair_ducts) and (number_of_tertiaryair_ducts > 0) ):
                staticpressureTAD = st.number_input('Static Pressure of Tertiary Air Duct %d:' %CountColumn1Expander3TAD, 0.00, 2000.00, 25.00, 10.00, key = CountColumn1Expander3TAD)
                np.arrayTADstaticpressures.append(-staticpressureTAD)
                CountColumn1Expander3TAD += 1 
         while ( (CountColumn1Expander3CoolerMidair <= number_of_coolermidair) and (number_of_coolermidair > 0) ):
                staticpressureCMA = st.number_input('Static Pressure of Cooler Mid Air Duct %d:' %CountColumn1Expander3CoolerMidair, 0.00, 2000.00, 100.00, 10.00, key = CountColumn1Expander3CoolerMidair)
                np.arrayCoolerMidAirstaticpressures.append(-staticpressureCMA)
                CountColumn1Expander3CoolerMidair += 1 
         if ( (backcalcordirectorindirect == 'Direct' and number_of_cooler_ventair_ducts > 0) or (backcalcordirectorindirect == 'Indirect (ESP Stack Flow - MidAir Flow)' and number_of_cooler_ventair_ducts > 0) ):
            staticpressureCVAdirect = st.number_input("Static Pressure of Cooler Vent Air:", 0.00, 2000.00, 100.00, 10.00)           
    
    
    
    with st.expander("DENSITY CALCULATIONS"):                               #EXPANDER 4 for DENSITY CALCULATIONS.
         st.write("In order to calculate the density of the Pre-Heater Downcomer Ducts, answer the following questions: in (%)")
         st.write("(**Enter 0** in the H20 Column if you are **not** considering water vapor).")   
         while( CountColumn1Expander4PH <= number_of_preheater_downcomer_ducts):
               PHO2 = st.number_input('Oxygen (O2) measurement in Pre Heater Downcomer Duct %d:' %CountColumn1Expander4PH, 0.00, 100.00, 1.12, 0.10, key = CountColumn1Expander4PH)
               np.arraypreheaterdowncomerductsO2.append(PHO2)
               PHCO2 = st.number_input('Carbon dioxide (CO2) measurement in Pre Heater Downcomer Duct %d:' %CountColumn1Expander4PH, 0.00, 100.00, 28.5, 0.10, key = CountColumn1Expander4PH)
               np.arraypreheaterdowncomerductsCO2.append(PHCO2)
               PHCO =  st.number_input('Carbon monoxide (CO) measurement in Pre Heater Downcomer Duct %d:' %CountColumn1Expander4PH, 0.000, 100.00, 0.134, 0.10, format="%.3f", key = CountColumn1Expander4PH)
               np.arraypreheaterdowncomerductsCO.append(PHCO)
               PHH2O = st.number_input('Water (H2O) measurement in Pre Heater Downcomer Duct %d:' %CountColumn1Expander4PH, 0.000, 100.00, 0.00, 0.10, key = CountColumn1Expander4PH)
               np.arraypreheaterdowncomerductsH2O.append(PHH2O) 
               CountColumn1Expander4PH += 1
    dfPHO2 = pd.DataFrame(np.arraypreheaterdowncomerductsO2, columns = ['O2'])
    dfPHCO2 = pd.DataFrame(np.arraypreheaterdowncomerductsCO2, columns = ['CO2'])
    dfPHCO = pd.DataFrame(np.arraypreheaterdowncomerductsCO, columns = ['CO'])
    dfPHH2O = pd.DataFrame(np.arraypreheaterdowncomerductsH2O, columns = ['H2O'])
    dfdensitydata = pd.concat([dfPHO2, dfPHCO2, dfPHCO, dfPHH2O], axis = 1)
    dfdensitydata['Density'] = (32*dfdensitydata['O2']+44*dfdensitydata['CO2']+18*dfdensitydata['H2O']+28*(100-dfdensitydata['O2']-dfdensitydata['CO2']-dfdensitydata['CO']-dfdensitydata['H2O']))/(2240) 
   
    
    
    with st.expander("PITOT TUBE CONSTANTS"):
         st.write("Answer the following questions:")                       #EXPANDER 5 for PITOT TUBE CONSTANTS.
         cooler_ESPstack_pitottubeconstant = st.number_input('Pitot Tube Constant of Cooler ESP stack:', 0.00, 1.00, 0.81, 0.01)
         while (CountColumn1Expander5PH <= number_of_preheater_downcomer_ducts):
                pitotconstantPH = st.number_input('Pitot Constant of Preheater Downcomer Duct %d:' %CountColumn1Expander5PH, 0.0000, 1.0000, 0.8467, 0.0001, format="%.4f", key = CountColumn1Expander5PH)
                np.arraypreheaterdowncomerductspitotconstants.append(pitotconstantPH)
                CountColumn1Expander5PH += 1
         while ( (CountColumn1Expander5TAD <= number_of_tertiaryair_ducts) and (number_of_tertiaryair_ducts > 0) ):
                pitotconstantTAD = st.number_input('Pitot Constant of Tertiary Air Duct %d:' %CountColumn1Expander5TAD, 0.0000, 1.0000, 0.8100, 0.0001, format="%.4f", key = CountColumn1Expander5TAD)
                np.arrayTADpitotconstants.append(pitotconstantTAD)
                CountColumn1Expander5TAD += 1 
         while ( (CountColumn1Expander5CoolerMidair <= number_of_coolermidair) and (number_of_coolermidair > 0) ):
                pitotconstantCMA = st.number_input('Pitot Constant of Cooler Mid Air Duct %d:' %CountColumn1Expander5CoolerMidair, 0.0000, 1.0000, 0.8100, 0.0001, format="%.4f", key = CountColumn1Expander5CoolerMidair)
                np.arrayCoolerMidAirpitotconstants.append(pitotconstantCMA)
                CountColumn1Expander5CoolerMidair += 1 
         if ( (backcalcordirectorindirect == 'Direct' and number_of_cooler_ventair_ducts > 0) or (backcalcordirectorindirect == 'Indirect (ESP Stack Flow - MidAir Flow)' and number_of_cooler_ventair_ducts > 0) ):
           pitottubeconstantCVAdirect = st.number_input("Pitot Tube Constant of Cooler Vent Air:", 0.0000, 1.0000, 0.7950, 0.0001, format ="%.4f") 
            
    dfPHpitotconstants = pd.DataFrame(np.arraypreheaterdowncomerductspitotconstants, columns = ['PH Pitot Constants'])
    dfTADpitotconstants = pd.DataFrame(np.arrayTADpitotconstants, columns = ['TAD Pitot Constants'])
    dfCMApitotconstants = pd.DataFrame(np.arrayCoolerMidAirpitotconstants, columns = ['CMA Pitot Constants'])
    dfpitotconstantsdata = pd.concat([dfPHpitotconstants, dfTADpitotconstants, dfCMApitotconstants], axis = 1) 
    
    
    
    with st.expander("POWER"):                                                          #EXPANDER 6 for POWER.
         st.write("Enter the Power in **Kilowatts (kW)**:")
         cooler_ESPstack_power = st.number_input("Power of the Cooler ESP Stack:", 0.00, 10000.00, 104.00, 10.00)
         while (CountColumn1Expander6PH <= number_of_preheater_downcomer_ducts):
                powerPH = st.number_input('Power of Preheater Downcomer Duct %d:' %CountColumn1Expander6PH, 0.00, 10000.00, 1906.00, 10.00, key = CountColumn1Expander6PH)
                np.arraypreheaterdowncomerductspower.append(powerPH)
                CountColumn1Expander6PH += 1
                dfPHpower = pd.DataFrame(np.arraypreheaterdowncomerductspower, columns = ['PH Power'])
                
    
    
    with st.expander("FAN OUTLET PRESSURES"):                                            #EXPANDER 7 for FAN OUTLET PRESSURES.
         st.write("Enter the Fan Outlet Pressures:")
         cooler_ESPstack_fanoutletpressure = st.number_input("Outlet Pressure of the Cooler ESP Stack:", 0.00, 1000.00, 20.00, 10.00)
         positiveornegativeESPoutletpr = st.radio(
                        "Is the Cooler ESP Outlet Pressure positive or negative?",
                            ('+','-'))
         if(positiveornegativeESPoutletpr == '+'):
           a = cooler_ESPstack_fanoutletpressure
         else:
           a = -(cooler_ESPstack_fanoutletpressure)
          
         while (CountColumn1Expander7PH <= number_of_preheater_downcomer_ducts):
                fanoutletpressurePH = st.number_input('Outlet Pressure of Preheater Downcomer Duct %d:' %CountColumn1Expander7PH, 0.00, 1000.00, 90.00, 10.00, key = CountColumn1Expander7PH)
                positiveornegativePHoutletpr = st.radio(
                        "Is the Pre Heater Downcomer Duct %d Outlet Pressure positive or negative?" %CountColumn1Expander7PH,
                            ('+','-'), key = CountColumn1Expander7PH)
                if(positiveornegativePHoutletpr == '+'):
                   np.arraypreheaterdowncomerductsfanoutletpressure.append(fanoutletpressurePH)
                else:
                   np.arraypreheaterdowncomerductsfanoutletpressure.append(-fanoutletpressurePH)
                CountColumn1Expander7PH += 1
                dfPHfanoutletpressure = pd.DataFrame(np.arraypreheaterdowncomerductsfanoutletpressure, columns = ['PH Outlet Pressure'])
                st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html = True)
                


#Lines 556-583 take care of the ESP sheet and it's required dataframe. And the link for downloading the excel as well.    
    if input_excel is not None:
        i = 1 
        np.ESPnamesarray = []
        while(i <= 1):
            (np.ESPnamesarray).append("ESP Stack %d" %i)
            i+=1
        dfESPnames = pd.DataFrame(np.ESPnamesarray, columns = ['Name'])     
    
        dfESPmeansqrt = np.sqrt(dfESPcolumns.mean())
        dfESPmean = pd.DataFrame(dfESPmeansqrt, columns = ['Sqrt DP'])
        dfESPmean.reset_index(drop=True, inplace=True)
        dfESP = pd.concat([dfESPnames, dfESPmean], axis = 1)
        dfESP['Temp'] = cooler_ESPstack_temperature
        dfESP['Temp K'] = dfESP['Temp']+273
        dfESP['Static Pressure'] = -cooler_ESPstack_staticpressure
        dfESP['Calculated Pressure'] = datum_pressure+dfESP['Static Pressure']
        dfESP['Temp CF'] = (273/10336)*(dfESP['Calculated Pressure']/dfESP['Temp K'])
        dfESP['Density'] = (cooler_air_density*273*dfESP['Calculated Pressure'])/(10336*(273+dfESP['Temp']))
        dfESP['Diameter'] = cooler_ESPstack_diameter
        dfESP['Area'] = ((np.pi)*cooler_ESPstack_diameter**2)/4
        dfESP['V'] = cooler_ESPstack_pitottubeconstant*dfESP['Sqrt DP']*(((2*9.81)**0.5)/np.sqrt(dfESP['Density']))
        dfESP['Flow m3/s'] = dfESP['V']*dfESP['Area']
        dfESP['Flow m3/hr'] = dfESP['Flow m3/s']*3600
        dfESP['Nm3/hr'] = (dfESP['Flow m3/hr']*273*(dfESP['Calculated Pressure']))/(10330*(273+dfESP['Temp']))
        dfESP['Nm3/kgcl'] = dfESP['Nm3/hr']/(clinker_capacity*1000)
        dfESP['Outlet Pressure'] = a
        dfESP['kW'] = cooler_ESPstack_power
        dfESP['% Efficiency'] = dfESP['Flow m3/s']*((a+cooler_ESPstack_staticpressure)/(102*0.95*dfESP['kW']))*100
      


#Lines 588-616 take care of the TAD sheet and it's required dataframe. And the link for downloading the excel as well.
    if input_excel is not None and (number_of_tertiaryair_ducts > 0):    
        i = 1 
        np.TADnamesarray = []
        while(i <= number_of_tertiaryair_ducts):
            (np.TADnamesarray).append("Tertiary Air Duct %d" %i)
            i+=1
        dfTADnames = pd.DataFrame(np.TADnamesarray, columns = ['Name'])     
    
        dfTADmeansqrt = np.sqrt(dfTADcolumns.mean())
        dfsqrt = pd.DataFrame(dfTADmeansqrt, columns = ['Sqrt DP'])
        dfsqrt.reset_index(drop=True, inplace=True) 
        dfTADtemperatures = pd.DataFrame(np.arrayTADtemperatures, columns = ['Temp'])
        dfTADdiameters = pd.DataFrame(np.arrayTADdiameters, columns = ['Diameter'])
        dfTADstaticpressures = pd.DataFrame(np.arrayTADstaticpressures, columns = ['Static Pressure'])
        dfTAD = pd.concat([dfTADnames, dfsqrt, dfTADtemperatures], axis = 1)
        dfTAD['Temp K'] =  dfTAD['Temp']+273
        dfTAD = pd.concat([dfTAD, dfTADstaticpressures], axis = 1)  
        dfTAD['Calculated Pressure'] = datum_pressure+dfTAD['Static Pressure']
        dfTAD['Temp CF'] = (273/10336)*(dfTAD['Calculated Pressure']/dfTAD['Temp K'])
        dfTAD['Density'] = (cooler_air_density*273*dfTAD['Calculated Pressure'])/(10336*(273+dfTAD['Temp']))
        dfTAD = pd.concat([dfTAD, dfTADdiameters], axis = 1)
        dfTAD['Area'] = ((np.pi)*dfTAD['Diameter']**2)/4           
        dfTAD['V'] = dfpitotconstantsdata['TAD Pitot Constants']*dfTAD['Sqrt DP']*(((2*9.81)**0.5)/np.sqrt(dfTAD['Density']))
        dfTAD['Flow m3/s'] = dfTAD['V']*dfTAD['Area']
        dfTAD['Flow m3/hr'] = dfTAD['Flow m3/s']*3600
        dfTAD['Nm3/hr'] = (dfTAD['Flow m3/hr']*273*(dfTAD['Calculated Pressure']))/(10330*(273+dfTAD['Temp']))
        dfTAD['Nm3/kgcl'] = dfTAD['Nm3/hr']/(clinker_capacity*1000)
    elif input_excel is not None and (number_of_tertiaryair_ducts == 0):
        dfTAD = pd.DataFrame([[np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]], columns = ['Name', 'Sqrt DP', 'Temp', 'Temp K', 'Static Pressure', 'Calculated Pressure', 'Temp CF', 'Density', 'Diameter', 'Area', 'V', 'Flow m3/s', 'Flow m3/hr', 'Nm3/hr', 'Nm3/kgcl'])


        
        
#Lines 622-650 take care of the CMA (or WHRS o/I) sheet and it's required dataframe. And the link for downloading the excel as well.
    if input_excel is not None and (number_of_coolermidair > 0):
        i = 1 
        np.CMAnamesarray = []
        while(i <= number_of_coolermidair):
            (np.CMAnamesarray).append("Cooler Mid Air %d" %i)
            i+=1
        dfCMAnames = pd.DataFrame(np.CMAnamesarray, columns = ['Name'])     
    
        dfCMAmeansqrt = np.sqrt(dfCMAcolumns.mean())
        dfCMAsqrt = pd.DataFrame(dfCMAmeansqrt, columns = ['Sqrt DP'])
        dfCMAsqrt.reset_index(drop=True, inplace=True) 
        dfCMAtemperatures = pd.DataFrame(np.arrayCoolerMidAirtemperatures, columns = ['Temp'])
        dfCMAdiameters = pd.DataFrame(np.arrayCoolerMidAirdiameters, columns = ['Diameter'])
        dfCMAstaticpressures = pd.DataFrame(np.arrayCoolerMidAirstaticpressures, columns = ['Static Pressure'])
        dfCMA = pd.concat([dfCMAnames, dfCMAsqrt, dfCMAtemperatures], axis = 1)
        dfCMA['Temp K'] =  dfCMA['Temp']+273
        dfCMA = pd.concat([dfCMA, dfCMAstaticpressures], axis = 1)  
        dfCMA['Calculated Pressure'] = datum_pressure+dfCMA['Static Pressure']
        dfCMA['Temp CF'] = (273/10336)*(dfCMA['Calculated Pressure']/dfCMA['Temp K'])
        dfCMA['Density'] = (cooler_air_density*273*dfCMA['Calculated Pressure'])/(10336*(273+dfCMA['Temp']))
        dfCMA = pd.concat([dfCMA, dfCMAdiameters], axis = 1)
        dfCMA['Area'] = ((np.pi)*dfCMA['Diameter']**2)/4
        dfCMA['V'] = dfpitotconstantsdata['CMA Pitot Constants']*dfCMA['Sqrt DP']*(((2*9.81)**0.5)/np.sqrt(dfCMA['Density']))
        dfCMA['Flow m3/s'] = dfCMA['V']*dfCMA['Area']
        dfCMA['Flow m3/hr'] = dfCMA['Flow m3/s']*3600
        dfCMA['Nm3/hr'] = (dfCMA['Flow m3/hr']*273*(dfCMA['Calculated Pressure']))/(10330*(273+dfCMA['Temp']))
        dfCMA['Nm3/kgcl'] = dfCMA['Nm3/hr']/(clinker_capacity*1000)
    elif input_excel is not None and (number_of_coolermidair == 0):
        dfCMA = pd.DataFrame([[np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]], columns = ['Name', 'Sqrt DP', 'Temp', 'Temp K', 'Static Pressure', 'Calculated Pressure', 'Temp CF', 'Density', 'Diameter', 'Area', 'V', 'Flow m3/s', 'Flow m3/hr', 'Nm3/hr', 'Nm3/kgcl'])
        

        

#Lines 656-685 take care of the PH Downcomer Ducts sheet and it's required dataframe. And the link for downloading the excel as well.    
    if input_excel is not None:
        i = 1 
        np.PHnamesarray = []
        while(i <= number_of_preheater_downcomer_ducts):
            (np.PHnamesarray).append("Pre Heater Downcomer Duct %d" %i)
            i+=1
        dfPHnames = pd.DataFrame(np.PHnamesarray, columns = ['Name'])     
    
        dfPHmeansqrt = np.sqrt(dfpreheatercolumns.mean())
        dfPHsqrt = pd.DataFrame(dfPHmeansqrt, columns = ['Sqrt DP'])
        dfPHsqrt.reset_index(drop=True, inplace=True) 
        dfPHtemperatures = pd.DataFrame(np.arraypreheaterdowncomerductstemperatures, columns = ['Temp'])
        dfPHdiameters = pd.DataFrame(np.arraypreheaterdowncomerductsdiameters, columns = ['Diameter'])
        dfPHstaticpressures = pd.DataFrame(np.arraypreheaterdowncomerductsstaticpressures, columns = ['Static Pressure'])
        dfPH = pd.concat([dfPHnames, dfPHsqrt, dfPHtemperatures], axis = 1)
        dfPH['Temp K'] =  dfPH['Temp']+273
        dfPH = pd.concat([dfPH, dfPHstaticpressures], axis = 1)  
        dfPH['Calculated Pressure'] = datum_pressure+dfPH['Static Pressure']
        dfPH['Temp CF'] = (273/10336)*(dfPH['Calculated Pressure']/dfPH['Temp K'])
        dfPH['Density'] =(dfdensitydata['Density']*273*dfPH['Calculated Pressure'])/(10336*(273+dfPH['Temp']))
        dfPH = pd.concat([dfPH, dfPHdiameters], axis = 1)
        dfPH['Area'] = ((np.pi)*dfPH['Diameter']**2)/4
        dfPH['V'] = dfpitotconstantsdata['PH Pitot Constants']*dfPH['Sqrt DP']*(((2*9.81)**0.5)/np.sqrt(dfPH['Density']))
        dfPH['Flow m3/s'] = dfPH['V']*dfPH['Area']
        dfPH['Flow m3/hr'] = dfPH['Flow m3/s']*3600
        dfPH['Nm3/hr'] = (dfPH['Flow m3/hr']*273*(dfPH['Calculated Pressure']))/(10330*(273+dfPH['Temp']))
        dfPH['Nm3/kgcl'] = dfPH['Nm3/hr']/(clinker_capacity*1000)
        dfPH['Outlet Pressure'] = dfPHfanoutletpressure['PH Outlet Pressure']
        dfPH['kW'] = dfPHpower['PH Power']
        dfPH['% Efficiency'] = dfPH['Flow m3/s']*((-dfPH['Static Pressure']+dfPHfanoutletpressure['PH Outlet Pressure'])/(102*0.95*dfPH['kW']))*100
        

#DATAFRAME containing all FAN FLOWS except for Cooler Vent Air.        
        dfnew = pd.concat([dfESP, dfTAD, dfCMA, dfPH])
        

        
#Lines 694-743 take care of the CVA fans data (DIRECT CALCULATION, BACK CALCULATION and ZERO case as well).   
    if input_excel is not None and ( backcalcordirectorindirect == 'Direct' and number_of_cooler_ventair_ducts > 0 ):  #Change 
        i = 1 
        np.CVAnamesarray = []
        while(i <= 1):
            (np.CVAnamesarray).append("Cooler Vent Air %d" %i)
            i+=1
        dfCVAnames = pd.DataFrame(np.CVAnamesarray, columns = ['Name'])
        
        dfCVAmeansqrt = np.sqrt(dfCVAcolumns.mean())
        dfCVAmean = pd.DataFrame(dfCVAmeansqrt, columns = ['Sqrt DP'])
        dfCVAmean.reset_index(drop=True, inplace=True)
        dfCVA = pd.concat([dfCVAnames, dfCVAmean], axis = 1)
        dfCVA['Temp'] = tempCVAdirect
        dfCVA['Temp K'] = tempCVAdirect+273
        dfCVA['Static Pressure'] = -staticpressureCVAdirect
        dfCVA['Calculated Pressure'] = datum_pressure+dfCVA['Static Pressure']
        dfCVA['Temp CF'] = (273/10336)*(dfCVA['Calculated Pressure']/dfCVA['Temp K'])
        dfCVA['Density'] = (cooler_air_density*273*dfCVA['Calculated Pressure'])/(10336*(273+dfCVA['Temp']))
        dfCVA['Diameter'] = diamCVAdirect
        dfCVA['Area'] = ((np.pi)*diamCVAdirect**2)/4
        dfCVA['V'] = pitottubeconstantCVAdirect*dfCVA['Sqrt DP']*(((2*9.81)**0.5)/np.sqrt(dfCVA['Density']))
        dfCVA['Flow m3/s'] = dfCVA['V']*dfCVA['Area']
        dfCVA['Flow m3/hr'] = dfCVA['Flow m3/s']*3600
        dfCVA['Nm3/hr'] = (dfCVA['Flow m3/hr']*273*(dfCVA['Calculated Pressure']))/(10330*(273+dfCVA['Temp']))
        dfCVA['Nm3/kgcl'] = dfCVA['Nm3/hr']/(clinker_capacity*1000)
    elif input_excel is not None and (backcalcordirectorindirect == 'Indirect (ESP Stack Flow - MidAir Flow)'):
        dfCVA = pd.DataFrame([['Cooler Vent Air 1', np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, dfESP['Nm3/kgcl']-(dfCMA['Nm3/kgcl'].sum(axis = 0))*0.97]])
    elif input_excel is not None and (number_of_cooler_ventair_ducts == 0):
        dfCVA = pd.DataFrame([[np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]], columns = ['Name', 'Sqrt DP', 'Temp', 'Temp K', 'Static Pressure', 'Calculated Pressure', 'Temp CF', 'Density', 'Diameter', 'Area', 'V', 'Flow m3/s', 'Flow m3/hr', 'Nm3/hr', 'Nm3/kgcl'])
    elif input_excel is not None and (number_of_cooler_ventair_ducts > 0 and backcalcordirectorindirect == 'Back Calculate'):
          i = 1
          np.CVAnamesarray = []
          while(i <= 1):
              (np.CVAnamesarray).append("Cooler Vent Air %d" %i)
              i+=1
          dfCVAnames = pd.DataFrame(np.CVAnamesarray, columns = ['Name'])  
        
          with st.expander("COOLER VENT AIR BACK CALCULATION"):
               st.write("Answer the following questions:")
               CVAbackcaltemp = st.number_input('Temperature of Cooler Vent Air:', 0.00, 2000.00, 338.00, 5.00) 
               A = np.array( [ [1,1], [(CVAbackcaltemp-20)*(0.237+23*(CVAbackcaltemp*10**(-6))), (ambient_air_temperature-20)*(0.237+23*(ambient_air_temperature*10**(-6))) ] ] )
               B = np.array( [ cooler_air_density*dfESP['Nm3/kgcl'], (cooler_air_density*dfESP['Nm3/kgcl']*(dfESP['Temp']-20))*(0.237+23*dfESP['Temp']*10**(-6)) ] ) 
               Fbhai =  linalg.solve(A,B)
               st.write("Cooler Vent Air Flow is (**X**, kg/kg cl):")
               st.write(float(Fbhai[0]))
               st.write("False Air Flow is (**Y**, kg/kg cl):") 
               st.write(float(Fbhai[1]))
               
               dfCVA = pd.DataFrame([['Cooler Vent Air 1', np.nan, CVAbackcaltemp, CVAbackcaltemp+273, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, float(Fbhai[0])/cooler_air_density]], columns = ['Name', 'Sqrt DP', 'Temp', 'Temp K', 'Static Pressure', 'Calculated Pressure', 'Temp CF', 'Density', 'Diameter', 'Area', 'V', 'Flow m3/s', 'Flow m3/hr', 'Nm3/hr', 'Nm3/kgcl'])
               #st.write("***") 
        
    if input_excel is not None: 
        dfnewCVAaswell = pd.concat([dfESP, dfTAD, dfCMA, dfPH, dfCVA])
        


        
#Code for COLUMN 2, taking care of the COOLER FANS. Lines 752-854 as of now.  
with col2:
    st.header("COOLER FANS")
    pitot_tube_constant_forcoolerfans = st.number_input('Enter the Pitot Tube Constant for Cooler Fans:', 0.0000, 1.0000, 0.8100, 0.0001, format = "%.4f")
    with st.expander("ANEMOMETER OR NOT?"):
         st.write("Answer the following questions: (Type 1 if yes, 0 otherwise)")
         CountColumn2Expander1 = 1           
         np.arrayforanemometeryesorno = []      #Array to hold yes or no responses in the form of 1 or 0.
         while ( (CountColumn2Expander1 <= number_of_cooler_fans) and (number_of_cooler_fans > 0) ):
                yorn = st.number_input("Was the measurement of the cooler fan %d taken by an anemometer?" %CountColumn2Expander1, 0, 1, 0, 1, key = CountColumn2Expander1) 
                np.arrayforanemometeryesorno.append(yorn)           #yorn means Yes or No.
                CountColumn2Expander1 += 1       #Using an array to store all the values of anemometer. 1 if Yes, 0 otherwise.
         
    
    with st.expander("DIAMETERS OR AREA?"):
         CountColumn2Expander2 = 1
         CountColumn2Expander2area = 1
         CountColumn2Expander2dia = 1
         np.arrayforcoolerfansarea = []   
         while( (CountColumn2Expander2 <= number_of_cooler_fans) ):
            choiceofareaordiameter = st.number_input('Choose if you want to enter the Area of Cooler Fan %d or the Diameter? (Type 1 for area, 0 for diameter)' %CountColumn2Expander2, 0, 1, 1, 1, key = CountColumn2Expander2)
            if(choiceofareaordiameter == 1):
               areacoolerfan = st.number_input('Enter the Area of Cooler Fan %d:' %CountColumn2Expander2, 0.00, 100.00, 1.23, 1.00, format = "%.4f", key = CountColumn2Expander2area)
               np.arrayforcoolerfansarea.append(areacoolerfan)
               CountColumn2Expander2area += 1 
            elif(choiceofareaordiameter == 0):
               diametercoolerfan = st.number_input('Enter the Diameter of Cooler Fan %d:' %CountColumn2Expander2, 0.00, 50.0, 2.00, 0.01, format = "%.4f", key = CountColumn2Expander2dia)
               np.arrayforcoolerfansarea.append(((np.pi)*(diametercoolerfan)**2)/4) 
               CountColumn2Expander2dia += 1 
            CountColumn2Expander2 += 1
               
    
    
    with st.expander("STATIC PRESSURES"):
         st.write("Enter just the **magnitude** of static pressure of the fans:")
         CountColumn2Expander3 = 1
         np.arrayforcoolerfanstaticpressures = []
         while ( (CountColumn2Expander3 <= number_of_cooler_fans) and (number_of_cooler_fans > 0) ):   
               staticpressureCF = st.number_input('Static pressure of cooler fan %d:' %CountColumn2Expander3, 0.00, 2000.00, 30.00, 10.00, key = CountColumn2Expander3)
               np.arrayforcoolerfanstaticpressures.append(-staticpressureCF)
               CountColumn2Expander3 += 1
                
    
    
    with st.expander("POWER"):
         st.write("Enter the Power in **KiloWatts(kW)**:")
         CountColumn2Expander4 = 1
         np.arrayforcoolerfanspower = []
         while ( (CountColumn2Expander4 <= number_of_cooler_fans) and (number_of_cooler_fans > 0) ):   
               powerCF = st.number_input('Power of cooler fan %d:' %CountColumn2Expander4, 0.00, 2000.00, 200.00, 10.00, key = CountColumn2Expander4)
               np.arrayforcoolerfanspower.append(powerCF)
               CountColumn2Expander4 += 1
               dfCFpower = pd.DataFrame(np.arrayforcoolerfanspower, columns = ['Power'])
                
    
    
    with st.expander("FAN OUTLET PRESSURES"):
         st.write("Enter the Fan Outlet Pressures:")
         CountColumn2Expander5 = 1
         np.arrayforcoolerfansoutletpressures = []
         while ( (CountColumn2Expander5 <= number_of_cooler_fans) and (number_of_cooler_fans > 0) ):   
               outletpressuresCF = st.number_input('Outlet Pressure of Cooler Fan %d:' %CountColumn2Expander5, 0.00, 2000.00, 900.00, 10.00, key = CountColumn2Expander5)
               positiveornegativeCFoutletpr = st.radio(
                        "Is the Cooler Fan %d Outlet Pressure positive or negative?" %CountColumn2Expander5,
                            ('+','-'), key = CountColumn2Expander5)
               if(positiveornegativeCFoutletpr == '+'):
                   np.arrayforcoolerfansoutletpressures.append(outletpressuresCF)
               else:
                   np.arrayforcoolerfansoutletpressures.append(-outletpressuresCF)
               CountColumn2Expander5 += 1
               dfCFfanoutletpressure = pd.DataFrame(np.arrayforcoolerfansoutletpressures, columns = ['Outlet Pressure']) 
               st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html = True)     
    
    
    
    if input_excel is not None and (number_of_cooler_fans > 0):  
       i = 1 
       np.CFnamesarray = []
       while(i <= number_of_cooler_fans):
            (np.CFnamesarray).append("Cooler Fan %d" %i)
            i+=1
       dfCFnames = pd.DataFrame(np.CFnamesarray, columns = ['Name'])         
       
       dfcoolerfancolumnsmean = dfcoolerfancolumns.mean()               
       dfCFmean = pd.DataFrame(dfcoolerfancolumnsmean, columns = ['Average Velocities'])
       dfCFmean.reset_index(drop=True, inplace=True)
       dfcoolerfanareas = pd.DataFrame(np.arrayforcoolerfansarea, columns = ['Areas'])    
       dfcoolerfansstaticpressure = pd.DataFrame(np.arrayforcoolerfanstaticpressures, columns = ['Static Pressures']) 
       dfanemometeryesorno = pd.DataFrame(np.arrayforanemometeryesorno, columns = ['Anemometer Y/N'])
       dfCF = pd.concat([dfCFnames, dfanemometeryesorno, dfCFmean, dfcoolerfanareas, dfcoolerfansstaticpressure], axis = 1)       
       dfCF['m3/sec'] = dfCF.apply(lambda row: row['Average Velocities']*row['Areas'] if row['Anemometer Y/N'] == 1 else pitot_tube_constant_forcoolerfans*(2*9.81)**0.5*row['Average Velocities']/(cooler_air_density)**0.5, axis = 1 )
       #Verify the formula to be used in case anemometer is not used.
       dfCF['m3/hr'] = dfCF['m3/sec']*3600
       dfCF['TCF'] = (273/(273+ambient_air_temperature))*((datum_pressure+dfCF['Static Pressures'])/10330)  
       dfCF['Nm3/hr'] = dfCF['TCF']*dfCF['m3/hr']
       dfCF['Nm3/s'] = dfCF['Nm3/hr']/3600
       dfCF['Nm3/kgcl'] = dfCF['Nm3/hr']/(clinker_capacity*1000)
       dfCF['Temp'] = ambient_air_temperature
       dfCF['Outlet Pressure'] = dfCFfanoutletpressure['Outlet Pressure']
       dfCF['Power'] = dfCFpower['Power']
       dfCF['% Efficiency'] = dfCF['m3/sec']*((dfCF['Static Pressures']+dfCF['Outlet Pressure'])/(102*0.95*dfCF['Power']))*100 
    elif input_excel is not None and (number_of_cooler_fans == 0):
       dfCF = pd.DataFrame()
       dfCF = pd.DataFrame([[np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]], columns = ['Name', 'Anemometer Y/N', 'Average Velocities', 'Areas', 'Static Pressures', 'm3/sec', 'm3/hr', 'TCF', 'Nm3/hr', 'Nm3/s', 'Nm3/kgcl', 'Temp', 'Outlet Pressure', 'Power', '% Efficiency']) 



        
#Code for Column 3, taking care of the COOLER HEAT BALANCE. Lines 860-984 as of now. 
with col3:
    st.header("COOLER HB")
    clinker_inlet_temperature = st.number_input('Clinker Inlet Temperature:', 0.00, 2000.00, 1450.00, 1.00)   
    clinker_outlet_temperature = st.number_input('Clinker Outlet Temperature:', 0.00, 2000.00, 260.00, 1.00)   
    cooler_radiation_losses = st.number_input('Enter the Cooler Radiation Losses (Heat):', 0.00, 100.00, 3.00, 0.01)
    

    
#Code for COOLER HEAT BALANCE INPUT SECTION. Lines 869-873.
    if input_excel is not None:    
      HeatBalanceInputData = [ [ 'Hot Clinker', 1, clinker_inlet_temperature, 0.186+54*clinker_inlet_temperature*10**(-6), (0.186+54*clinker_inlet_temperature*10**(-6))*(clinker_inlet_temperature-REFERENCE_TEMPERATURE_NTP)], 
                               [ 'Cooling Air', dfCF['Nm3/kgcl'].sum(axis = 0)*cooler_air_density, ambient_air_temperature, 0.237+23*ambient_air_temperature*10**(-6), (dfCF['Nm3/kgcl'].sum(axis = 0))*(cooler_air_density)*((0.237+23*ambient_air_temperature*10**(-6))*(ambient_air_temperature-REFERENCE_TEMPERATURE_NTP))],
                               ]
      dfInputHeatBalance = pd.DataFrame(HeatBalanceInputData, columns = ['Item', 'Flow (kg/kg clinker)', 'Temp (Celsius)', 'Cp (kcal/kg celsius)', 'Heat (kcal/kg clinker)']) 
    
    

    
#Code for COOLER HEAT BALANCE OUTPUT SECTION. Lines 879-984 as of now.
    if input_excel is not None:
        HeatBalanceOutputDataSame = [ ['Clinker Leaving the Cooler', 1, clinker_outlet_temperature, 0.186+(54*clinker_outlet_temperature*10**(-6)), (0.186+(54*clinker_outlet_temperature*10**(-6)))*(clinker_outlet_temperature-REFERENCE_TEMPERATURE_NTP)],
                                ['Cooler Radiation Losses', np.nan, np.nan, np.nan, cooler_radiation_losses],     
                                ] 
        
        dfHeatBalanceOutputSame = pd.DataFrame(HeatBalanceOutputDataSame, columns = ['Item', 'Flow (kg/kg clinker)', 'Temp (Celsius)', 'Cp (kcal/kg celsius)', 'Heat (kcal/kg clinker)'])
        

        
#TAD HEAT BALANCE OUTPUT. Lines 889-905. 
    if input_excel is not None and (number_of_tertiaryair_ducts > 0):
        i = 1
        np.TAtoILCnamesarray = []
        while(i <= number_of_tertiaryair_ducts):
             (np.TAtoILCnamesarray).append("Tertiary Air to ILC %d" %i)
             i+=1  
        dfTAtoILCnames = pd.DataFrame(np.TAtoILCnamesarray, columns = ['Item'])
        
        HeatBalanceOutputDataTAD = pd.DataFrame()
        HeatBalanceOutputDataTAD = dfTAtoILCnames
        HeatBalanceOutputDataTAD['Flow (kg/kg clinker)'] = dfTAD['Nm3/kgcl']*cooler_air_density
        HeatBalanceOutputDataTAD['Temp (Celsius)'] = dfTAD['Temp']
        HeatBalanceOutputDataTAD['Cp (kcal/kg celsius)'] = 0.237+(23*dfTAD['Temp']*10**(-6))
        HeatBalanceOutputDataTAD['Heat (kcal/kg clinker)'] = (dfTAD['Nm3/kgcl']*cooler_air_density)*(0.237+(23*dfTAD['Temp']*10**(-6)))*(dfTAD['Temp']-REFERENCE_TEMPERATURE_NTP)
    elif input_excel is not None and (number_of_tertiaryair_ducts == 0):
        HeatBalanceOutputDataTAD = pd.DataFrame()
        HeatBalanceOutputDataTAD = pd.DataFrame([[np.nan, np.nan, np.nan, np.nan, np.nan]], columns = ['Item', 'Flow (kg/kg clinker)', 'Temp (Celsius)', 'Cp (kcal/kg celsius)', 'Heat (kcal/kg clinker)'])
                

            
#CMA HEAT BALANCE OUTPUT. Lines 910-926. 
    if input_excel is not None and (number_of_coolermidair > 0):
        i = 1
        np.CoolerMidAirnamesarray = []
        while(i <= number_of_coolermidair):
             (np.CoolerMidAirnamesarray).append("Cooler Mid Air %d" %i)
             i+=1
        dfCoolerMidAirnames = pd.DataFrame(np.CoolerMidAirnamesarray, columns = ['Item'])     
            
        HeatBalanceOutputDataCMA = pd.DataFrame()
        HeatBalanceOutputDataCMA = dfCoolerMidAirnames
        HeatBalanceOutputDataCMA['Flow (kg/kg clinker)'] = dfCMA['Nm3/kgcl']*cooler_air_density
        HeatBalanceOutputDataCMA['Temp (Celsius)'] = dfCMA['Temp']
        HeatBalanceOutputDataCMA['Cp (kcal/kg celsius)'] = 0.237+(23*dfCMA['Temp']*10**(-6))
        HeatBalanceOutputDataCMA['Heat (kcal/kg clinker)'] = (dfCMA['Nm3/kgcl']*cooler_air_density)*(0.237+(23*dfCMA['Temp']*10**(-6)))*(dfCMA['Temp']-REFERENCE_TEMPERATURE_NTP)
    elif input_excel is not None and (number_of_coolermidair == 0):
        HeatBalanceOutputDataCMA = pd.DataFrame()
        HeatBalanceOutputDataCMA = pd.DataFrame([[np.nan, np.nan, np.nan, np.nan, np.nan]], columns = ['Item', 'Flow (kg/kg clinker)', 'Temp (Celsius)', 'Cp (kcal/kg celsius)', 'Heat (kcal/kg clinker)'])
        

        
#CVA HEAT BALANCE OUTPUT. Lines 931-958.        
    if input_excel is not None and (number_of_cooler_ventair_ducts > 0):
        i = 1
        np.CoolerVentAirnamesarray = []
        while(i <= number_of_coolermidair):
             (np.CoolerVentAirnamesarray).append("Cooler Vent Air %d" %i)
             i+=1
        dfCoolerVentAirnames = pd.DataFrame(np.CoolerVentAirnamesarray, columns = ['Item']) 
        
        HeatBalanceOutputDataCVA = pd.DataFrame()
        HeatBalanceOutputDataCVA = dfCoolerVentAirnames
        
        if (backcalcordirectorindirect == 'Direct'):
          HeatBalanceOutputDataCVA['Flow (kg/kg clinker)'] = dfCVA['Nm3/kgcl']*cooler_air_density 
          HeatBalanceOutputDataCVA['Temp (Celsius)'] = dfCVA['Temp']
          HeatBalanceOutputDataCVA['Cp (kcal/kg celsius)'] = 0.237+(23*dfCVA['Temp']*10**(-6))  
        elif (backcalcordirectorindirect == 'Back Calculate'):
          HeatBalanceOutputDataCVA['Flow (kg/kg clinker)'] = Fbhai[0] 
          HeatBalanceOutputDataCVA['Temp (Celsius)'] = CVAbackcaltemp
          HeatBalanceOutputDataCVA['Cp (kcal/kg celsius)'] = 0.237+(23*CVAbackcaltemp*10**(-6)) 
        else: 
          HeatBalanceOutputDataCVA['Flow (kg/kg clinker)'] = (dfESP['Nm3/kgcl']-(dfCMA['Nm3/kgcl'].sum(axis = 0))*0.97)*cooler_air_density
          HeatBalanceOutputDataCVA['Temp (Celsius)'] = dfESP['Temp']
          HeatBalanceOutputDataCVA['Cp (kcal/kg celsius)'] = 0.237+(23*dfESP['Temp']*10**(-6)) 
       
        HeatBalanceOutputDataCVA['Heat (kcal/kg clinker)'] = (HeatBalanceOutputDataCVA['Flow (kg/kg clinker)'])*HeatBalanceOutputDataCVA['Cp (kcal/kg celsius)']*(HeatBalanceOutputDataCVA['Temp (Celsius)']-REFERENCE_TEMPERATURE_NTP)
    elif input_excel is not None and (number_of_cooler_ventair_ducts == 0):
        HeatBalanceOutputDataCVA = pd.DataFrame()
        HeatBalanceOutputDataCVA = pd.DataFrame([[np.nan, np.nan, np.nan, np.nan, np.nan]], columns = ['Item', 'Flow (kg/kg clinker)', 'Temp (Celsius)', 'Cp (kcal/kg celsius)', 'Heat (kcal/kg clinker)'])
        

        
#HEAT BALANCE OUTPUT (excluding Secondary Air). Lines 963-965.        
    if input_excel is not None:     
      HeatBalanceOutputDataCVA.reset_index(drop=True, inplace=True) 
      dfOutputHeatBalance = pd.concat([dfHeatBalanceOutputSame, HeatBalanceOutputDataTAD, HeatBalanceOutputDataCMA, HeatBalanceOutputDataCVA])     
    


#SECONDARY AIR CALCULATIONS. Line 970-984.   
      SAflowkgkgclinker = dfInputHeatBalance['Flow (kg/kg clinker)'].sum(axis = 0) - dfOutputHeatBalance['Flow (kg/kg clinker)'].sum(axis = 0)   
      HeatSA = dfInputHeatBalance['Heat (kcal/kg clinker)'].sum(axis = 0)-dfOutputHeatBalance['Heat (kcal/kg clinker)'].sum(axis = 0)
      acoeff = 23*10**(-6)
      bcoeff = 0.237 - (REFERENCE_TEMPERATURE_NTP)*23*(10**(-6))        
      ccoeff = -(HeatSA)/SAflowkgkgclinker - ((REFERENCE_TEMPERATURE_NTP)*0.237)
      discriminant = (bcoeff**2)-4*acoeff*ccoeff  
      sol2 = (-bcoeff+np.sqrt(discriminant))/(2*acoeff)  
     
      dfOutputHeatBalance.loc[len(dfOutputHeatBalance.index)] = ['Secondary Air to Kiln', float(SAflowkgkgclinker), sol2, 0.237+(23*sol2*10**(-6)), HeatSA] 
    
    
      st.write("Cooler Recuperation Efficiency:")
      st.write( (HeatSA+HeatBalanceOutputDataTAD['Heat (kcal/kg clinker)'].sum(axis = 0))/dfInputHeatBalance['Heat (kcal/kg clinker)'].sum(axis = 0) )
      st.write("Cooler Heat Losses:")
      st.write( dfInputHeatBalance['Heat (kcal/kg clinker)'].sum(axis = 0)-(HeatSA+HeatBalanceOutputDataTAD['Heat (kcal/kg clinker)'].sum(axis = 0)) )
    


    
#Code for the CONTAINER. Including BLOWERS/PA FANS code and KILN HEAT balance. Lines 990-1023 as of now.
with st.container():
    col4, col5 = st.columns(2)
    with col4:
       st.header("BLOWERS/PA Fans")      #Code for PA Fans/ Blowers. Lines 992-1119.
       CountColumn4Expander1KB = 1
       CountColumn4Expander1CB = 1 
       CountColumn4Expander1PAF = 1
       np.arrayKBareas = []
       np.arrayCBareas = [] 
       np.arrayPAFareas = [] 
    
       CountColumn5Expander1KB = 1
       CountColumn5Expander1CB = 1 
       CountColumn5Expander1PAF = 1
       np.arrayKBtemps = []
       np.arrayCBtemps = [] 
       np.arrayPAFtemps = []    
       
       
       with st.expander("AREAS"):
        st.write("Enter the Areas:")
        while (CountColumn4Expander1KB <= number_of_kiln_blowers):
                areaKB = st.number_input('Area of Kiln Blower %d:' %CountColumn4Expander1KB, 0.00, 100.00, 0.25, 0.01, key = CountColumn4Expander1KB)
                np.arrayKBareas.append(areaKB)
                CountColumn4Expander1KB += 1
        while (CountColumn4Expander1CB <= number_of_calciner_blowers and number_of_calciner_blowers > 0):
                areaCB = st.number_input('Area of Calciner Blower %d:' %CountColumn4Expander1CB, 0.00, 100.00, 0.25, 0.01, key = CountColumn4Expander1CB)
                np.arrayCBareas.append(areaCB)
                CountColumn4Expander1CB += 1 
        while (CountColumn4Expander1PAF <= number_of_PA_fans):
                areaPAF = st.number_input('Area of PA Fan %d:' %CountColumn4Expander1PAF, 0.00, 100.00, 0.25, 0.01, key = CountColumn4Expander1PAF)
                np.arrayPAFareas.append(areaPAF)
                CountColumn4Expander1PAF += 1  
                
       
       with st.expander("TEMPERATURES"): 
        st.write("Enter the temperatures in **Celsius**:")
        #temperature_treya = st.number_input('Temperature:', 0.00, 100.00, 50.00)  #CONFIRM WITH SIR!!!!
        while (CountColumn5Expander1KB <= number_of_kiln_blowers):
                tempKB = st.number_input('Temperature of Kiln Blower %d:' %CountColumn5Expander1KB, 0.00, 100.00, 39.00, 1.00, key = CountColumn5Expander1KB)
                np.arrayKBtemps.append(tempKB)
                CountColumn5Expander1KB += 1
        while (CountColumn5Expander1CB <= number_of_calciner_blowers and number_of_calciner_blowers > 0):
                tempCB = st.number_input('Temperature of Calciner Blower %d:' %CountColumn5Expander1CB, 0.00, 100.00, 39.00, 1.00, key = CountColumn5Expander1CB)
                np.arrayCBtemps.append(tempCB)
                CountColumn5Expander1CB += 1 
        while (CountColumn5Expander1PAF <= number_of_PA_fans):
                tempPAF = st.number_input('Temperature of PA Fan %d:' %CountColumn5Expander1PAF, 0.00, 100.00, 39.00, 1.00, key = CountColumn5Expander1PAF)
                np.arrayPAFtemps.append(tempPAF)
                CountColumn5Expander1PAF += 1  
                
       

#Code for Kiln Blowers. Lines 1044-1064.       
       if input_excel is not None:
        i = 1
        np.KBnamesarray = []
        while(i <= number_of_kiln_blowers):
             (np.KBnamesarray).append("Kiln Blower %d" %i)
             i+=1
        dfKBnames = pd.DataFrame(np.KBnamesarray, columns = ['Name']) 
        
        dfkilnblowerscolumnsmean = dfkilnblowerscolumns.mean()
        dfKBmean = pd.DataFrame(dfkilnblowerscolumnsmean, columns = ['Average Velocities'])
        dfKBmean.reset_index(drop=True, inplace=True)
        dfKBareas = pd.DataFrame(np.arrayKBareas, columns = ['Area'])
        dfKBtemps = pd.DataFrame(np.arrayKBtemps, columns = ['Temperature'])
        dfKB = pd.concat([dfKBnames, dfKBmean, dfKBareas, dfKBtemps], axis = 1)
        dfKB['2*(Area)'] = dfKB['Area']*2
        dfKB['Volumetric Flow Rate m3/s'] = dfKB['2*(Area)']*dfKB['Average Velocities']
        dfKB['Volumetric Flow Rate m3/hr'] = dfKB['Volumetric Flow Rate m3/s']*3600
        dfKB['TCF'] = 273/(273+dfKB['Temperature'])
        dfKB['Nm3/hr'] = dfKB['TCF']*dfKB['Volumetric Flow Rate m3/hr']
        dfKB['Nm3/s'] = dfKB['Nm3/hr']/3600
        dfKB['Nm3/kgcl'] = dfKB['Nm3/hr']/(clinker_capacity*1000) 
               
       

#Code for CALCINER BLOWERS. Lines 1069-1091.    
       if input_excel is not None and (number_of_calciner_blowers > 0):
        i = 1
        np.CBnamesarray = []
        while(i <= number_of_calciner_blowers):
             (np.CBnamesarray).append("Calciner Blower %d" %i)
             i+=1
        dfCBnames = pd.DataFrame(np.CBnamesarray, columns = ['Name']) 
        
        dfcalcinerblowerscolumnsmean = dfcalcinerblowerscolumns.mean()
        dfCBmean = pd.DataFrame(dfcalcinerblowerscolumnsmean, columns = ['Average Velocities'])
        dfCBmean.reset_index(drop=True, inplace=True)
        dfCBareas = pd.DataFrame(np.arrayCBareas, columns = ['Area'])
        dfCBtemps = pd.DataFrame(np.arrayCBtemps, columns = ['Temperature'])
        dfCB = pd.concat([dfCBnames, dfCBmean, dfCBareas, dfCBtemps], axis = 1)
        dfCB['2*(Area)'] = dfCB['Area']*2
        dfCB['Volumetric Flow Rate m3/s'] = dfCB['2*(Area)']*dfCB['Average Velocities']
        dfCB['Volumetric Flow Rate m3/hr'] = dfCB['Volumetric Flow Rate m3/s']*3600
        dfCB['TCF'] = 273/(273+dfCB['Temperature'])
        dfCB['Nm3/hr'] = dfCB['TCF']*dfCB['Volumetric Flow Rate m3/hr']
        dfCB['Nm3/s'] = dfCB['Nm3/hr']/3600
        dfCB['Nm3/kgcl'] = dfCB['Nm3/hr']/(clinker_capacity*1000)
       elif input_excel is not None and (number_of_calciner_blowers == 0):
        dfCB = pd.DataFrame([[np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]], columns = ['Name', 'Average Velocities', 'Area', 'Temperature', '2*(Area)', 'Volumetric Flow Rate m3/s', 'Volumetric Flow Rate m3/hr', 'TCF', 'Nm3/hr', 'Nm3/s', 'Nm3/kgcl'])
        
       
    
#Code for PA FANS. Lines 1096-1116.    
       if input_excel is not None:
        i = 1
        np.PAFnamesarray = []
        while(i <= number_of_PA_fans):
             (np.PAFnamesarray).append("PA Fan %d" %i)
             i+=1
        dfPAFnames = pd.DataFrame(np.PAFnamesarray, columns = ['Name'])
        
        dfPAfanscolumnsmean = dfPAfanscolumns.mean()
        dfPAFmean = pd.DataFrame(dfPAfanscolumnsmean, columns = ['Average Velocities'])
        dfPAFmean.reset_index(drop=True, inplace=True)
        dfPAFareas = pd.DataFrame(np.arrayPAFareas, columns = ['Area'])
        dfPAFtemps = pd.DataFrame(np.arrayPAFtemps, columns = ['Temperature'])
        dfPAF = pd.concat([dfPAFnames, dfPAFmean, dfPAFareas, dfPAFtemps], axis = 1)
        dfPAF['2*(Area)'] = dfPAF['Area']*2
        dfPAF['Volumetric Flow Rate m3/s'] = dfPAF['2*(Area)']*dfPAF['Average Velocities']
        dfPAF['Volumetric Flow Rate m3/hr'] = dfPAF['Volumetric Flow Rate m3/s']*3600
        dfPAF['TCF'] = 273/(273+dfPAF['Temperature'])
        dfPAF['Nm3/hr'] = dfPAF['TCF']*dfPAF['Volumetric Flow Rate m3/hr']
        dfPAF['Nm3/s'] = dfPAF['Nm3/hr']/3600
        dfPAF['Nm3/kgcl'] = dfPAF['Nm3/hr']/(clinker_capacity*1000)  
        
       if input_excel is not None:
        dftreya = pd.concat([dfKB, dfCB, dfPAF])
        
        

#Code for "KILN HEAT BALANCE". Lines 1124- as of now.    
    with col5:
       st.header("KILN HB")
       with st.expander("HEAT INPUT INFORMATION"):
        st.write("**MOISTURES**")
        kiln_feed_moisture = st.number_input("Kiln Feed Moisture:", 0.00, 5.00, 0.50)
        coal_moisture = st.number_input("Coal Moisture:", 0.00, 100.00, 4.00)
        st.write("***")
        
        st.write("**TEMPERATURES** in **Celsius**")
        kiln_feed_temperature = st.number_input("Temperature of Kiln Feed:", 0.000, 1000.000, 65.000, format = "%.3f")
        fuel_temperature = st.number_input("Temperature of Fuel:", 0.000, 1000.000, 50.000, format = "%.3f")
        primary_air_temperature = st.number_input("Temperature of Primary Air:", 0.000, 1000.000, 60.000, format = "%.3f")
        coal_moisture_temperature = st.number_input("Temperature of Coal Moisture:", 0.000, 1000.000, 58.000, format = "%.3f")
        transport_air_temperature = st.number_input("Temperature of Transport Air:", 0.000, 1000.000, 50.000, format = "%.3f")
        st.write("***")
        
        st.write("**FUEL QUANTITIES**")
        fuel_qty_kiln = st.number_input("Fuel Quantity in Kiln (in tonnes):", 0.00, 2000.00, 31.31)
        fuel_qty_calciner = st.number_input("Fuel Quantity in Calciner (in tonnes):", 0.00, 2000.00, 31.31)
        fuel_qty_total = fuel_qty_kiln+fuel_qty_calciner
        
      
       with st.expander("HEAT OUTPUT INFORMATION"):  
        st.write("**RADIATION VALUES**")
        PH_radiation_values = st.number_input("PH Radiation Value:", 0.00, 100.00, 15.00)
        cooler_radiation_values = st.number_input("Cooler Radiation Value:", 0.00, 100.00, 3.00)
        TAD_radiation_values = st.number_input("TAD Radiation Value:", 0.00, 100.00, 2.00)
        st.write("***")
        
        st.write("**RETURN DUST QUANTITIES**")
        CountColumn5Expander2PH = 1
        np.arrayforreturnqtydust = []
        while(CountColumn5Expander2PH <= number_of_preheater_downcomer_ducts):
            returnqtydustPH = st.number_input('Return Dust Quantity of Preheater Downcomer Duct %d:' %CountColumn5Expander2PH, 0.00, 100.00, 4.00, format="%.4f", key = CountColumn5Expander2PH)
            np.arrayforreturnqtydust.append(returnqtydustPH)
            CountColumn5Expander2PH += 1
        st.write("***")
      
       
        
       with st.expander("HEAT OF REACTION"):
        HORmanualorcalc = st.number_input("Do you want to manually enter the Heat of Reaction value or you want to calculate it? (Type 1 for manual and 0 for calculation).", 0, 1, 0, 1)
        st.write("***")
        if (HORmanualorcalc == 0):
          percental2o3 = st.number_input("Percentage (%) of Al2O3 (Aluminum Oxide)", 0.000, 100.000, 4.960, 0.01, format = "%.3f")
          percentmgo = st.number_input("Percentage (%) of MgO (Magnesium Oxide)", 0.000, 100.000, 1.380, 0.01, format = "%.3f")
          percentcao = st.number_input("Percentage (%) of CaO (Calcium Oxide)", 0.000, 100.000, 64.310, 0.01, format = "%.3f")
          percentsio2 = st.number_input("Percentage (%) of SiO2 (Silicon Dioxide)", 0.000, 100.000, 21.340, 0.01, format = "%.3f")
          percentfe2o3 = st.number_input("Percentage (%) of Fe2O3 (Ferric Oxide)", 0.000, 100.000, 4.880, 0.01, format = "%.3f")
          HOR = 4.11*percental2o3+6.484*percentmgo+7.646*percentcao-5.116*percentsio2-0.589*percentfe2o3
          st.write("The Heat of Reaction is:")
          st.write(HOR)
        elif (HORmanualorcalc == 1):
          HOR = st.number_input("Enter the Heat of Reaction:", 0.0000, 2000.0000, 400.0000, format = "%.4f")   
        
       
    
       with st.expander("KILN RADIATION"):
        st.write("Answer the following questions:")
        diameter = st.number_input('Kiln diameter (m)', 0.01, 100.0, 4.75)
        ambient_velocity = st.number_input('Ambient velocity', 0.00, 100.00, 3.50)
        temp_unit = st.selectbox('Unit', ('Celsius', 'Kelvin'))
        emissivity = st.slider('Emissivity', 0.0, 1.0, 0.77)
        interval = st.slider('Interval', 1, 10, 1)
      

#Code for KILN RADIATION table. Lines 1191-1196.      
       if input_excel_kilnsurftemps is not None:
          df = pd.read_excel(input_excel_kilnsurftemps, header = None)  
          kiln = Kiln(diameter, ambient_velocity, ambient_air_temperature, temp_unit, emissivity, interval, df)
          kiln.df['Radiation'] = kiln.radiation()/(clinker_capacity*1000) 
          kiln.df['Convection'] = kiln.convection()/(clinker_capacity*1000)
          kiln.df['TotalLoss'] = kiln.df['Radiation'] + kiln.df['Convection']
            
      

#OUTPUT HEAT KILN BALANCE Code. Lines 1201-1212        
       if (input_excel and input_excel_kilnsurftemps) is not None:
        KHBOutputDataSame = [
                            [ 'Heat of Reaction', np.nan, np.nan, np.nan, np.nan, np.nan, HOR],
                            [ 'Kiln Radiation', np.nan, np.nan, np.nan, np.nan, np.nan, df['TotalLoss'].sum(axis = 0)],
                            [ 'PH Radiation', np.nan, np.nan, np.nan, np.nan, np.nan, PH_radiation_values],
                            [ 'Cooler Radiation', np.nan, np.nan, np.nan, np.nan, np.nan, cooler_radiation_values],
                            [ 'TAD Radiation', np.nan, np.nan, np.nan, np.nan, np.nan, TAD_radiation_values],
                            [ 'Heat in Clinker', clinker_outlet_temperature, clinker_outlet_temperature-REFERENCE_TEMPERATURE_NTP, 0.186+0.000054*clinker_outlet_temperature, 1, np.nan, (0.186+0.000054*clinker_outlet_temperature)*(clinker_outlet_temperature-REFERENCE_TEMPERATURE_NTP)],
                            [ 'Heat of Evaporation of Moisture', np.nan, np.nan, np.nan, np.nan, np.nan, (kilnfeed_factor*(kiln_feed_moisture/100)*((100-kiln_feed_temperature)+540+0.45*(( (dfPH['Temp'].sum(axis = 0))/number_of_preheater_downcomer_ducts)-100))+( (fuel_qty_total*(100-coal_moisture))/(clinker_capacity*100)*(coal_moisture/100)*((100-fuel_temperature)+540+0.45*(( (dfPH['Temp'].sum(axis = 0))/number_of_preheater_downcomer_ducts)-100)))) ],
                            [ 'Incomplete Combustion', np.nan, np.nan, np.nan, np.nan, dfdensitydata.iat[0,2]*10000, ((dfdensitydata.iat[0,2]*10000*10**-6*67636)/22.414)*dfPH.iat[0,14] ],
                            ]
        dfKHBOutputSame = pd.DataFrame(KHBOutputDataSame, columns = ['HEAT', 'Temp', 'Delt T', 'Cp', 'Volume or Mass', 'Density', 'kcal/kg cl'])
        

#Code for PH Return Dust Dataframe and then for PH exit gas DataFrame. Lines 1216-1246.      
       if input_excel is not None:
        i = 1
        np.PHDustnamesarray = []
        np.PHExitGasnamesarray = []
        while(i <= number_of_preheater_downcomer_ducts):
             (np.PHDustnamesarray).append("Heat in PH. %d Dust" %i)
             (np.PHExitGasnamesarray).append("PH %d" %i)   
             i+=1
        dfPHDustnames = pd.DataFrame(np.PHDustnamesarray, columns = ['HEAT']) 
        dfPHExitGasnames = pd.DataFrame(np.PHExitGasnamesarray, columns = ['HEAT'])
        
        dfPHReturnQtyDust = pd.DataFrame(np.arrayforreturnqtydust, columns = ['Return Qty Dust'])
        
        KHBOutputDust = pd.DataFrame()
        KHBOutputDust['HEAT'] = dfPHDustnames
        KHBOutputDust['Temp'] = dfPH['Temp'] 
        KHBOutputDust['Delt T'] = dfPH['Temp']-REFERENCE_TEMPERATURE_NTP
        KHBOutputDust['Cp'] = 0.201+0.000101*dfPH['Temp']
        KHBOutputDust['Volume or Mass'] = (kilnfeed_factor*dfPHReturnQtyDust['Return Qty Dust'])/100
        KHBOutputDust['Density'] = np.nan
        KHBOutputDust['kcal/kg cl'] = KHBOutputDust['Volume or Mass']*KHBOutputDust['Cp']*KHBOutputDust['Delt T']
        
        
        KHBOutputExitGas = pd.DataFrame()
        KHBOutputExitGas['HEAT'] = dfPHExitGasnames
        KHBOutputExitGas['Temp'] = dfPH['Temp']
        KHBOutputExitGas['Delt T'] = dfPH['Temp']-REFERENCE_TEMPERATURE_NTP
        KHBOutputExitGas['Cp'] = 0.25+0.000023*dfPH['Temp']
        KHBOutputExitGas['Volume or Mass'] = dfPH['Nm3/kgcl']
        KHBOutputExitGas['Density'] = dfdensitydata['Density']
        KHBOutputExitGas['kcal/kg cl'] = KHBOutputExitGas['Volume or Mass']*KHBOutputExitGas['Cp']*KHBOutputExitGas['Delt T']*KHBOutputExitGas['Density']         
        

        
#Code for Mid Air DataFrame. Lines 1251-1269. 
       if input_excel is not None and (number_of_coolermidair > 0):
        i = 1;
        np.midairnamesarray = []
        while(i <= number_of_coolermidair):
             (np.midairnamesarray).append("Mid Air %d" %i)
             i+=1
        dfmidairnames = pd.DataFrame(np.midairnamesarray, columns = ['HEAT']) 
        
        KHBOutputCMA = pd.DataFrame()
        KHBOutputCMA['HEAT'] = dfmidairnames
        KHBOutputCMA['Temp'] = dfCMA['Temp']
        KHBOutputCMA['Delt T'] = dfCMA['Temp']-REFERENCE_TEMPERATURE_NTP
        KHBOutputCMA['Cp'] = 0.237+0.000023*KHBOutputCMA['Temp']
        KHBOutputCMA['Volume or Mass'] = dfCMA['Nm3/kgcl']
        KHBOutputCMA['Density'] = cooler_air_density
        KHBOutputCMA['kcal/kg cl'] = KHBOutputCMA['Volume or Mass']*KHBOutputCMA['Cp']*KHBOutputCMA['Delt T']*KHBOutputCMA['Density']
       elif input_excel is not None and (number_of_coolermidair == 0):
        KHBOutputCMA = pd.DataFrame()
        KHBOutputCMA = pd.DataFrame([['Mid Air', np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]], columns = ['HEAT', 'Temp', 'Delt T', 'Cp', 'Volume or Mass', 'Density', 'kcal/kg cl'])
        
       
       if input_excel is not None and (number_of_cooler_ventair_ducts > 0): 
        i = 1;
        np.coolerventnamesarray = []
        while(i <= number_of_cooler_ventair_ducts):
             (np.coolerventnamesarray).append("Cooler Vent %d" %i)
             i+=1
        dfcoolerventnames = pd.DataFrame(np.coolerventnamesarray, columns = ['HEAT'])     
        KHBOutputCVA = pd.DataFrame()
        KHBOutputCVA['HEAT'] = dfcoolerventnames
        
        if (backcalcordirectorindirect == 'Direct'):
          KHBOutputCVA['Temp'] = dfCVA['Temp']
        elif (backcalcordirectorindirect == 'Back Calculate'):
          KHBOutputCVA['Temp'] = CVAbackcaltemp
        else:
          KHBOutputCVA['Temp'] = dfESP['Temp']  
        KHBOutputCVA['Delt T'] = KHBOutputCVA['Temp']-REFERENCE_TEMPERATURE_NTP
        KHBOutputCVA['Cp'] = 0.237+(23*KHBOutputCVA['Temp']*10**-6)
        
        if (backcalcordirectorindirect == 'Direct'):
          KHBOutputCVA['Volume or Mass'] = dfCVA['Nm3/kgcl']  
        elif (backcalcordirectorindirect == 'Back Calculate'):
          KHBOutputCVA['Volume or Mass'] = Fbhai[0]/cooler_air_density
        else:
          KHBOutputCVA['Volume or Mass'] = dfESP['Nm3/kgcl']-(dfCMA['Nm3/kgcl'].sum(axis = 0))*0.97  
        
        KHBOutputCVA['Density'] = cooler_air_density
        KHBOutputCVA['kcal/kg cl'] = KHBOutputCVA['Volume or Mass']*KHBOutputCVA['Cp']*KHBOutputCVA['Delt T']*KHBOutputCVA['Density']
       elif input_excel is not None and (number_of_cooler_ventair_ducts == 0):
        KHBOutputCVA = pd.DataFrame([['Cooler Vent', np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]], columns = ['HEAT', 'Temp', 'Delt T', 'Cp', 'Volume or Mass', 'Density', 'kcal/kg cl'])
            

#Final OUTPUT for KILN HEAT BALANCE OUTPUT.        
       if (input_excel and input_excel_kilnsurftemps) is not None:
           dfKHBOutput = pd.concat([KHBOutputDust, dfKHBOutputSame, KHBOutputExitGas, KHBOutputCMA, KHBOutputCVA])


#Code for KILN HEAT BALANCE INPUT.
       if (input_excel and input_excel_kilnsurftemps) is not None:
        KHBInputDataSame = [ 
                           [ 'Heat in Kiln Feed', kiln_feed_temperature, kiln_feed_temperature-REFERENCE_TEMPERATURE_NTP, 0.205+0.0000101*(kiln_feed_temperature-REFERENCE_TEMPERATURE_NTP), (kilnfeed_factor)*(100-kiln_feed_moisture)/100, np.nan, ((kilnfeed_factor)*(100-kiln_feed_moisture)/100)*(0.205+0.0000101*(kiln_feed_temperature-REFERENCE_TEMPERATURE_NTP))*(kiln_feed_temperature-REFERENCE_TEMPERATURE_NTP) ],
                           [ 'Heat in Fuel', fuel_temperature, fuel_temperature-REFERENCE_TEMPERATURE_NTP, 0.262+0.00039*(fuel_temperature-REFERENCE_TEMPERATURE_NTP), (fuel_qty_total*(100-coal_moisture))/(clinker_capacity*100), np.nan, ((fuel_qty_total*(100-coal_moisture))/(clinker_capacity*100))*(0.262+0.00039*(fuel_temperature-REFERENCE_TEMPERATURE_NTP))*(fuel_temperature-REFERENCE_TEMPERATURE_NTP) ], 
                           [ 'Heat in Cooling Air', ambient_air_temperature, ambient_air_temperature-REFERENCE_TEMPERATURE_NTP, 0.237+(23*ambient_air_temperature*10**(-6)), dfCF['Nm3/kgcl'].sum(axis = 0), cooler_air_density, (dfCF['Nm3/kgcl'].sum(axis = 0)* cooler_air_density)*(0.237+(23*ambient_air_temperature*10**(-6)))*(ambient_air_temperature-REFERENCE_TEMPERATURE_NTP)*(cooler_air_density)                            ],
                           [ 'Heat from Primary Air', primary_air_temperature, primary_air_temperature-REFERENCE_TEMPERATURE_NTP, 0.237+0.0005*(primary_air_temperature-REFERENCE_TEMPERATURE_NTP), 0.005, cooler_air_density, 0.005*(0.237+0.0005*(primary_air_temperature-REFERENCE_TEMPERATURE_NTP))*(primary_air_temperature-REFERENCE_TEMPERATURE_NTP)*(cooler_air_density) ],
                           [ 'Sensible Heat from KF moisture', kiln_feed_temperature, kiln_feed_temperature-REFERENCE_TEMPERATURE_NTP, 1, (kilnfeed_factor*kiln_feed_moisture)/100, np.nan, ((kilnfeed_factor*kiln_feed_moisture)/100)*(kiln_feed_temperature-REFERENCE_TEMPERATURE_NTP)  ],
                           [ 'Sensible Heat from Coal moisture', coal_moisture_temperature, coal_moisture_temperature-REFERENCE_TEMPERATURE_NTP, 1, ((fuel_qty_total*(100-coal_moisture))/(clinker_capacity*100))*(coal_moisture/100), np.nan, ((fuel_qty_total*((100-coal_moisture))/(clinker_capacity*100))*(coal_moisture/100))*(coal_moisture_temperature-REFERENCE_TEMPERATURE_NTP)],
                           [ 'Heat from Transport Air', transport_air_temperature, transport_air_temperature-REFERENCE_TEMPERATURE_NTP, 0.237+0.0005*(transport_air_temperature-REFERENCE_TEMPERATURE_NTP), dfKB['Nm3/kgcl'].sum(axis = 0) + dfCB['Nm3/kgcl'].sum(axis = 0), cooler_air_density, (dfKB['Nm3/kgcl'].sum(axis = 0) + dfCB['Nm3/kgcl'].sum(axis = 0))*(0.237+0.0005*(transport_air_temperature-REFERENCE_TEMPERATURE_NTP))*(transport_air_temperature-REFERENCE_TEMPERATURE_NTP)*cooler_air_density ],
                           [ 'Heat through combustion of coal', np.nan, np.nan, np.nan, np.nan, np.nan, dfKHBOutput['kcal/kg cl'].sum(axis = 0)-( ((kilnfeed_factor)*(100-kiln_feed_moisture)/100)*(0.205+0.0000101*(kiln_feed_temperature-REFERENCE_TEMPERATURE_NTP))*(kiln_feed_temperature-REFERENCE_TEMPERATURE_NTP) + ((fuel_qty_total*(100-coal_moisture))/(clinker_capacity*100))*(0.262+0.00039*(fuel_temperature-REFERENCE_TEMPERATURE_NTP))*(fuel_temperature-REFERENCE_TEMPERATURE_NTP) + (dfCF['Nm3/kgcl'].sum(axis = 0)* cooler_air_density)*(0.237+(23*ambient_air_temperature*10**(-6)))*(ambient_air_temperature-REFERENCE_TEMPERATURE_NTP)*(cooler_air_density) + 0.005*(0.237+0.0005*(primary_air_temperature-REFERENCE_TEMPERATURE_NTP))*(primary_air_temperature-REFERENCE_TEMPERATURE_NTP)*(cooler_air_density) + ((kilnfeed_factor*kiln_feed_moisture)/100)*(kiln_feed_temperature-REFERENCE_TEMPERATURE_NTP) + ((fuel_qty_total*((100-coal_moisture))/(clinker_capacity*100))*(coal_moisture/100))*(coal_moisture_temperature-REFERENCE_TEMPERATURE_NTP) + (dfKB['Nm3/kgcl'].sum(axis = 0) + dfCB['Nm3/kgcl'].sum(axis = 0))*(0.237+0.0005*(transport_air_temperature-REFERENCE_TEMPERATURE_NTP))*(transport_air_temperature-REFERENCE_TEMPERATURE_NTP)*cooler_air_density ) ], 
                           ] 
        dfKHBInput = pd.DataFrame(KHBInputDataSame, columns = ['HEAT', 'Temp', 'Delt T', 'Cp', 'Volume or Mass', 'Density', 'kcal/kg cl'])        



        
#Code for the "AVERAGE VALUES" section. Lines 1327-1352.
if(options == 'Average Values'):
    st.title("MEAN AND ORIGINAL EXCEL SHEETS")
    
    if input_excel is not None:
       vieworiginalsheetyesorno = st.radio(
                        "Do you want to view the original sheet in the form of a table?",
                            ('No','Yes'))
       if vieworiginalsheetyesorno == 'Yes':
          st.write(dfinputexcel.style.background_gradient())

       vieworiginalsheetyesorno = st.radio(
                        "Do you want to view the mean values sheet in the form of a table?",
                            ('No','Yes'))
       if vieworiginalsheetyesorno == 'Yes':
          st.write(dfappendedoriginalandaverages.style.background_gradient())
            
       st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html = True)     
       st.write("You can download the mean values excel sheet from the link given below.")
       
       download_link = df_to_link(dfappendedoriginalandaverages, title='Average Values', filename='AVERAGEVALUES.csv')
       st.markdown(download_link, unsafe_allow_html=True) 
       
       url7 = "https://assets8.lottiefiles.com/private_files/lf30_b4njgmxj.json"
       res7_json = load_lottieurl(url7)
       st_lottie(res7_json) 
    st.write("***")
    

    
    
#Code for the "SPLIT DATAFRAMES" section. Lines 1358-1438.
elif(options == 'Split DataFrames'):   
    st.title("INDIVIDUAL DATASETS (Original)")
    
    if input_excel is not None:
       viewPHsheetyesornoOG = st.radio(
                        "Do you want to view the original Preheater Downcomer Ducts sheet in the form of a table?",
                            ('No','Yes'))
       if viewPHsheetyesornoOG == 'Yes':
          st.write(dfpreheatercolumns.style.background_gradient())
    
    
    if input_excel is not None and (number_of_tertiaryair_ducts > 0):   
       viewTADsheetyesornoOG = st.radio(
                        "Do you want to view the original Tertiary Air Ducts sheet in the form of a table?",
                            ('No','Yes'))
       if viewTADsheetyesornoOG == 'Yes':
          st.write(dfTADcolumns.style.background_gradient())
            
    
    if input_excel is not None and (number_of_coolermidair > 0):   
       viewCMAsheetyesornoOG = st.radio(
                        "Do you want to view the original Cooler Mid Air Ducts sheet in the form of a table?",
                            ('No','Yes'))
       if viewCMAsheetyesornoOG == 'Yes':
          st.write(dfCMAcolumns.style.background_gradient())   
        
    
    if input_excel is not None and (number_of_cooler_ventair_ducts > 0 and backcalcordirectorindirect == 'Direct'):    
       viewCVAsheetyesornoOG = st.radio(
                        "Do you want to view the original Cooler Vent Air Ducts sheet in the form of a table?",
                            ('No','Yes'))
       if viewCVAsheetyesornoOG == 'Yes':
          st.write(dfCVAcolumns.style.background_gradient())
        
    
    if input_excel is not None:   
       viewESPsheetyesornoOG = st.radio(
                        "Do you want to view the original ESP Stack sheet in the form of a table?",
                            ('No','Yes'))
       if viewESPsheetyesornoOG == 'Yes':
          st.write(dfESPcolumns.style.background_gradient())
            
    
    if input_excel is not None and (number_of_cooler_fans > 0):        
       viewCFsheetyesornoOG = st.radio(
                        "Do you want to view the original Cooler Fans sheet in the form of a table?",
                            ('No','Yes'))
       if viewCFsheetyesornoOG == 'Yes':
          st.write(dfcoolerfancolumns.style.background_gradient())
        
    
    if input_excel is not None:    
       viewkilnblowersheetyesornoOG = st.radio(
                        "Do you want to view the original Kiln Blowers sheet in the form of a table?",
                            ('No','Yes'))
       if viewkilnblowersheetyesornoOG == 'Yes':
          st.write(dfkilnblowerscolumns.style.background_gradient()) 
        
    
    if input_excel is not None and (number_of_calciner_blowers > 0):   
       viewcalcinerblowerssheetyesornoOG = st.radio(
                        "Do you want to view the original Calciner Blowers sheet in the form of a table?",
                            ('No','Yes'))
       if viewcalcinerblowerssheetyesornoOG == 'Yes':
          st.write(dfcalcinerblowerscolumns.style.background_gradient())
        
    
    if input_excel is not None:     
       viewPAsheetyesornoOG = st.radio(
                        "Do you want to view the original PA Fans sheet in the form of a table?",
                            ('No','Yes'))
       if viewPAsheetyesornoOG == 'Yes':
          st.write(dfPAfanscolumns.style.background_gradient()) 
  
       
    st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html = True)
    if input_excel is not None:    
      url8 = "https://assets2.lottiefiles.com/packages/lf20_9r4hjuko.json"
      res8_json = load_lottieurl(url8)
      st_lottie(res8_json)
    st.write("***")
        
        

        
#Code for the "FAN FLOWS" section. Lines 1444-1531.
elif(options == 'Fan Flows'):   
    st.title("FAN FLOWS")
    
    if input_excel is not None:
       dfPH.loc[len(dfPH)] = [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, 'Total Pre Heater Downcomer Duct Flow:', np.nan, np.nan, np.nan, np.nan, dfPH['Flow m3/hr'].sum(axis = 0), dfPH['Nm3/hr'].sum(axis = 0), dfPH['Nm3/kgcl'].sum(axis = 0), np.nan, dfPH['kW'].sum(axis = 0), np.nan] 
       viewPHsheetyesorno = st.radio(
                        "Do you want to view the Preheater Downcomer Ducts data in the form of a table?",
                            ('No','Yes'))
       if viewPHsheetyesorno == 'Yes':
          AgGrid(dfPH)
    
    
    if input_excel is not None and (number_of_tertiaryair_ducts > 0): 
       dfTAD.loc[len(dfTAD)] = [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, 'Total Tertiary Air Duct Flow:', np.nan, np.nan, np.nan, np.nan, dfTAD['Flow m3/hr'].sum(axis = 0), dfTAD['Nm3/hr'].sum(axis = 0), dfTAD['Nm3/kgcl'].sum(axis = 0)]  
       viewTADsheetyesorno = st.radio(
                        "Do you want to view the Tertiary Air Ducts data in the form of a table?",
                            ('No','Yes'))
       if viewTADsheetyesorno == 'Yes':
          AgGrid(dfTAD)
            
    
    if input_excel is not None and (number_of_coolermidair > 0):
       dfCMA.loc[len(dfCMA)] = [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, 'Total Cooler Mid Air Duct Flow:', np.nan, np.nan, np.nan, np.nan, dfCMA['Flow m3/hr'].sum(axis = 0), dfCMA['Nm3/hr'].sum(axis = 0), dfCMA['Nm3/kgcl'].sum(axis = 0)] 
       viewCMAsheetyesorno = st.radio(
                        "Do you want to view the Cooler Mid Air Ducts data in the form of a table?",
                            ('No','Yes'))
       if viewCMAsheetyesorno == 'Yes':
          AgGrid(dfCMA)   
        
    
    if input_excel is not None:  
       viewESPsheetyesorno = st.radio(
                        "Do you want to view the ESP Stack data in the form of a table?",
                            ('No','Yes'))
       if viewESPsheetyesorno == 'Yes':
          AgGrid(dfESP)
            
    
    if input_excel is not None:           
       if (number_of_cooler_ventair_ducts > 0 and backcalcordirectorindirect == 'Direct'):
         viewCVAsheetyesorno = st.radio(
                          "Do you want to view the Cooler Vent Air Ducts data in the form of a table?",
                            ('No','Yes'))
         if viewCVAsheetyesorno == 'Yes':
            AgGrid(dfCVA)
       
       download_link = df_to_link(dfESP, title='ESP Stack Duct Sheet', filename='ESP Fan Flow Data.csv')
       st.markdown(download_link, unsafe_allow_html=True)
                  
    
    if input_excel is not None and (number_of_tertiaryair_ducts > 0):
       download_link = df_to_link(dfTAD, title='TAD Sheet', filename='TAD Fan Flow Data.csv')
       st.markdown(download_link, unsafe_allow_html=True) 
    
    
    if input_excel is not None and (number_of_coolermidair > 0):
       download_link = df_to_link(dfCMA, title='CMA Sheet', filename='CMA Data.csv')
       st.markdown(download_link, unsafe_allow_html=True)
        
    
    if input_excel is not None:    
       download_link = df_to_link(dfPH, title='PH Downcomer Duct Sheet', filename='PH Fan Flow Data.csv')
       st.markdown(download_link, unsafe_allow_html=True) 
        
    
    if input_excel is not None and (number_of_cooler_ventair_ducts > 0 and backcalcordirectorindirect == 'Direct'): 
        download_link = df_to_link(dfCVA, title='Cooler Vent Air Duct Sheet', filename='CVA Fan Flow Data.csv')
        st.markdown(download_link, unsafe_allow_html=True)  
        
    
    if input_excel is not None and (number_of_cooler_ventair_ducts > 0 and backcalcordirectorindirect == 'Direct'): 
        download_link = df_to_link(dfnewCVAaswell, title='Fan Flows Data (with CVA)', filename = 'B.csv')
        st.markdown(download_link, unsafe_allow_html=True)
    
    
    if input_excel is not None and (number_of_cooler_ventair_ducts == 0 or (backcalcordirectorindirect == 'Back Calculate' and number_of_cooler_ventair_ducts > 0) or (backcalcordirectorindirect == 'Indirect (ESP Stack Flow - MidAir Flow)' and number_of_cooler_ventair_ducts > 0) ): 
        download_link = df_to_link(dfnew, title='Fan Flows Data', filename='A.csv')
        st.markdown(download_link, unsafe_allow_html=True)
        
        
    st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html = True)
    
    if input_excel is not None:    
       st.write("The **Fan Flows Data** sheet displays the data in the given order: ESP, TAD's, CMA's, PH Downcomer Ducts, then CVA (row-wise).") 
       url9 = "https://assets4.lottiefiles.com/packages/lf20_nxgyehwv.json"
       res9_json = load_lottieurl(url9)
       st_lottie(res9_json)
    st.write("***") 
        


        
#Code for the "COOLER FANS" section. Lines 1537-1556.
elif(options == 'Cooler Fans' and number_of_cooler_fans > 0):   
    st.title("COOLER FANS")
    
    if input_excel is not None:
       dfCF.loc[len(dfCF)] = [np.nan, np.nan, np.nan, 'Total Cooler Flow:', np.nan, np.nan, dfCF['m3/hr'].sum(axis = 0), np.nan, dfCF['Nm3/hr'].sum(axis = 0), np.nan, dfCF['Nm3/kgcl'].sum(axis = 0), np.nan, np.nan, dfCF['Power'].sum(axis = 0), np.nan]
       viewCFsheetyesorno = st.radio(
                        "Do you want to view the Cooler Fans data in the form of a table?",
                            ('No','Yes'))
       if viewCFsheetyesorno == 'Yes': 
         AgGrid(dfCF) 
       
       download_link = df_to_link(dfCF, title='Cooler Fans Data', filename='CoolerFans.csv')
       st.markdown(download_link, unsafe_allow_html=True) 
       
    
       st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html = True)      
       url10 = "https://assets10.lottiefiles.com/temp/lf20_TtN4ps.json"
       res10_json = load_lottieurl(url10)
       st_lottie(res10_json)
    st.write("***")
    


    
#Code for "BLOWERS/PA FANS" section. Lines 1562-1625 as of now.
elif(options == "Blowers/PA Fans"):
    st.title("BLOWERS/PA FANS")
    st.subheader("Kiln blower, Calciner Blower, PA Fans")
    
    if input_excel is not None:
        dfKB.loc[len(dfKB)] = [np.nan, np.nan, 'Total Kiln Blower Flow:', np.nan, np.nan, np.nan, dfKB['Volumetric Flow Rate m3/hr'].sum(axis = 0), np.nan, dfKB['Nm3/hr'].sum(axis = 0), np.nan, dfKB['Nm3/kgcl'].sum(axis = 0)] 
        viewKBsheetyesorno = st.radio(
                          "Do you want to view the Kiln Blowers sheet in the form of a table?",
                            ('No','Yes'))
        if viewKBsheetyesorno == 'Yes':
          AgGrid(dfKB)
          
        
    if input_excel is not None and (number_of_calciner_blowers > 0):
        dfCB.loc[len(dfCB)] = [np.nan, np.nan, 'Total Calciner Blower Flow:', np.nan, np.nan, np.nan, dfCB['Volumetric Flow Rate m3/hr'].sum(axis = 0), np.nan, dfCB['Nm3/hr'].sum(axis = 0), np.nan, dfCB['Nm3/kgcl'].sum(axis = 0)] 
        viewCBsheetyesorno = st.radio(
                          "Do you want to view the Calciner Blowers sheet in the form of a table?",
                            ('No','Yes'))
        if viewCBsheetyesorno == 'Yes':
          AgGrid(dfCB)  
        
    
    if input_excel is not None:
        dfPAF.loc[len(dfPAF)] = [np.nan, np.nan, 'Total PA Fans Flow:', np.nan, np.nan, np.nan, dfPAF['Volumetric Flow Rate m3/hr'].sum(axis = 0), np.nan, dfPAF['Nm3/hr'].sum(axis = 0), np.nan, dfPAF['Nm3/kgcl'].sum(axis = 0)] 
        viewPAFsheetyesorno = st.radio(
                          "Do you want to view the PA Fans sheet in the form of a table?",
                            ('No','Yes'))
        if viewPAFsheetyesorno == 'Yes':
          AgGrid(dfPAF)    
    
    
    if input_excel is not None: 
      dftreya.loc[len(dftreya)] = [np.nan, np.nan, 'Total Flow:', np.nan, np.nan, np.nan, dftreya['Volumetric Flow Rate m3/hr'].sum(axis = 0), np.nan, dftreya['Nm3/hr'].sum(axis = 0), np.nan, dftreya['Nm3/kgcl'].sum(axis = 0)]   
      viewtreyasheetyesorno = st.radio(
                          "Do you want to view the PA Fans/Blowers sheet in the form of a table?",
                            ('No','Yes'))
      if viewtreyasheetyesorno == 'Yes':
        AgGrid(dftreya)  
        
        
    if input_excel is not None:
      download_link = df_to_link(dfKB, title='Kiln Blower Sheet', filename='KB.csv')
      st.markdown(download_link, unsafe_allow_html=True) 
    
    
    if input_excel is not None and (number_of_calciner_blowers > 0):
      download_link = df_to_link(dfCB, title='Calciner Blower Sheet', filename='CB.csv')
      st.markdown(download_link, unsafe_allow_html=True)  
        
    
    if input_excel is not None:
      download_link = df_to_link(dfPAF, title='PA Fans Sheet', filename='PAF.csv')
      st.markdown(download_link, unsafe_allow_html=True) 
      
      st.write("You can download the Treya sheet from the link given below.")         
    
      download_link = df_to_link(dftreya, title='Three Fans Data', filename='3.csv')
      st.markdown(download_link, unsafe_allow_html=True)
        
      st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html = True)
      url11 = "https://assets1.lottiefiles.com/private_files/lf30_b5nyw28b.json"
      res11_json = load_lottieurl(url11)
      st_lottie(res11_json)
    st.write("***")
    
    

    
#Code for "COOLER HEAT BALANCE" section. Lines 1631-1678.
elif(options == "Cooler Heat Balance"):
    st.title("COOLER HEAT BALANCE")
            
    if input_excel is not None: 
      dfInputHeatBalance.loc[len(dfInputHeatBalance)] = ['Total Heat Input', dfInputHeatBalance['Flow (kg/kg clinker)'].sum(axis = 0), np.nan, np.nan, dfInputHeatBalance['Heat (kcal/kg clinker)'].sum(axis = 0)]  
      viewInputHBsheetyesorno = st.radio(
                        "Do you want to view the Input Heat Balance sheet in the form of a table?",
                            ('No','Yes'))
      if viewInputHBsheetyesorno == 'Yes':
        AgGrid(dfInputHeatBalance) 
        
        
      dfOutputHeatBalance.loc[len(dfOutputHeatBalance)] = ['Total Heat Output', dfOutputHeatBalance['Flow (kg/kg clinker)'].sum(axis = 0), np.nan, np.nan, dfOutputHeatBalance['Heat (kcal/kg clinker)'].sum(axis = 0)]
      dfOutputHeatBalance.loc[len(dfOutputHeatBalance)] = [np.nan, np.nan, np.nan, np.nan, np.nan]
      viewOutputHBsheetyesorno = st.radio(
                        "Do you want to view the Output Heat Balance sheet in the form of a table?",
                            ('No','Yes'))
      if viewOutputHBsheetyesorno == 'Yes':
        AgGrid(dfOutputHeatBalance) 
        
      
      dfCoolerHeatBalance = pd.concat([dfOutputHeatBalance, dfInputHeatBalance], axis = 0)  
      #st.write(dfCoolerHeatBalance)  
    
    
      viewCoolerHBsheetyesorno = st.radio(
                        "Do you want to view the Cooler Heat Balance sheet in the form of a table?",
                            ('No','Yes'))
      if viewCoolerHBsheetyesorno == 'Yes':
        AgGrid(dfCoolerHeatBalance)   
              
      
      download_link = df_to_link(dfInputHeatBalance, title='Input HB Sheet', filename='InputHB.csv')
      st.markdown(download_link, unsafe_allow_html=True) 
        
      download_link = df_to_link(dfOutputHeatBalance, title='Output HB Sheet', filename='OutputHB.csv')
      st.markdown(download_link, unsafe_allow_html=True) 
      
      st.write("You can download the Cooler Heat Balance Sheet from the link given below:")
      download_link = df_to_link(dfCoolerHeatBalance, title='Cooler HB Sheet', filename='CoolerHB.csv')
      st.markdown(download_link, unsafe_allow_html=True)  
        
    st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html = True)    
    if input_excel is not None:
      url12 = "https://assets6.lottiefiles.com/packages/lf20_6di23gcc.json"
      res12_json = load_lottieurl(url12)
      st_lottie(res12_json)
    st.write("***")
    



#Code for "KILN RADIATION" section. Lines 1684-1705.    
elif(options == "Kiln Radiation"):
    st.title("KILN RADIATION")
    if input_excel_kilnsurftemps is not None:
      st.set_option('deprecation.showPyplotGlobalUse', False)   #Think about a workaround for this.  
      st.write(kiln.df.style.background_gradient(cmap='hot_r'))
    
      download_link = df_to_link(df, title='Kiln Radiation Sheet', filename='KilnRadiationCalculations.csv')
      st.markdown(download_link, unsafe_allow_html=True) 
    
      fig, ax = plt.subplots(figsize=(15,5))
      sns.scatterplot(x=df.Length, y=df.Length, data=df, ci=None, palette="muted", ax=ax)
      ax.set_title('Colored kiln', fontweight = "bold", fontsize=16, pad=20),
      ax.set_ylabel('Length')
      st.pyplot(fig)  
        
      fig, ax = plt.subplots(figsize=(15,5))
      sns.scatterplot(x=df.Length, y=df.Temp, data=df, ci=None, palette="muted", ax=ax)
      ax.set_title('Temperature along kiln length', fontweight = "bold", fontsize=16, pad=20),
      ax.set_ylabel('Temp')
      st.pyplot(fig)
    
      fig, ax = plt.subplots(figsize=(15,5))
      sns.scatterplot(x=df.Length, y=df.TotalLoss, data=df, ci=None, palette="muted", ax=ax)
      ax.set_title('Temperature along kiln length', fontweight = "bold", fontsize=16, pad=20),
      ax.set_ylabel('Temp')
      st.pyplot(fig)
        
      
      df.plot.scatter('Length', 'Length', c = 'Temp', cmap='hot_r', title='Colored kiln') 
      st.pyplot()
      df.plot.scatter('Length', 'Temp', c = 'Temp', cmap='hot_r', colorbar=True, title='Temperature along kiln length')
      st.pyplot()
      df.plot.scatter('Length', 'TotalLoss', c = 'TotalLoss', cmap='hot_r', colorbar=True, title='Heat loss along kiln length')
      st.pyplot()
    
    if input_excel is not None:
    
      url13 = "https://assets6.lottiefiles.com/private_files/lf30_vcuxubyd.json"
      res13_json = load_lottieurl(url13)
      st_lottie(res13_json)
    st.write("***")
    
    


#Code for "KILN HEAT BALANCE" section. Lines 1711-1759 as of now. 
elif(options == "Kiln Heat Balance"):
    st.title("KILN HEAT BALANCE")
    if input_excel is not None and input_excel_kilnsurftemps is not None:
      dfKHBInput.loc[len(dfKHBInput)] = ['Total Heat In', np.nan, np.nan, np.nan, np.nan, np.nan, dfKHBInput['kcal/kg cl'].sum(axis = 0)]
      dfKHBInput.loc[len(dfKHBInput)] = [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]
      viewInputKHBsheetyesorno = st.radio(
                        "Do you want to view the Input Kiln Heat Balance sheet in the form of a table?",
                            ('No','Yes'))
      if viewInputKHBsheetyesorno == 'Yes':
        AgGrid(dfKHBInput) 
        
      
      download_link = df_to_link(dfKHBInput, title='Input Kiln HB Sheet', filename='InputKHB.csv')
      st.markdown(download_link, unsafe_allow_html=True)   
        
    
    if (input_excel and input_excel_kilnsurftemps) is not None: 
      dfKHBOutput.loc[len(dfKHBOutput)] = ['Total Heat Out', np.nan, np.nan, np.nan, np.nan, np.nan, dfKHBOutput['kcal/kg cl'].sum(axis = 0)]       
      viewOutputKHBsheetyesorno = st.radio(
                        "Do you want to view the Output Kiln Heat Balance sheet in the form of a table?",
                            ('No','Yes'))
      if viewOutputKHBsheetyesorno == 'Yes':
        AgGrid(dfKHBOutput)  
        
        
      download_link = df_to_link(dfKHBOutput, title='Output Kiln HB Sheet', filename='OutputKHB.csv')
      st.markdown(download_link, unsafe_allow_html=True)  
        
      dfKilnHB = pd.concat([dfKHBInput, dfKHBOutput], axis = 0)
      #st.write(dfKilnHB)
        
      
      viewKHBsheetyesorno = st.radio(
                        "Do you want to view the Kiln Heat Balance sheet in the form of a table?",
                            ('No','Yes'))
      if viewKHBsheetyesorno == 'Yes':
        AgGrid(dfKilnHB)  
        
        
      st.write("You can download the Kiln Heat Balance Sheet from the link given below:")  
      download_link = df_to_link(dfKilnHB, title='Kiln HB Sheet', filename='KHB.csv')
      st.markdown(download_link, unsafe_allow_html=True)   
   
    st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html = True)
    if input_excel and input_excel_kilnsurftemps is not None:
      url14 = "https://assets3.lottiefiles.com/packages/lf20_yppp9lxb.json"
      res14_json = load_lottieurl(url14)
      st_lottie(res14_json)
    st.write("***")
    


#https://www.analyticsvidhya.com/blog/2021/06/style-your-pandas-dataframe-and-make-it-stunning/    
#https://discuss.streamlit.io/t/pyplotglobalusewarning/6578/5          PLot ERROR, Depreciation. Help on this link.     
#No code for dashboard reset. Just a simple hack ;).
