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

## Web console overview
## VMs or containers?
## Launching VMs
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