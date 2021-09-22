import ast
import json
import time
import uuid

from bson.objectid import ObjectId
from flask import Flask, Response, jsonify, make_response, redirect, request
from flask.helpers import flash, get_flashed_messages, send_file
from flask.json import dumps
from pymongo import MongoClient, database
from pymongo.bulk import _DELETE_ALL
from pymongo.errors import DuplicateKeyError
import json, os, sys
from ast import literal_eval
from bson.json_util import dumps
sys.path.append('./data')
 

#connect to MongoDB

mongodb_hostname = os.environ.get("MONGO_HOSTNAME","localhost")
client = MongoClient('mongodb://'+mongodb_hostname+':27017/')

#choose databese
db=client['DSMarkets']

users=db['Users']
products=db['Products']
bug=db['Bug']
productss=[]



app = Flask(__name__)

import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.INFO)


login_email="none"
users_sessions = {}

def create_session(email):
    user_uuid = str(uuid.uuid1())
    users_sessions[user_uuid] = (email, time.time())
    return user_uuid  

def is_session_valid(user_uuid):
    return user_uuid in users_sessions


@app.route("/hello",methods=['GET'])
def elina():
    return Response("hello my name is elina",status=200,mimetype='application/json')


#DIMIOURGIA XRISTI
@app.route('/register', methods=['POST'])
def register():
    data=None
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "username" in data or not "password" in data:
        return Response("Information incomplete",status=500,mimetype="application/json")

    username = data['username']
    password = data['password']
    email=data['email']
    category=data['category']
    


    
    if users.find({"email":email}).count()==0:
        if category=="admin":
            user = {"username": username,  "password": password ,"email":email , "category":category}
            users.insert_one(user)
            return Response(data['email']+" was added to the MongoDB",status=200, mimetype='application/json') 
        else:
            user= {"username": username,  "password": password ,"email":email , "category":category}
            users.insert_one(user)
            return Response(data['email']+" was added to the MongoDB",status=200, mimetype='application/json') 
    
        
    else:
        return Response("A user with the given email already exists",status=400, mimetype='application/json')

#login
@app.route('/login', methods=['POST'])
def login():
    global login_email
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "email" in data or not "password" in data:
        return Response("Information incomplete",status=500,mimetype="application/json")

    if ( users.find({"email":data['email'], "password":data['password'] }).count()==1): 
        user_uuid=create_session('email')
        res = {"uuid": user_uuid, "email": data['email']}
        login_email=data['email']
        return Response(json.dumps(res),status=200, mimetype='application/json')
    
    else:
        return Response("Wrong email or password.",status=400,mimetype='application/json') 
   

#insert product
@app.route('/insertProduct',methods=['POST'])
def insertp():
    global login_email
    uuid = request.headers.get('Authorization')

    if is_session_valid(str(uuid)):
        for i in users.find({}):
            if i['email']==login_email:
                if i['category']=="admin":
       
            
      
                    data=None
                    dcode=0
                    try:
                        data=json.loads(request.data)


                    except Exception as e:
                            return Response("bad json content",status=500,mimetype='application/json')
                    if data == None:
                            return Response("bad request",status=500,mimetype='application/json')
                    if not "name" in data:
                            return Response("Information Incomplete",status=500,mimetype='application/json')
                            
                    name=data['name']
                    price=data['price']
                    category=data['category']
                    description=data['description']
                    stock=data['stock']
                    prod_id=len(productss)+1
                    productss.append({
                    "prod_id":prod_id
                    })

                    prod={"name":name, "price":price, "category":category, "description":description ,"stock":stock }

                    products.insert_one(prod)
                    print (prod)
                        

                        
                    return Response(data['name'] + "Was Added to mongodb",status=200,mimetype='application/json')

                else:
                    return Response ("This function didnt allowed",status=401,mimetype='application/json')
    else:
        return Response("User not Authenticated",status=400,mimetype='application/json')



@app.route('/show_id',methods=['GET'])
def show():
  var=[]
  all_prod=products.find({})
  for ad in all_prod:
      
        print (ad['_id'])
  return Response ("all ok",status=200,mimetype='application/json')




#patch product
@app.route("/patchProduct/<_id>",methods=['PATCH'])
def patchpr(_id):
    data=None
    uuid = request.headers.get('Authorization')

    if is_session_valid(str(uuid)):
        for i in users.find({}):
            if i['email']==login_email:
                if i['category']=="admin":
   

                    try:
                        data=json.loads(request.data)
                    except Exception as e:
                        return Response("bad json content",status=500,mimetype='application/json')
                    if data == None:
                        return Response("bad request",status=500,mimetype='application/json')

                
                    name=data['name']

                    price=data['price']
                    
                    describe=data['describe']

                    stock=data['stock']
                
                    

                    if name!=None:
                        products.find_one_and_update({"_id":ObjectId(_id)},{"$set":{"name":name}})
                    if price !=None:    
                        products.find_one_and_update({"_id":ObjectId(_id)},{"$set":{"price":price}})
                    if describe!=None:
                        products.find_one_and_update({"_id":ObjectId(_id)},{"$set":{"description":describe}})
                    if stock!=None:
                        products.find_one_and_update({"_id":ObjectId(_id)},{"$set":{"stock":stock}})

                    return Response("Product updated",status=200,mimetype='application/json')
                else:
                    return Response("Function dont allowed",status=401,mimetype='application/json')
    else:
        return Response ("User not authenicated",status=400,mimetype='application/json')

                

