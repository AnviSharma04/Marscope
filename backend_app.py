"""MARSCOPE backend: curated Mars data + terrain-aware A* route planner.
Elevations are APPROXIMATE (inverse-distance interpolation of published MOLA-derived
landmark values). For precise values, sample the Mars Trek MOLA DEM (https://trek.nasa.gov/mars/)."""
import heapq, math
from flask import Flask, jsonify, request
from flask_cors import CORS
app = Flask(__name__); CORS(app)
R = 3389.5
SRC = {"trek": "https://trek.nasa.gov/mars/",
       "usgs": "https://astrogeology-usgs.hub.arcgis.com/pages/interactive-maps-mars",
       "sharp": "https://science.nasa.gov/resource/curiositys-proposed-path-up-mount-sharp/",
       "raw": "https://mars.nasa.gov/mars2020/multimedia/raw-images/"}
# (lat, lon, approx elevation km)
ANCH = [(18.4,77.5,-2.6),(-5.4,137.8,-4.4),(18.65,-133.8,21.2),(-13,-59,-4.5),(-42.4,70.5,-7.1),
        (-14.6,175.5,-1.9),(45,118,-4.0),(0,-100,7),(20,0,0.5),(-2,-5,-1.4),(25,147,14),(8,70,0),
        (60,0,-3),(-70,0,3),(-30,-130,3),(5,-45,-1)]
POIS = [
 dict(name="Jezero Crater (Perseverance)",lat=18.44,lon=77.45,type="Rover site",desc="Ancient delta and lake bed; Perseverance sampling site.",src=SRC["raw"]),
 dict(name="Gale Crater (Curiosity)",lat=-4.59,lon=137.44,type="Rover site",desc="Landing site of Curiosity; layered sediments.",src=SRC["sharp"]),
 dict(name="Mount Sharp (Aeolis Mons)",lat=-5.08,lon=137.85,type="Geology",desc="5 km central mound in Gale; Curiosity's climb through exposed strata.",src=SRC["sharp"]),
 dict(name="Olympus Mons",lat=18.65,lon=-133.8,type="Volcano",desc="Tallest known volcano in the Solar System.",src=SRC["trek"]),
 dict(name="Valles Marineris",lat=-14.0,lon=-59.0,type="Canyon",desc="Canyon system ~4,000 km long.",src=SRC["usgs"]),
 dict(name="Gusev Crater (Spirit)",lat=-14.57,lon=175.47,type="Rover site",desc="Spirit rover landing region; volcanic plains.",src=SRC["trek"]),
 dict(name="Meridiani Planum (Opportunity)",lat=-1.95,lon=-5.53,type="Rover site",desc="Hematite-rich plains explored by Opportunity.",src=SRC["usgs"]),
 dict(name="Hellas Planitia",lat=-42.4,lon=70.5,type="Basin",desc="Deepest, widest impact basin on Mars.",src=SRC["usgs"]),
 dict(name="Elysium Planitia (InSight)",lat=4.5,lon=135.6,type="Lander site",desc="InSight landing region.",src=SRC["trek"]),
]
HAZ = [
 dict(name="Olympus Mons escarpment",lat=18.65,lon=-133.8,radius_km=300,type="Steep volcanic scarp",severity=3),
 dict(name="Valles Marineris canyon walls",lat=-13,lon=-59,radius_km=450,type="Canyon walls / steep slopes",severity=3),
 dict(name="Noctis Labyrinthus fractures",lat=-7,lon=-100,radius_km=250,type="Fractured rough terrain",severity=3),
 dict(name="Hellas basin dust & pressure extremes",lat=-42.4,lon=70.5,radius_km=600,type="Extreme environment",severity=2),
 dict(name="Gale Crater rim",lat=-5.4,lon=137.8,radius_km=80,type="Crater rim / rough surface",severity=2),
 dict(name="Jezero Crater rim",lat=18.4,lon=77.7,radius_km=30,type="Crater rim / rough surface",severity=2),
 dict(name="Elysium Mons slopes",lat=25,lon=147,radius_km=200,type="Volcanic slopes",severity=2),
]
def hav(a,b,c,d):
    p=math.pi/180; h=math.sin((c-a)*p/2)**2+math.cos(a*p)*math.cos(c*p)*math.sin((d-b)*p/2)**2
    return 2*R*math.asin(math.sqrt(h))
