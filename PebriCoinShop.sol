// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract PebriCoinShop {
    string public name = "Pebri Coin";
    string public symbol = "PEBRI";
    uint8 public decimals = 0; // 0 decimals to make calculations transparent and easy for students to follow
    
    address public owner;
    
    // Product details
    string public productName = "Buku Belajar Smart-Contract Pemula";
    uint256 public productPrice = 10; // 10 PEBRI
    uint256 public productStock = 100;
    
    mapping(address => uint256) public balanceOf;
    
    event Transfer(address indexed from, address indexed to, uint256 value);
    event Purchase(address indexed buyer, string product, uint256 quantity, uint256 totalCost);
    event StockUpdated(uint256 newStock);
    event CoinsMinted(address indexed to, uint256 amount);

    modifier onlyOwner() {
        require(msg.sender == owner, "Hanya Owner yang dapat melakukan ini");
        _;
    }

    constructor() {
        owner = msg.sender;
        balanceOf[owner] = 1000; // Owner gets initial supply
        emit CoinsMinted(owner, 1000);
    }

    function mint(address to, uint256 amount) public onlyOwner {
        balanceOf[to] += amount;
        emit CoinsMinted(to, amount);
        emit Transfer(address(0), to, amount);
    }

    function beliBarang(uint256 quantity) public {
        require(quantity > 0, "Jumlah pembelian harus lebih dari 0");
        require(productStock >= quantity, "Stok tidak mencukupi");
        
        uint256 totalCost = productPrice * quantity;
        require(balanceOf[msg.sender] >= totalCost, "Saldo Pebri Coin Anda tidak mencukupi");
        
        // Deduct buyer's balance, add to owner's balance
        balanceOf[msg.sender] -= totalCost;
        balanceOf[owner] += totalCost;
        
        // Deduct stock
        productStock -= quantity;
        
        emit Transfer(msg.sender, owner, totalCost);
        emit Purchase(msg.sender, productName, quantity, totalCost);
        emit StockUpdated(productStock);
    }
    
    function refillStock(uint256 amount) public onlyOwner {
        productStock += amount;
        emit StockUpdated(productStock);
    }
    
    function setProductDetails(string memory newName, uint256 newPrice) public onlyOwner {
        productName = newName;
        productPrice = newPrice;
    }
}
