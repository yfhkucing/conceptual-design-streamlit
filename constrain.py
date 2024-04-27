import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from ADRpy import unitconversions as co
from ADRpy import constraintanalysis as ca
from ADRpy import airworthiness as aw

from ADRpy import atmospheres as at
# from streamlit_gsheets import GSheetsConnection
import pandas as pd
import math

st.write('Constrain analysis')

#conn = st.connection("gsheets", type=GSheetsConnection)

with st.container():

    col1,col2,col3,col4,col5,col6 = st.columns(6)

    with col1:
        st.write("Takeoff")
        Tow = st.number_input("Take off weight (kg)",key= 'tow',value= 1900.0)
        Runwayelev= st.number_input("Runway elevation (m)")
        groundrun= st.number_input("Ground run (m)",step=0.1,key='groundrun',value= 200.0)
    with col2:
        st.write("Turn")
        load_factor= st.number_input("Load factor",step=0.1,key='load factor',value=1.0)
        turn_alt= st.number_input("Turning alt (m)",step=0.1,key='turnalt',value= 2000.0)
        turnspeed= st.number_input("Turning speed (m/s)",step=0.1,key='turnspeed',value=45.0)*1.94384
    with col3:
        st.write("Climb")
        climb_alt= st.number_input("Climb altitude (m)",step=0.1,key='climbalt')
        climbrate=  st.number_input("climb rate (m/s)",step=0.1,key='climbrate',value=4.0)*196.85
        #climb_sp= (climbrate/196.85)/math.sin(math.radians(lock6[4]))
        climbspeed= st.number_input("Climb speed (m/s)",step=0.1,key='climb speed',value= 45.0)*1.94384
    with col4:
        st.write('Cruise')
        cruisealt= st.number_input("Cruise altitude (m)",step=0.1,key='cruisealt',value= 2500.0)
        cruisespeed= st.number_input("Cruise speed (m/s)",step=0.1,key='cruisespeed',value=50.0)*1.94384
        cruisethrust= st.number_input("Thrust percentage",step=0.1,key='cruisethrust',value= 1.0)
    with col5:
        st.write('service')
        servceil= st.number_input("Service ceiling (m)",step=0.1,key='servceil',value=3000.0)
        est_roc= st.number_input("best RoC (m/s)",step=0.1,key='secclimb',value= 5.0)*1.94384
        stall= st.number_input("stall speed (m/s)",step=0.1,key='stall',value= 30.0)*1.94384
    with col6:
        st.write('flight envelope')
        divespd= st.number_input("dive speed (m/s)",key='divespeed',value= cruisespeed/1.94384*1.2)*1.94384
        wfrac= st.number_input("weight fraction",key='wfrac',value=1)
        category= st.selectbox("category",['util','comm','aero'])

    designbrief = {'rwyelevation_m':Runwayelev, 'groundrun_m':groundrun, # <- Take-off requirements
                    'stloadfactor': load_factor, 'turnalt_m': turn_alt, 'turnspeed_ktas': turnspeed, # <- Turn requirements
                    'climbalt_m': climb_alt, 'climbspeed_kias': climbspeed, 'climbrate_fpm': climbrate, # <- Climb requirements
                    'cruisealt_m': cruisealt, 'cruisespeed_ktas': cruisespeed, 'cruisethrustfact': cruisethrust, # <- Cruise requirements
                    'servceil_m': servceil, 'secclimbspd_kias': est_roc, # <- Service ceiling requirements
                    'vstallclean_kcas': stall} # <- Required clean stall speed
    
    csbrief={'cruisespeed_keas': cruisespeed, 'divespeed_keas': divespd,
         'altitude_m': cruisealt,
         'weightfraction': 1, 'certcat': category}

    TOW_kg = Tow

with st.container():
    col1,col2,col3,col4 = st.columns(4)

    with col1:
        st.write("Design definition")
        aspect_ratio= st.number_input('Aspect ratio',step=0.1,key='aspect_ratio',value=8.0)
        sweep_LE= st.number_input('Leading edge sweep (deg)',step=0.1,key='sweep_LE',value=0.0)
        offset_temp= st.number_input('offset ISA temperature (celcius)',key= "offset temp")
        #st.write("weight (N) = " +str(round(co.kg2n(TOW_kg),2)))

    with col2:
        st.write("Coefficients")
        Cdto= st.number_input('CD takeoff',step=0.0001,key='cdto',value=0.04)
        Clto= st.number_input('CL takeoff',step=0.0001,key='clto',value= 1.5)
        Clmaxto= st.number_input('CL max takeoff',step=0.0001,key='clmaxto')

    with col3:
        st.write("Coefficients")
        ClmaxcleanTO= st.number_input('CL max clean takeoff',step=0.0001,key='clmaxcleanto',value= 1.5)
        CdmincleanTO= st.number_input('CD min clean takeoff',step=0.0001,key='cdmaxcleanto',value= 0.01)
        wheel_friction= st.number_input('Wheel friction coefficient',step=0.0001,key='wheelf',value= 0.03)

    with col4:
        st.write("Coefficients")
        clminclean= st.number_input('CL min clean',step=0.0001,key='clminclean',value= -1.0)
        clmaxclean= st.number_input('CL max clean',step=0.0001,key='clmaxclean',value= 1.45)
        clslope= st.number_input('CL alpha (per radian)',step=0.0001,key='clslope',value= 1.0)

