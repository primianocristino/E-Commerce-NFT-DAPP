// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./IERC20Token.sol";
import "./library/ERC20.sol";
import "./library/utils/math/SafeMath.sol";
import "./library/utils/SafeERC20.sol";

contract ERC20Token is ERC20, IERC20Token {
    using SafeMath for uint256;
    using SafeERC20 for ERC20Token;

    address dex;

    constructor(address parent, uint256 initialSupply) ERC20("ERC20", "ETH") {
        dex = parent;
        _mint(msg.sender, initialSupply);
    }

    /**
     * @dev Function to mint tokens
     * @param to The address that will receive the minted tokens.
     * @param value The amount of tokens to mint.
     
     */
    function mint(address to, uint256 value) external virtual override {
        require(msg.sender == dex, "Cannot increase totalsupply");
        _mint(to, value);
    }

    function burn(address account, uint256 amount) external virtual override {
        require(msg.sender == dex, "Cannot decrease totalsupply");
        _burn(account, amount);
    }

    function minimalIncreaseAllowance(address spender, uint256 addedValue)
        external
        virtual
        override
        returns (bool)
    {
        address owner = msg.sender;
        require(owner != address(this), "dio cane");
        uint256 current_allowance = allowance(owner, spender);
        if (addedValue > current_allowance)
            return increaseAllowance(spender, addedValue - current_allowance);
        return true;
    }
}