#delete product
@app.route('/deleteProduct/<_id>',methods=['DELETE'])
def deletep(_id):
    prod=products.find({"_id" : ObjectId(_id)})
    for i in users.find({}):
            if i['email']==login_email:
                if i['category']=="admin":
                    if prod!=None:
                        products.delete_one({"_id": ObjectId(_id)})
                        return Response ("product deleted",status=200,mimetype='application/json')
                    else:
                        return Response("No product Found",status=401,mimetype='application/json')
                else:
                    return Response("Function dont allowed",status=401,mimetype='application/json')


        
        


#find product
@app.route('/findProduct',methods=['POST'])
def findp():
    
    uuid = request.headers.get('Authorization')

    if is_session_valid(str(uuid)):
    
        all_prod=products.find({})
        name=""
        category=""
        price=""
        output=[]
        data = None 
        try:
            data = json.loads(request.data)
        except Exception as e:
            return Response ("empty data",status=400,mimetype='application/json')

        name=data['name']
        price=data['price']
        _id=data['_id']
        if name=="" and category=="" and _id=="":
            return Response ("empty fields",status=401,mimetype='application/json')
        if name!=None:
            for i in all_prod:
                if name==i['name']:
                    output.append({
                        "name":i['name'],
                        "category":i['category'],
                        "price":i['price'],
                        "description":i['description']
                    
                     })
                    for i in products.find({}).sort('name'):
                        print(i)
                elif price==i['price']:
                    output.append({
                        "name":i['name'],
                        "category":i['category'],
                        "price":i['price'],
                        "description":i['description']

                    })
                    for i in products.find({}).sort('price'):
                        print(i)

                elif _id==i['_id']:
                    output.append({
                        "name":i['name'],
                        "category":i['category'],
                        "price":i['price'],
                        "description":i['description']

                    })

            return Response (json.dumps(output) ,status=200,mimetype='application/json')
        
    else:
        return Response ("User not authenicated",status=400,mimetype='application/json')

        
#pros8iki sto kala8i
@app.route('/addtobug/<_id>',methods=['POST'])       
def add(_id):

    uuid = request.headers.get('Authorization')

    if is_session_valid(str(uuid)):    
    
        data=None
        try:
            data = json.loads(request.data)
        except Exception as e:
            return Response("bad json content",status=500,mimetype='application/json')
        if data == None:
            return Response("bad request",status=500,mimetype='application/json')
        if not "count" in data or not "username" in data:
            return Response("Information incomplete",status=500,mimetype="application/json")

        username=data['username']
        counted=data['count']
        prod=products.find_one({"_id":ObjectId(_id)})
        print (prod)
        if prod!=None:
            if (int(counted)<int(prod['stock'])):
                    var={"_id":ObjectId(_id), "count":counted ,"username":username}
                    if bug.find_one({"_id":ObjectId(_id)}):
                        return Response ("Product already to store (continue to buy products or pay",status=200,mimetype='application/json')
                    else:
                        bug.insert_one(var)
                    return Response ("Product(s) ready to buy",status=200,mimetype='application/json')
            else:
                    return Response("We haven't enough stock please buy less products",status=401,mimetype='application/json')
        else:
                    return Response ("No product found with that _id" , status=401 ,mimetype='application/json')
    else:
        return Response("User not Authenticated",status=400,mimetype='application/json')


#emfanisi kala8iou
@app.route('/showb',methods=['GET'])
def showb():
    ab=bug.find({})
    for i in ab:
        print (i)
    return Response("all ok",status=200,mimetype='application/json')

#diagrafi ap to kala8i
@app.route('/deleteb<_id>',methods=['DELETE'])
def deleteb(_id):
    if ObjectId(_id)!=None:
        bug.delete_one({"_id":ObjectId(_id)})
        return Response("Product(s) deleted",status=200,mimetype='application/json')
    else:
        return Response("No product found with that email",status=404,mimetype='application/json')
#agora proiontws
@app.route('/productbuy',methods=['POST'])
def buy():

    uuid = request.headers.get('Authorization')

    if is_session_valid(str(uuid)):

        pb=dumps(bug.find_one({}))
        var=ast.literal_eval(str(pb))
        
        data=None
        try:
            data= json.loads(request.data)
        except Exception as e:
            return Response("bad json content",status=500,mimetype='application/json')
        if data == None:
            return Response("bad request",status=500,mimetype='application/json')
        credit_card=data['credit_card']
        if len(credit_card)==16:
            print(credit_card)
            for i in users.find({}):
                if i['email']==login_email:
                    users.find_one_and_update({"email":login_email} , {"$set":{"orderHistory":[var]}})
                    return Response("Your buy was succesful",status=200,mimetype='application/json')
        else:
                return Response("Card number incorrect",status=400,mimetype='application/json')
    
    else:
        return Response("User not Authenticated",status=400,mimetype='application/json')

#emfanisi istorikou paraggeliwn
@app.route('/history/<string:email>',methods=['GET'])
def history(email):
    user=users.find_one({"email":email})
    print (user['orderHistory'])
    return Response ("Check your order history",status=200,mimetype='application/json')

#diagrafi user
@app.route('/userdelete/<string:email>',methods=['DELETE'])
def usdel(email):
    uuid = request.headers.get('Authorization')
    if is_session_valid(str(uuid)):
            if email == None:
                return Response("Bad request", status=500, mimetype='application/json')
            else:
                var=users.find_one({"email":'email'})
                users.delete_one({"email": email})
                return Response(json.dumps(var)+"User deleted successfuly", status=200, mimetype='application/json')
    else:
            return Response("User not authenticated",status=401,mimetype='application/json')


# Εκτέλεση flask service σε debug mode, στην port 5000. 
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

