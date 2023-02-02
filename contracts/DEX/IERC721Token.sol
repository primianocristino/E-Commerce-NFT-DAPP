// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface IERC721Token {
    function checkEditMetadata(
        string calldata product_id,
        string calldata metadata
    ) external;

    function checkAddMetadata(string calldata metadata)
        external
        view
        returns (bool);

    function getServerData()
        external
        view
        returns (
            string memory,
            string memory,
            string memory,
            string memory
        );

    function getTokenID(string calldata productID)
        external
        view
        returns (uint256);

    function getURI(string calldata productID)
        external
        view
        returns (string memory);

    function generateToken(
        address owner,
        string calldata product_id,
        string calldata metadata
    ) external;

    function burn(address owner, string calldata product_id) external;
}
