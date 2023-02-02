// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./library/ERC721.sol";
import "./IERC721Token.sol";
import "./library/utils/Strings.sol";

contract ERC721Token is ERC721, IERC721Token {
    struct TokenCheck {
        string hashMetadata;
        bool exists;
    }

    using Strings for uint256;
    //using Strings for address;

    mapping(string => uint256) private _product2token;
    mapping(uint256 => string) private _token2product;

    mapping(uint256 => string) private _token2metadata;
    // mapping(string => uint256) private _metadata2token;

    mapping(string => TokenCheck) private _metadata2hashInfo;

    uint256 count;
    string private protocol;
    string private domain;
    string private api;
    string private port;
    address private admin;
    address private parent;

    constructor(
        string memory server_protocol,
        string memory server_domain,
        string memory server_port,
        string memory server_api,
        address server_admin
    ) ERC721("ERC721-NFT", "NFT") {
        count = 0;
        admin = server_admin;
        parent = msg.sender;
        setServerData(server_protocol, server_domain, server_port, server_api);
    }

    /*
    function getMetadataHash(string calldata product_id)
        public
        view
        returns (string memory)
    {
        uint256 tokenID = _product2token[product_id];
        return _token2hash[tokenID];
    }
    */

    function buildHashMetadata(
        string calldata product_id,
        string calldata metadata
    ) internal pure returns (string memory) {
        string memory pdim = string(abi.encodePacked(product_id, metadata));
        bytes32 kecca_output = keccak256(abi.encodePacked(pdim));
        return Strings.toHexString(uint256(kecca_output), 32);
    }

    function checkEditMetadata(
        string calldata product_id,
        string calldata metadata
    ) external override {
        uint256 tokenID = _product2token[product_id];
        string memory oldMetadata = _token2metadata[tokenID];
        require(_metadata2hashInfo[oldMetadata].exists, "NFT doesn't exists");

        require(
            !_metadata2hashInfo[metadata].exists ||
                Strings.equal(oldMetadata, metadata),
            "NFT is duplicated"
        );
        delete _metadata2hashInfo[oldMetadata];

        string memory newHashMetadata = buildHashMetadata(product_id, metadata);
        _metadata2hashInfo[metadata].hashMetadata = newHashMetadata;
        _metadata2hashInfo[metadata].exists = true;
        _token2metadata[tokenID] = metadata;
    }

    function checkAddMetadata(string calldata metadata)
        external
        view
        override
        returns (bool)
    {
        //string memory hashMetadata = buildHashMetadata(product_id, metadata);
        return !_metadata2hashInfo[metadata].exists;
    }

    //////////////////////////////////////////////////////////////////////////////

    function setServerData(
        string memory server_protocol,
        string memory server_domain,
        string memory server_port,
        string memory server_api
    ) public {
        require(msg.sender != address(0), "No valid caller");
        require(
            msg.sender == admin ||
                msg.sender == address(this) ||
                msg.sender == parent,
            "Caller cannot set these parameters"
        );

        protocol = server_protocol;
        domain = server_domain;
        port = server_port;
        api = server_api;
    }

    function getServerData()
        external
        view
        override
        returns (
            string memory,
            string memory,
            string memory,
            string memory
        )
    {
        return (protocol, domain, port, api);
    }

    //////////////////////////////////////////////////////////////////////////////

    function getTokenID(string calldata productID)
        external
        view
        override
        returns (uint256)
    {
        uint256 tokenID = _product2token[productID];
        _requireMinted(tokenID);
        return tokenID;
    }

    function getURI(string calldata productID)
        external
        view
        override
        returns (string memory)
    {
        return tokenURI(_product2token[productID]);
    }

    function bytesTokenURI(uint256 tokenID) public view returns (bytes memory) {
        _requireMinted(tokenID);
        //string memory product_id = _token2product[tokenID];

        string memory metadata = _token2metadata[tokenID];
        return
            abi.encodePacked(
                protocol,
                "://",
                domain,
                ":",
                port,
                "/",
                api,
                // "?id=",
                // product_id,
                "?meta=",
                _metadata2hashInfo[metadata].hashMetadata
            );
    }

    function tokenURI(uint256 tokenID)
        public
        view
        virtual
        override
        returns (string memory)
    {
        return string(bytesTokenURI(tokenID));
    }

    //////////////////////////////////////////////////////////////////

    function generateToken(
        address owner,
        string calldata product_id,
        string calldata metadata
    ) external override {
        require(owner != address(0), "No usable owner");

        _product2token[product_id] = ++count;
        uint256 token_id = _product2token[product_id];
        _mint(owner, token_id);
        _token2product[token_id] = product_id;

        string memory hashMetadata = buildHashMetadata(product_id, metadata);

        _metadata2hashInfo[metadata].exists = true;
        _metadata2hashInfo[metadata].hashMetadata = hashMetadata;
        _token2metadata[token_id] = metadata;
    }

    function burn(address owner, string calldata product_id) external override {
        require(owner != address(0), "NFT owner cannot be ERC721");
        require(
            owner == admin || owner == ownerOf(_product2token[product_id]),
            "No valid owner"
        );

        uint256 tokenID = _product2token[product_id];
        string memory metadata = _token2metadata[tokenID];
        _burn(tokenID);

        delete _metadata2hashInfo[metadata];
        delete _token2metadata[tokenID];

        delete _product2token[product_id];
        delete _token2product[tokenID];
    }
}
