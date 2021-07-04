from flask import Flask, render_template, request, redirect, flash, session
from traffic import *
from graph import *
import time

app = Flask(__name__)
app.secret_key = "super secret key"


option_list = list_types()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/editjnpage')
def loadeditjnpage():
    jnlist = list_all_junctions()
    return render_template('addDetails.html', option_list=option_list, jnlist=jnlist)

@app.route('/editrdpage')
def loadeditrdpage():
    jnlist = list_all_junctions()
    return render_template('addRoadDetails.html', jnlist=jnlist)

@app.route('/addjn',methods=['GET', 'POST'])
def addjn():
    
    if request.method == 'POST':
        
        isPresent = create_junction(request.form['jname'],request.form['jtype'])
        if(isPresent == True):
            flash('Junction already exists')
        else:
            flash('Junction added successfully')
        return redirect('/editjnpage')
    else:
        
        return redirect('/editjnpage')

@app.route('/deljn',methods=['GET', 'POST'])
def deljn():
    
    if request.method == 'POST':
        
        delete_junction(request.form['jname'])
        flash('Junction deleted successfully')
        return redirect('/editjnpage')
    else: 
        return redirect('/editjnpage')

@app.route('/addrd',methods=['GET', 'POST'])
def addrd():
    
    if request.method == 'POST':
        value = request.form.get('blocked')
        if(value == None):
            value = 'false'
        sameJn,isExists = add_road(request.form['jname1'],request.form['jname2'],float(request.form['distance']),request.form['rname'],value)
        if(sameJn == True):
            flash('Select two different Junctions')
        if(isExists):
            flash('Road already exists between the two junctions')
        else:
            flash('Road added successfully')
        return redirect('/editrdpage')
    else:
        
        return redirect('/editrdpage')

@app.route('/delrd',methods=['GET', 'POST'])
def delrd():
    
    if request.method == 'POST':
        sameJn = delete_road(request.form['jname1'],request.form['jname2'])
        if(sameJn == True):
            flash('Select two different junctions')
        else:
            flash('Road deleted successfully')
        return redirect('/editrdpage')
    else: 
        return redirect('/editrdpage')

@app.route('/editrd',methods=['GET', 'POST'])
def editrd():
    
    if request.method == 'POST':
        value = request.form.get('blocked')
        if(value == None):
            value = 'false'
        sameJn = edit_road(request.form['jname1'],request.form['jname2'],value)
        if(sameJn == True):
            flash('Select two different Junctions')
        else:
            flash('Road details changed successfully')
        return redirect('/editrdpage')
    else:
        
        return redirect('/editrdpage')

@app.route('/mainpage')
def mainpage():
    jnlist = list_all_junctions()
    rdlist = list_relationships()
    city_map(jnlist,rdlist)
    
    return render_template('map.html', isRoute = False, isRoute_byType = False, jnlist = jnlist,option_list=option_list , current_time = int(time.time()))

@app.route('/shortestroute', methods = ["POST"])
def shortestroute():
    isValid, junctionlist, roadlist, splitdist , cost = shortest_route(request.form['jname1'],request.form['jname2'])
    jnlist = list_all_junctions()
    rdlist = list_relationships()
    if(isValid):
        city_map(jnlist,rdlist,junctionlist)
        return render_template('map.html', option_list=option_list , isRoute = True, isRoute_byType = False, jnlist = jnlist,current_time = int(time.time()),cost = cost,junctionlist = junctionlist,roadlist =roadlist,  scroll='short_route')
    else:
        flash("Sorry! No routes available for now")
        return render_template('map.html', option_list=option_list , isRoute = False, isRoute_byType = False, jnlist = jnlist,current_time = int(time.time()),  scroll='short_route')

@app.route('/shortest_route_by_type', methods = ["POST"])
def short_route_by_type():
    isValid, junctionlist, roadlist, cost = shortest_route_by_type(request.form['jname'],request.form['jtype'])
    jnlist = list_all_junctions()
    rdlist = list_relationships()
    if(isValid):
        city_map(jnlist,rdlist,junctionlist, True)
        return render_template('map.html', option_list=option_list , isRoute_byType = True, isRoute = False, jnlist = jnlist,current_time = int(time.time()),cost = cost,junctionlist = junctionlist,roadlist =roadlist,  scroll='short_route_by_type')
    else:
        flash("Sorry! No routes available for now")
        return render_template('map.html', option_list=option_list , isRoute = False, isRoute_byType = False, jnlist = jnlist,current_time = int(time.time()),  scroll='short_route')    

if __name__ == "__main__":
    # add neo4j login details here later !!!  
    
    app.run(debug=True)
