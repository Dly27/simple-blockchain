import hashlib
import json
from time import time
import pymysql


class Block:
    def __init__(self, index, ts, data, prev_hash):
        self.index = index
        self.ts = ts
        self.data = data
        self.prev_hash = prev_hash
        self.hash = self.calculate_hash()
        self.nonce = 0

    def calculate_hash(self):
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

    def mine_block(self, diff):
        target = "0" * diff

        while self.hash[:diff] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()


class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
        self.pending_transactions = []

    connection = pymysql.connect(
        host='localhost',
        user='username',
        password='password',
        database='accounts'
    )

    def create_genesis_block(self):
        return Block(0, time(), [], "0")

    def add_block(self, block):
        self.chain.append(block)

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            if current_block.hash != current_block.calculate_hash():
                return False
            if current_block.prev_hash != previous_block.hash:
                return False
        return True

    def add_transaction(self, transaction):
        sender_account = Account(transaction.sender)
        sender_account.load()
        if sender_account.balance >= transaction.amount:
            sender_account.balance -= transaction.amount
            sender_account.save()
            self.pending_transactions.append(transaction)

def mine_pending_transactions(self):
    block_data = [tx.to_dict() for tx in self.pending_transactions]
    new_block = Block(len(self.chain), time(), block_data, self.chain[-1].hash)
    new_block.mine_block(4)
    self.add_block(new_block)

    for tx in self.pending_transactions:
        sender_account = Account(tx.sender)
        sender_account.load()
        recipient_account = Account(tx.recipient)
        recipient_account.load()
        sender_account.balance -= tx.amount
        recipient_account.balance += tx.amount
        sender_account.save()
        recipient_account.save()

    self.pending_transactions = []


class Transaction:
    def __init__(self, sender, recipient, amount, ts):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.ts = ts

    def to_dict(self):
        return {
            'sender': self.sender,
            'recipient': self.recipient,
            'amount': self.amount,
            'timestamp': self.ts
        }

class Account:
    def __init__(self, address, balance):
        self.address = address
        self.balance = 0

    def save(self):
        with Blockchain.connection.cursor() as cursor:
            sql = "INSERT INTO accounts (address, balance) VALUES (%s, %s) ON DUPLICATE KEY UPDATE balance = %s"
            cursor.execute(sql, (self.address, self.balance))
            Blockchain.connection.commit()

    def load(self):
        with Blockchain.connection.cursor() as cursor:
            sql = "SELECT balance FROM accounts WHERE address = %s"
            cursor.execute(sql, (self.address))
            result = cursor.fetchone()
            if result:
                self.balance = result[0]