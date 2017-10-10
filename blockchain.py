import hashlib
import json
from time import time
from uuid import uuid4
from textwrap import dedent
from flask import Flask, jsonify, request

class Blockchain(object):
    def __init__(self):
        self.chain=[]
        self.current_transactions = []

        #create genesis block
        self.new_block(previous_hash=1,proof=100)


    #instantiate node
    app = Flask(__name__)

    #Generate a globally unique address for this node
    node_identifier = str(uuid4()).replace('-','')

    #instantiate the blockchain
    blockchain = Blockchain()

    @app.route('/mine',methods=['GET'])

    def mine():
        #We run the proof of work algorithm to get the next proof
        last_block = blockchain.last_block
        last_proof = last_block['proof']
        proof = blockchain.proof_of_work(last_proof)

        #We must receive a reward for finding the proof
        #The sender is "0" to signify that this node has mined a new coin
        blockchain.new_transaction(
            sender='0',
            recipient=node_identifier,
            amount=1,
        )

        #Forge a new block by adding it to the chain
        block = blockchain.new_block(proof)

        response = {
            'message':"New block forged",
            'index':block['index'],
            'transactions':block['transactions'],
            'proof':block['proof']
            'previous_hash':block['previous_hash'],
        }
        return jsonify(response), 200

    @app.route('/transactions/new',methods = ['POST'])

    def new_transaction():
        values = request.get_json()

        #Check that teh requested fields are in the POSTed data
        required = ['sender','recipient','amount']
        if not all(k in values for k in required):
            return 'Missing values', 400

        #Create a new transaction
        index = blockchain.new_transaction(values['sender'],values['recipient'],values['amount'])

        response = {'message':f"Transaction will be added to block {index}"}
        return jsonify(response),201

    @app.route('/chain',methods=['GET'])

    def full_chain():
        response = {
            'chain':blockchain.chain,
            'length':len(blockchain.chain),
        }
        return jsonify(response),200

    if __name__=='__main__':
        app.run(host='0.0.0.0',port=5000)

    def proof_of_work(self,last_proof):
        """
        Simple Proof of Work Algorithm:
        - Find a number p' such that hash(pp') contains leading 4 zeros, where p is  the previous proof and p' is the new proof

        :param last_proof: <int>
        :return: <int>
        """
        proof = 0
        while self.valid_proof(last_proof,proof) is False:
            proof+=1
        return proof

    @staticmethod
    def valid_proof(last_proof,proof):
        """
        Validates the proof: Does hash(last_proof,proof) contain 4 leading zeroes?

        :param last_proof: <int> Previous proof
        :param proof: <int> Current proof
        :return: <bool> True if correct, False if not.
        """

        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4]=="0000"

    def new_block(self):
        """
        Create a new block in the blockchain

        :param proof: <int> The proof given by the Proof of Work algorithm
        :param previous_hash: (Optional) <str> Hash of previous block
        :return: <dict> New Block

        """
        block={
            'index': len(self.chain)+1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof ,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }

        #Reset the current list of transactions
        self.current_transactions = []
        self.chain.append(block)
        return block


    def new_transaction(self):
        
        """
        Create a new transaction to go into the next mined block
        
        :param sender: <str> Address of the sender 
        :param recipient: <str> Address of the recipient 
        :param amount: <int> Amount 
        :return: <int> The index of the block that will hold this transaction

        """

        self.current_transactions.append({
            'sender':sender,
            'recipient':recipient,
            'amount':amount,
        })

        return self.last_block['index']+1

        


    @staticmethod
    def hash(block):
        """
        Creates a SHA256 hash of a block

        :param block: <dict> Block
        :return: <str>

        """
        #We must make sure that the dictionary is ordered, or we'll have inconsistent hashes
        block_string = json.dumps(block,sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()


    @property
    def last_block(self):
        #Returns the last block in the chain
        retun self.chain[-1]