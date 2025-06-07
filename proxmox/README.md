# Proxmox

Here the goal is to set up a server using proxmox. Youtube video series [here](https://www.youtube.com/watch?v=LCjuiIswXGs).

Proxmox is a virtualization platform that allows you to run virtual machines as well as containers.

## Installation process

Go to the downloads [page](https://www.proxmox.com/en/downloads) in Proxmox and download Proxmox VE ISO.
Use [usbimager](https://gitlab.com/bztsrc/usbimager) to create a bootable USB to install Proxmox.
During installation there will be networking configuration (see below). Prior to booting into Proxmox it is useful to find a few of the fields required. Also note when booting up you'll want to enable hardware-accelerated KVM virtualization. On my machine, in the advanced mode of the BIOS screen, go to "CPU Configuration", then enable Intel Virtualization Technology. This could vary, but should be accessible in BIOS.
- Management Interface: this is the network port Proxmox server will use. Wired ethernet is best for stability, this can be found on linux (all commands will be for linux) with `ip a`. Look for something like `enp3s0` or `eth0`
- Hostname (FQDN): FQDN = Fully Qualified Domain Name. This is the name of your Proxmox server (e.g. `pve1.home-network.io`)
- IP Address (CIDR): Look for the value next to `inet` associated with your management interface (from running `ip a`). Look for something like `192.168.1.123/24`. For the last part (here `123`) it is best to choose something outside of your DHCP range (which is typically less than 100).
- Gateway and DNS Server: To find the gateway and dns run: `nmcli device show` look for the lines `IP4.GATEWAY` (e.g. `192.168.1.1`) and `IP4.DNS[1]` (e.g. `192.168.1.1` or `8.8.8.8`)
Now when starting up the machine that will host the Proxmox server, open the boot menu. Boot into UEFI mode if possible. This should start up Proxmox and we can then choose the `Install Proxmox VE` option.
After a bit more setup you will get to the `Management Network Configuration` where you will select the following fields (as explained above): 
- Management Interface
- Hostname (FQDN)
- IP Address (CIDR)
- Gateway
- DNS Server

On the initial reboot into Proxmox it will give you a URL to connect to your server (you should see port 8006). When you go to this, it will ask for a username and password. Use the password that you set up, and `root` for the username.

Once logged into the Proxmox server, it can be shutdown with:
```bash
shutdown now
```
OR
```bash
poweroff
```

Or from the web UI go to `Node -> Shutdown`

## Web console overview

The web console will be accessible on your LAN using the IP address on port 8006 (IP:8006).

On the left sidebar under `Datacenter` you should see the server that was created e.g. `pve1`. Under the `Summary` you can see high level information about the hardware and use on the server. A shell and system setting are also available.

Make sure to install the available updates. You may need to click `Refresh`. Unless you buy the enterprise version this will appear to error out, but it is only due to not being able to connect to the paid repository. After refreshing, you can then click `Upgrade`.

Note there are buttons at the top right to create a new virtual machine and another to create a container.

## VMs or containers?

Containers consume fewer resources, especially RAM. If the host server has less resources then it may be better to go with containers over VMs. Typically if you can get away with using a container, you should since they consume fewer resources. 
One big benefit of VMs is that if you're running a cluster with multiple host servers and you want to migrate a VM to a different host, you can do a live migration and keep the VM running (and any applications it's supporting); whereas with containers they will need to shutdown during a migration. Also note that not all applications will run in a container.

## Launching VMs

- On the top right in the web UI click `Create VM`
- Choose a node (in the case of a single node, there will only be 1 option), an ID (this needs to be unique and it may be nice to have a range for VMs, a range for Containers, a range for VM templates, etc.), and a name which should reflect its purpose.
- Next we will go to OS and we need to select an ISO image, however we currently have none
    - Click the dropdown on your node `pve1` under `Datacenter`, then click on local (pve1), then click on `ISO Images`
    - We will use the `Download from URL` button but we first need to get the URL for the ISO image.
    - Go to [ubuntu.com](ubuntu.com) and navigate to download ubuntu server section and find the URL for the ISO image (ChatGPT or any other LLM with web search can help find this quickly) e.g. https://releases.ubuntu.com/noble/ubuntu-24.04.2-live-server-amd64.iso
    - Copy this URL into the field in `Download from URL` and click `Query URL` and then `Download`
- With the ISO image downloaded we can go back through `Create VM` and now use this ISO image for the OS
- We will use the defaults for the `System` settings
- For `Disks` we will select/check the `Discard` option to help with storage cleanup/management on the underlying hard drive. For the disk size, we will use 16 GB.
- For `CPU` we may want to use more than 1 core for heavier compute applications, especially if it's running slowly, otherwise we can stick with 1.
- For `Memory` we will keep the 2 GB default.
- For now we will also keep the default `Network` settings.

## Creating VM templates
## Launching containers
## Creating container templates
## Managing users
## Backups and snapshots
## Integrated firewall
## CLI
## Networking
## Shared storage
## Clustering
## High availability