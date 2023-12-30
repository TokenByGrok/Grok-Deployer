import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import requests
from requests.structures import CaseInsensitiveDict
import json
import re
import time
from solcx import compile_standard, install_solc
from web3 import Web3
from eth_account import Account
import sys
import requests
sys.set_int_max_str_digits(0)

#chromedriver_autoinstaller.install()
driver=webdriver.Chrome()
driver.get("https://twitter.com/i/flow/login?redirect_after_login=%2Fi/grok")


def Grok():
    print("========================================\n\nWelcome to GROK AI Deployer\n\nPlease Log In with a Premium X account that has access to Grok\n\nThe next steps will be automated\n\n========================================")
    try:
        input_element = WebDriverWait(driver,300).until(
            EC.presence_of_element_located((By.XPATH, "//textarea[@placeholder='Grok something']"))
            )
        print("Starting the Conversation")
        
        #driver.minimize_window()
        
        input_element.send_keys("Give me a catchy name for a memecoin, should be a single word. It will be deployed on Ethereum Network. Get inspiration from all the trending memecoins and give me a cool funny name.You will only respond with the name , without any detail emojis symbols or description")
       
        time.sleep(1)
    except Exception as e:
        print(e)
        print("INFO:TIMEOUT GROK INPUT FIELD")
     
    submit = driver.find_element(By.XPATH, "//div[@aria-label='Grok something']")
    submit.click()

    try:
        time.sleep(5)
        coin_name = driver.find_element(By.XPATH, '//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div/div/div[3]/div[1]/div/div/div[2]/div/div/div[2]/div/div[2]/div/span/span').get_attribute('innerHTML')
        coin_name=re.sub(r'[^\w]', '', coin_name)
        print("Name:", coin_name)
    except Exception as e:
        print(e)
        print("Something went wrong while getting name")
        
    time.sleep(1)    
       
    input_element.send_keys("Give me a symbol shorter than 5 letters for my memecoin above.You will only respond with the name using letters and maybe numbers, without any details. Do not use long description in the message")
    time.sleep(1)
    submit.click()

        
    try:
        time.sleep(5)
        coin_symbol = driver.find_element(By.XPATH, '//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div/div/div[3]/div[1]/div/div/div[4]/div/div/div[2]/div/div[2]/div/span/span').get_attribute('innerHTML')
        coin_symbol=re.sub(r'[^\w]', '', coin_symbol)
        print("Symbol:", coin_symbol)
    except Exception as e:
        print(e)
        print("Something went wrong getting symbol")

    time.sleep(1)
    input_element.send_keys("Come up with an image description for my coin. Do not use emojis")
    time.sleep(1)
    submit.click()

    try:
        time.sleep(10)
        coin_description = driver.find_element(By.XPATH, '//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div/div/div[3]/div[1]/div/div/div[6]/div/div/div[2]/div/div[2]/div/span/span').get_attribute('innerHTML')
        print("Description:", coin_description)
    except Exception as e:
        print(e)
        print("Something went wrong getting coin description")

    time.sleep(1)
    input_element.send_keys("What should be the total supply? Respond only with the number, no letters, no symbols, no emojis. Format the response as a number smaller than 10 million")
    time.sleep(1)
    submit.click()
        
    try:
        time.sleep(5)
        coin_supply = driver.find_element(By.XPATH, '//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div/div/div[3]/div[1]/div/div/div[8]/div/div/div[2]/div/div[2]/div/span/span').get_attribute('innerHTML')
        formattedsupply=coin_supply
        formattedsupply=re.sub(r'[^\w]', '', formattedsupply)
        formattedsupply=int(formattedsupply)
        print("Supply:", formattedsupply)
    except Exception as e:
        print(e)
        print("went wrong")

    time.sleep(2)
    driver.quit()
    
    return coin_name,coin_symbol,formattedsupply,coin_description
    
    
