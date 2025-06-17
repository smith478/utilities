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
- We can now click on the VM we have created (named `100`) and here are a few important settings:
    - Start at boot: this will determine if the VM automatically starts up when Proxmox boots up.
    - Start/shutdown order: this will help you control the order that different VMs are started/stopped. (e.g. if you have a database server with other VMs that rely on that database server)
- To start the VM click on `console`, then you can click the power button or simply `Start Now`
- On the initial startup you will have to install Ubuntu server (sticking almost entirely with defaults is fine for now)

Once the VM boots up and we log in, we will use a terminal (outside of proxmox) to connect (SSH) to this VM (node) using its IP address. We can use the following command:
```bash
ssh <USERNAME>@<IP ADDRESS>
```

We should now update ubuntu server:
```bash
sudo apt update && sudo apt dist-upgrade
```

Now it is a good idea to install the QEMU guest agent:
```bash
sudo apt install qemu-guest-agent
```

Before we start the service we need to go back to the proxmox UI, go to our VM and click on `Options`. Then `Edit` the `QEMU Guest Agent` and select `Use QEMU Guest Agent`. It will show `Enabled` in red. This indicates we need to restart the VM to actually see the change. 
To restart we can go back to the terminal and run `sudo poweroff`. Then in the proxmox UI we can start the VM again, and we should now see (under Options) the QEMU guest agent is now enabled.

We can verify this service is running:
```bash
systemctl status qemu-guest-agent.service 
```
If for some reason it was not running we could start it with:
```bash
systemctl status qemu-guest-agent.service
```

Since this is meant as a webserver we can install apache2:
```bash
sudo apt install apache2
```

After the package installs you should be able to type in the VMs IP address into a web browser and see Apache's default page.

## Creating VM templates

We will start by connecting to the VM via SSH as shown above. Note that while we want to create a template the automatically duplicates the VM setup, there are certain things we don't want to duplicate like SSH keys.

CloudInit is a great tool that does a number of things including creating templates that will help you set up linux servers. It can also handle things like avoiding duplication of SSH host keys.

Verify that `cloud-init` is installed
```bash
apt search cloud-init
```
If it is not installed, we can install it with:
```bash
sudo apt install cloud-init
```

We will remove the SSH host keys so that CloudInit knows to recreate them.
```bash
cd /etc/ssh
sudo rm ssh_host_*
```

We also need to remove the machine ID, which can be viewed with `cat /etc/machine-id`. It is typically not enough to simply delete this file. We need to empty out the file:
```bash
sudo truncate -s 0 /etc/machine-id
```

We need to check for a symbolic link 
```bash
ls -l /var/lib/dbus/machine-id
```
If you can see symlink then there's nothing further to do here. If not we can create one
```bash
sudo ln -s /etc/machine-id /var/lib/dbus/machine-id
```

There's a few other commands to run that will help clean the template.
```bash
sudo apt clean
sudo apt autoremove
```

Go back to the proxmox UI and right click on the VM (e.g. named 100 webserver), then click on `Convert to template`.

Next click on the hardware in the proxmox UI of our new template, and remove the attachment to the iso for the virtual disk. To do this, click `Edit` and then select `Do not use any media`. Now click `Add` and choose `CloudInit Drive` and choose `local-lvm` for the storage option.

With CloudInit set up, we can click on `Cloud-Init` on the sidebar and edit the following fields:
- User
- Password
- SSH Public Key (if you have one)

Finally click `Regenerate Image` and we are done with the template.

To create a VM from the template, right click on the template and choose `Clone`. For the mode typically you will want to select `Full Clone`. For storage, it's best to be explicit and choose `local-lvm`. For the name we can choose some new name (e.g. `webserver-1`). You could continue this process and create another VM (e.g. `webserver-2`).

Using the IP address of our 2 new webserver VMs we can ssh into them. Both of these will have the same hostname (i.e. `webserver`). Edit the hostname:
```bash
sudo nano /etc/hostname
```
We can then append a `-1` and `-2` to each of the webservers. Then `control` + `O`, `Enter/return` to save the file, then `control` + `X` to exit out.
Now edit the hosts file:
```bash
sudo nano /etc/hosts
```
Similarly here we will update the current `webserver` hostname. Then reboot:
```bash
sudo reboot
```
Remember to do this with both VMs.

## Launching containers

We first need to download a template. Under our `pve1` node, click on `local(pve1)` and then `CT Templates` (on the sidebar). From here click on the `Templates` button. Here you can search `ubuntu` to narrow down the list. We will choose the latest LTS version of Ubuntu, and click `Download`.

Now we can click the `Create CT` button at the top. 
- For `Hostname` we can use `webserver-ct`
- Create a password
- We can click `Next` and choose the (ubuntu) template that we downloaded previously.
- For the root disk we will increase the storage to 16 GB
- For now we will also leave the CPU cores at 1
- We will set memory to 1024 (for both memory and swap)
- In the Netork config we will select `DHCP` for IPv4 and IPv6
- Leave the defaults for `DNS`

This should be quick to be generated and you should now see it under the `pve1` node. We can click on it and then select `Options` from the sidebar. This gives a list of config options, we will change `Start at boot` to "yes" and leave the rest at the defaults.

## Creating container templates
## Managing users
## Backups and snapshots
## Integrated firewall
## CLI
## Networking
## Shared storage
## Clustering
## High availability