import os
import time
import datetime
import urllib.request
import urllib.error
import argparse
import concurrent.futures
import threading
import statistics
from queue import Queue
from urllib.request import urlopen

# Thread-local storage for authentication handlers
thread_local = threading.local()
HOME = "/nfs/home/jjg"
MAX_RETRIES = 3  # Number of retries for each website
RETRY_DELAY = 2  # Seconds to wait between retries

def get_password_manager():
    """Create or return thread-local password manager"""
    if not hasattr(thread_local, "password_mgr"):
        thread_local.password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
    return thread_local.password_mgr

def check_single_website_with_retry(website):
    """Check a single website multiple times and return the best outcome"""
    results = []
    
    for attempt in range(MAX_RETRIES):
        result = check_single_website(website)
        results.append(result)
        
        # If we got a successful response, we can stop retrying
        if result["success"] and result["code"] == 200:
            return result
            
        # Wait before retrying
        if attempt < MAX_RETRIES - 1:
            time.sleep(RETRY_DELAY)
    
    # If we get here, we need to determine the best result to return
    # Priority: 1. Any successful result (code 200)
    # 2. The most common result (if there's a consensus)
    # 3. The result with the lowest HTTP error code
    
    # Check if any attempt was successful
    successful_results = [r for r in results if r["success"] and r["code"] == 200]
    if successful_results:
        return successful_results[0]
    
    # Check for consensus in error codes
    error_codes = [r["code"] for r in results if r["code"] is not None]
    if error_codes:
        # Use the most common error code, or the lowest if there's a tie
        from collections import Counter
        common_codes = Counter(error_codes).most_common()
        max_count = common_codes[0][1]
        most_common_codes = [code for code, count in common_codes if count == max_count]
        best_code = min(most_common_codes)
        
        for result in results:
            if result["code"] == best_code:
                # Update the message to indicate multiple attempts were made
                result["status"] = f"{website.ljust(50)} - HTTP Error: {best_code} (after {MAX_RETRIES} attempts)"
                return result
    
    return results[0]

def check_single_website(website):
    """Check a single website and return its status"""
    try:
        # Ensure the website has a valid URL format
        if not website.startswith(("http://", "https://")):
            website = f"https://{website}"

        # Handle authentication for certain sites
        password_mgr = get_password_manager()
        
        if "arthorp" in website or "swp" in website:
            password_mgr.add_password(None, website, "gpcr", "xtal")
        if "arthorc" in website or "swc" in website:
            password_mgr.add_password(None, website, "big", "fat secret")

        handler = urllib.request.HTTPBasicAuthHandler(password_mgr)
        opener = urllib.request.build_opener(handler)
        urllib.request.install_opener(opener)
        opener.open(website)

        # Request website
        status_code = urlopen(website, timeout=10).getcode()
        return {
            "website": website,
            "status": f"{website.ljust(50)} - {status_code}",
            "code": status_code,
            "success": True
        }

    except urllib.error.HTTPError as error:
        return {
            "website": website,
            "status": f"{website.ljust(50)} - HTTP Error: {error.code}",
            "code": error.code,
            "success": False
        }

    except urllib.error.URLError as error:
        if "excipients.ucsf.bkslab.org" in str(error.reason):
            return {
                "website": website,
                "status": "",
                "code": None,
                "success": False
            }
        return {
            "website": website,
            "status": f"{website.ljust(50)} - URL Error: {error.reason}",
            "code": None,
            "success": False
        }

    except Exception as exc:
        return {
            "website": website,
            "status": f"{website.ljust(50)} - Unexpected Error: {exc}",
            "code": None,
            "success": False
        }

