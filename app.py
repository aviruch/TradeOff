from flask import Flask, render_template, url_for, request, redirect
app = Flask(__name__)
import pandas as pd
import math

@app.route("/")
def main():
    return render_template('tradeoff.html')

@app.route('/tradeoff',methods = ['POST', 'GET'])
def tradeoff():
   if request.method == 'POST':
               
      #surface_area = float(request.form['surface_area'])

      zone_orientation = request.form['zone_orientation']
      position = request.form['position']
      wall_area = float(request.form['wall_area'])
      Uow = float(request.form['Uwall'])
      if Uow > 0.4:
          U0w = 0.4  #Btu/h.sft.F
      elif Uow < 0.05:
          Uow = 0.05 #Btu/h.sft.F

      vf_area = float(request.form['vf_area'])
      length = float(request.form['length'])
      breadth = float(request.form['breadth'])
      overhang_depth = float(request.form['overhang_depth'])
      overhang_height = float(request.form['overhang_height'])
      orientation = request.form['orientation']
      Uvf = float(request.form['Uvf'])
      SHGC = float(request.form['SHGC'])
      HC = float(request.form['HC'])
      if HC > 20:
            HC = 20 #Btu/sft.F



      material = request.form['material']
      sky_area = float(request.form['sky_area'])
      sky_depth = float(request.form['sky_depth'])
      sky_length = float(request.form['sky_length'])
      sky_width = float(request.form['sky_width'])
      Usky = float(request.form['Usky'])
      SHGC_sky = float(request.form['SHGC_sky'])

      floor_area = float(request.form['floor_area'])
      floor = request.form['floor']
      Ufloor = float(request.form['Ufloor'])
     
      roof_area = float(request.form['roof_area'])
      Uroof = float(request.form['Uroof'])

      FAF = float(request.form['FAF'])
      CDD50 = float(request.form['CDD50'])
      CDD65 = float(request.form['CDD65'])
      HDD50  = float(request.form['HDD50'])
      HDD65  = float(request.form['HDD65'])
      CDH80  = float(request.form['CDH80'])
     

      #-----------------------Lighting_zone------------------------------------------------------------------------
        #-----------------------VF-------------------------------------------------------
          #---------------------vf_VA-----------------------------------------
      vf_VLT = 1.00
      PF = overhang_depth/(length+overhang_height)

      if orientation == "north" :
      	PCC1 = -0.5
       	PCC2 = 0.22
      else : 
      	PCC1 = -0.97
      	PCC2 = 0.38

      vf_VA = vf_area*vf_VLT*(1+(PCC1*PF)+(PCC2*PF**2))

          #------------------------sky_VA-------------------------------------
      if material == "glass" :
      	sky_VLT = 1.27
      elif material == "plastic" : 
      	sky_VLT = 1.2
      if sky_area == 0:
            sky_VA = 0
      else :
            sky_VA = sky_area*sky_VLT*10**(-0.25*5*sky_depth*(sky_width+sky_length)/(sky_width+sky_length))
      
          
      if vf_VA > sky_VA :
      	VA = vf_VA
      	fen_area = vf_area
      	area = wall_area
      else : 
      	VA = sky_VA
      	fen_area = sky_area
      	area = roof_area
      P1 = 0.737
      P2 = -3.17*10**(-4)
      P3 = -24.71
      P4 = 0.234
      DI = 50  #fc

      Kd_zone = P1 + (P2*DI*VA/fen_area)*(1-math.exp((P3+P4*DI)*VA/area))
      
      LPD = 1.2  # W/ft**2
      LPD_adj = LPD*(1-Kd_zone)

      Lighting_zone = LPD_adj*floor_area*216

      #---------------------HVAC_surface---------------------------------------------------------------------------------------
       #--------------------------wall-----------------------------------------------------------------------------------
      data_cool=pd.read_csv('static/cooling_delta.csv', index_col=0)
      data_hot = pd.read_csv('static/heating_delta.csv', index_col=0)
      cool_coeff = pd.read_csv('static/cooling_coeff.csv', index_col=0)
      hot_coeff = pd.read_csv('static/heating_coeff.csv', index_col=0)

      for i in range(1,len(data_cool)+1):
          c = "C" + str(i) 
          globals()["C%i" % i] = data_cool.loc[c,position]

      opaque_area = wall_area - vf_area
      EPD = 0.75 #W/sft
      G = EPD + LPD_adj
      SAc = vf_area*1.163*SHGC*(1-PCC1*PF + PCC2*PF**2)
      EAc = SAc/wall_area
      UO = (opaque_area*Uow + vf_area*Uvf)/(wall_area)
      VS = 500
      DR = 17
      
      B = (DR/10)+1
      Ac = (CDH80/10000)+2
      CP1 = C5
      CP2 = (C15/B**3) + (C16/((Ac**2)*(B**2))) + C17
      CP3 = (C1/Ac**3) + (C2*B**3)
      CP4 = (C12/((Ac**2)*(B**2))) + (C13/B**3) + C14
      CP5 = C18
      CP6 = (C6*math.sqrt(B)*math.log(Ac)) + C7
      CP7 = (C19/((Ac**2)*(B**2))) + C20/(Ac*B) + (C21*Ac**2)/(math.sqrt(B)+C22)
      CP8 = (C8/((Ac**2)*(B**2))) + C9/(Ac*B) + (C21*Ac**2)/(math.sqrt(B)+C11)

      SCMC = 1.43*opaque_area*(1-math.exp(-CP1*(HC-1)))*(CP2+CP3*Uow-(CP4/(1+(CP5 + CP6*Uow)*math.exp(-(CP7+CP8*Uow**2)*(HC-1)))))
      #print("SCMC is", SCMC)

      for i in range(1,5):
            c = "CU" + str(i) 
            globals()["CU%i" % i] = cool_coeff.loc[c,zone_orientation]

      for i in range(1,5):
            c = "CUO" + str(i) 
            globals()["CUO%i" % i] = cool_coeff.loc[c,zone_orientation]

      for i in range(1,6):
            c = "CXUO" + str(i) 
            globals()["CXUO%i" % i] = cool_coeff.loc[c,zone_orientation]

      for i in range(1,9):
            c = "CM" + str(i) 
            globals()["CM%i" % i] = cool_coeff.loc[c,zone_orientation]

      for i in range(1,10):
            c = "CG" + str(i) 
            globals()["CG%i" % i] = cool_coeff.loc[c,zone_orientation]

      for i in range(1,8):
            c = "CS" + str(i) 
            globals()["CS%i" % i] = cool_coeff.loc[c,zone_orientation]

      for i in range(1,14):
            c = "CC" + str(i) 
            globals()["CC%i" % i] = cool_coeff.loc[c,zone_orientation]

      CLU= opaque_area*Uow*(CU1*CDH80 + CU2*CDH80**2 + CU3*(VS*CDH80)**2 + CU4*DR)
      print("CLU is", CLU)

      CLUO = wall_area*UO*(CUO1*EAc*VS*CDD50 + CUO2*G + CUO3*G**2*EAc**2*VS*CDD50 + CUO4*G**2*EAc**2*VS*CDD65)
      print("CLUO is", CLUO)

      CLXUO = wall_area/UO*(CXUO1*EAc*VS*CDD50 + CXUO2*EAc*(VS*CDD50)**2 + CXUO3*G*CDD50 + CXUO4*VS*CDD50*(G*EAc)**2 + CXUO5*G**2*CDD65)
      print("CLXUO is", CLXUO)

      CLM = opaque_area*SCMC*(CM1 + CM2*EAc*VS*CDD50 + CM3*EAc*VS*CDD65 + CM4*EAc**2*VS*CDD50 + CM5*G**2*CDD65 + CM6*G*CDD50 + 
                CM7*G*CDD65 + CM8*G*EAc*VS*CDD50)
      print("CLM is", CLM)

      CLG = wall_area*(G*(CG1+CG2*CDD50+CG3*EAc*(VS*CDD50)**2+CG4*EAc**2*VS*CDD50 + CG5*CDD65 + CG6*CDD50**3 + CG7*CDD65**3) + 
            G**2*(CG8*EAc*VS*CDD50 + CG9*EAc**2*VS*CDD50))
      print("CLG is", CLG)

      CLS = wall_area*(EAc*(CS1+CS2*VS*CDD50+CS3*(VS*CDD50)**2+CS4*VS*CDD65+CS5*(VS*CDD65)**2)+EAc**2*(CS6+CS7*(VS*CDD65)**2))
      print("CLS is", CLS)

      CLC = wall_area*(CC1*CDD50 + CC2*CDD50**2 + CC3*CDH80 + CC4*CDH80**2 + CC5*CDD65 + CC6*(VS*CDD65)**2 + CC7*VS*CDD50 + 
            CC8*(VS*CDD50)**2+ CC9*(VS*CDH80)**2 + CC10*VS + CC11*DR + CC12*DR**2 + CC13)
      print("CLC is", CLC)

      COOL_wallVf = 0.005447*(CLU+CLUO+CLXUO+CLM+CLG+CLS+CLC)
      print("Cool for vertical fenestration is", COOL_wallVf)
      #print("COOL is", COOL)

      #---------------------------------------------------------------------------------------------------------------------------------------
      PCH1 = 0
      PCH2 = 0
      SAh = vf_area*1.163*SHGC*(1-PCH1*PF + PCH2*PF**2)
      EAh = SAh/wall_area

      for i in range(1,len(data_hot)+1):
            h = "H" + str(i) 
            globals()["H%i" % i] = data_hot.loc[h,position]

      HP1 = H6
      Ah = HDD65/100 + 2
      HP2 = H14*math.log(Ah) + H15
      HP3 = H1*Ah**3 + H2*Ah**2 + H3/math.sqrt(Ah) + H4/math.sqrt(Ah) + H5
      HP4 = H11*Ah**2 + H12/(Ah**2) + H13
      HP5 = H16
      HP6 = H7*Ah + H8
      HP7 = H17/(Ah**3) + H18
      HP8 = H9/(Ah**3) + H10

      SHMC = 1.43*opaque_area*(1-math.exp(-HP1*(HC-1)))*(HP2 + HP3*Uow - (HP4/(1+(HP5+HP6*Uow)*math.exp(-(HP7+HP8*Uow**2)*(HC-1)))))
      #print("SHMC is", SHMC)

      for i in range(1,3):
            h = "HU" + str(i) 
            globals()["HU%i" % i] = hot_coeff.loc[h,zone_orientation]

      for i in range(1,8):
            h = "HM" + str(i) 
            globals()["HM%i" % i] = hot_coeff.loc[h,zone_orientation]

      for i in range(1,4):
            h = "HUO" + str(i) 
            globals()["HUO%i" % i] = hot_coeff.loc[h,zone_orientation]

      for i in range(1,4):
            h = "HXUO" + str(i) 
            globals()["HXUO%i" % i] = hot_coeff.loc[h,zone_orientation]

      for i in range(1,7):
            h = "HG" + str(i) 
            globals()["HG%i" % i] = hot_coeff.loc[h,zone_orientation]

      for i in range(1,5):
            h = "HS" + str(i) 
            globals()["HS%i" % i] = hot_coeff.loc[h,zone_orientation]

      for i in range(1,8):
          h = "HC" + str(i) 
          globals()["HC%i" % i] = hot_coeff.loc[h,zone_orientation]

      HLU = opaque_area*Uow*(HU1*HDD50 + HU2*(VS*HDD65)**2)
      print("HLU is", HLU)

      HLUO = wall_area*UO*(HUO1*HDD50 + HUO2*HDD65 + HUO3*EAh*VS*HDD65)
      print("HLUO is", HLUO)

      HLXUO = wall_area*((1/UO)*(HXUO1*EAh*(VS*HDD50)**2 + HXUO2*EAh*(VS*HDD65)**2)+(1/UO**2)*(HXUO3*EAh**2*VS*HDD65))
      print("HLXUO is", HLXUO)

      HLM = opaque_area*SHMC*(HM1 + HM2*G*UO*HDD65 + HM3*G**2*EAh**2*VS*HDD50 + HM4*UO*EAh*VS*HDD65 + HM5*UO*HDD50 + HM6*EAh*(VS*HDD65)**2
               + HM7*EAh**2*VS*HDD65/UO)
      print("HLM is", HLM)

      HLG = wall_area*(G*(HG1*HDD65 + HG2*UO*HDD65 + HG3*EAh*VS*HDD65 + HG4*EAh**2*VS*HDD50)*G**2*(HG5*HDD65+HG6*EAh**2*VS*HDD65))
      print("HLG is", HLG)

      HLS = wall_area*(EAh*(HS1*VS*HDD65 + HS2*(VS*HDD50)**2) + EAh**2*(HS3*VS*HDD50 + HS4*VS*HDD65))
      print("HLS is", HLS)

      HLC = wall_area*(HC1 + HC2*HDD65 + HC3*HDD65**2 + HC4*VS**2 + HC5*VS*HDD50 + HC6*VS*HDD65 + HC7*(VS*HDD50)**2)
      print("HLC is", HLC)

      HEAT_wallVf = 0.007669*(HLU + HLUO + HLXUO + HLM + HLG + HLS + HLC)
      print("Heat for vertical fenestration is", HEAT_wallVf)
      #print("HOT is", HEAT)
       
      HVAC_wallVf = COOL_wallVf + HEAT_wallVf
      print("HVAC for vertical fenestration is", HVAC_wallVf)

      #----------------------skylights-------------------------------------------------------------------------------------
      c2 = 1.09*10**(-2)
      h2 = 2.12*10**(-4)
      h3 = -1.68*10**(-4)

      COOL_sky = sky_area*c2*CDD50*0.093*SHGC_sky
      HEAT_sky = sky_area*HDD65*0.66*(h2*Usky+h3*1.163*SHGC_sky)

      HVAC_sky = COOL_sky + HEAT_sky
      print("HVAC for skylights is", HVAC_sky)

      #----------------------floor-----------------------------------------------------------------------------------------
      if floor == "ground_floor" :
            Ccoef1 = 0
            Ccoef2 = 0
            Hcoef = 2.28*10**(-4)
      else :
            Ccoef1 = 7.09*10**(-4)
            Ccoef2 = 0
            Hcoef = 2.43*10**(-4)

      COOL_floor = floor_area*Ufloor*0.08*(Ccoef1*CDD50+Ccoef2)
      HEAT_floor = floor_area*Hcoef*Ufloor*HDD65*0.66

      HVAC_floor = COOL_floor + HEAT_floor
      print("HVAC for floor is", HVAC_floor)


      #----------------------roof-----------------------------------------------------------------------------------------
      Ccoef1 = 0
      Ccoef2 = 0
      Hcoef = 2.28*10**(-4)
            
      COOL_roof = roof_area*Uroof*0.08*(Ccoef1*CDD50+Ccoef2)
      HEAT_roof = roof_area*Hcoef*Uroof*HDD65*0.66

      HVAC_roof = COOL_roof + HEAT_roof
      print("HVAC for roof is", HVAC_roof)

      #-------------------------------EPF---------------------------------------------------------------------------
      HVAC_surface = HVAC_wallVf + HVAC_roof + HVAC_floor + HVAC_sky
      EPF = FAF*(HVAC_surface+Lighting_zone)    #return "%s" %EPF
      return render_template('output.html', base_EPF=EPF, text_Uow=Uow, text_Uvf=Uvf, text_SHGC=SHGC, text_Usky=Usky, 
            text_SHGC_sky=SHGC_sky, text_Uroof=Uroof, text_Ufloor=Ufloor, CDD50=CDD50, CDD65=CDD65, HDD50=HDD50,
            HDD65=HDD65, CDH80=CDH80, zone_orientation=zone_orientation, wall_area=wall_area, HC=HC, vf_area=vf_area, 
            position=position, length=length, breadth=breadth, overhang_height=overhang_height, overhang_depth=overhang_depth,
            orientation=orientation, material=material, sky_area=sky_area, sky_depth=sky_depth, sky_length=sky_length, sky_width=sky_width,
            roof_area=roof_area, floor_area=floor_area, FAF=FAF, floor=floor)
      
