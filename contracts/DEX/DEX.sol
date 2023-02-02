// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./ERC20Token.sol";
import "./library/utils/SafeERC20.sol";
import "./ERC721Token.sol";
import "./IDEX.sol";
import "./library/utils/Strings.sol";

contract DEX is IDEX {
    using SafeERC20 for ERC20Token;
    using Strings for address;
    struct ProductInfo {
        bool initialized;
        uint256 price;
        uint256 amount;
        uint256 discount;
        address owner;
        bool is_nft;
        //address buyer;
    }

    ERC20Token public token;
    ERC721Token public token_nft;

    mapping(string => ProductInfo) orders;
    mapping(string => bool) private is_nft;

    address admin;

    event Deposited(uint256 amount);
    event Withdrawn(uint256 amount);
    event Approve(address _from, address _to, uint256 amount);
    event SetProduct(address _from, ProductInfo product_info);
    event Order(address _buyer, ProductInfo[] orders, uint256 total_amount);

    constructor(
        uint256 initialSupply,
        string memory server_protocol,
        string memory server_domain,
        string memory server_port,
        string memory server_api
    ) {
        admin = msg.sender;
        token = new ERC20Token(address(this), initialSupply);
        token_nft = new ERC721Token(
            server_protocol,
            server_domain,
            server_port,
            server_api,
            admin
        );

        //token.mint(address(this), 1000000000000000000 ether);
    }

    function increaseSupply(uint256 amount) external override {
        require(msg.sender == admin, "Cannot increase totalsupply");

        token.mint(address(this), amount);
    }

    function decreaseSupply(uint256 amount) external override {
        require(msg.sender == admin, "Cannot decrease totalsupply");
        token.burn(address(this), amount);
    }

    function addProduct(
        string calldata id,
        uint256 price,
        uint256 amount,
        uint256 discount,
        string calldata metadata
    ) external override {
        require(orders[id].initialized == false, "Product alredy exists");
        require(amount == 0 || amount == 1, "NFT must be one and only");
        require(price >= 0, "Price cannot be negative");
        require(price % 10**10 == 0, "Invalid price");
        require(discount >= 0, "Discount cannot be negative");
        require(
            token_nft.checkAddMetadata(metadata),
            "NFT metadata cannot be added"
        );

        orders[id] = ProductInfo(
            true,
            price,
            amount,
            discount,
            msg.sender,
            true
        );

        token_nft.generateToken(msg.sender, id, metadata);

        emit SetProduct(msg.sender, orders[id]);
    }

    function addProduct(
        string calldata id,
        uint256 price,
        uint256 amount,
        uint256 discount
    ) external override {
        require(orders[id].initialized == false, "Product alredy exists");
        require(amount >= 0, "Amount cannot be negative");
        require(price >= 0, "Price cannot be negative");
        require(price % 10**10 == 0, "Invalid price");
        require(discount >= 0, "Discount cannot be negative");

        orders[id] = ProductInfo(
            true,
            price,
            amount,
            discount,
            msg.sender,
            false
        );

        emit SetProduct(msg.sender, orders[id]);
    }

    function getProduct(string calldata id)
        external
        view
        override
        returns (
            string memory product_id,
            uint256 price,
            uint256 amount,
            uint256 discount,
            address owner,
            bool nft
        )
    {
        require(orders[id].initialized, "Product not found");

        return (
            id,
            orders[id].price,
            orders[id].amount,
            orders[id].discount,
            orders[id].owner,
            orders[id].is_nft
        );
    }

    function editProduct(
        string calldata id,
        uint256 price,
        uint256 amount,
        uint256 discount,
        string calldata metadata
    ) external override {
        require(orders[id].initialized == true, "Product not exists");

        require(
            orders[id].owner == msg.sender,
            string(
                abi.encodePacked(
                    bytes("The caller must be the owner "),
                    abi.encodePacked(
                        bytes(orders[id].owner.toHexString()),
                        abi.encodePacked(
                            bytes(" "),
                            bytes(msg.sender.toHexString())
                        )
                    )
                )
            )
        );

        require(price >= 0, "Price cannot be negative");
        require(price % 10**10 == 0, "Invalid price");
        require(amount == 0 || amount == 1, "NFT must be one and only");
        require(discount >= 0, "Discount cannot be negative");

        require(
            !Strings.equal(metadata, "d41d8cd98f00b204e9800998ecf8427e"),
            "Invalid metadata"
        );
        token_nft.checkEditMetadata(id, metadata);

        orders[id].price = price;
        orders[id].amount = amount;
        orders[id].discount = discount;

        emit SetProduct(msg.sender, orders[id]);
    }

    function editProduct(
        string calldata id,
        uint256 price,
        uint256 amount,
        uint256 discount
    ) external override {
        require(orders[id].initialized == true, "Product not exists");

        require(
            orders[id].owner == msg.sender,
            string(
                abi.encodePacked(
                    bytes("The caller must be the owner "),
                    abi.encodePacked(
                        bytes(orders[id].owner.toHexString()),
                        abi.encodePacked(
                            bytes(" "),
                            bytes(msg.sender.toHexString())
                        )
                    )
                )
            )
        );
        require(amount >= 0, "Amount cannot be negative");
        require(price >= 0, "Price cannot be negative");
        require(price % 10**10 == 0, "Invalid price");
        require(discount >= 0, "Discount cannot be negative");

        orders[id].price = price;
        orders[id].amount = amount;
        orders[id].discount = discount;

        emit SetProduct(msg.sender, orders[id]);
    }

    function deleteProduct(string calldata id) external override {
        require(orders[id].initialized == true, "Product not exists");
        require(
            orders[id].owner == msg.sender || msg.sender == admin,
            "The caller must be the owner or the admin"
        );

        if (orders[id].is_nft == true) token_nft.burn(msg.sender, id);

        delete orders[id];

        emit SetProduct(msg.sender, orders[id]);
    }

    function getTotalCostCart(
        string[] calldata ids,
        uint256[] calldata ids_amount
    ) public view returns (uint256) {
        uint256 amountTobuy = 0;

        for (uint256 i = 0; i < ids.length; i++) {
            require(ids_amount[i] > 0, "Amount cannot be 0");
            require(orders[ids[i]].initialized == true, "Product not exists");
            require(orders[ids[i]].amount > 0, "Product is out of order");
            require(
                orders[ids[i]].amount >= ids_amount[i],
                "Not enough products"
            );
            uint256 price = orders[ids[i]].price;
            uint256 discount = orders[ids[i]].discount;
            amountTobuy += (price - (price * discount) / 100) * ids_amount[i];
        }
        return amountTobuy;
    }

    function buyProducts(string[] calldata ids, uint256[] calldata ids_amount)
        external
        override
    {
        uint256 amountToBuy = getTotalCostCart(ids, ids_amount);

        require(
            amountToBuy <= token.balanceOf(msg.sender),
            "Insufficient funds"
        );

        ProductInfo[] memory local_bought_items = new ProductInfo[](ids.length);
        for (uint256 i = 0; i < ids.length; i++) {
            require(
                orders[ids[i]].owner != msg.sender,
                "Cannot buy your own product"
            );

            uint256 price = orders[ids[i]].price;
            uint256 discount = orders[ids[i]].discount;
            uint256 final_price = (price - (price * discount) / 100) *
                ids_amount[i];

            token.safeTransferFrom(
                msg.sender,
                orders[ids[i]].owner,
                ids_amount[i] * final_price
            );

            if (orders[ids[i]].is_nft) {
                uint256 tokenId = token_nft.getTokenID(ids[i]);
                bytes memory data = token_nft.bytesTokenURI(tokenId);

                token_nft.safeTransferFrom(
                    orders[ids[i]].owner,
                    msg.sender,
                    tokenId,
                    data
                );
                orders[ids[i]].owner = msg.sender;
            }

            orders[ids[i]].amount -= ids_amount[i];

            local_bought_items[i] = orders[ids[i]];
        }
        emit Order(msg.sender, local_bought_items, amountToBuy);
    }

    function deposit() external payable override {
        uint256 amountTobuy = msg.value;
        uint256 dexBalance = token.balanceOf(address(this));
        require(amountTobuy > 0, "You need to send some ether");
        require(amountTobuy <= dexBalance, "Not enough tokens in the reserve");
        token.safeTransfer(msg.sender, amountTobuy);

        emit Deposited(amountTobuy);
    }

    function withdraw(uint256 amount) external override {
        require(amount > 0, "Devi vendere almeno qualche token");
        uint256 allowance = token.allowance(msg.sender, address(this));
        require(allowance >= amount, "Verifica l'indennita' del token");
        token.safeTransferFrom(msg.sender, address(this), amount);
        payable(msg.sender).transfer(amount);

        emit Withdrawn(amount);
    }

    function getBalance(address account)
        external
        view
        override
        returns (uint256)
    {
        return token.balanceOf(account);
    }

    function uint2str(uint256 i) internal pure returns (string memory str) {
        if (i == 0) return "0";
        uint256 j = i;
        uint256 length;
        while (j != 0) {
            length++;
            j /= 10;
        }
        bytes memory bstr = new bytes(length);
        uint256 k = length - 1;
        while (i != 0) {
            bstr[k--] = bytes1(uint8(48 + (i % 10)));
            i /= 10;
        }
        str = string(bstr);
    }

    function getAllowance(address owner, address delegate)
        external
        view
        override
        returns (uint256)
    {
        return token.allowance(owner, delegate);
    }

    function getToken() external view override returns (IERC20) {
        return token;
    }

    function getTokenNft() external view returns (ERC721) {
        return token_nft;
    }

    function balanceOf(address tokenOwner)
        external
        view
        override
        returns (uint256)
    {
        return token.balanceOf(tokenOwner);
    }

    function getURI(string calldata productID)
        external
        view
        override
        returns (string memory)
    {
        return token_nft.getURI(productID);
    }
}
