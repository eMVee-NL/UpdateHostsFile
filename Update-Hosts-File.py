import subprocess
import re
import os
import sys
import argparse

# Define color codes
GREEN = '\033[92m'
RED = '\033[91m'
BLUE = '\033[94m'
YELLOW = '\033[93m'
RESET = '\033[0m'

def banner():
    print(f'''{GREEN}
       __  __          __      __       __  __           __       _______ __   
      / / / /___  ____/ /___ _/ /____  / / / /___  _____/ /______/ ____(_) /__ 
     / / / / __ \\/ __  / __ `/ __/ _ \\/ /_/ / __ \\/ ___/ __/ ___/ /_  / / / _ \\
    / /_/ / /_/ / /_/ / /_/ / /_/  __/ __  / /_/ (__  ) /_(__  ) __/ / / /  __/
    \\____/ .___/\\__,_/\\__,_/\\__/\\___/_/ /_/\\____/____/\\__/____/_/   /_/_/\\___/ 
        /_/  {RESET}    
                    {RED} with NetExec under the hood!     {RESET}   

    Created by {GREEN}eMVee{RESET} and inspired by {GREEN}Extravenger{RESET} during OSEP course
    ''')

def check_root():
    """Check if the script is run as root."""
    if os.geteuid() != 0:
        print("\033[91mWarning: This script must be run as root or with sudo to modify /etc/hosts.\033[0m")
        sys.exit(1)

def check_netexec():
    """Check if the netexec command is available."""
    result = subprocess.run("command -v netexec", shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print("\033[91mError: netexec command not found. Please install it before running this script.\033[0m")
        sys.exit(1)

def run_command(command):
    """Run a shell command and return the output."""
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout.strip()

def parse_output(output, protocol):
    """Parse the output based on the protocol and return formatted lines."""
    lines = output.splitlines()
    formatted_lines = []

    for line in lines:
        if protocol.lower() in line.lower():
            if protocol.lower() == "ldap":
                # For LDAP, we want to extract the IP, machine name, and domain not sure why there are no results shown now
                match = re.search(r'SMB\s+(\d+\.\d+\.\d+\.\d+)\s+\d+\s+(\S+)\s+\[.*?\(name:(.*?)\)\s+\(domain:(.*?)\)', line)
                if match:
                    ip = match.group(1)
                    machine_name = match.group(2)
                    domain = match.group(4) if match.group(4) else ""
                    formatted_line = f"{ip} {machine_name} {machine_name}.{domain}" if domain else f"{ip} {machine_name} "
                    formatted_lines.append(formatted_line)
            elif protocol.lower() == "ssh":
                # For SSH, we only want the IP address
                match = re.search(r'SSH\s+(\d+\.\d+\.\d+\.\d+)', line)
                if match:
                    ip = match.group(1)
                    formatted_lines.append(f"{ip} ")
            elif protocol.lower() == "wmi":
                # For WMI, we want to extract the IP, machine name, and domain
                match = re.search(r'RPC\s+(\d+\.\d+\.\d+\.\d+)\s+\d+\s+(\S+)\s+\[.*?\(name:(.*?)\)\s+\( domain:(.*?)\)', line)
                if match:
                    ip = match.group(1)
                    machine_name = match.group(3)
                    domain = match.group(4) if match.group(4) else ""
                    formatted_line = f"{ip} {machine_name} {machine_name}.{domain}" if domain else f"{ip} {machine_name} "
                    formatted_lines.append(formatted_line)
            else:
                # For other protocols, extract IP, machine name, and domain
                match = re.search(r'(\d+\.\d+\.\d+\.\d+)\s+\S+\s+(\S+)\s+\[.*?\(name:(.*?)\)\s+\(domain:(.*?)\)', line)
                if match:
                    ip = match.group(1)
                    machine_name = match.group(3)
                    domain = match.group(4) if match.group(4) else ""
                    formatted_line = f"{ip} {machine_name} {machine_name}.{domain}" if domain else f"{ip} {machine_name} "
                    formatted_lines.append(formatted_line)

    return formatted_lines

def main():
    # Print banner
    banner()

    # Check if the script is run as root
    check_root()

    # Check if netexec is available
    check_netexec()

    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Enumerate network protocols and update /etc/hosts.")
    parser.add_argument('--subnet', type=str, help="Subnet to scan.")
    parser.add_argument('--quick', action='store_true', help="Run only the SMB protocol.")
    parser.add_argument('--all', action='store_true', help="Run all protocols.")
    parser.add_argument('--protocol', type=str, choices=["smb", "winrm", "rdp", "mssql", "ldap", "vnc", "ssh", "wmi", "ftp"],
                        help="Specify a single protocol to run.")
    parser.add_argument('--protocols', type=str, help="Specify comma separated multiple protocols to run. (smb,rdp)")

    args = parser.parse_args()

    # Determine which protocols to run
    protocols = []
    if args.quick:
        protocols = ["smb"]
    elif args.all:
        protocols = ["smb", "winrm", "rdp", "mssql", "ldap", "vnc", "ssh", "wmi", "ftp"]
        print("\033[93mWarning: Running all protocols may take a while. Do you want to continue? (y/n)\033[0m")
        confirm = input().strip().lower()
        if confirm != 'y':
            print("Please use --quick or --protocol options.")
            sys.exit(0)
    elif args.protocols:
        protocols = args.protocols.strip("").split(",")
        # print(protocols)
    elif args.protocol:
        protocols = [args.protocol]
    else:
        parser.print_help()
        sys.exit(0)

    try:
        # Ask the user for the target subnet
        print("Enter the target subnet (e.g., 172.16.120.0/24): ")
        if args.subnet:
            target = args.subnet
        else:
            exit("[!] Please specify the subnet")

        # Prepare to write to /etc/hosts
        with open("/etc/hosts", "a") as hosts_file:
            hosts_file.write(f"# The below entries belong to {target}\n")


            # Loop through each protocol
            for protocol in protocols:
                print(f"\033[92m[I] Enumerating via {protocol} protocol...\033[0m")
                command = f"netexec --no-progress {protocol} {target}"
                output = run_command(command)

                # Parse the output and write to /etc/hosts
                formatted_lines = parse_output(output, protocol)
                
                # Write a comment line for the protocol
                if formatted_lines:
                    hosts_file.write(f"# Found via {protocol}\n")
                    for line in formatted_lines:
                        hosts_file.write(line + "\n")
                        print(line)

    except KeyboardInterrupt:
        print("\n\033[91m[!] Script interrupted by user. Exiting...\033[0m")
        sys.exit(0)

if __name__ == "__main__":
    main()