@app.route('/analyse',methods = ['POST', 'GET'])
def analyse():
   if request.method == 'POST':
               
      #surface_area = float(request.form['surface_area'])

      zone_orientation = request.form['zone_orientation']
      position = request.form['position']
      wall_area = float(request.form['wall_area'])
      Uow = float(request.form['Uwall'])
      if Uow > 0.4:
          U0w = 0.4  #Btu/h.sft.F
      elif Uow < 0.05:
          Uow = 0.05 #Btu/h.sft.F

      vf_area = float(request.form['vf_area'])
      length = float(request.form['length'])
      breadth = float(request.form['breadth'])
      overhang_depth = float(request.form['overhang_depth'])
      overhang_height = float(request.form['overhang_height'])
      orientation = request.form['orientation']
      Uvf = float(request.form['Uvf'])
      SHGC = float(request.form['SHGC'])
      HC = float(request.form['HC'])
      if HC > 20:
            HC = 20 #Btu/sft.F



      material = request.form['material']
      sky_area = float(request.form['sky_area'])
      sky_depth = float(request.form['sky_depth'])
      sky_length = float(request.form['sky_length'])
      sky_width = float(request.form['sky_width'])
      Usky = float(request.form['Usky'])
      SHGC_sky = float(request.form['SHGC_sky'])

      floor_area = float(request.form['floor_area'])
      floor = request.form['floor']
      Ufloor = float(request.form['Ufloor'])
     
      roof_area = float(request.form['roof_area'])
      Uroof = float(request.form['Uroof'])

      FAF = float(request.form['FAF'])
      CDD50 = float(request.form['CDD50'])
      CDD65 = float(request.form['CDD65'])
      HDD50  = float(request.form['HDD50'])
      HDD65  = float(request.form['HDD65'])
      CDH80  = float(request.form['CDH80'])

      base_EPF = float(request.form['base_EPF'])

      #-----------------------Lighting_zone------------------------------------------------------------------------
        #-----------------------VF-------------------------------------------------------
          #---------------------vf_VA-----------------------------------------
      vf_VLT = 1.00
      PF = overhang_depth/(length+overhang_height)

      if orientation == "north" :
            PCC1 = -0.5
            PCC2 = 0.22
      else : 
            PCC1 = -0.97
            PCC2 = 0.38

      vf_VA = vf_area*vf_VLT*(1+(PCC1*PF)+(PCC2*PF**2))

          #------------------------sky_VA-------------------------------------
      if material == "glass" :
            sky_VLT = 1.27
      elif material == "plastic" : 
            sky_VLT = 1.2
      if sky_area == 0:
            sky_VA = 0
      else :
            sky_VA = sky_area*sky_VLT*10**(-0.25*5*sky_depth*(sky_width+sky_length)/(sky_width+sky_length))
      
          
      if vf_VA > sky_VA :
            VA = vf_VA
            fen_area = vf_area
            area = wall_area
      else : 
            VA = sky_VA
            fen_area = sky_area
            area = roof_area
      P1 = 0.737
      P2 = -3.17*10**(-4)
      P3 = -24.71
      P4 = 0.234
      DI = 50  #fc

      Kd_zone = P1 + (P2*DI*VA/fen_area)*(1-math.exp((P3+P4*DI)*VA/area))
      
      LPD = 1.2  # W/ft**2
      LPD_adj = LPD*(1-Kd_zone)

      Lighting_zone = LPD_adj*floor_area*216

      #---------------------HVAC_surface---------------------------------------------------------------------------------------
       #--------------------------wall-----------------------------------------------------------------------------------
      data_cool=pd.read_csv('static/cooling_delta.csv', index_col=0)
      data_hot = pd.read_csv('static/heating_delta.csv', index_col=0)
      cool_coeff = pd.read_csv('static/cooling_coeff.csv', index_col=0)
      hot_coeff = pd.read_csv('static/heating_coeff.csv', index_col=0)

      for i in range(1,len(data_cool)+1):
          c = "C" + str(i) 
          globals()["C%i" % i] = data_cool.loc[c,position]

      opaque_area = wall_area - vf_area
      EPD = 0.75 #W/sft
      G = EPD + LPD_adj
      SAc = vf_area*1.163*SHGC*(1-PCC1*PF + PCC2*PF**2)
      EAc = SAc/wall_area
      UO = (opaque_area*Uow + vf_area*Uvf)/(wall_area)
      VS = 500
      DR = 17
      
      B = (DR/10)+1
      Ac = (CDH80/10000)+2
      CP1 = C5
      CP2 = (C15/B**3) + (C16/((Ac**2)*(B**2))) + C17
      CP3 = (C1/Ac**3) + (C2*B**3)
      CP4 = (C12/((Ac**2)*(B**2))) + (C13/B**3) + C14
      CP5 = C18
      CP6 = (C6*math.sqrt(B)*math.log(Ac)) + C7
      CP7 = (C19/((Ac**2)*(B**2))) + C20/(Ac*B) + (C21*Ac**2)/(math.sqrt(B)+C22)
      CP8 = (C8/((Ac**2)*(B**2))) + C9/(Ac*B) + (C21*Ac**2)/(math.sqrt(B)+C11)

      SCMC = 1.43*opaque_area*(1-math.exp(-CP1*(HC-1)))*(CP2+CP3*Uow-(CP4/(1+(CP5 + CP6*Uow)*math.exp(-(CP7+CP8*Uow**2)*(HC-1)))))
      #print("SCMC is", SCMC)

      for i in range(1,5):
            c = "CU" + str(i) 
            globals()["CU%i" % i] = cool_coeff.loc[c,zone_orientation]

      for i in range(1,5):
            c = "CUO" + str(i) 
            globals()["CUO%i" % i] = cool_coeff.loc[c,zone_orientation]

      for i in range(1,6):
            c = "CXUO" + str(i) 
            globals()["CXUO%i" % i] = cool_coeff.loc[c,zone_orientation]

      for i in range(1,9):
            c = "CM" + str(i) 
            globals()["CM%i" % i] = cool_coeff.loc[c,zone_orientation]

      for i in range(1,10):
            c = "CG" + str(i) 
            globals()["CG%i" % i] = cool_coeff.loc[c,zone_orientation]

      for i in range(1,8):
            c = "CS" + str(i) 
            globals()["CS%i" % i] = cool_coeff.loc[c,zone_orientation]

      for i in range(1,14):
            c = "CC" + str(i) 
            globals()["CC%i" % i] = cool_coeff.loc[c,zone_orientation]

      CLU= opaque_area*Uow*(CU1*CDH80 + CU2*CDH80**2 + CU3*(VS*CDH80)**2 + CU4*DR)

      CLUO = wall_area*UO*(CUO1*EAc*VS*CDD50 + CUO2*G + CUO3*G**2*EAc**2*VS*CDD50 + CUO4*G**2*EAc**2*VS*CDD65)

      CLXUO = wall_area/UO*(CXUO1*EAc*VS*CDD50 + CXUO2*EAc*(VS*CDD50)**2 + CXUO3*G*CDD50 + CXUO4*VS*CDD50*(G*EAc)**2 + CXUO5*G**2*CDD65) 

      CLM = opaque_area*SCMC*(CM1 + CM2*EAc*VS*CDD50 + CM3*EAc*VS*CDD65 + CM4*EAc**2*VS*CDD50 + CM5*G**2*CDD65 + CM6*G*CDD50 + 
                CM7*G*CDD65 + CM8*G*EAc*VS*CDD50)

      CLG = wall_area*(G*(CG1+CG2*CDD50+CG3*EAc*(VS*CDD50)**2+CG4*EAc**2*VS*CDD50 + CG5*CDD65 + CG6*CDD50**3 + CG7*CDD65**3) + 
            G**2*(CG8*EAc*VS*CDD50 + CG9*EAc**2*VS*CDD50))

      CLS = wall_area*(EAc*(CS1+CS2*VS*CDD50+CS3*(VS*CDD50)**2+CS4*VS*CDD65+CS5*(VS*CDD65)**2)+EAc**2*(CS6+CS7*(VS*CDD65)**2))

      CLC = wall_area*(CC1*CDD50 + CC2*CDD50**2 + CC3*CDH80 + CC4*CDH80**2 + CC5*CDD65 + CC6*(VS*CDD65)**2 + CC7*VS*CDD50 + 
            CC8*(VS*CDD50)**2+ CC9*(VS*CDH80)**2 + CC10*VS + CC11*DR + CC12*DR**2 + CC13)

      COOL_wallVf = 0.005447*(CLU+CLUO+CLXUO+CLM+CLG+CLS+CLC)
      #print("COOL is", COOL)

      #---------------------------------------------------------------------------------------------------------------------------------------
      PCH1 = 0
      PCH2 = 0
      SAh = vf_area*1.163*SHGC*(1-PCH1*PF + PCH2*PF**2)
      EAh = SAh/wall_area

      for i in range(1,len(data_hot)+1):
            h = "H" + str(i) 
            globals()["H%i" % i] = data_hot.loc[h,position]

      HP1 = H6
      Ah = HDD65/100 + 2
      HP2 = H14*math.log(Ah) + H15
      HP3 = H1*Ah**3 + H2*Ah**2 + H3/math.sqrt(Ah) + H4/math.sqrt(Ah) + H5
      HP4 = H11*Ah**2 + H12/(Ah**2) + H13
      HP5 = H16
      HP6 = H7*Ah + H8
      HP7 = H17/(Ah**3) + H18
      HP8 = H9/(Ah**3) + H10

      SHMC = 1.43*opaque_area*(1-math.exp(-HP1*(HC-1)))*(HP2 + HP3*Uow - (HP4/(1+(HP5+HP6*Uow)*math.exp(-(HP7+HP8*Uow**2)*(HC-1)))))
      #print("SHMC is", SHMC)

      for i in range(1,3):
            h = "HU" + str(i) 
            globals()["HU%i" % i] = hot_coeff.loc[h,zone_orientation]

      for i in range(1,8):
            h = "HM" + str(i) 
            globals()["HM%i" % i] = hot_coeff.loc[h,zone_orientation]

      for i in range(1,4):
            h = "HUO" + str(i) 
            globals()["HUO%i" % i] = hot_coeff.loc[h,zone_orientation]

      for i in range(1,4):
            h = "HXUO" + str(i) 
            globals()["HXUO%i" % i] = hot_coeff.loc[h,zone_orientation]

      for i in range(1,7):
            h = "HG" + str(i) 
            globals()["HG%i" % i] = hot_coeff.loc[h,zone_orientation]

      for i in range(1,5):
            h = "HS" + str(i) 
            globals()["HS%i" % i] = hot_coeff.loc[h,zone_orientation]

      for i in range(1,8):
          h = "HC" + str(i) 
          globals()["HC%i" % i] = hot_coeff.loc[h,zone_orientation]

      HLU = opaque_area*Uow*(HU1*HDD50 + HU2*(VS*HDD65)**2)

      HLUO = wall_area*UO*(HUO1*HDD50 + HUO2*HDD65 + HUO3*EAh*VS*HDD65)

      HLXUO = wall_area*((1/UO)*(HXUO1*EAh*(VS*HDD50)**2 + HXUO2*EAh*(VS*HDD65)**2)+(1/UO**2)*(HXUO3*EAh**2*VS*HDD65))

      HLM = opaque_area*SHMC*(HM1 + HM2*G*UO*HDD65 + HM3*G**2*EAh**2*VS*HDD50 + HM4*UO*EAh*VS*HDD65 + HM5*UO*HDD50 + HM6*EAh*(VS*HDD65)**2
               + HM7*EAh**2*VS*HDD65/UO)

      HLG = wall_area*(G*(HG1*HDD65 + HG2*UO*HDD65 + HG3*EAh*VS*HDD65 + HG4*EAh**2*VS*HDD50)*G**2*(HG5*HDD65+HG6*EAh**2*VS*HDD65))

      HLS = wall_area*(EAh*(HS1*VS*HDD65 + HS2*(VS*HDD50)**2) + EAh**2*(HS3*VS*HDD50 + HS4*VS*HDD65))

      HLC = wall_area*(HC1 + HC2*HDD65 + HC3*HDD65**2 + HC4*VS**2 + HC5*VS*HDD50 + HC6*VS*HDD65 + HC7*(VS*HDD50)**2)

      HEAT_wallVf = 0.007669*(HLU + HLUO + HLXUO + HLM + HLG + HLS + HLC)
      #print("HOT is", HEAT)
       
      HVAC_wallVf = COOL_wallVf + HEAT_wallVf

      #----------------------skylights-------------------------------------------------------------------------------------
      c2 = 1.09*10**(-2)
      h2 = 2.12*10**(-4)
      h3 = -1.68*10**(-4)

      COOL_sky = sky_area*c2*CDD50*0.093*SHGC_sky
      HEAT_sky = sky_area*HDD65*0.66*(h2*Usky+h3*1.163*SHGC_sky)

      HVAV_sky = COOL_sky + HEAT_sky

      #----------------------floor-----------------------------------------------------------------------------------------
      if floor == "ground_floor" :
            Ccoef1 = 0
            Ccoef2 = 0
            Hcoef = 2.28*10**(-4)
      else :
            Ccoef1 = 7.09*10**(-4)
            Ccoef2 = 0
            Hcoef = 2.43*10**(-4)

      COOL_floor = floor_area*Ufloor*0.08*(Ccoef1*CDD50+Ccoef2)
      HEAT_floor = floor_area*Hcoef*Ufloor*HDD65*0.66

      HVAC_floor = COOL_floor + HEAT_floor

      #----------------------roof-----------------------------------------------------------------------------------------
      Ccoef1 = 0
      Ccoef2 = 0
      Hcoef = 2.28*10**(-4)
            
      COOL_roof = roof_area*Uroof*0.08*(Ccoef1*CDD50+Ccoef2)
      HEAT_roof = roof_area*Hcoef*Uroof*HDD65*0.66

      HVAC_roof = COOL_roof + HEAT_roof

      #-------------------------------EPF---------------------------------------------------------------------------
      HVAC_surface = HVAC_wallVf + HVAC_roof + HVAC_floor + HVAV_sky
      EPF = FAF*(HVAC_surface+Lighting_zone)    #return "%s" %EPF
      savings = (base_EPF-EPF)*100/base_EPF
      if savings < 0.0001:
            savings = 0
            
      return render_template("output1.html",text=EPF, base_EPF=base_EPF,savings=savings)

if __name__ == "__main__":
    app.run(debug = True)
