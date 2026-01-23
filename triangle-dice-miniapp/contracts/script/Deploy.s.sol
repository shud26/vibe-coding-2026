// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {Script, console} from "forge-std/Script.sol";
import {MockUSDC} from "../src/MockUSDC.sol";
import {TriangleDiceEscrow} from "../src/TriangleDiceEscrow.sol";

contract DeployScript is Script {
    function run() external {
        uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");
        address feeCollector = vm.envAddress("FEE_COLLECTOR");

        vm.startBroadcast(deployerPrivateKey);

        // Deploy MockUSDC
        MockUSDC usdc = new MockUSDC();
        console.log("MockUSDC deployed at:", address(usdc));

        // Deploy TriangleDiceEscrow
        TriangleDiceEscrow escrow = new TriangleDiceEscrow(address(usdc), feeCollector);
        console.log("TriangleDiceEscrow deployed at:", address(escrow));

        // Mint some test USDC to deployer
        usdc.mint(msg.sender, 1000_000_000); // 1000 USDC
        console.log("Minted 1000 USDC to deployer");

        vm.stopBroadcast();

        // Output for frontend config
        console.log("\n=== Frontend Config ===");
        console.log("VITE_USDC_ADDRESS=", address(usdc));
        console.log("VITE_ESCROW_ADDRESS=", address(escrow));
    }
}

contract DeployWithExistingUSDC is Script {
    function run() external {
        uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");
        address feeCollector = vm.envAddress("FEE_COLLECTOR");
        address usdcAddress = vm.envAddress("USDC_ADDRESS");

        vm.startBroadcast(deployerPrivateKey);

        // Deploy TriangleDiceEscrow with existing USDC
        TriangleDiceEscrow escrow = new TriangleDiceEscrow(usdcAddress, feeCollector);
        console.log("TriangleDiceEscrow deployed at:", address(escrow));

        vm.stopBroadcast();
    }
}
