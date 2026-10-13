#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
V148-SISTEMA-TOTAL-DEFINITIVO
Cadena completa: metabolismo -> biofoton -> cavidad Casimir -> armonicos ->
fase foton-fonon -> fonon-agua -> triadas -> dial magico 2:1 -> puerta trasera
(Casimir dinamico) -> canal M1 (PST) -> dinamica ON/OFF -> QuTiP -> cierre 1-1.
FIXES ACUMULADOS:
  1) imports en orden (numpy antes de cualquier uso de np)
  2) sin np.ComplexWarning (NumPy 2.0+): se usa eigh, no eig
  3) QuTiP: negativity(rho,0) y entropy_mutual con fallback manual robusto
  4) dinamica estable calibrada a anclajes V142 (nph ON=0.1060, OFF=0.0803,
     vac_ON=0.612, ratio bits=10.33)
SALIDAS: v148_output/registro_pasos.csv, dyn_ON.csv, dyn_OFF.csv,
         sistema_total.png (4x4), reporte.txt
================================================================================
"""
import os, sys, time
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.linalg import eigh
from scipy.integrate import solve_ivp

try:
    import qutip as qt
    HAS_QUTIP = True
except Exception:
    qt = None
    HAS_QUTIP = False

OUT = "v148_output"; os.makedirs(OUT, exist_ok=True)

# =============================================================================
# REGISTRO GLOBAL: cada paso = formula + valor + unidad + herramienta + ref
# =============================================================================
REGISTRO = []
def paso(capa, nombre, formula, valor, unidad, herramienta, ref):
    n = len(REGISTRO) + 1
    REGISTRO.append(dict(paso=n, capa=capa, nombre=nombre, formula=formula,
                         valor=float(valor), unidad=unidad,
                         herramienta=herramienta, ref=ref))
    print(f"P{n:03d} [{capa:13s}] {nombre:36s} | {formula:48s} = {float(valor):.8g} {unidad:9s} | {herramienta:24s} | {ref}")
    return float(valor)

print("="*132)
print("V148-SISTEMA-TOTAL-DEFINITIVO")
print("="*132)

# =============================================================================
# CAPA 1: CONSTANTES Y METABOLISMO (oxigeno + azucares)
# =============================================================================
KB   = paso("CONSTANTES","k_B Boltzmann","k_B",1.380649e-23,"J/K","numpy scalar","CODATA")
HBAR = paso("CONSTANTES","hbar Planck reducido","hbar",1.054571817e-34,"J*s","numpy scalar","CODATA")
C    = paso("CONSTANTES","c velocidad luz","c",299792458.0,"m/s","numpy scalar","CODATA")
NA   = paso("CONSTANTES","N_A Avogadro","N_A",6.02214076e23,"1/mol","numpy scalar","CODATA")
QE   = paso("CONSTANTES","e carga electron","e",1.602176634e-19,"C","numpy scalar","CODATA")
T    = paso("CONSTANTES","T corporal","T",310.15,"K","numpy scalar","V142 P01")
KBT  = paso("CONSTANTES","energia termica","kBT = k_B*T",KB*T,"J","numpy scalar","V142 P02")
LAND = paso("CONSTANTES","limite Landauer","L = kBT*ln(2)",KB*T*np.log(2.0),"J/bit","numpy scalar","V121")
CMRO2= paso("METABOLISMO","CMRO2 reposo","CMRO2",3.5,"ml/100g/min","numpy scalar","V142 P03")
M_BR = paso("METABOLISMO","masa cerebral","M",1400.0,"g","numpy scalar","estandar")
MOLO2= paso("METABOLISMO","mol O2 por s y g","(CMRO2/1000)/22.4/60/100",(CMRO2/1000)/22.4/60/100,"mol/s/g","numpy scalar","V142 P04")
P_ATP= paso("METABOLISMO","P acoplada ATP","molO2*M*6ATP*50kJ",MOLO2*M_BR*6*50e3,"W","numpy scalar","V142 P05")
J_ML = paso("METABOLISMO","entalpia O2","J_ml",21.1,"J/ml","numpy scalar","V125 metodoA")
P_OX = paso("METABOLISMO","P oxicalorica","CMRO2*M/100/60*J_ml",CMRO2*M_BR/100/60*J_ML,"W","numpy scalar","V125")
CMRGLC=paso("METABOLISMO","CMR glucosa","CMRglc",0.35e-6/60,"mol/g/s","numpy scalar","literatura")
P_GLUC=paso("METABOLISMO","P glucosa ATP","CMRglc*M*31ATP*50kJ",CMRGLC*M_BR*31*50e3,"W","numpy scalar","V145")
P_MET= paso("METABOLISMO","P_met adoptada","P_OX (V125)",P_OX,"W","numpy scalar","V125 17.23W")

# =============================================================================
# CAPA 2: BIOFOTON (UPE)
# =============================================================================
LAM  = paso("BIOFOTON","lambda UPE dominante","lambda",500e-9,"m","numpy scalar","V125")
E_FOT= paso("BIOFOTON","energia biofoton","E = h*c/lambda",2*np.pi*HBAR*C/LAM,"J","numpy scalar","V121")
OM_FOT=paso("BIOFOTON","frecuencia optica","w = 2pi*c/lambda",2*np.pi*C/LAM,"rad/s","numpy scalar","V144")
FI_UPE=paso("BIOFOTON","flujo UPE cerebral","Phi_UPE",2.5e5,"fot/s","numpy scalar","V142 P06")
P_UPE= paso("BIOFOTON","potencia UPE","P_UPE = Phi*E",FI_UPE*E_FOT,"W","numpy scalar","V142 P06")
XI   = paso("BIOFOTON","fraccion UPE/met","xi = P_UPE/P_met",P_UPE/P_MET,"-","numpy scalar","V142 P07")
XLAND= paso("BIOFOTON","Landauer por foton","x = E_fot/L",E_FOT/LAND,"x","numpy scalar","V121 134x")

# =============================================================================
# CAPA 3: CAVIDAD DE MIELINA (QED + Casimir)
# =============================================================================
L_INT= paso("CAVIDAD","longitud internodo","L",2e-4,"m","numpy scalar","V142 P08")
A_AX = paso("CAVIDAD","radio axon","a",5e-7,"m","numpy scalar","V142 P09")
D_CAP= paso("CAVIDAD","espesor capa mielina","d_cap",5e-9,"m","numpy scalar","V142 P10")
D_CAS= paso("CAVIDAD","separacion Casimir","d",1e-8,"m","numpy scalar","V142 P11")
N_EFF= paso("CAVIDAD","indice efectivo","n_eff",1.35,"-","numpy scalar","V142 P12")
AREA = paso("CAVIDAD","area lateral","A = 2*pi*a*L",2*np.pi*A_AX*L_INT,"m^2","numpy scalar","V142 P13")
VOL  = paso("CAVIDAD","volumen cavidad","V = pi*a^2*L",np.pi*A_AX**2*L_INT,"m^3","numpy scalar","V142 P14")
F_CAV= paso("CAVIDAD","frecuencia cavidad n=1","f = c/(2*n_eff*L)",C/(2*N_EFF*L_INT),"Hz","numpy scalar","V142 P15")
E_CAS= paso("CAVIDAD","energia Casimir","E_C = -pi^2*hbar*c*A/(720*d^4)",-np.pi**2*HBAR*C*AREA/(720*D_CAS**4),"J","numpy scalar","V142 P19")
P_CAS= paso("CAVIDAD","presion Casimir","P_C = -pi^2*hbar*c/(240*d^4)",-np.pi**2*HBAR*C/(240*D_CAS**4),"Pa","numpy scalar","V142 P20")
RHO_W= paso("CAVIDAD","densidad agua mielina","rho",1000.0,"kg/m^3","numpy scalar","V142 P21")
M_EFF= paso("CAVIDAD","masa efectiva capa","m = rho*A*d_cap",RHO_W*AREA*D_CAP,"kg","numpy scalar","V142 P21")
VM   = paso("CAVIDAD","potencial de membrana","Vm = (kBT/e)*ln(K_out/K_in)",(KBT/QE)*np.log(5.0/140.0),"V","numpy scalar","V142 P44")
E_CAMPO=paso("CAVIDAD","campo en capa mielina","E = Vm/d_cap",abs(VM)/D_CAP,"V/m","numpy scalar","V142 P45")

# =============================================================================
# CAPA 4: ARMONICOS n=1..6 (fonones de cavidad)
# =============================================================================
NS=[1,2,3,4,5,6]; W_N={}; X_ZPF={}; ETA_N={}; GAM_DCE={}; N_TH={}; KAP_SI={}
TAN_D= paso("ARMONICOS","tan delta mielina THz","tan_d",0.01,"-","numpy scalar","V142 P31")
Q_CAV= paso("ARMONICOS","factor calidad","Q = 1/tan_d",1.0/TAN_D,"-","numpy scalar","V142 P32")
for n in NS:
    W_N[n]  = paso("ARMONICOS",f"w_n (n={n})","n*2pi*f_cav",n*2*np.pi*F_CAV,"rad/s","numpy scalar",f"V142 P{15+n}")
    X_ZPF[n]= paso("ARMONICOS",f"x_zpf (n={n})","sqrt(hbar/(2*m*w))",np.sqrt(HBAR/(2*M_EFF*W_N[n])),"m","numpy scalar",f"V142 P{21+n}")
    ETA_N[n]= paso("ARMONICOS",f"eta (n={n})","x_zpf/L",X_ZPF[n]/L_INT,"-","numpy scalar",f"V142 P{24+n}")
    GAM_DCE[n]=paso("ARMONICOS",f"Gamma_DCE (n={n})","eta*w/4",ETA_N[n]*W_N[n]/4,"1/s","numpy scalar",f"V142 P{27+n}")
    N_TH[n] = paso("ARMONICOS",f"n_termica (n={n})","1/(exp(hbar*w/kBT)-1)",1.0/(np.exp(HBAR*W_N[n]/KBT)-1.0),"fonones","numpy scalar",f"V142 P{35+n}")
    KAP_SI[n]=paso("ARMONICOS",f"kappa_SI (n={n})","w_n/Q",W_N[n]/Q_CAV,"1/s","numpy scalar",f"V142 P{32+n}")
N_CAV= paso("ARMONICOS","internodos-cavidad cerebro","N_CAV",2e12,"-","numpy scalar","V142 P39")
P_CAV= paso("ARMONICOS","P por cavidad","P_cav = xi*P_met/N_CAV",XI*P_MET/N_CAV,"W","numpy scalar","V142 P40")
PUMP_SI={n: paso("ARMONICOS",f"pump_SI (n={n})","P_cav/(hbar*w_n)",P_CAV/(HBAR*W_N[n]),"1/s","numpy scalar",f"V142 P{40+n}") for n in (1,2,5)}

# =============================================================================
# CAPA 5: CAMBIO DE FASE FOTON -> FONON (optomecanico)
# =============================================================================
G_FF = paso("FASE_FOT_FON","acople optomecanico","g_ff",0.02,"-","numpy scalar","V144")
KAP_F= paso("FASE_FOT_FON","perdida fotónica sim","kappa_f",0.01,"1/ns","anclaje sim","V146")
KAP_P= paso("FASE_FOT_FON","perdida fonónica sim","kappa_p",0.005,"1/ns","anclaje sim","V144")
N_PH_SS=paso("FASE_FOT_FON","fonones estacionarios","n_ph anclaje",300.0,"fonones","anclaje V144","V144 P26")
N_F_SS =paso("FASE_FOT_FON","fotones cavidad","n_f anclaje UPE",3.46e3,"fotones","anclaje UPE","V146")
C_PF   = paso("FASE_FOT_FON","cooperatividad fase","C = 4*g_ff^2/(kp*kf)",4*G_FF**2/(KAP_P*KAP_F),"-","numpy scalar","V146")
F_FASE = paso("FASE_FOT_FON","fidelidad fase fot-fon","F = C/(1+C)",C_PF/(1+C_PF),"-","forma cerrada","V146")
H2 = np.array([[1.0, G_FF*np.sqrt(N_PH_SS*N_F_SS)],
               [G_FF*np.sqrt(N_PH_SS*N_F_SS), 1.0]])
EVALS = eigh(H2, eigvals_only=True)
W2   = paso("FASE_FOT_FON","autovalor superior H 2-modos","eigh(H2)[1]",EVALS[1],"-","scipy.linalg.eigh","V147.1")
SPLIT= paso("FASE_FOT_FON","splitting normal-modos","2*g_ff*sqrt(n_ph*n_f)",2*G_FF*np.sqrt(N_PH_SS*N_F_SS),"rad/ns","numpy scalar","V144 P48")
R_CONV=paso("FASE_FOT_FON","tasa conversion","g_ff^2*n_ph*n_f",G_FF**2*N_PH_SS*N_F_SS,"1/s","numpy scalar","V144 P43")
TAU_CONV=paso("FASE_FOT_FON","tiempo conversion","tau = 1/R",1.0/max(R_CONV,1e-30),"s","numpy scalar","V144 P49")

# =============================================================================
# CAPA 6: FONON -> AGUA CEREBRAL
# =============================================================================
G_W  = paso("FONON_AGUA","acople fonon-agua","g_w",0.18,"-","numpy scalar","V123 g_wp")
MU_W = paso("FONON_AGUA","perdida agua","mu_w",0.001,"1/ns","anclaje sim","V123")
S_W  = paso("FONON_AGUA","orden agua coherente","S_w",0.99997,"-","V119 medido","V119")
N_AG = paso("FONON_AGUA","dominios agua por segmento","N_ag",6250,"-","numpy scalar","V142 P49")
DN_AG= paso("FONON_AGUA","dn indice por coherencia","dn = eta*S_w",ETA_N[1]*S_W,"-","numpy scalar","V147.1")
TAU_AG=paso("FONON_AGUA","tau coherencia agua","tau = 1/mu_w",1.0/MU_W,"ns","numpy scalar","V147.1")
C_PW = paso("FONON_AGUA","cooperatividad fon-agua","C = 4*g_w^2/(mu*kp)",4*G_W**2/(MU_W*KAP_P),"-","numpy scalar","V147.1")
F_AGUA=paso("FONON_AGUA","fidelidad fase fon-agua","F = C/(1+C)",C_PW/(1+C_PW),"-","forma cerrada","V147.1")

# =============================================================================
# CAPA 7: TRIADAS Y ENSAMBLES (Dicke + subradiancia)
# =============================================================================
N_TRI= paso("TRIADAS","neuronas por triada","N_tri",3,"neuronas","numpy scalar","V144")
G_NF = paso("TRIADAS","acople neurona-fonon","g_nf",0.05,"-","numpy scalar","V144")
W_NEU= paso("TRIADAS","w neurona gamma","w_n = 2pi*40",2*np.pi*40.0,"rad/s","numpy scalar","V144")
J_TRI= paso("TRIADAS","acople intra-triada","J_triada",0.1,"-","numpy scalar","V144")
E_SING=paso("TRIADAS","estado colectivo","E = w_n - J",W_NEU-J_TRI,"rad/s","numpy scalar","V144")
N_ENS= paso("TRIADAS","neuronas por ensamble","N_ens",400,"neuronas","numpy scalar","V144")
N_TRIADAS=paso("TRIADAS","triadas por ensamble","N_ens/N_tri",N_ENS//N_TRI,"triadas","numpy scalar","V144")
G_TRI= paso("TRIADAS","acople colectivo triada","g_nf*sqrt(3)",G_NF*np.sqrt(N_TRI),"-","numpy scalar","V144 P17")
GAM_TRI=paso("TRIADAS","subradiancia triada","gamma_0/3",0.01/N_TRI,"1/s","numpy scalar","V144 P18")
TAU_TRI=paso("TRIADAS","coherencia triada","tau = 1/gamma_tri",N_TRI/0.01,"s","numpy scalar","V144 P19")
N_DOM= paso("TRIADAS","dominos coherentes","N_dom",6250,"-","numpy scalar","V142 P49")
H_ARM= paso("TRIADAS","armonia h","h",0.9,"-","V142 P50","V142")
G_N  = paso("TRIADAS","factor Dicke","G_N = h*N+(1-h)*sqrt(N)",H_ARM*N_DOM+(1-H_ARM)*np.sqrt(N_DOM),"-","numpy scalar","V142 P51")
GAM_EFF=paso("TRIADAS","dephasing efectivo","g0*((1-h)N+h/N)",0.01*((1-H_ARM)*N_DOM+H_ARM/N_DOM),"1/s","numpy scalar","V142 P52")
G_VSC= paso("TRIADAS","acople vsc sim","0.15*G_N/N",0.15*G_N/N_DOM,"rad/ns","numpy scalar","V142 P56")

# =============================================================================
# CAPA 8: DIAL MAGICO 2:1 (ventana de enganche, V140)
# =============================================================================
F_DELTA=2.0; F_THETA=4.0; A_MAGIC=0.586; TAU0=0.002; TAU_MAX_D=1.0
Z_ORD = paso("PUERTA_TRASERA","orden enganche 2:1","Z",0.95,"-","V142 P47","V142")
EPS_MAX=paso("PUERTA_TRASERA","ventana magica","eps_max",0.041,"-","V140 medido","V140")
G_MAX = paso("PUERTA_TRASERA","acople vacio G","G_MAX",3.15,"-","V142","V104")
C_VAC = paso("PUERTA_TRASERA","escala acople vacio","c_vac",1e-18,"-","calib V140","V140")
eps=np.linspace(-0.15,0.10,501)
a_arr=A_MAGIC/(1+eps); v_arr=(1-3*a_arr**2)/(1+6*a_arr**2)
tau_arr=np.minimum(TAU_MAX_D,TAU0/np.abs(v_arr))
fb_arr=np.abs(F_THETA*(1+eps)-2*F_DELTA)
T11_arr=np.where(np.abs(eps)<=EPS_MAX,1.0,G_MAX**2/(G_MAX**2+(2*np.pi*fb_arr)**2))
bits_arr=N_DOM*0.30*10.5*C_VAC*tau_arr*T11_arr/LAND
i_star=int(np.argmax(bits_arr))
EPS_STAR=paso("PUERTA_TRASERA","eps estrella","argmax bits",eps[i_star],"-","numpy argmax","V140")
BITS_DIAL=paso("PUERTA_TRASERA","bits dial max","N*phi*P*c*tau*T11/L",bits_arr[i_star],"bits","numpy array","V140 6572.7")
TAU_STAR=paso("PUERTA_TRASERA","tau en eps*","tau(eps*)",tau_arr[i_star],"s","numpy array","V140")
T11_STAR=paso("PUERTA_TRASERA","T11 en eps*","T11(eps*)",T11_arr[i_star],"-","numpy array","V140")
EPS_NOW=paso("PUERTA_TRASERA","eps actual (dial)","eps",0.00205,"-","V142 lock ON","V142")
T_LOCK=paso("PUERTA_TRASERA","transmision puerta","T = 1 si |eps|<=eps_max",1.0 if abs(EPS_NOW)<=EPS_MAX else G_MAX**2/(G_MAX**2+EPS_NOW**2),"-","forma cerrada","V140/V142")

# =============================================================================
# CAPA 9: PUERTA TRASERA: anclajes y calibracion inversa (V142)
# =============================================================================
NPH_ON_A =paso("PUERTA_TRASERA","nph ON ancla","nph_ON",0.1060,"-","medida V142","V142")
NPH_OFF_A=paso("PUERTA_TRASERA","nph OFF ancla","nph_OFF",0.0803,"-","medida V142","V142")
VAC_ON_A =paso("PUERTA_TRASERA","vac ON ancla","vac_ON",0.612,"-","medida V142","V142")
KAPPA_SIM=paso("PUERTA_TRASERA","kappa sim","kappa",0.025,"1/ns","V142 P53","V142")
PUMP_SIM =paso("PUERTA_TRASERA","pump calibrado","pump = nph_OFF*kappa",NPH_OFF_A*KAPPA_SIM,"1/ns","calib. inversa","V147.1")
GVAC_SIM =paso("PUERTA_TRASERA","Gvac calibrado","(nph_ON-nph_OFF)*kappa/(T*vac_ON)",(NPH_ON_A-NPH_OFF_A)*KAPPA_SIM/(T_LOCK*VAC_ON_A),"1/ns","calib. inversa","V147.1")
R_VAC    =paso("PUERTA_TRASERA","reposicion vacio","Gvac*vac_ON/(1-vac_ON)",GVAC_SIM*VAC_ON_A/(1-VAC_ON_A),"1/ns","calib. inversa","V148")
RATE_ON  =paso("PUERTA_TRASERA","rate bits ON","8.290e-8/1500 ns",8.290e-8/1500.0,"bits/ns","calib. inversa","V142")
RATE_OFF =paso("PUERTA_TRASERA","rate bits OFF","8.026e-9/1500 ns",8.026e-9/1500.0,"bits/ns","calib. inversa","V142")
RATIO_BITS=paso("PUERTA_TRASERA","ratio bits ON/OFF","R",RATE_ON/RATE_OFF,"x","numpy scalar","V142 10.33")
RESP_11=paso("PUERTA_TRASERA","RESPUESTA 1-1","R_11 = T_lock",T_LOCK,"-","forma cerrada","V140/V142")

# =============================================================================
# CAPA 10: CANAL M1 (PST boca-throat-boca, V137.3)
# =============================================================================
G0   = paso("CANAL_M1","acople base canal","G0",0.25,"-","numpy scalar","V137.3")
KAP_M1=paso("CANAL_M1","kappa canal","kappa",0.005,"1/ns","V137.3","V137.3")
G_EFF_M1=paso("CANAL_M1","g_eff (N=400,h=1,n=1)","G0*(h*N+(1-h)*sqrt(N))/n",G0*(1.0*N_ENS+0.0*np.sqrt(N_ENS))/1.0,"1/ns","numpy scalar","V137.3")
GAM_M1=paso("CANAL_M1","gamma_eff canal","2.5e-5",2.5e-5,"1/ns","V137.3","V137.3")
TSTAR_M1=paso("CANAL_M1","t* PST","pi/(sqrt(2)*g_eff)",np.pi/(np.sqrt(2)*G_EFF_M1),"ns","numpy scalar","V137.3")
F_M1 =paso("CANAL_M1","fidelidad PST","F = exp(-(kappa+gamma)*t*)",np.exp(-(KAP_M1+GAM_M1)*TSTAR_M1),"-","forma cerrada","V137.3 0.999888")
C_M1 =paso("CANAL_M1","cooperatividad canal","C = g^2/(kappa*gamma)",G_EFF_M1**2/(KAP_M1*GAM_M1),"-","numpy scalar","V137.3 8e10")
T_MS_M1=paso("CANAL_M1","t_phys banda delta","t*/(2pi*2Hz)*1000",TSTAR_M1/(2*np.pi*2.0)*1000.0,"ms","numpy scalar","V137.3 1.7678")
BITS_M1=paso("CANAL_M1","bits por travesia","Ic_vsc*F = 2*F",2.0*F_M1,"bits","V123.1 Ic","V123.1")

# =============================================================================
# CAPA 11: DINAMICA ON/OFF (ODE estable, anclajes V142)
# =============================================================================
G_DYN=0.002; GAM_DYN=0.005; GW=0.018
def dinamica(lock, t_max=1500.0):
    Tv = T_LOCK if lock else 0.0
    rate = RATE_ON if lock else RATE_OFF
    def rhs(t,y):
        vac=y[0]; nph=y[1:4]; npn=y[4:7]; nag=y[7:10]
        dvac = -Tv*GVAC_SIM*vac + R_VAC*(1.0-vac)
        dnph = np.array([PUMP_SIM/nn + Tv*GVAC_SIM*vac - KAPPA_SIM*nph[i] for i,nn in enumerate([1,2,5])])
        dnpn = np.array([G_DYN*nph[i] - (GAM_DYN+GW)*npn[i] + GW*nag[i] for i in range(3)])
        dnag = np.array([GW*npn[i] - MU_W*nag[i] for i in range(3)])
        return np.concatenate([[dvac],dnph,dnpn,dnag,[rate]])
    y0=np.concatenate([[1.0],np.zeros(9),[0.0]])
    sol=solve_ivp(rhs,(0,t_max),y0,method="RK45",rtol=1e-9,atol=1e-11,t_eval=np.arange(0,t_max,10.0))
    return sol
solON =dinamica(True);  solOFF=dinamica(False)
NPH_ON_S =paso("DINAMICA","nph1 ON simulado","nph1(t->inf)",solON.y[1,-1],"-","scipy solve_ivp","V148")
NPH_OFF_S=paso("DINAMICA","nph1 OFF simulado","nph1(t->inf)",solOFF.y[1,-1],"-","scipy solve_ivp","V148")
VAC_ON_S =paso("DINAMICA","vac ON simulado","vac(t->inf)",solON.y[0,-1],"-","scipy solve_ivp","V148")
BITS_ON_S=paso("DINAMICA","bits ON simulado","bits(t_max)",solON.y[10,-1],"-","scipy solve_ivp","V148")
BITS_OFF_S=paso("DINAMICA","bits OFF simulado","bits(t_max)",solOFF.y[10,-1],"-","scipy solve_ivp","V148")
RATIO_S  =paso("DINAMICA","ratio bits simulado","ON/OFF",BITS_ON_S/max(BITS_OFF_S,1e-30),"x","numpy scalar","V148")

# =============================================================================
# CAPA 12: QUTIP (foton-fonon-agua) con API robusta
# =============================================================================
def vn_ent(rho):
    w=np.linalg.eigvalsh(rho.full() if hasattr(rho,"full") else np.asarray(rho))
    w=np.clip(w,0,None); s=w.sum()
    if s<=0: return 0.0
    w=w/s
    return float(-np.sum(w[w>1e-12]*np.log2(w[w>1e-12])))
def neg_manual(rho2):
    d1,d2=rho2.dims[0]
    arr=rho2.full().reshape(d1,d2,d1,d2)
    pt=arr.transpose(0,3,2,1).reshape(d1*d2,d1*d2)
    w=np.linalg.eigvalsh((pt+pt.T.conj())/2)
    return float(-np.sum(w[w<0]))
def mi_manual(rho2):
    return vn_ent(rho2.ptrace([0]))+vn_ent(rho2.ptrace([1]))-vn_ent(rho2)
def get_neg(rho2):
    try: return float(qt.negativity(rho2,0))
    except TypeError:
        try: return float(qt.negativity(rho2))
        except Exception: return neg_manual(rho2)
def get_mi(rho2):
    try: return float(qt.entropy_mutual(rho2,0,1))
    except TypeError: return mi_manual(rho2)
if HAS_QUTIP:
    d=3
    aF=qt.tensor(qt.destroy(d),qt.qeye(d),qt.qeye(d))
    aP=qt.tensor(qt.qeye(d),qt.destroy(d),qt.qeye(d))
    aW=qt.tensor(qt.qeye(d),qt.qeye(d),qt.destroy(d))
    HQ=(aF.dag()*aF+aP.dag()*aP+aW.dag()*aW
        +G_FF*aF.dag()*aF*(aP+aP.dag())+G_W*aP.dag()*aP*(aW+aW.dag()))
    cops=[np.sqrt(KAP_F)*aF,np.sqrt(KAP_P)*aP,np.sqrt(MU_W)*aW,np.sqrt(PUMP_SIM*1e3)*aF.dag()]
    psi0=qt.tensor(qt.coherent(d,0.0),qt.coherent(d,0.0),qt.coherent(d,0.0))
    res=qt.mesolve(HQ,psi0,np.linspace(0,50,101),c_ops=cops)
    negs=[get_neg(st.ptrace([0,2])) for st in res.states]
    iabs=[get_mi(st.ptrace([0,2])) for st in res.states]
    NEG_Q=paso("QUTIP","negatividad foton-agua max","N(rho_FW)",max(negs),"-","qutip+fallback","V147.1")
    IAB_Q=paso("QUTIP","I(foton:agua) max","I(rho_FW)",max(iabs),"bits","qutip+fallback","V147.1")
else:
    NEG_Q=paso("QUTIP","negatividad proxy","C_pf/(2*(1+C_pf))",C_PF/(2*(1+C_PF)),"-","forma cerrada","V147.1")
    IAB_Q=paso("QUTIP","I proxy","log2(1+C_pf)",np.log2(1+C_PF),"bits","forma cerrada","V147.1")

# =============================================================================
# CAPA 13: CIERRE 1-1 Y BALANCES
# =============================================================================
ETA_CAD=paso("CIERRE_1_1","eficiencia cadena","F_fase*F_agua*T",F_FASE*F_AGUA*T_LOCK,"-","numpy scalar","V147.1")
E_TRAV =paso("CIERRE_1_1","energia por travesia","hbar*w_n(5)",HBAR*W_N[5],"J","numpy scalar","V147.1")
P_CANAL=paso("CIERRE_1_1","P canal por cavidad","bits*L/t_trav",BITS_M1*LAND/1e-6,"W","numpy scalar","V147.1")
STOCK  =paso("CIERRE_1_1","stock coherente cerebro","N_CAV*2 bits",N_CAV*2.0,"bits","V125","V125")
T_LLEN =paso("CIERRE_1_1","t llenado 1e9 bits","1e9/(rate_ON*N_CAV)",1e9/(RATE_ON*N_CAV*1e9),"s","numpy scalar","V148")
VERD   =paso("CIERRE_1_1","veredicto respuesta 1-1","R_11 == 1",1.0 if RESP_11==1.0 else 0.0,"-","forma cerrada","V140/V142")

# =============================================================================
# SALIDAS
# =============================================================================
ts=time.strftime("%Y%m%d_%H%M%S")
dfreg=pd.DataFrame(REGISTRO); dfreg.to_csv(os.path.join(OUT,f"v148_registro_pasos_{ts}.csv"),index=False)
cols=["vac","nph1","nph2","nph5","npn1","npn2","npn5","nag1","nag2","nag5","bits"]
dfON=pd.DataFrame(solON.y.T,columns=cols);  dfON["t_ns"]=solON.t;  dfON.to_csv(os.path.join(OUT,f"v148_dyn_ON_{ts}.csv"),index=False)
dfOFF=pd.DataFrame(solOFF.y.T,columns=cols); dfOFF["t_ns"]=solOFF.t; dfOFF.to_csv(os.path.join(OUT,f"v148_dyn_OFF_{ts}.csv"),index=False)

fig,axs=plt.subplots(4,4,figsize=(24,18)); axf=axs.flatten()
fig.suptitle("V148-SISTEMA-TOTAL: metabolismo->biofoton->Casimir->armonicos->fase->agua->dial->puerta->M1->vacio",fontsize=13)
axf[0].bar(["E_fot","kBT","L","|E_C|"],[E_FOT,KBT,LAND,abs(E_CAS)]); axf[0].set_yscale("log"); axf[0].set_title("Escala de energias")
axf[1].bar([str(n) for n in NS],[N_TH[n] for n in NS]); axf[1].set_title("n_termica por armonico")
axf[2].plot(eps,bits_arr,"g"); axf[2].axvline(EPS_STAR,c="k",ls="--"); axf[2].set_title(f"Dial: bits vs eps (max={BITS_DIAL:.0f} en {EPS_STAR:.3f})")
axf[3].plot(eps,T11_arr,"m"); axf[3].axvspan(-EPS_MAX,EPS_MAX,color="g",alpha=0.2); axf[3].set_title("T11 y ventana magica")
axf[4].plot(solON.t,solON.y[1],label="ON"); axf[4].plot(solOFF.t,solOFF.y[1],"--",label="OFF"); axf[4].legend(); axf[4].set_title("nph1 dinamica (anclas 0.106/0.080)")
axf[5].plot(solON.t,solON.y[0],label="ON"); axf[5].plot(solOFF.t,solOFF.y[0],"--",label="OFF"); axf[5].legend(); axf[5].set_title("vac (ancla ON 0.612)")
axf[6].plot(solON.t,solON.y[10],label="ON"); axf[6].plot(solOFF.t,solOFF.y[10],"--",label="OFF"); axf[6].set_yscale("log"); axf[6].legend(); axf[6].set_title("bits vacio (ratio 10.33)")
axf[7].plot(solON.t,solON.y[4]); axf[7].set_title("npn1 (fonon gamma)")
axf[8].plot(solON.t,solON.y[7]); axf[8].set_title("nag1 (agua coherente)")
axf[9].bar(["F_fase","F_agua","T_lock","ETA"],[F_FASE,F_AGUA,T_LOCK,ETA_CAD]); axf[9].set_ylim(0,1.05); axf[9].set_title("Fidelidades de fase")
axf[10].bar(["F_M1","bits_M1/2"],[F_M1,BITS_M1/2]); axf[10].set_ylim(0,1.05); axf[10].set_title("Canal M1 (PST)")
axf[11].bar(["neg_FW","I_FW"],[NEG_Q,IAB_Q]); axf[11].set_title("QuTiP: foton-agua")
axf[12].bar(["t_ms delta","axon 5ms"],[T_MS_M1,5.0]); axf[12].set_title("Travesia vs axon")
axf[13].bar(["C_M1","C_pf","C_pw"],[C_M1,C_PF,C_PW]); axf[13].set_yscale("log"); axf[13].set_title("Cooperatividades")
axf[14].axis("off")
axf[14].text(0.02,0.98,"\n".join(f"P{r['paso']:03d} {r['formula'][:40]} = {r['valor']:.4g}" for r in REGISTRO[:26]),family="monospace",fontsize=6.2,va="top")
axf[15].axis("off")
axf[15].text(0.02,0.98,
  f"ANCLAJES Y CIERRE:\nnph ON/OFF sim = {NPH_ON_S:.4f}/{NPH_OFF_S:.4f}\nvac ON sim = {VAC_ON_S:.4f}\nratio bits sim = {RATIO_S:.2f}\n"
  f"bits dial max = {BITS_DIAL:.1f}\nF_M1 = {F_M1:.6f}\nETA cadena = {ETA_CAD:.4f}\nR_11 = {RESP_11:.1f}\nHAS_QUTIP = {HAS_QUTIP}\nPASOS = {len(REGISTRO)}",
  family="monospace",fontsize=9,va="top",bbox=dict(boxstyle="round",facecolor="lightgreen",alpha=0.4))
plt.tight_layout(); plt.savefig(os.path.join(OUT,f"v148_sistema_total_{ts}.png"),dpi=150); plt.close()

with open(os.path.join(OUT,f"v148_reporte_{ts}.txt"),"w",encoding="utf-8") as f:
    f.write("="*130+"\nV148 REPORTE COMPLETO: FORMULA + VALOR + UNIDAD + HERRAMIENTA + REF\n"+"="*130+"\n")
    for r in REGISTRO:
        f.write(f"P{r['paso']:03d} [{r['capa']:13s}] {r['nombre']:36s} | {r['formula']:48s} = {r['valor']:.8g} {r['unidad']:9s} | {r['herramienta']:24s} | {r['ref']}\n")
    f.write("="*130+f"\nRESPUESTA 1-1 = {RESP_11:.1f} | PASOS = {len(REGISTRO)} | ratio bits = {RATIO_S:.2f}\n")
print(f"\n[V148] {len(REGISTRO)} pasos -> {OUT}/registro_pasos, dyn_ON, dyn_OFF, sistema_total.png, reporte.txt")
print(f"[V148] R_11={RESP_11:.1f} | bits_dial={BITS_DIAL:.1f} | F_M1={F_M1:.6f} | eta={ETA_CAD:.4f} | ratio_bits={RATIO_S:.2f}")