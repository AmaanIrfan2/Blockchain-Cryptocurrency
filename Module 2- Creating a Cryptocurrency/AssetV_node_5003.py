#Module 2- Creating the Cryptocurrency 

#install flask, pip install requests==2.18.4, postman, spyder

# part 1- Creating the blockchain

import datetime
import hashlib
import json
from flask import Flask, jsonify, request 
import requests
from uuid import uuid4
from urllib.parse import urlparse 

class Blockchain:
    
#method for initializing blockchain
    def __init__(self):
        self.chain=[]
        self.transactions=[]
        self.create_block(proof = 1, previous_hash='0')
        self.nodes= set() #set of all unique nodes 
        
#method for creating the blocks
    def create_block(self, proof, previous_hash):
        block={'index': len(self.chain) + 1,
               'timestamp': str(datetime.datetime.now()),
               'proof': proof,
               'previous_hash': previous_hash,
               'transactions': self.transactions}
        self.transactions=[]
        self.chain.append(block)
        return block

#method to get the last block
    def get_previous_block(self):
        return self.chain[-1]

#method for proof of work (PoS) 
#(Objective is to define a problem 
#that is hard to solve but east to verify)

    def proof_of_work(self, previous_proof):
        new_proof=1
        check_proof= False
        while check_proof is False:
            hash_operation= hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] =="0000":
                check_proof= True
            else:
                new_proof += 1
        return new_proof

#method to create unique hash for every block 
    def hash(self, block):
        encoded_block= json.dumps(block, sort_keys=True).encode() #converts the block into JSON strings
        return hashlib.sha256(encoded_block).hexdigest()
        
#method to check if the blockchain is valid (through previous_hash and proof)
    
    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block= chain[block_index]
            if block['previous_hash'] != self.hash(previous_block):
                return False
            previous_proof= previous_block['proof']
            proof= block['proof']
            hash_operation= hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            previous_block=block
            block_index +=1           
        return True

# to add new transactions to the list of transactions in blockchain 
    def add_transactions(self, sender, receiver, amount):
        self.transactions.append({'sender': sender,
                                  'receiver': receiver,
                                  'amount': amount})
        # fetches the last block, and returns the index of the next block where this transaction will be added 
        previous_block= self.get_previous_block()
        return previous_block['index'] + 1

#allowing the addition of new nodes to blockchain network
    def add_node(self, address):
        parsed_url=urlparse(address) #parse the URL in its components 
        self.nodes.add(parsed_url.netloc) #extracts host and port, and adds new node to the blockchain network  
    
    def replace_chain(self):
        network= self.nodes
        longest_chain= None
        max_length= len(self.chain)
        for node in network:
            response = requests.get(f'http://{node}/get_chain')
            if response.status_code == 200:
                length= response.json()['length']
                chain = response.json()['block']
                if length>max_length and self.is_chain_valid(chain):
                    max_length= length
                    longest_chain= chain
        if longest_chain:
            self.chain= longest_chain
            return True
        return False                  
        
# part 2- Mining the Blockchain 

# creating the web app
app= Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

#create address for node on port 5000
node_address= str(uuid4()).replace('-','')

#creating a blockchain
blockchain= Blockchain()

#mining a new block 
@app.route('/mine_block', methods= ['GET']) #defines homepage route, run
def mine_block():
    previous_block= blockchain.get_previous_block() #retrieves the last block, also called previous block 
    previous_proof= previous_block['proof'] # get proof number of last block
    proof= blockchain.proof_of_work(previous_proof) # using proof of work to find new valid proof
    previous_hash= blockchain.hash(previous_block) #hashing the previous block again
    blockchain.add_transactions(sender= node_address, receiver= 'Saman', amount=1)
    block= blockchain.create_block(proof, previous_hash) #creates a new block with valid proof and hash of the previous block, also adds the new block to the blockchain
    response = {'Message': 'Congratulations! You have successfully mined the block', #this is the response for the users to knoe details about the block that is mined 
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash'],
                'transactions': block['transactions']}
    
    return jsonify(response), 200

#Getting the full list of blockchain 
@app.route('/get_chain', methods= ['GET'])
def get_chain():
    response= { 'block': blockchain.chain,
               'length': len(blockchain.chain)}
    return jsonify(response), 200

#Check if the blockchain is valid 
@app.route('/is_valid', methods= ['GET'])
def is_valid():
    is_valid= blockchain.is_chain_valid(blockchain.chain)
    
    if is_valid:
        response = {'message' : 'Congratulations! Blockchain is valid'}
    else:
        response= {'message' : 'Saman! Your Blockchain is invalid'}
    return jsonify(response), 200

# Adding a new transaction to the blockchain 
@app.route('/add_transactions', methods= ['POST']) #Only accepts post requests, meaning user have to send data
def add_transactions():
    json = request.get_json() #extracts data in json format 
    transaction_keys= ['sender', 'receiver', 'amount']
    if not all(key in json for key in transaction_keys):
        return 'some elements of the transaction are missing', 400
    index= blockchain.add_transactions(json['sender'], json['receiver'], json['amount']) #Stores the transaction on blockchain and returns the index of the block
    response = {'message': f'Your transaction has been added to the block {index}'}
    return jsonify(response), 201

#part 3- Decentralizing the Blockchain 

#Connecting new nodes 
@app.route('/connect_node', methods= ['POST']) 
def connect_node():
    json = request.get_json() #get json data from request
    nodes = json.get('nodes') #extract nodes from the data
    if nodes is None:
        return "No Node", 400
    for node in nodes: #adding each node to the blockchain 
        blockchain.add_node(node)
    response = {'message': 'The following nodes have been added to the blockchain',
                'total_nodes': list(blockchain.nodes)}
    return jsonify(response), 201

#replacing the chain by the longest chain if needed 

#Check if the blockchain is valid 
@app.route('/replace_chain', methods= ['GET'])
def replace_chain():
    is_chain_replaced = blockchain.replace_chain()
    
    if is_chain_replaced:
        response = {'message' : 'The node has different chain so the chain is replaced',
                    'new_chain': blockchain.chain}
    else:
        response= {'message' : 'The chain is same as it is the largest chain',
                   'actual_chain' : blockchain.chain}
    return jsonify(response), 200

#running the app
app.run(host= '0.0.0.0', port= 5003)
