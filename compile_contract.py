import json
import os
import sys

def main():
    print("Installing python compilation dependencies (py-solc-x)...")
    # Install py-solc-x
    os.system(f"{sys.executable} -m pip install py-solc-x")
    
    try:
        import solcx
    except ImportError:
        print("Failed to import py-solc-x. Please install it manually: pip install py-solc-x")
        sys.exit(1)
        
    print("Installing Solidity compiler v0.8.20...")
    try:
        solcx.install_solc('0.8.20')
    except Exception as e:
        print(f"Failed to install solc compiler: {e}")
        print("If you are offline, you can use the pre-compiled contract_data.json file.")
    
    print("Compiling PebriCoinShop.sol...")
    try:
        contract_path = 'PebriCoinShop.sol'
        if not os.path.exists(contract_path):
            print(f"Error: {contract_path} not found.")
            sys.exit(1)
            
        compiled_sol = solcx.compile_files(
            [contract_path],
            output_values=['abi', 'bin'],
            solc_version='0.8.20',
            evm_version='paris'
        )
        
        contract_key = 'PebriCoinShop.sol:PebriCoinShop'
        if contract_key not in compiled_sol:
            # Try just the class name or check keys
            keys = list(compiled_sol.keys())
            contract_key = [k for k in keys if 'PebriCoinShop' in k][0]
            
        contract_interface = compiled_sol[contract_key]
        
        data = {
            "abi": contract_interface['abi'],
            "bytecode": contract_interface['bin']
        }
        
        with open("contract_data.json", "w") as f:
            json.dump(data, f, indent=4)
            
        print("Compilation successful! Saved ABI and Bytecode to contract_data.json")
    except Exception as e:
        print(f"Compilation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
