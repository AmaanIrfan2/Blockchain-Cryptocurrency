# part 1- Creating a Blockchain 

import datetime
import hashlib
import json
from flask import Flask, jsonify

class Blockchain:
    
#method for initializing blockchain
    def __init__(self):
        self.chain=[]
        self.create_block(proof = 1, previous_hash='0')
        
#method for creating the blocks
    def create_block(self, proof, previous_hash):
        block={'index': len(self.chain) + 1,
               'timestamp': str(datetime.datetime.now()),
               'proof': proof,
               'previous_hash': previous_hash}
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

# part 2- Mining the Blockchain 

# creating the web app
app= Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

#creating a blockchain
blockchain= Blockchain()

#mining a new block 
@app.route('/mine_block', methods= ['GET']) #defines homepage route, run
def mine_block():
    previous_block= blockchain.get_previous_block() #retrieves the last block, also called previous block 
    previous_proof= previous_block['proof'] # get proof number of last block
    proof= blockchain.proof_of_work(previous_proof) # using proof of work to find new valid proof
    previous_hash= blockchain.hash(previous_block) #hashing the previous block again
    block= blockchain.create_block(proof, previous_hash) #creates a new block with valid proof and hash of the previous block, also adds the new block to the blockchain
    response = {'Message': 'Congratulations! You have successfully mined the block', #this is the response for the users to knoe details about the block that is mined 
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash']}
    
    return jsonify(response), 200

#Getting the full list of blockchain 
@app.route('/get_chain', methods= ['GET'])
def get_chain():
    response= { 'block': blockchain.chain,
               'length': len(blockchain.chain)}
    return jsonify(response), 200

#running the app
app.run(host= '0.0.0.0', port= 5000)