def genImage(coin_description):
    #time to get image
    print("===========\nGenerating Logo\n===========")
    url = "https://api.openai.com/v1/images/generations"

    headers = CaseInsensitiveDict()
    headers["Content-Type"] = "application/json"
    headers["Authorization"] = "Bearer OPENAI_KEY"

    imgprompt="'"+coin_description+"'"
    imgprompt=re.sub(r'[^\w]', ' ', imgprompt)

    data = '{"model": "dall-e-3","prompt": "'+imgprompt+'","n": 1, "size": "1024x1024"}'


    resp = requests.post(url, headers=headers, data=data)
    imgurl=json.loads(resp.text)
    return imgurl['data'][0]['url']
    
def deploy_coin(thename,thesymbol,coin_supply):
    
    print(coin_supply)
    coin_supply=coin_supply*pow(10,9)
    print(coin_supply)
    

    #use this contract as base
    with open("ca_file.sol", "r") as file:
        ca_source = file.read()

    install_solc("0.8.19")

    compiled_sol = compile_standard(
        {
            "language": "Solidity",
            "sources": {"ca_file.sol": {"content": ca_source}},
            "settings": {
                "outputSelection": {
                    "*": {
                        "*": [
                            "abi",
                            "metadata",
                            "evm.bytecode",
                            "evm.bytecode.sourceMap",
                        ]  # output needed to interact with and deploy contract
                    }
                }
            },
        },
        solc_version="0.8.19",
    )

    # get bytecode
    bytecode = compiled_sol["contracts"]["ca_file.sol"]["GrokIsDev"]["evm"][
        "bytecode"
    ]["object"]

    # get abi
    abi = json.loads(
        compiled_sol["contracts"]["ca_file.sol"]["GrokIsDev"]["metadata"]
    )["output"]["abi"]


    '''
    chain_id = 5
    w3 = Web3(Web3.HTTPProvider("https://gateway.tenderly.co/public/goerli"))
    private_key = (
        "PRIVATE_KEY"
    )  # leaving the private key like this is very insecure if you are working on real world project
    acct = Account.from_key(private_key)
    address=acct.address

    print(address)

    '''

    w3 = Web3(Web3.HTTPProvider("https://rpc.ankr.com/eth"))
    chain_id = 1
    private_key = (
        "PRIVATE_KEY"
    )  # leaving the private key like this is very insecure if you are working on real world project
    acct = Account.from_key(private_key)
    address=acct.address
    

    usegas=w3.eth.gas_price+15/100*w3.eth.gas_price
    print(usegas*pow(10,-9))
    print("Abort if gas too high")


    time.sleep(1)


    # Create the contract in Python
    ca_file = w3.eth.contract(abi=abi, bytecode=bytecode)
    # Get the latest transaction
    nonce = w3.eth.get_transaction_count(address)
    # build transaction

    
    transaction = ca_file.constructor(str(thename),str(thesymbol),int(coin_supply)).build_transaction(
        {
        "chainId": chain_id, 
        "gasPrice": int(usegas), 
        "from": address, 
        "nonce": nonce
        }
    )



    estimate = w3.eth.estimate_gas(transaction)
    print("ESTIMATED GAS COST - " + str(estimate*usegas*pow(10,-18))+" ETH")

    for a in range(0,10):
        time.sleep(1)
        print("Deploying in " + str(10-a))

    # Sign the transaction
    sign_transaction = w3.eth.account.sign_transaction(transaction, private_key=private_key)
    print("Deploying Contract!")

    # Send the transaction
    transaction_hash = w3.eth.send_raw_transaction(sign_transaction.rawTransaction)

    # Wait for the transaction to be mined, and get the transaction receipt
    print("TX Hash " + str(transaction_hash.hex()))
    print("Waiting for transaction to finish...")
    transaction_receipt = w3.eth.wait_for_transaction_receipt(transaction_hash,timeout=240)
    print(f"Done! Contract deployed to {transaction_receipt.contractAddress}")
    coin_ca=transaction_receipt.contractAddress

    time.sleep(2)

    #start adding lp
    UniRouterV2 = '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D'

    #pancakeswap router abi 
    panabi = '[{"inputs":[{"internalType":"address","name":"_factory","type":"address"},{"internalType":"address","name":"_WETH","type":"address"}],"stateMutability":"nonpayable","type":"constructor"},{"inputs":[],"name":"WETH","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"tokenA","type":"address"},{"internalType":"address","name":"tokenB","type":"address"},{"internalType":"uint256","name":"amountADesired","type":"uint256"},{"internalType":"uint256","name":"amountBDesired","type":"uint256"},{"internalType":"uint256","name":"amountAMin","type":"uint256"},{"internalType":"uint256","name":"amountBMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"addLiquidity","outputs":[{"internalType":"uint256","name":"amountA","type":"uint256"},{"internalType":"uint256","name":"amountB","type":"uint256"},{"internalType":"uint256","name":"liquidity","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"amountTokenDesired","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"addLiquidityETH","outputs":[{"internalType":"uint256","name":"amountToken","type":"uint256"},{"internalType":"uint256","name":"amountETH","type":"uint256"},{"internalType":"uint256","name":"liquidity","type":"uint256"}],"stateMutability":"payable","type":"function"},{"inputs":[],"name":"factory","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"uint256","name":"reserveIn","type":"uint256"},{"internalType":"uint256","name":"reserveOut","type":"uint256"}],"name":"getAmountIn","outputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"}],"stateMutability":"pure","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"reserveIn","type":"uint256"},{"internalType":"uint256","name":"reserveOut","type":"uint256"}],"name":"getAmountOut","outputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"}],"stateMutability":"pure","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"}],"name":"getAmountsIn","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"}],"name":"getAmountsOut","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountA","type":"uint256"},{"internalType":"uint256","name":"reserveA","type":"uint256"},{"internalType":"uint256","name":"reserveB","type":"uint256"}],"name":"quote","outputs":[{"internalType":"uint256","name":"amountB","type":"uint256"}],"stateMutability":"pure","type":"function"},{"inputs":[{"internalType":"address","name":"tokenA","type":"address"},{"internalType":"address","name":"tokenB","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountAMin","type":"uint256"},{"internalType":"uint256","name":"amountBMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"removeLiquidity","outputs":[{"internalType":"uint256","name":"amountA","type":"uint256"},{"internalType":"uint256","name":"amountB","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"removeLiquidityETH","outputs":[{"internalType":"uint256","name":"amountToken","type":"uint256"},{"internalType":"uint256","name":"amountETH","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"removeLiquidityETHSupportingFeeOnTransferTokens","outputs":[{"internalType":"uint256","name":"amountETH","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"},{"internalType":"bool","name":"approveMax","type":"bool"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"removeLiquidityETHWithPermit","outputs":[{"internalType":"uint256","name":"amountToken","type":"uint256"},{"internalType":"uint256","name":"amountETH","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"},{"internalType":"bool","name":"approveMax","type":"bool"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"removeLiquidityETHWithPermitSupportingFeeOnTransferTokens","outputs":[{"internalType":"uint256","name":"amountETH","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"tokenA","type":"address"},{"internalType":"address","name":"tokenB","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountAMin","type":"uint256"},{"internalType":"uint256","name":"amountBMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"},{"internalType":"bool","name":"approveMax","type":"bool"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"removeLiquidityWithPermit","outputs":[{"internalType":"uint256","name":"amountA","type":"uint256"},{"internalType":"uint256","name":"amountB","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapETHForExactTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactETHForTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactETHForTokensSupportingFeeOnTransferTokens","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactTokensForETH","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactTokensForETHSupportingFeeOnTransferTokens","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactTokensForTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactTokensForTokensSupportingFeeOnTransferTokens","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"uint256","name":"amountInMax","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapTokensForExactETH","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"uint256","name":"amountInMax","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapTokensForExactTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"},{"stateMutability":"payable","type":"receive"}]'

    #Deployed Token ABI
    abi = '[{"constant":true,"inputs":[],"name":"name","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"spender","type":"address"},{"name":"tokens","type":"uint256"}],"name":"approve","outputs":[{"name":"success","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"totalSupply","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"from","type":"address"},{"name":"to","type":"address"},{"name":"tokens","type":"uint256"}],"name":"transferFrom","outputs":[{"name":"success","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"_totalSupply","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"tokenOwner","type":"address"}],"name":"balanceOf","outputs":[{"name":"balance","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"a","type":"uint256"},{"name":"b","type":"uint256"}],"name":"safeSub","outputs":[{"name":"c","type":"uint256"}],"payable":false,"stateMutability":"pure","type":"function"},{"constant":false,"inputs":[{"name":"to","type":"address"},{"name":"tokens","type":"uint256"}],"name":"transfer","outputs":[{"name":"success","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"a","type":"uint256"},{"name":"b","type":"uint256"}],"name":"safeDiv","outputs":[{"name":"c","type":"uint256"}],"payable":false,"stateMutability":"pure","type":"function"},{"constant":true,"inputs":[{"name":"a","type":"uint256"},{"name":"b","type":"uint256"}],"name":"safeMul","outputs":[{"name":"c","type":"uint256"}],"payable":false,"stateMutability":"pure","type":"function"},{"constant":true,"inputs":[{"name":"tokenOwner","type":"address"},{"name":"spender","type":"address"}],"name":"allowance","outputs":[{"name":"remaining","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"a","type":"uint256"},{"name":"b","type":"uint256"}],"name":"safeAdd","outputs":[{"name":"c","type":"uint256"}],"payable":false,"stateMutability":"pure","type":"function"},{"inputs":[],"payable":false,"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"name":"from","type":"address"},{"indexed":true,"name":"to","type":"address"},{"indexed":false,"name":"tokens","type":"uint256"}],"name":"Transfer","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"tokenOwner","type":"address"},{"indexed":true,"name":"spender","type":"address"},{"indexed":false,"name":"tokens","type":"uint256"}],"name":"Approval","type":"event"}]'

    sender_address = address #TokenAddress of holder
    weth = w3.to_checksum_address("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2")  #weth Address

    #Create Instance of Pancakerouter Address Contract
    contract = w3.eth.contract(UniRouterV2, abi=panabi)

    #Create instance of deployed smart contract
    tokenAddress = w3.to_checksum_address(transaction_receipt.contractAddress)  #Contract address
    token = w3.eth.contract(tokenAddress, abi=abi)

     #Approve Token before adding Liquidity

    totalSupply = token.functions.totalSupply().call()

    usegas=w3.eth.gas_price+15/100*w3.eth.gas_price
    #start = time.time()
    approve = token.functions.approve(UniRouterV2, totalSupply).build_transaction({
              'from': sender_address,
              'gasPrice': int(usegas),
              'nonce': nonce+1,
              })

    signed_txn = w3.eth.account.sign_transaction(approve, private_key=private_key)
    tx_token = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    print("Approving...")
    transaction_receipt = w3.eth.wait_for_transaction_receipt(tx_token,timeout=240)
    print("Approved: " + w3.to_hex(tx_token))

    time.sleep(2)

    #Creating Liquidity pair

    amountTokenDesired = totalSupply-1
    amountTokenMin = totalSupply-2
    amountETHMin = 100000000000000000000
    to = sender_address
    deadline = int(time.time()) + 1000000

    usegas=w3.eth.gas_price+15/100*w3.eth.gas_price
    addliq = contract.functions.addLiquidityETH(
        tokenAddress,amountTokenDesired, amountTokenMin, amountETHMin, to, deadline
    ).build_transaction({
                'from': sender_address,
                'value': w3.to_wei('1', 'ether'),
                'gasPrice': int(usegas),
                'nonce': nonce+2,
                })


    signed_txn = w3.eth.account.sign_transaction(addliq, private_key=private_key)
    tx_token = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    print("Creating lp at: " + str(w3.to_hex(tx_token)))
    transaction_receipt = w3.eth.wait_for_transaction_receipt(tx_token,timeout=240)
    print("Liquidity added. Token should be live! " + str(w3.to_hex(tx_token)))
    
    print("\n===========\nSummary\n-Your coin address:",coin_ca)
    

from_Grok=Grok()
imageurl=genImage(from_Grok[3])
deploy_coin(from_Grok[0],from_Grok[1],from_Grok[2])
    
print("-Coin Name:",from_Grok[0])
print("-Coin Symbol:",from_Grok[1])
print("-Coin Supply:",from_Grok[2])

img_data = requests.get(imageurl).content
img_name=from_Grok[0] + ".jpg"
with open(img_name, 'wb') as handler:
    handler.write(img_data)
print("The image was saved in the current folder\nYou can verify your contract on etherscan using the content from ca_file.sol")