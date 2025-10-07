import click
import requests
import json
import os
from typing import List

class VSCodeExtensionDownloader:

    def __init__(self, extension, proxy=None, version=None, destination=None, no_cache=False, print=False):
        self.extension = extension
        self.proxy = proxy
        self.version = version
        self.destination = destination
        self.no_cache = no_cache
        self.print = print

    def _print(self, msg):
        if self.print:
            print(msg)

    def download(self):
        publisher, extension_name = self.extension.split('.')
        self._print(f"{'=' * 50}")
        self._print(f"Downloading {publisher}.{extension_name}")
        self._print(f"{'=' * 50}")
        self._download_vscode_extension(publisher, extension_name, self.proxy, self.version, self.destination, self.no_cache)

    def _download_vscode_extension(self, publisher, extension_name, proxy, specific_version, destination, no_cache):
            api_url = f"https://marketplace.visualstudio.com/_apis/public/gallery/extensionquery"
    
            payload = json.dumps({
                "filters": [{
                    "criteria": [
                        {"filterType": 7, "value": f"{publisher}.{extension_name}"}
                    ]
                }],
                "flags": 914
            })

            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json;api-version=3.0-preview.1',
                'User-Agent': 'Offline VSIX/1.0'
            }

            session = requests.Session()
            
            if proxy:
                self._print(f"Using proxy: {proxy}")
                session.proxies = {"http": proxy, "https": proxy}

            self._print("Querying Marketplace API...")
            response = session.post(api_url, headers=headers, data=payload)

            if response.status_code != 200:
                self._print("Failed to query Marketplace API")
                return

            extension_data = response.json()
            if specific_version:
                version = specific_version
            else:
                try:
                    results = extension_data["results"]
                    if not results:
                        self._print(f"Extension not found: {publisher}.{extension_name}")
                        return
                    exts = results[0]["extensions"]
                    if not exts:
                        self._print(f"Extension not found: {publisher}.{extension_name}")
                        return
                    vers = exts[0]["versions"]
                    if not vers:
                        self._print(f"Extension not found: {publisher}.{extension_name}")
                        return
                    version = vers[0]["version"]
                except (KeyError, IndexError, TypeError):
                    self._print(f"Extension not found: {publisher}.{extension_name}")
                    return

            if destination:
                if not os.path.exists(destination):
                    os.makedirs(destination)
                file_path = os.path.join(destination, f"{publisher}.{extension_name}-{version}.vsix")
            else:
                if not os.path.exists("extensions"):
                    os.makedirs("extensions")
                file_path = os.path.join("extensions", f"{publisher}.{extension_name}-{version}.vsix")

            if not no_cache and os.path.exists(file_path):
                self._print(f"File {file_path} already exists.")
                self._print("Use --no-cache to force re-download.")
                return

            download_url = f"https://{publisher}.gallery.vsassets.io/_apis/public/gallery/publisher/{publisher}/extension/{extension_name}/{version}/assetbyname/Microsoft.VisualStudio.Services.VSIXPackage"

            self._print(f"Downloading version {version}...")
            download_response = session.get(download_url)

            if download_response.status_code == 200:
                with open(file_path, "wb") as f:
                    f.write(download_response.content)
                self._print(f"{'*'*50}")
                self._print(f"Successfully downloaded to: {file_path}")
                self._print(f"{'*'*50}")
            else:
                self._print(f"Failed to download {publisher}.{extension_name}-{version}.vsix")

def download_plugins_from_file(file_path: str, proxy=None, version=None, destination=None, no_cache=False, verbose=False):
    with open(file_path, 'r') as f:
        extensions = f.readlines()
    for extension in extensions:
        extension = extension.strip()
        if extension:
            downloader = VSCodeExtensionDownloader(extension, proxy, version, destination, no_cache, verbose)
            downloader.download()


@click.command()
@click.argument('extension', nargs=1, required=False)
@click.option('--version', default=None, help='Specific version to download.')
@click.option('--destination', default=None, help='Destination folder.')
@click.option('--no-cache', is_flag=True, default=False, help='Force re-download even if the extension already exists.')
@click.option('--no-print', is_flag=True, default=True, help='Without output print')
@click.option('--file', default=None, help='Path to a text file with extensions to download, one per line.')
@click.option('--proxy', default=None, help='Proxy URL.')
def cli(extension, file, proxy, version, destination, no_cache, no_print):
    if file:
        download_plugins_from_file(file, proxy, version, destination, no_cache, no_print)
    elif extension:
        downloader = VSCodeExtensionDownloader(extension, proxy, version, destination, no_cache, no_print)
        downloader.download()
    else:
        print("Please provide either an extension or a file containing extensions.")

if __name__ == '__main__':
    cli()
