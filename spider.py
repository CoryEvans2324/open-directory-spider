import re
import time
import requests
from bs4 import BeautifulSoup


PATTERN = re.compile(r'\?(C=(N|M|S|D)[;&]?O=(D|A))|\?[NMSDAnmsda]+')  # pattern to find IGNORED_HREFS
EXT_PATTERN = re.compile(r'\.[A-Za-z0-9]+$')  # pattern to find IGNORED_EXTS
IGNORED_HREFS = ['/', '../', '#', 'wget-log']  # hrefs to ignore


def is_dir(url):
    """ Returns True if given url belongs to a directory, otherwise returns false """
    return True if url[-1] == '/' else False


def write_link(url):
    """ Appends links to a text file """
    with open('links.txt', 'a') as file:
        file.write(url.lower() + "\n")


def write_stats(stat):
    """ Appends statistics to a text file """
    with open('stats.txt', 'a') as file:
        file.write(stat + "\n")


def crawl(website, recursive=True):
    """ Crawls the given website. 'recursive' tells if you want to crawl through folders/directories """
    print(f'Crawling {website}...')

    # Make a request and make soup
    try:
        r = requests.get(website, timeout=6)

    except requests.exceptions.Timeout:
        print("ERROR: Request timed out!\nRetrying in 5 seconds...")
        time.sleep(5)
        crawl(website)

    except requests.exceptions.ConnectionError:
        print('ERROR: Make sure you are connected to the internet!')

    else:
        soup = BeautifulSoup(r.text, 'html.parser')

    # Get all the links from soup
    for link in soup.find_all('a'):
        href = link.get('href')  # Value of the href attribute of link
        # Use regex to find url patterns to ignore
        matches = re.finditer(PATTERN, href)
        for match in matches:
            # Add matches to IGNORED_URLS list
            IGNORED_HREFS.append(match.group())

        if href in IGNORED_HREFS:
            # Continue to next iteration if url is to be ignored
            continue
        else:
            # Otherwise, do this:

            # Sometimes urls start from '/'. e.g. "/books/", "/songs/" etc.
            # If that's the case, ignore the first element of url i.e. '/'
            url = f"{website}{href[1:]}" if href[0] == '/' else f"{website}{href}"

            if is_dir(url) and recursive:
                # If url points to a directory, and recursive is True
                crawl(url)  # Crawl that url
                continue
            else:
                # If url points to a file
                write_link(url)  # Write that url to a file


def count_extensions(extensions):
    """ Prints the count of files belonging to an extension """

    # Iterate through extensions list
    for ext in extensions:
        ext_count = 0  # Extension Count

        # Open links file to read
        with open('links.txt', 'r') as links:
            # Iterate through the lines
            for line in links:
                # Use regex to find extension instances on line
                matches = re.finditer(f'.{ext}$', line)
                for match in matches:
                    # Count extensions
                    ext_count += 1
        print(f'{ext}: {ext_count} files')
        write_stats(f'{ext}: {ext_count} files')


def getStats():
    """ Shows statistics related to OD """

    # Make an empty extensions list
    extensions = list()

    # Open links file to read
    with open('links.txt', 'r') as links:
        # Iterate through each line
        for line_num, line in enumerate(links, start=1):
            # Use regex to find extension patterns in line
            matches = re.finditer(EXT_PATTERN, line)
            for match in matches:
                # Add matches to extensions list
                extensions.append(match.group().lower())  # Used lower() for string comparison

            # Convert extensions list to a set
            # to filter out the duplicate extensions from the list
            extensions_set = set(extensions)

            # Convert the set back to list (without duplicates)
            extensions = list(extensions_set)

    # Print the results
    print(f'{line_num} total links')
    print(f'Found these extensions: {extensions}')

    # Write the results to stats file
    write_stats(f'{line_num} total links\nFound these extensions: {extensions}')

    # Count the no. of files belonging to each extension
    count_extensions(extensions)


def main():
    # Webiste to crawl
    website = 'https://korea-dpr.com/mp3/'

    # Crawl the wesbite
    crawl(website)

    # Write the website URL to stats file
    write_stats(f'URL: {website}\n')

    # get the stats and print them
    getStats()


if __name__ == '__main__':
    main()
