import osmnx as ox

def update_details():
    G = ox.graph_from_place('Coimbatore district, Tamil Nadu, India',network_type='drive')
    ox.save_graphml(G,"coimbatore.graphml")

G = ox.load_graphml("coimbatore.graphml",int)
hospitals = ox.pois_from_place('Coimbatore district, Tamil Nadu, India',{'amenity':'hospital'})
print(hospitals["name"])