def elev(lat,lon):
    n=d=0
    for la,lo,e in ANCH:
        k=hav(lat,lon,la,lo)
        if k<1: return e*1000
        w=1/k**3; n+=w*e; d+=w
    return n/d*1000
def hazards_at(lat,lon): return [h for h in HAZ if hav(lat,lon,h["lat"],h["lon"])<h["radius_km"]]
def terrain(e):
    return ("High volcanic/highland terrain" if e>5000 else "Southern highlands / cratered uplands" if e>0
            else "Northern lowland plains" if e>-4000 else "Deep basin or crater floor")
def astar(s,e,w):
    N=50; pad=3
    la0=min(s[0],e[0])-pad; la1=max(s[0],e[0])+pad; lo0=min(s[1],e[1])-pad; lo1=max(s[1],e[1])+pad
    dla=(la1-la0)/N; dlo=(lo1-lo0)/N
    pos=lambda i,j:(la0+i*dla,lo0+j*dlo)
    cell=lambda p:(round((p[0]-la0)/dla),round((p[1]-lo0)/dlo))
    cache={}
    def info(n):
        if n not in cache:
            la,lo=pos(*n); cache[n]=(elev(la,lo),sum(h["severity"] for h in hazards_at(la,lo)))
        return cache[n]
    S,G=cell(s),cell(e); pq=[(0,S)]; g={S:0}; prev={}
    while pq:
        _,u=heapq.heappop(pq)
        if u==G: break
        for di in(-1,0,1):
            for dj in(-1,0,1):
                if not(di or dj): continue
                v=(u[0]+di,u[1]+dj)
                if not(0<=v[0]<=N and 0<=v[1]<=N): continue
                a,b=pos(*u),pos(*v); d=hav(*a,*b)
                sl=math.degrees(math.atan(abs(info(v)[0]-info(u)[0])/(d*1000)))
                c=g[u]+d*(1+w*(sl/3+info(v)[1]*1.5))
                if c<g.get(v,1e18):
                    g[v]=c; prev[v]=u; heapq.heappush(pq,(c+hav(*b,*pos(*G)),v))
    path=[G]
    while path[-1]!=S: path.append(prev[path[-1]])
    pts=[list(s)]+[list(pos(*n)) for n in path[::-1][1:-1]]+[list(e)]
    return pts
def describe(name,pts):
    dist=sum(hav(*pts[i],*pts[i+1]) for i in range(len(pts)-1)); maxs=0; hz={}
    for i in range(len(pts)-1):
        d=hav(*pts[i],*pts[i+1]) or 1e-6
        maxs=max(maxs,math.degrees(math.atan(abs(elev(*pts[i+1])-elev(*pts[i]))/(d*1000))))
    for p in pts:
        for h in hazards_at(*p): hz[h["name"]]=h
    near=[p["name"] for p in POIS if any(hav(q[0],q[1],p["lat"],p["lon"])<150 for q in pts)]
    return dict(name=name,points=pts,distance_km=round(dist,1),max_slope_deg=round(maxs,2),
                hazards=list(hz.values()),pois=near,
                elev_start_m=round(elev(*pts[0])),elev_end_m=round(elev(*pts[-1])))
@app.get("/api/health")
def health(): return jsonify(ok=True)
@app.get("/api/pois")
def pois(): return jsonify(POIS)
@app.get("/api/hazards")
def hazards(): return jsonify(HAZ)
@app.get("/api/location")
def location():
    lat,lon=float(request.args["lat"]),float(request.args["lon"]); e=elev(lat,lon)
    near=min(POIS,key=lambda p:hav(lat,lon,p["lat"],p["lon"]))
    return jsonify(lat=lat,lon=lon,elevation_m=round(e),terrain=terrain(e),
        nearest_feature=near["name"],nearest_km=round(hav(lat,lon,near["lat"],near["lon"])),
        hazards=hazards_at(lat,lon),
        environment="No in-situ weather data bundled; see Mars 2020 raw images for surface context.",
        sources=[SRC["trek"],SRC["usgs"],SRC["raw"]])
@app.get("/api/route")
def route():
    g=request.args.get; s=(float(g("slat")),float(g("slon"))); e=(float(g("elat")),float(g("elon")))
    return jsonify([describe("Safest (terrain-aware A*)",astar(s,e,3.0)),
                    describe("Balanced",astar(s,e,0.8)),
                    describe("Direct line",[list(s),list(e)])])
if __name__=="__main__": app.run(host="0.0.0.0",port=5000)
