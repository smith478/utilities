## Setup
1. Download and install [Tailscale](https://tailscale.com/download)
2. log in to the admin [console](https://login.tailscale.com/admin/machines)
    - Add any devices that should be able to connect to the network (under the client device option)
3. install the tailscale [cli](https://tailscale.com/kb/1080/cli) on any machine that will be serving the application.

### To serve application
For options around serving run
```bash
tailscale serve --help
```
To serve use the port the application is running on:
```bash
sudo tailscale serve --http 8501 localhost:8501
```

## VS Code remote connection
Remote tunneling in VS Code is also available by clicking on the user profile in the bottom left and then selecting `Turn on Remote Tunnel Access`

## Notes
Use poe for common commands