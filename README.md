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
### List of Cronjob Times
*/5 6-17 * * 1-5 ~/miniconda3/bin/python /mnt/nfs/home/jjg/python_scripts/check_websites/check_websites_status.py -m process
0 19-23,0-5 * * 1-5 ~/miniconda3/bin/python /mnt/nfs/home/jjg/python_scripts/check_websites/check_websites_status.py -m process
0 * * * SAT,SUN ~/miniconda3/bin/python /mnt/nfs/home/jjg/python_scripts/check_websites/check_websites_status.py -m process
3 8 * * * ~/miniconda3/bin/python /mnt/nfs/home/jjg/python_scripts/check_websites/check_websites_status.py -m process -v -e
3 17 * * * ~/miniconda3/bin/python /mnt/nfs/home/jjg/python_scripts/check_websites/check_websites_status.py -m process -v -e
### Add/Delete Websites
Edit the file called "websites.txt". The file shows which websites are being proxied to which machine.
