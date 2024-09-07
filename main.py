import hashlib, json, sys
import random
import copy
import time
import rsa
import pickle
import logging

def displayConsoleArt():
    art = """
    =====================================================
    |||||||||||||||||||||||||||||||||||||||||||||||||||||
    ||                                                ||
    ||                BLOCKCHAIN SIMULATOR            ||
    ||                                                ||
    ||             Secure, Decentralized,             ||
    ||             Transparent Transactions           ||
    ||                                                ||
    |||||||||||||||||||||||||||||||||||||||||||||||||||||
    =====================================================
    """
    print(art)
displayConsoleArt()

logging.basicConfig(level=logging.INFO)

(publicKey, privateKey) = rsa.newkeys(512)

def hashMe(msg=""):
    if type(msg) != str:
        msg = json.dumps(msg, sort_keys=True)
    if sys.version_info.major == 2:
        return unicode(hashlib.sha256(msg).hexdigest(), 'utf-8')
    else:
        return hashlib.sha256(str(msg).encode('utf-8')).hexdigest()

random.seed(0)

def logTransaction(txn):
    print(f"Transaction logged: {txn}")

def makeTransaction(maxValue=3):
    sign = int(random.getrandbits(1)) * 2 - 1
    amount = random.randint(1, maxValue)
    alicePays = sign * amount
    bobPays = -1 * alicePays

    return {'Alice': alicePays, 'Bob': bobPays}

txnBuffer = [makeTransaction() for i in range(30)]

def updateState(txn, state):
    state = state.copy()
    for key in txn:
        if key in state.keys():
            state[key] += txn[key]
        else:
            state[key] = txn[key]
    return state

def isValidTxn(txn, state):
    if sum(txn.values()) != 0:
        return False

    for key in txn.keys():
        if key in state.keys():
            acctBalance = state[key]
        else:
            acctBalance = 0
        if (acctBalance + txn[key]) < 0:
            return False

    return True

def signTxn(txn, privateKey):
    txnStr = json.dumps(txn, sort_keys=True)
    return rsa.sign(txnStr.encode('utf-8'), privateKey, 'SHA-256')

def verifyTxn(txn, signature, publicKey):
    txnStr = json.dumps(txn, sort_keys=True)
    try:
        rsa.verify(txnStr.encode('utf-8'), signature, publicKey)
        return True
    except:
        return False

state = {u'Alice': 50, u'Bob': 50}
genesisBlockTxns = [state]
genesisBlockContents = {u'blockNumber': 0, u'parentHash': None, u'txnCount': 1, u'txns': genesisBlockTxns, 'timestamp': time.time()}
genesisHash = hashMe(genesisBlockContents)
genesisBlock = {u'hash': genesisHash, u'contents': genesisBlockContents}
genesisBlockStr = json.dumps(genesisBlock, sort_keys=True)

chain = [genesisBlock]

def makeBlock(txns, chain):
    parentBlock = chain[-1]
    parentHash = parentBlock[u'hash']
    blockNumber = parentBlock[u'contents'][u'blockNumber'] + 1
    txnCount = len(txns)
    blockContents = {
        u'blockNumber': blockNumber,
        u'parentHash': parentHash,
        u'txnCount': txnCount,
        'txns': txns,
        'timestamp': time.time(),
        'nonce': 0
    }
    blockHash = hashMe(blockContents)
    block = {u'hash': blockHash, u'contents': blockContents}
    return block

def mineBlock(block, difficulty=2):
    prefix = '0' * difficulty
    nonce = 0
    while True:
        block['contents']['nonce'] = nonce
        blockHash = hashMe(block['contents'])
        if blockHash.startswith(prefix):
            block['hash'] = blockHash
            return block
        else:
            nonce += 1

blockSizeLimit = 5

while len(txnBuffer) > 0:
    bufferStartSize = len(txnBuffer)
    txnList = []
    while (len(txnBuffer) > 0) & (len(txnList) < blockSizeLimit):
        newTxn = txnBuffer.pop()
        validTxn = isValidTxn(newTxn, state)

        if validTxn:
            txnList.append(newTxn)
            state = updateState(newTxn, state)
            logTransaction(newTxn)
        else:
            print("Ignored Transaction")
            sys.stdout.flush()
            continue

    myBlock = mineBlock(makeBlock(txnList, chain))
    chain.append(myBlock)


def checkBlockHash(block):
    expectedHash = hashMe(block[u'contents'])
    if block['hash'] != expectedHash:
        raise Exception('Block Hash mismatch of block %s' % block['contents']['blockNumber'])
    return

def checkBlockValidity(block, parent, state, difficulty=2):
    parentNumber = parent['contents']['blockNumber']
    parentHash = parent['hash']
    blockNumber = block['contents']['blockNumber']

    if blockNumber != parentNumber + 1:
        raise Exception('Block number does not match the expected value at block %s' % blockNumber)

    if block['contents']['parentHash'] != parentHash:
        raise Exception('Parent hash not accurate at block %s' % blockNumber)

    prefix = '0' * difficulty
    if not block['hash'].startswith(prefix):
        raise Exception('Invalid Proof of Work')

    for txn in block['contents']['txns']:
        if isValidTxn(txn, state):
            state = updateState(txn, state)
        else:
            raise Exception('Invalid Transaction in Block %s: %s' % (blockNumber, txn))

    checkBlockHash(block)

    return state



def checkChain(chain):
    if type(chain) == str:
        try:
            chain = json.loads(chain)
            assert(type(chain) == list)
        except:
            return False
    elif type(chain) != list:
        return False

    state = {}
    for txn in chain[0]['contents']['txns']:
        state = updateState(txn, state)
    checkBlockHash(chain[0])
    parent = chain[0]

    for block in chain[1:]:
        state = checkBlockValidity(block, parent, state)
        parent = block

    return state

checkChain(chain)

chainAsText = json.dumps(chain, sort_keys=True)
checkChain(chainAsText)

nodeBchain = copy.copy(chain)
nodeBtxns = [makeTransaction() for i in range(5)]
newBlock = mineBlock(makeBlock(nodeBtxns, nodeBchain))

print("Blockchain on Node A is currently %s blocks long" % len(chain))

try:
    print("New Block Received; checking validity...")
    state = checkBlockValidity(newBlock, chain[-1], state)
    chain.append(newBlock)
except Exception as e:
    print(f"Error: {e}. Invalid block; ignoring and waiting for the next block...")

print("Blockchain on Node A is now %s blocks long" % len(chain))

def saveChain(chain, filename="blockchain.pkl"):
    with open(filename, 'wb') as f:
        pickle.dump(chain, f)

def loadChain(filename="blockchain.pkl"):
    try:
        with open(filename, 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        return None

saveChain(chain)
loadedChain = loadChain()


