#!/usr/bin/env python

from jinja2 import Template
from requests import get
from lxml.html import fromstring, tostring

def render(template, url):
    r = get(url)
    bodyxml = fromstring(r.content).body
    body = (bodyxml.text or '') +\
        ''.join([tostring(child) for child in bodyxml.iterchildren()])
    with open(template, "r") as tfile:
        return Template(tfile.read()).render(body=body)

def replace(htmlfile, template, url):
    newpage = render(template, url)
    with open(htmlfile, "w") as outfile:
        outfile.write(newpage)

if __name__ == '__main__':
    replace("faq.html", "faq.template", "http://treasure.webuda.com/ogdfaq.html")

