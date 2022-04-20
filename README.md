# pve-spice-manager
An executable and python script to quickly open SPICE terminals.

You must have virt-viewer installed for this to work, you can download it here: https://virt-manager.org/download/ Make sure to download virt-viewer and not virt-manager.
 
Downloads: [https://github.com/realdeadbeef/pve-spice-manager/releases](https://github.com/realdeadbeef/pve-spice-manager/releases)

Setup:  
1. Add a new user in Datacenter > Permissions > Users > Add.
2. Fill out the required fields making sure to change the realm to Proxmox VE Authentication Server unless you know why you need to change this.
3. Add a new resource pool to contain SPICE enabled VMs in Datacenter > Permissions > Pools > Create.
4. Give the pool a name like SPICE-Servers.
5. Add a new role to be assigned to your user which gives them the nessecary permissions in Datacenter > Permissions > Roles > Create.
6. Give the role a name like SPICE-Role and assign the following permissions: `Pool.Audit, VM.Console, VM.Config.CDROM, VM.PowerMgmt`.
7. Now assign the role to your new user by going to Datacenter > Permissions > Add > User.
8. The path should be set to `/pool/<your-pool-name>`, the user should be set to the user you created, the role should be set to the one you created and the propagate checkbox should be enabled.
9. Now select your pool from the left hand side and go to members.
10. Add the VMs you wish to be in this pool.
11. Done!  

Note: For a VM to support SPICE, it must first be enabled on the VM. To do this, go to the desired VM's hardware configuration and change the display to SPICE.

For sound: To use sound you need to add it in the VM's hardware settings. To do this, go to desired VM's hardware configuration and click on add, select audio device, don't change the audio device unless you know what you're doing and make sure the backend driver is set to SPICE.
