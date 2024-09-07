# Blockchain Simulator

## Overview

Welcome to the Blockchain Simulator project! This simulation provides a basic implementation of a blockchain with proof-of-work consensus, digital signatures, and transaction management. It's designed to help understand the core concepts of blockchain technology and its operations.

## Features

- **Basic Blockchain Structure**: Implements a simple blockchain with blocks containing transactions and metadata.
- **Proof of Work**: Uses a proof-of-work mechanism to mine new blocks, ensuring network security and integrity.
- **Transaction Validation**: Validates transactions to prevent double-spending and overdrafts.
- **Digital Signatures**: Utilizes RSA digital signatures to ensure the authenticity and integrity of transactions.
- **Chain Persistence**: Saves and loads the blockchain using Python's `pickle` module.
- **Console Art**: Displays a custom ASCII banner to enhance the visual appeal of the simulator.

## How It Works

1. **Initialization**:
   - The blockchain is initialized with a genesis block containing the initial state of accounts.
   
2. **Transaction Generation**:
   - Random transactions are generated and added to a transaction buffer.

3. **Block Mining**:
   - Transactions are grouped into blocks, and each block is mined using a proof-of-work algorithm to find a nonce that satisfies the difficulty requirement.

4. **Transaction Logging**:
   - Valid transactions are logged and added to the blockchain.

5. **Validation**:
   - Each block's validity is checked against the previous block, and the proof of work is verified.

6. **Chain Management**:
   - The blockchain can be saved to and loaded from a file, allowing persistence between sessions.

## Setup and Usage

1. **Install Dependencies**:
   Make sure you have the required Python libraries installed:
   ```bash
   pip install rsa
