import subprocess

def connect_vpn(server_address, username, password):
    command = [
        'sudo', 'openconnect', server_address,
        '--user', username,
        '--passwd-on-stdin'
    ]
    process = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout, stderr = process.communicate(input=password.encode())
    if process.returncode == 0:
        print("VPN connection established successfully.")
    else:
        print(f"Failed to connect to VPN. Error: {stderr.decode()}")

if __name__ == "__main__":
    server_address = "197.243.17.148"
    username = "name"
    password = "password"
    connect_vpn(server_address, username, password)