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
 - */5 6-17 * * 1-5 \<full_python_path\> \<path\>/Check-Website-Status/check_websites_status.py -m process
   - Run script every 5 minutes at 6am to 5pm from Monday to Friday 
 - 0 19-23,0-5 * * 1-5 \<full_python_path\> \<path\>/Check-Website-Status/check_websites_status.py -m process
   - Run script every hour at 7pm to 5am from Monday to Friday
 - 0 * * * SAT,SUN \<full_python_path\> \<path\>/Check-Website-Status/check_websites_status.py -m process
   - Run script every hour on Saturday to Sunday
 - 3 8 * * * \<full_python_path\> \<path\>/Check-Website-Status/check_websites_status.py -m process -v -e
   - Run script once at 8:03am everyday
 - 3 17 * * * \<full_python_path\> \<path\>/Check-Website-Status/check_websites_status.py -m process -v -e
   - Run script once at 5:03pm everyday
### Add/Delete Websites
Edit the file called "websites.txt". The file shows which websites are being proxied to which machine.
