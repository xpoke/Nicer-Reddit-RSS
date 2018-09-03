# Flask server to fetch, parse and return reddit RSS feeds, making a more user friendly experience
# Skeleton based on github.com/therippa/kaRdaSShian
# Inline images idea originated from inline-reddit.com

# By default listens on port 8080
# Use a url that looks like this:
#   http://ip:8080/
#   http://ip:8080/?limit=10
#   http://ip:8080/?feed=cad769dfgbjhlk64kljhv7q&user=xpoke&limit=20
# The url params are optional

# Dependencies:
# * Python 3
#   * urllib
#   * tldextract
#   * flask
#   * lxml

# Constants
user_agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'
snoo_src = 'https://i.redd.it/zug7bj3rmzj11.png'
port = 8080

import urllib
import tldextract
from flask import Flask, request
from lxml import etree as ET

app = Flask(__name__)
@app.route('/', methods=['GET'])

def main():
    # Get call parameters
    feed = request.args.get('feed')
    user = request.args.get('user')
    limit = request.args.get('limit')

    # Create/open request, spoof user agent for picky feeds
    url = 'https://www.reddit.com/.rss?'
    if feed: url = url+'feed='+feed+'&'
    if user: url = url+'user='+user+'&'
    if limit: url = url+'limit='+limit
    req = urllib.request.Request(url, headers={'User-Agent': user_agent})
    fetched_feed = urllib.request.urlopen(req).read()

    # Parse RSS as xml
    rss_root = ET.fromstring(fetched_feed)
    ns = '{http://www.w3.org/2005/Atom}'

    # Change feed's title
    feed_title = rss_root.find(ns+'title')
    if user: feed_title.text = user+'\'s reddit'

    # Run on articles
    for rss_entry in rss_root.findall(ns+'entry'):

        # Get common entry values
        title = rss_entry.find(ns+'title').text
        poster_name = rss_entry.find(ns+'author').find(ns+'name').text
        poster_href = rss_entry.find(ns+'author').find(ns+'uri').text
        subreddit = rss_entry.find(ns+'category').attrib['label']
        content = rss_entry.find(ns+'content')

        # Parse HTML content as XML, add span to ensure parsing works
        content_root = ET.fromstring('<span>'+content.text+'</span>')

        # Extract common content values
        for a in content_root.iter('a'):
            if a.text == '[link]': link_href = a.attrib['href']
            if a.text == '[comments]': comments_href = a.attrib['href']
        thumb_src = ''
        for img in content_root.iter('img'):
            thumb_src = img.attrib['src']
        md_div = ''
        for div in content_root.iter('div'):
            if 'class' in div.attrib:
                if div.attrib['class'] == 'md':
                    md_div = div

        # Create a new content root that we will build
        nc = ET.Element('table')
        nc_tr = ET.SubElement(nc, 'tr')
        nc_main = ET.SubElement(nc_tr, 'td')
        nc_content = ET.SubElement(nc_main, 'div')

        # Content case #1 - Inline images
        if link_href.rsplit('.', 1)[1] in ('jpg', 'gif', 'gifv', 'png', 'tiff'):

            # Turn gifv links into gif, otherwise keep same
            content_image_src = link_href.replace('gifv', 'gif')

            # Create image element
            nc_main_img_a = ET.SubElement(nc_content, 'a')
            nc_main_img_a.set('href', link_href)
            nc_main_img = ET.SubElement(nc_main_img_a, 'img')
            nc_main_img.set('src', content_image_src)
            nc_main_img.set('align', 'center')
            nc_main_img.set('height', '600em')
            ET.SubElement(nc_content, 'br')
            ET.SubElement(nc_content, 'br')

        # Other cases
        else:
            # Prepare layout for thumbnail
            nc_content_table = ET.SubElement(nc_content, 'table')
            nc_content_tr = ET.SubElement(nc_content_table, 'tr')

            # Add thumbnail to the right of the content section
            nc_thumb = ET.SubElement(nc_content_tr, 'td')
            nc_thumb.set('align', 'center')
            nc_thumb_a = ET.SubElement(nc_thumb, 'a')
            nc_thumb_a.set('href', link_href)
            nc_thumb_img = ET.SubElement(nc_thumb_a, 'img')
            nc_thumb_img.set('src', thumb_src)
            nc_td_pad = ET.SubElement(nc_content_tr, 'td')
            nc_td_pad.set('width', '5px')

            nc_content_main = ET.SubElement(nc_content_tr, 'td')

            # Content case #2 - Reddit self posts
            if link_href == comments_href:
                nc_thumb_img.set('src', snoo_src)
                if md_div is not '': 
                    nc_content_main.append(md_div)
                else:
                    nc_selfpost_span = ET.SubElement(nc_content_main, 'span')
                    nc_selfpost_span.text = title

            # Content case #3 - Any link post
            else:
                # Prepare "pretty" content url
                purl = link_href

                # Strip protocols
                _, purl = purl.split('://', 1)
                if purl.startswith('www.'): purl = purl[len('www.'):]

                # Split url to parts (subdomain, domain, filename)
                if '/' in purl: 
                    purl_host, purl_fn = purl.split('/', 1)
                    purl_fn = '/'+purl_fn
                else:
                    purl_host, purl_fn = (purl, '') 
                purl_subdomain, purl_domain, purl_suffix = tldextract.extract(purl_host)
                purl_domain = purl_domain+'.'+purl_suffix

                # Shorten filename
                purl_maxlen = 60
                purl_len = len(purl_subdomain)+len(purl_domain)+len(purl_fn)
                if purl_len > purl_maxlen:
                    purl_fn_newlen = purl_maxlen-len(purl_subdomain)-len(purl_domain)-3
                    if purl_fn_newlen < 0: purl_fn_newlen = 1
                    purl_fn = purl_fn[:purl_fn_newlen]+'...'

                # Write pretty url to content
                nc_link_a = ET.SubElement(nc_content_main, 'a')
                nc_link_a.set('href', link_href)
                if purl_subdomain:
                    nc_link_subdomain = ET.SubElement(nc_link_a, 'span')
                    nc_link_subdomain.text = purl_subdomain+'.'
                nc_link_domain_b = ET.SubElement(nc_link_a, 'b')
                nc_link_domain = ET.SubElement(nc_link_domain_b, 'span')
                nc_link_domain.text = purl_domain
                if purl_fn:
                    nc_link_fn = ET.SubElement(nc_link_a, 'span')
                    nc_link_fn.text = purl_fn

                # Handle case of missing thumbnail
                if thumb_src == '':
                    nc_content_tr.remove(nc_thumb)
                    nc_content_tr.remove(nc_td_pad)
                    ET.SubElement(nc_content_main, 'br')
                    ET.SubElement(nc_content_main, 'br')

        # Add content footer
        show_prefix = False
        show_poster = False
        nc_footer = ET.SubElement(nc_main, 'div')
        if show_prefix:
            nc_footer_prefix = ET.SubElement(nc_footer, 'span')
            nc_footer_prefix.text = 'Posted to '
        nc_subreddit_a = ET.SubElement(nc_footer, 'a')
        nc_subreddit_a.set('href', 'https://www.reddit.com/'+subreddit)
        nc_subreddit_a.text = subreddit
        if show_poster:
            nc_footer_divider = ET.SubElement(nc_footer, 'span')
            nc_footer_divider.text = ' by '
            nc_poster_a = ET.SubElement(nc_footer, 'a')
            nc_poster_a.set('href', poster_href)
            nc_poster_a.text = poster_name[1:]
        nc_footer_divider = ET.SubElement(nc_footer, 'span')
        nc_footer_divider.text = ' - '
        nc_comments_a = ET.SubElement(nc_footer, 'a')
        nc_comments_a.set('href', comments_href)
        nc_comments_a.text = '[comments]'  

        # Put modified content into the feed
        content.text = ET.tostring(nc)

    return(ET.tostring(rss_root, encoding='unicode', method='xml'),
             200, {'Content-Type': 'application/xml'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(port))