def check_websites(verbose):
    """Checks website statuses from a file using multiple threads and logs the results."""
    # Read and filter website list safely
    with open(f"{HOME}/python_scripts/websites.txt", "r") as f:
        websites = [line.strip() for line in f if line.strip() and not line.startswith("#")]

    if not websites:
        print("No websites found in the websites.txt file.")
        return False, []

    # Prepare status log file
    timestamp = datetime.datetime.now().strftime("%A, %d. %B %Y %I:%M%p")
    message_lines = [f"Timestamp: {timestamp}\n", "Website".ljust(50) + "Status Code\n"]

    print(f"Timestamp: {timestamp}\n")
    print("Website".ljust(50) + "Status Code")
    
    good_sites = []
    error_sites = []
    
    # Process websites with ThreadPoolExecutor
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        # Submit all website checking tasks with retry logic
        future_to_website = {executor.submit(check_single_website_with_retry, website): website for website in websites}
        
        # Process results as they complete
        for future in concurrent.futures.as_completed(future_to_website):
            result = future.result()
            if result["success"] and result["code"] == 200:
                good_sites.append(result["status"])
            elif result["status"]:  # Only add non-empty status lines
                error_sites.append(result["status"])
                print(result["status"])
    
    # Add error sites to message lines
    message_lines.extend(error_sites)
    
    # Logging good sites if verbose mode is on
    if verbose:
        separator = "=" * 70
        print(separator)
        message_lines.append(separator)
        message_lines.extend(good_sites)
        for site in good_sites:
            print(site)

    # Write all output to file in one go
    with open(f"{HOME}/python_scripts/website_status_message.txt", "w") as message:
        message.write("\n".join(message_lines) + "\n")
    
    # Return whether there were errors and the message lines
    return len(error_sites) > 0, message_lines

def check_websites_with_processes(verbose):
    """Checks website statuses from a file using multiple processes and logs the results."""
    # Read and filter website list safely
    with open(f"{HOME}/python_scripts/websites.txt", "r") as f:
        websites = [line.strip() for line in f if line.strip() and not line.startswith("#")]

    if not websites:
        print("No websites found in the websites.txt file.")
        return False, []

    # Prepare status log file
    timestamp = datetime.datetime.now().strftime("%A, %d. %B %Y %I:%M%p")
    message_lines = [f"Timestamp: {timestamp}\n", "Website".ljust(50) + "Status Code\n"]

    print(f"Timestamp: {timestamp}\n")
    print("Website".ljust(50) + "Status Code")
    
    # Process websites with ProcessPoolExecutor
    with concurrent.futures.ProcessPoolExecutor(max_workers=min(8, os.cpu_count() or 1)) as executor:
        # Submit all website checking tasks with retry logic
        results = list(executor.map(check_single_website_with_retry, websites))
    
    good_sites = []
    error_sites = []
    
    # Process results
    for result in results:
        if result["success"] and result["code"] == 200:
            good_sites.append(result["status"])
        elif result["status"]:  # Only add non-empty status lines
            error_sites.append(result["status"])
            print(result["status"])
    
    # Add error sites to message lines
    message_lines.extend(error_sites)
    
    # Logging good sites if verbose mode is on
    if verbose:
        separator = "=" * 70
        print(separator)
        message_lines.append(separator)
        message_lines.extend(good_sites)
        for site in good_sites:
            print(site)

    # Write all output to file in one go
    with open(f"{HOME}/python_scripts/website_status_message.txt", "w") as message:
        message.write("\n".join(message_lines) + "\n")
    
    # Return whether there were errors and the message lines
    return len(error_sites) > 0, message_lines

def send_message():
    """Sends the website status report via email."""
    os.system(f"mail -s 'Daily Website Status Check' jjg9803@gmail.com khtang015@gmail.com jir322@gmail.com < {HOME}/python_scripts/website_status_message.txt")

def main():
    """Main function for argument parsing and execution."""
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", action="store_true", help="Shows websites that returned 200.")
    parser.add_argument("-m", "--mode", choices=["thread", "process"], default="thread", 
                       help="Select parallelization mode: thread or process (default: thread)")
    parser.add_argument("-e", "--email", action="store_true", 
                       help="Send email regardless of errors (default: only send on errors)")
    args = parser.parse_args()

    start_time = time.time()
    
    # Check websites using the selected mode
    if args.mode == "thread":
        has_errors, message_lines = check_websites(args.verbose)
    else:
        has_errors, message_lines = check_websites_with_processes(args.verbose)
    
    print(f"Completed in {time.time() - start_time:.2f} seconds")
    
    # Only send email if there are errors or explicitly requested
    if has_errors or args.email:
        print("Sending email notification...")
        send_message()
    else:
        print("No errors detected - skipping email notification.")

if __name__ == "__main__":
    main()