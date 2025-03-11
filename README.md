This basic blockchain network allows nodes to add mine block with unique hash (uses SHA-256 algorithm), mined blocks has necessary details such as hash of the last block index, timestamp, proof, has of the last mined block, and transaction detail.

A cryptocurrency is built on top of this blockchain, a mempool is added along with a method to add new nodes to the network. 

Also Implemented the concensus of replacing the short chain with the longest chain through the method "replace_chain"

For adding the transactions to the blockchain, I made address node on three ports (port 5001, port 5002, port 5003) that can send cryptocurrency to each other. 

Later I mine these transactions to add them to the blockchain and follow the concensus to maintain consistency. 
