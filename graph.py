from traffic import *
import networkx as nx
import matplotlib.pyplot as plt
from bokeh.io import output_file, save
from bokeh.models import (
    BoxZoomTool,
    Circle,
    HoverTool,
    MultiLine,
    Plot,
    Range1d,
    ResetTool,
)
from bokeh.palettes import Spectral4
from bokeh.plotting import from_networkx


def city_map(jnlist,roadlist, srjunclist = None, by_type = False ):
    G = nx.Graph()
    edge_attrs = {}
    distlist = {}
    smalldistlist = {}
    UNBLOCKED_COLOR, BLOCKED_COLOR, ROUTE_COLOR = "black", "red", "green"
    JUNC_COLOR, BUNK_COLOR, HOSP_COLOR, OTHER_COLOR = (
        "darkblue",
        "darkorange",
        "red",
        "yellow",
    )
    total_list = roadlist
    nodeList = jnlist
    isEmpty = True
    if(srjunclist !=None):
        isEmpty = False
    for node in nodeList:
        distlist[node] = ""
    for record in total_list:
        fromjn = record[0]
        tojn = record[3]
        length = record[1]
        blocked = record[2]
        edge_color = UNBLOCKED_COLOR if blocked == "true" else BLOCKED_COLOR
        
        if(srjunclist !=None):
            for i in range(len(srjunclist) - 1):
                if((fromjn == srjunclist[i] and tojn == srjunclist[i+1]) or (tojn == srjunclist[i] and fromjn == srjunclist[i+1])):
                    
                    edge_color = ROUTE_COLOR
                    
        
        fromtype = record[4]
        totype = record[5]
        '''smalldistlist = {tojn: length}
        distlist.update(fromjn=smalldistlist)
        print(distlist)'''
        G.add_nodes_from([fromjn, tojn])
        attrs = {
            fromjn: {
                "name": fromjn,
                "type": fromtype,
                "color": JUNC_COLOR
                if fromtype == "Junction"
                else BUNK_COLOR
                if fromtype == "Petrol Station"
                else HOSP_COLOR
                if fromtype == "Hospital"
                else OTHER_COLOR,
            },
            tojn: {
                "name": tojn,
                "type": totype,
                "color": JUNC_COLOR
                if totype == "Junction"
                else BUNK_COLOR
                if totype == "Petrol Station"
                else HOSP_COLOR
                if totype == "Hospital"
                else OTHER_COLOR,
            },
        }
        nx.set_node_attributes(G, attrs)
        G.add_edge(fromjn, tojn, length=length)

        edge_attrs[(fromjn, tojn)] = edge_color

    nx.set_edge_attributes(G, edge_attrs, "edge_color")

    # Show with Bokeh
    plot = Plot(
        plot_width=800,
        plot_height=600,
        x_range=Range1d(-1.1, 1.1),
        y_range=Range1d(-1.1, 1.1),
    )
    '''plot.title.text = ""
    plot.legend.location = 'bottom_right'
    plot.legend.title = "Legend"'''

    node_hover_tool = HoverTool(tooltips=[("Name", "@name"), ("Type", "@type")])
    plot.add_tools(node_hover_tool, BoxZoomTool(), ResetTool())

    graph_renderer = from_networkx(G, nx.spring_layout, scale=1, center=(0, 0))

    graph_renderer.node_renderer.glyph = Circle(size=20, fill_color="color")
    graph_renderer.node_renderer.hover_glyph = Circle(size=25, fill_color="color")
    graph_renderer.edge_renderer.glyph = MultiLine(
        line_color="edge_color", line_alpha=0.8, line_width= 2
    )
    

    plot.renderers.append(graph_renderer)
    
    if(isEmpty == True):
        output_file("./static/city_map.html")
        save(plot)
    
    elif(isEmpty == False and by_type == False):
        output_file("./static/city_map1.html")
        save(plot)
    else:
        output_file("./static/city_map2.html")
        save(plot)







"""jlist, rlist, dist = shortest_route_by_type("Junction4", "Hospital")
jlength = len(jlist)
G = nx.path_graph(jlength)
names = {}
for i in range(0, jlength):
    names[i] = jlist[i]
H = nx.relabel_nodes(G, names)
nx.draw(H)
plt.show()

"""

