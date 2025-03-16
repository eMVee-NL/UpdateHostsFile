# UpdateHostsFile
UpdateHostsFile is a python script to update /etc/hosts with ip addresses and hostnames found by netexec
In the OSEP challenges there a a few machines that should be added to the `/etc/hosts` file. This was something I did not like.
Based on a oneliner shared by Extravenger, I decided to write a python script to use the other protocols as well.

![image](https://github.com/user-attachments/assets/73e790f3-05a0-470d-b587-9f3d4b60825f)


## Usage
> [!WARNING]
> > It should run with sudo or root privileges since the file `/etc/hosts` will be adjusted.

Perhaps you want to create a backup of this file first.

Use `--quick` argument to run a quick enumeration and add the results based on SMB
```bash
sudo python3 Update-Hosts-File.py --quick  --subnet 192.168.10.0/24
```

Use the `--protocol <PROTOCOL>` argument to run a specific enumeration and add the results based on the provided protocol
```bash
sudo python3 Update-Hosts-File.py --protocol rdp  --subnet 192.168.10.0/24
```

Use the `--all`  argument to run all protocols with netexec. This might take a while. 
```bash
sudo python3 Update-Hosts-File.py --all  --subnet 192.168.10.0/24
```

You can also specify multiple protocols within a single scan
```bash
sudo python3 Update-Hosts-File.py --protocols smb,rdp --subnet 192.168.10.0/24
```


## Issue
Somehow I got issues in retrieving the correct output with LDAP. Not sure why, if you know and can fix it. Let me know!