with st.container():
    st.write('wing area and power')
    col1,col2=st.columns(2)
    with col1:
        wing_s2= st.number_input('wing area',key='wing_s2',value= 20.0)
    with col2:
        power_bhp= st.number_input('power bhp',key= 'power bhp')


servceil_fraction = st.slider('service ceiling weight fraction',key='servceil frac',value=0.85)
designdefinition = {'aspectratio':aspect_ratio, 'sweep_le_deg':sweep_LE, 'sweep_mt_deg':0, 
                        'wingarea_m2':wing_s2,
                        'weightfractions': {'turn': 1.0, 'climb': 1.0, 'cruise': 0.99, 'servceil': servceil_fraction},
                        'weight_n': co.kg2n(TOW_kg)}

designpropulsion = "piston"
    
designperformance = {'CDTO': Cdto, 'CLTO': Clto, 'CLmaxTO': Clmaxto, 'CLmaxclean': ClmaxcleanTO, 'mu_R': wheel_friction,
                        'CDminclean': CdmincleanTO,'CLmaxclean': clmaxclean, 'CLminclean': clminclean, 'CLslope': clslope,
                        'etaprop': {'take-off': 0.75, 'climb': 0.8, 'cruise': 0.85, 'turn': 0.85, 'servceil': 0.8}}
    
designatm =at.Atmosphere(offset_temp)

designbrief_array =np.array([Tow, Runwayelev, groundrun, load_factor, turn_alt, turnspeed, 
                    climb_alt, climbspeed, climbrate, cruisealt, cruisespeed, 
                    cruisethrust, servceil, est_roc, stall])

designdefinition_array = np.array([ aspect_ratio, sweep_LE, 0, co.kg2n(TOW_kg)])
    
designperformance_array = np.array([Cdto, Clto, Clmaxto, ClmaxcleanTO, wheel_friction, CdmincleanTO,
                          clmaxclean,clminclean,clslope])

with st.container():
    atmospheric_data= {
            'parameter':
            [
                'air density (kg/m^3)','air pressure (pa)','air temperature (c)',
            ],
            'value':
            [
                designatm.airdens_kgpm3(),designatm.airpress_pa(),designatm.airtemp_c()
            ]
        }
    st.dataframe(data=atmospheric_data)

    
with st.container():
    st.write('constrain diagram')
    concept = ca.AircraftConcept(designbrief, designdefinition, designperformance, 
                                        designatm, designpropulsion)
    wslist_pa = np.arange(100, 1400, 2.5)
    preq = concept.powerrequired(wslist_pa, TOW_kg)
    Smin_m2 = concept.smincleanstall_m2(TOW_kg)
    wingarea_m2 = co.kg2n(TOW_kg) / wslist_pa # x axis
    plt.rcParams["figure.figsize"] = [8,6]
    plt.rcParams['figure.dpi'] = 180

    plt.plot(wingarea_m2, preq['take-off'],  label = 'Take-off')
    plt.plot(wingarea_m2, preq['turn'], label = 'Turn')
    plt.plot(wingarea_m2, preq['climb'], label = 'Climb')
    plt.plot(wingarea_m2, preq['cruise'], label = 'Cruise')
    plt.plot(wingarea_m2, preq['servceil'], label = 'Service ceiling')

    combplot = plt.plot(wingarea_m2, preq['combined'], label = 'Combined')

    plt.setp(combplot, linewidth=4)

    stall_label = 'Clean stall at ' + str(round(designbrief['vstallclean_kcas'],2)) + 'KCAS'

    plt.plot([Smin_m2, Smin_m2], [0, 1500], label = stall_label)

    legend = plt.legend(loc='lower right')
    plt.scatter(wing_s2,power_bhp)
    plt.ylabel("Power required (HP)")
    plt.xlabel("S (m$^2$)")
    plt.title("Minimum SL power required (MTOW = " + str(round(TOW_kg)) + "kg)")
    plt.xlim(min(wingarea_m2), max(wingarea_m2))
    # plt.ylim(0, max(preq['combined']) * 1.1)
    plt.grid(True)

    st.pyplot(plt)

with st.container():
    st.write('V-N diagram')
    concept2 = aw.CertificationSpecifications(designbrief, designdefinition, designperformance, 
                                        designatm, designpropulsion, csbrief)
    points = concept2.flightenvelope(textsize=15, figsize_in=[15, 10])
    st.pyplot(points)


