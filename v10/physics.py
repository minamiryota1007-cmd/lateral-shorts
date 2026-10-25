"""Educational toy model of a vertically rising projectile; NOT a real-world firing prediction."""
import json, math
from pathlib import Path
MASS=0.0102
V0=330.0
DIAMETER=0.00907
RHO0=1.225
SCALE_HEIGHT=8500.0
G=9.81
DT=0.005
AREA=math.pi*(DIAMETER/2)**2

def derivative(height, velocity, cd):
    rho=RHO0*math.exp(-max(0,height)/SCALE_HEIGHT)
    return velocity, -G-(rho*cd*AREA*velocity*abs(velocity))/(2*MASS)

def advance(h,v,cd,dt):
    a1,b1=derivative(h,v,cd)
    a2,b2=derivative(h+a1*dt/2,v+b1*dt/2,cd)
    a3,b3=derivative(h+a2*dt/2,v+b2*dt/2,cd)
    a4,b4=derivative(h+a3*dt,v+b3*dt,cd)
    return h+dt*(a1+2*a2+2*a3+a4)/6, v+dt*(b1+2*b2+2*b3+b4)/6

def simulate(cd):
    h,v,t=0.0,V0,0.0
    data=[{"t":0.0,"h":0.0,"v":V0}]
    next_sample=.1
    while t<35 and v>0:
        hn,vn=advance(h,v,cd,DT)
        tn=t+DT
        if vn<=0:
            mix=v/(v-vn)
            peak_t=t+mix*DT
            peak_h=h+(hn-h)*mix
            data.append({"t":round(peak_t,4),"h":round(peak_h,3),"v":0})
            return {"cd":cd,"peakHeightM":round(peak_h,2),"apexTimeS":round(peak_t,3),"samples":data}
        t,h,v=tn,hn,vn
        if t+1e-8 >=next_sample:
            data.append({"t":round(t,3),"h":round(h,3),"v":round(v,3)})
            next_sample+=.1
    raise RuntimeError("Model did not reach apex")

def main():
    cases={str(cd):simulate(cd) for cd in (0.30,0.45,1.00)}
    energy=.5*MASS*V0**2
    bowling_mass=energy/(G*12)
    out={
        "model":"simplified vertical ascent under drag; no wind; constant Cd; exponentially declining air density; not an actual firing prediction",
        "assumptions":{"massKg":MASS,"initialSpeedMps":V0,"diameterM":DIAMETER,"gravityMps2":G,"seaLevelDensityKgM3":RHO0,"densityScaleHeightM":SCALE_HEIGHT,"baseCd":.45},
        "initialEnergyJ":round(energy,3),
        "bowlingComparison":{"heightM":12,"ballMassKg":round(bowling_mass,2),"energyJ":round(bowling_mass*G*12,1)},
        "base":cases["0.45"],"sensitivity":[{"cd":cd,"heightM":cases[str(cd)]["peakHeightM"],"apexTimeS":cases[str(cd)]["apexTimeS"]} for cd in (0.30,0.45,1.00)]
    }
    destination=Path(__file__).resolve().parent/"src"/"physics.json"
    destination.parent.mkdir(parents=True,exist_ok=True)
    destination.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding="utf-8")
    print("Kinetic energy:",out["initialEnergyJ"],"J")
    print("Bowling ball equivalent:",out["bowlingComparison"]["ballMassKg"],"kg at 12m")
    for case in out["sensitivity"]:
        print(f"Cd={case['cd']:.2f}: apex {case['heightM']:.1f}m at {case['apexTimeS']:.2f}s")
    print("Saved:",destination)

if __name__=="__main__":
    main()
