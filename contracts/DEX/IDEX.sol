// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./library/IERC20.sol";

interface IDEX {
    function increaseSupply(uint256 amount) external;

    function decreaseSupply(uint256 amount) external;

    function addProduct(
        string calldata id,
        uint256 price,
        uint256 amount,
        uint256 discount,
        string calldata metadata
    ) external;

    function addProduct(
        string calldata id,
        uint256 price,
        uint256 amount,
        uint256 discount
    ) external;

    function getProduct(string calldata id)
        external
        view
        returns (
            string memory product_id,
            uint256 price,
            uint256 amount,
            uint256 discount,
            address builder,
            bool nft
        );

    function editProduct(
        string calldata id,
        uint256 price,
        uint256 amount,
        uint256 discount,
        string calldata metadata
    ) external;

    function editProduct(
        string calldata id,
        uint256 price,
        uint256 amount,
        uint256 discount
    ) external;

    function deleteProduct(string calldata id) external;

    function buyProducts(string[] calldata ids, uint256[] calldata ids_amount)
        external;

    function deposit() external payable;

    function withdraw(uint256 amount) external;

    function getBalance(address account) external view returns (uint256);

    function getAllowance(address owner, address delegate)
        external
        view
        returns (uint256);

    function getToken() external view returns (IERC20);

    function balanceOf(address tokenOwner) external view returns (uint256);

    function getURI(string calldata productID)
        external
        view
        returns (string memory);
}
