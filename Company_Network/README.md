# Multi-Department Enterprise Network Design

##  Project Overview
This project demonstrates the design and implementation of a segmented corporate network using **Cisco Packet Tracer**. The architecture provides departmental isolation through VLANs while maintaining seamless inter-departmental communication and centralized network services via a "Router-on-a-Stick" configuration.

##  Key Features & Technologies
* **VLAN Segmentation**: Logically divided the network into three departments: **IT/Admin (VLAN 10)**, **HR/Finance (VLAN 20)**, and **Sales/Reception (VLAN 30)**.
* **Inter-VLAN Routing**: Implemented sub-interfaces on a Cisco 1941 Router to allow communication across different subnets.
* **Centralized DHCP Service**: Configured a single server to dynamically assign IP addresses to wired and wireless devices across all VLANs.
* **DHCP Relay (IP Helper)**: Applied `ip helper-address` commands to forward DHCP requests from broadcast domains to the management server.
* **Wireless Infrastructure**: Deployed Access Points to provide mobility for laptops and smartphones within their assigned VLAN environments.

##  Network Topology
The network consists of a central 2960 Switch, a 1941 Router, a Windows-based Server, and various end-devices including PCs, Laptops, and Smartphones.



##  Configuration Highlights

### 1. Switching & Trunking
Ports were assigned to specific access VLANs, and the router link was configured as an 802.1Q Trunk.

### 2. Router-on-a-Stick (Inter-VLAN Routing)
Virtual sub-interfaces were created on the router to act as the Default Gateway for each department. 

### 3. Centralized DHCP Server Configuration
The server was configured with distinct pools to automate IP management across the network.

### in summary
Network Design Project: Multi-VLAN Enterprise Infrastructure

Designed and deployed a segmented network for three departments using VLANs and Router-on-a-Stick architecture in Cisco Packet Tracer.

Configured a centralized DHCP Server and implemented IP Helper-Address (DHCP Relay) on a Cisco 1941 Router to provide dynamic addressing across multiple subnets.

Optimized network traffic and security by implementing 802.1Q Trunking and successfully verified full inter-VLAN connectivity via end-to-end ping testing.