# Check-Website-Status
This is a python script that will check the status of all websites that are running under the Shoichet/Irwin Lab.
## How To Use Flags/Options
usage: check_websites_status.py [-h] [-v] [-m {thread,process}] [-e]
### Flags
 - -h, --help
   - show this help message and exit
 - -v, --verbose
   - Shows websites that returned 200.
 - -m {thread,process}, --mode {thread,process}
   - Select parallelization mode: thread or process (default: thread)
 - -e, --email
   - Send email regardless of errors (default: only send on errors)
### Add/Delete Websites
Edit the file called "websites.txt". The file shows which websites are being proxied to which machine.
