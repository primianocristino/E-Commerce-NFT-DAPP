// SPDX-License-Identifier: MIT
import "./library/IERC20.sol";

pragma solidity ^0.8.0;

interface IERC20Token is IERC20 {
    function mint(address to, uint256 value) external;

    function burn(address account, uint256 amount) external;

    function minimalIncreaseAllowance(address spender, uint256 addedValue)
        external
        returns (bool);
}
