from neo4j import GraphDatabase
from itertools import islice

# Database Credentials

uri = "bolt://localhost:7687"

userName = "neo4j"

password = "sai"

graphDB_Driver = GraphDatabase.driver(uri, auth=(userName, password))


def list_all_junctions():
    """Lists all Junctions"""
    with graphDB_Driver.session() as graphDB_Session:
        cqlNodeQuery = "MATCH (x:Junction) RETURN x.name"

        nodes = graphDB_Session.run(cqlNodeQuery)
        nodeList = []

        for node in nodes:
            node = str(node)
            pos = node.find("'")
            node = node[pos + 1 : -2]
            nodeList.append(node)
        snodeList = sorted(nodeList)
        return snodeList


def list_relationships():
    with graphDB_Driver.session() as graphDB_Session:
        cqlNodeQuery = "MATCH (x:Junction)-[r:connects]-(y:Junction) RETURN x.name,r.distance,r.unblocked,y.name,x.type,y.type"
        all_rel = graphDB_Session.run(cqlNodeQuery)
        all_list = []

        for record in all_rel:
            small_list = [
                record[0],
                record[1],
                record[2],
                record[3],
                record[4],
                record[5],
            ]
            all_list.append(small_list)
        sall_list = sorted(all_list)
        return sall_list


def shortest_route_by_type(start, btype):
    """Shortest distance between two junctions"""
    with graphDB_Driver.session() as graphDB_Session:
        cqlPathQuery = (
            '''MATCH (start:Junction{name:"'''
            + start
            + '''"}), (end:Junction{type:"'''
            + btype
            + """"}), x= (start)-[r*]-(end) where all(y in relationships(x) where y.unblocked="true")
CALL gds.alpha.shortestPath.stream({
nodeQuery:'MATCH(n:Junction) RETURN id(n) AS id',
relationshipQuery:'MATCH (n:Junction)-[r:connects]-(m:Junction) WHERE r.unblocked="true" RETURN id(n) AS source, id(m) as target,  r.distance AS distance',
startNode: start,
endNode: end,
relationshipWeightProperty: 'distance'
})
YIELD nodeId, cost
RETURN gds.util.asNode(nodeId).name AS name, cost,r;"""
        )
        shortestPath = graphDB_Session.run(cqlPathQuery)
        results = []
        countlist = []
        junctionlist = []
        roadlist = []
        costlist = []
        mincost = 0
        mincount = 0
        isValid = True
        i = 0
        for record in shortestPath:
            i += 1
            results.append(record)
            if i != 1 and record["name"] == results[0]["name"]:
                countlist.append(i - 1 - mincount)
                mincount = i - 1
        if not results:
            isValid = False
        else:
            countlist.append(i - sum(countlist))

            Results = iter(results)
            Results = [list(islice(Results, elem)) for elem in countlist]
            for i in range(len(Results)):
                costlist.append(Results[i][countlist[i] - 1]["cost"])
            mincost = min(costlist)
            minindex = costlist.index(min(costlist))
            result = Results[minindex]
            for record in result:
                test_list = list(record)
                junctionlist.append(test_list[0])

            relations = result[0][2]

            for relation in relations:
                roadlist.append(relation["name"])
        
        return isValid, junctionlist, roadlist, mincost


def shortest_route(start, end):
    """Shortest distance between two junctions"""
    with graphDB_Driver.session() as graphDB_Session:
        isValid = True
        cqlPathQuery = (
            '''MATCH (start:Junction{name:"'''
            + start
            + '''"}), (end:Junction{name:"'''
            + end
            + """"}), x= (start)-[r*]-(end) where all(y in relationships(x) where y.unblocked="true")
CALL gds.alpha.shortestPath.stream({
nodeQuery:'MATCH(n:Junction) RETURN id(n) AS id',
relationshipQuery:'MATCH (n:Junction)-[r:connects]-(m:Junction) WHERE r.unblocked="true" RETURN id(n) AS source, id(m) as target,  r.distance AS distance',
startNode: start,
endNode: end,
relationshipWeightProperty: 'distance'
})
YIELD nodeId, cost
RETURN gds.util.asNode(nodeId).name AS name, cost,r;"""
        )
        shortestPath = graphDB_Session.run(cqlPathQuery)
        results = []
        junctionlist = []
        roadlist = []
        costlist = []
        splitcost = []
        for record in shortestPath:
            results.append(record)
            
        if not results:
            isValid = False
        else:
            for record in results:

                junctionlist.append(record["name"])
                costlist.append(record["cost"])
            for i in range(1, len(costlist)):
                splitcost.append(costlist[i] - costlist[i - 1])
            relations = results[0][2]

            for relation in relations:
                roadlist.append(relation["name"])
        if not isValid:
            return isValid, junctionlist, roadlist, splitcost , ''
        else:
            return isValid, junctionlist, roadlist, splitcost , costlist[len(costlist) - 1]
            


def create_junction(name, atype):
    isPresent = False
    with graphDB_Driver.session() as graphDB_Session:
        nodeList = list_all_junctions()
        if name in nodeList:
            isPresent = True
        else:
            cqlNodeQuery = (
                'create (j1:Junction{name:"' + name + '",type:"' + atype + '"})'
            )
            graphDB_Session.run(cqlNodeQuery)
    return isPresent


def add_road(junc1, junc2, distance, roadname, unblocked):
    sameJn, isExists = False,False 
    with graphDB_Driver.session() as graphDB_Session:
        if (junc1 == junc2):
            sameJn = True
        else: 
            cqlTestQuery = (
                '''match (m:Junction{name:"'''
                + junc1
                + '''"}),(n:Junction{name:"'''
                + junc2
                + """"})
            return exists((m)-[:connects]-(n))"""
            )
            test = graphDB_Session.run(cqlTestQuery)
            ans = [record[0] for record in test][0]
            if ans:
                isExists = True
            else:
                cqlRelQuery = (
                    '''match (m:Junction),(n:Junction) where m.name="'''
                    + junc1
                    + '''" and n.name="'''
                    + junc2
                    + '''"
                create (m)<-[r:connects{name:"'''
                    + roadname
                    + """",distance:"""
                    + str(distance)
                    + ''',unblocked:"'''
                    + unblocked
                    + """"}]-(n)"""
                )
                graphDB_Session.run(cqlRelQuery)
    return sameJn,isExists


def delete_junction(junction):
    
    with graphDB_Driver.session() as graphDB_Session:
        cqlNodeQuery = (
            '''Match (n:Junction) where n.name = "'''
            + junction
            + """" detach delete n"""
        )
        graphDB_Session.run(cqlNodeQuery)

def delete_road(junc1,junc2):
    sameJn = False
    with graphDB_Driver.session() as graphDB_Session:
        if(junc1 == junc2):
            sameJn = True
        else:
            cqlNodeQuery = ('''MATCH (n:Junction {name:"'''+junc1+'''"})-[r:connects]-(m:Junction {name:"'''+junc2+'''"}) DELETE r ''')
            graphDB_Session.run(cqlNodeQuery)
    return sameJn

def edit_road(junc1,junc2,unblocked):
    sameJn = False
    with graphDB_Driver.session() as graphDB_Session:
        if(junc1 == junc2):
            sameJn = True
        else:
            cqlNodeQuery = ('''MATCH (n:Junction {name:"'''+junc1+'''"})-[r:connects]-(m:Junction {name:"'''+junc2+'''"}) SET r.unblocked = "''' +unblocked+'''"''')
            graphDB_Session.run(cqlNodeQuery)
    return sameJn

def list_types():
    return ['Junction','Hospital','Petrol Station','Other']

