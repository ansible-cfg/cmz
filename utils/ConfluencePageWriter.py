#!/usr/bin/env python

import sys
import json
import requests
import argparse

class ConfluencePageWriter:
    """
    A class for creating or updating a page in the Confluence Wiki.
    """

    def __init__(self, base_url, username, password):
        self.base_url = base_url
        self.rest_url = base_url + "/rest/api/content"
        self.username = username
        self.password = password
        self.allow_update = True
        self.space_key = None
        self.parent = None
        self.parent_id = None
        self.title = None
        self.message = ""
        self.response = None

    def set_space_key(self, space_key):
        self.space_key = space_key

    def set_parent(self, parent):
        self.parent = parent

    def set_title(self, title):
        self.title = title

    def set_allow_update(self, allow_update):
        self.allow_update = allow_update

    def get_response(self):
        return self.response

    def get_message(self):
        return self.message

    def write(self, page_content):
        self.message = ""
        if not self.parent == None:
            # There is a parent page so find it
            try:
                parent_page_info = self.__get_page_info(self.space_key, self.parent)
            except Exception, e:
                self.message = str(e)
                return False
            if parent_page_info == None:
                self.message = "Unable to find parent page"
                return False
            self.parent_id = str(parent_page_info['id'])
        # See if the page already exists
        try:
            page_info = self.__get_page_info(self.space_key, self.title, self.parent_id)
        except Exception, e:
            self.message = str(e)
            return False
        if not page_info == None:
            if not self.allow_update:
                self.message = "Not allowed to update existing page - use set_allow_update()"
                return False
            # Update the page
            page_info['body']['storage']['value'] = page_content
            page_info['version']['number'] += 1
            headers = {'Content-Type': 'application/json'}
            self.response = requests.put(page_info['_links']['self'], auth=(self.username, self.password), headers=headers, data=json.dumps(page_info))
            if not self.response.status_code == 200:
                self.message = self.response.json()['message']
                return False
        else:
            # Create a new page
            page_info = {"type": "page", "title": self.title, "space": {"key": self.space_key}}
            page_info['body'] = {"storage": {"value": page_content, "representation": "storage"}}
            if not self.parent_id == None:
                page_info['ancestors'] = [{"id": self.parent_id}]
            headers = {'Content-Type': 'application/json'}
            self.response = requests.post(self.rest_url, auth=(self.username, self.password), headers=headers, data=json.dumps(page_info))
            if not self.response.status_code == 200:
                self.message = self.response.json()['message']
                return False
        return True

    def __get_page_info(self, space_key, title, parent_id=None):
        page_info = None
        if parent_id == None:
            query_url = self.base_url + "/rest/api/content/search?expand=body.storage,version&cql=type=page AND space='" + space_key + "' AND title='" + title + "'"
        else:
            query_url = self.base_url + "/rest/api/content/search?expand=body.storage,version&cql=type=page AND space='" + space_key + "' AND title='" + title + "' AND parent=" + str(parent_id)
        self.response = requests.get(query_url, auth=(self.username, self.password))
        # Check the response
        if self.response.ok and len(self.response.json()['results']) > 0:
            page_info = self.response.json()['results'][0]
        elif not self.response.ok:
            try:
                self.message = self.response.json()['message']
            except:
                self.message = "HTTP " + str(self.response.status_code)
            self.response.raise_for_status()
        return page_info


if __name__ == "__main__":
    # Define the script arguments
    parser = argparse.ArgumentParser(description='Create or update a Confluence Wiki page')
    parser.add_argument('--base_url', help='Base URL', required=True)
    parser.add_argument('--space_key', help='Space Key', required=True)
    parser.add_argument('--title', help='The page title', required=True)
    parser.add_argument('--parent', help='The title of the parent page', required=False)
    parser.add_argument('--username', help='The username', default=None, required=False)
    parser.add_argument('--password', help='The password', default=None, required=False)
    parser.add_argument('--content', help='A file containing the page content', type=argparse.FileType('r'), required=False)

    args, unknown = parser.parse_known_args()
    if unknown:
        sys.stderr.write("Unknown arguments: %s\n" % unknown)

    # Create the writer object
    pageWriter = ConfluencePageWriter(args.base_url, args.username, args.password)
    pageWriter.set_space_key(args.space_key)
    pageWriter.set_title(args.title)
    if args.parent:
        pageWriter.set_parent(args.parent)
    content = ""
    if args.content:
        # Read the file
        content = args.content.read()

    # Write the page
    if not pageWriter.write(content):
        sys.stderr.write("Page write failed - " + pageWriter.get_message() + "\n")
        sys.exit(1)

    sys.exit(0)
