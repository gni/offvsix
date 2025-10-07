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
        ext = (self.extension or "").strip()
        if "." not in ext:
            self._print(f"Invalid extension identifier: {ext}. Use the form publisher.extension")
            return {
                "ok": False,
                "extension": ext,
                "error": "invalid_extension",
                "message": f"Invalid extension identifier: {ext}. Use the form publisher.extension"
            }
        publisher, extension_name = ext.split(".", 1)
        if not publisher or not extension_name:
            self._print(f"Invalid extension identifier: {ext}. Use the form publisher.extension")
            return {
                "ok": False,
                "extension": ext,
                "error": "invalid_extension",
                "message": f"Invalid extension identifier: {ext}. Use the form publisher.extension"
            }
        self._print(f"{'=' * 50}")
        self._print(f"Downloading {publisher}.{extension_name}")
        self._print(f"{'=' * 50}")
        return self._download_vscode_extension(publisher, extension_name, self.proxy, self.version, self.destination, self.no_cache)

    def _download_vscode_extension(self, publisher, extension_name, proxy, specific_version, destination, no_cache):
            ext_id = f"{publisher}.{extension_name}"
            api_url = f"https://marketplace.visualstudio.com/_apis/public/gallery/extensionquery"
    
            payload = json.dumps({
                "filters": [{
                    "criteria": [
                        {"filterType": 7, "value": ext_id}
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
            try:
                response = session.post(api_url, headers=headers, data=payload, timeout=20)
            except requests.RequestException as e:
                self._print(f"Failed to query Marketplace API: {e}")
                return {
                    "ok": False,
                    "extension": ext_id,
                    "error": "network",
                    "message": str(e)
                }

            if response.status_code != 200:
                self._print("Failed to query Marketplace API")
                return {
                    "ok": False,
                    "extension": ext_id,
                    "error": "http_error",
                    "status_code": response.status_code,
                    "message": "Failed to query Marketplace API"
                }

            try:
                extension_data = response.json()
            except ValueError:
                self._print("Failed to parse Marketplace API response")
                return {
                    "ok": False,
                    "extension": ext_id,
                    "error": "invalid_json",
                    "message": "Failed to parse Marketplace API response"
                }

            if specific_version:
                version = specific_version
            else:
                try:
                    results = extension_data.get("results") or []
                    if not results:
                        self._print(f"Extension not found: {ext_id}")
                        return {"ok": False, "extension": ext_id, "error": "not_found", "message": f"Extension not found: {ext_id}"}
                    exts = results[0].get("extensions") or []
                    if not exts:
                        self._print(f"Extension not found: {ext_id}")
                        return {"ok": False, "extension": ext_id, "error": "not_found", "message": f"Extension not found: {ext_id}"}
                    vers = exts[0].get("versions") or []
                    if not vers:
                        self._print(f"Extension not found: {ext_id}")
                        return {"ok": False, "extension": ext_id, "error": "not_found", "message": f"Extension not found: {ext_id}"}
                    version = vers[0].get("version")
                    if not version:
                        self._print(f"Extension not found: {ext_id}")
                        return {"ok": False, "extension": ext_id, "error": "not_found", "message": f"Extension not found: {ext_id}"}
                except (AttributeError, IndexError, TypeError):
                    self._print(f"Extension not found: {ext_id}")
                    return {"ok": False, "extension": ext_id, "error": "not_found", "message": f"Extension not found: {ext_id}"}

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
                return {
                    "ok": True,
                    "extension": ext_id,
                    "publisher": publisher,
                    "name": extension_name,
                    "version": version,
                    "file_path": file_path,
                    "cached": True
                }

            download_url = f"https://{publisher}.gallery.vsassets.io/_apis/public/gallery/publisher/{publisher}/extension/{extension_name}/{version}/assetbyname/Microsoft.VisualStudio.Services.VSIXPackage"

            self._print(f"Downloading version {version}...")
            try:
                download_response = session.get(download_url, timeout=60)
            except requests.RequestException as e:
                self._print(f"Failed to download asset: {e}")
                return {
                    "ok": False,
                    "extension": ext_id,
                    "error": "network",
                    "message": str(e)
                }

            if download_response.status_code == 200:
                with open(file_path, "wb") as f:
                    f.write(download_response.content)
                self._print(f"{'*'*50}")
                self._print(f"Successfully downloaded to: {file_path}")
                self._print(f"{'*'*50}")
                return {
                    "ok": True,
                    "extension": ext_id,
                    "publisher": publisher,
                    "name": extension_name,
                    "version": version,
                    "file_path": file_path,
                    "cached": False
                }
            else:
                self._print(f"Failed to download {publisher}.{extension_name}-{version}.vsix")
                return {
                    "ok": False,
                    "extension": ext_id,
                    "error": "download_failed",
                    "status_code": download_response.status_code,
                    "message": f"Failed to download {publisher}.{extension_name}-{version}.vsix"
                }

def download_plugins_from_file(file_path: str, proxy=None, version=None, destination=None, no_cache=False, verbose=False):
    results = []
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return results
    with open(file_path, 'r', encoding='utf-8') as f:
        extensions = f.readlines()
    for extension in extensions:
        extension = extension.strip()
        if extension:
            downloader = VSCodeExtensionDownloader(extension, proxy, version, destination, no_cache, verbose)
            res = downloader.download()
            results.append(res)
    return results

@click.command()
@click.argument('extension', nargs=1, required=False)
@click.option('--version', default=None, help='Specific version to download.')
@click.option('--destination', default=None, help='Destination folder.')
@click.option('--no-cache', is_flag=True, default=False, help='Force re-download even if the extension already exists.')
@click.option('--no-print', is_flag=True, default=True, help='Without output print')
@click.option('--file', default=None, help='Path to a text file with extensions to download, one per line.')
@click.option('--proxy', default=None, help='Proxy URL.')
@click.option('--json', 'as_json', is_flag=True, default=False, help='Output result as JSON.')
def cli(extension, file, proxy, version, destination, no_cache, no_print, as_json):
    if file:
        results = download_plugins_from_file(file, proxy, version, destination, no_cache, False if as_json else no_print)
        if as_json:
            print(json.dumps({"results": results}, ensure_ascii=False))
    elif extension:
        downloader = VSCodeExtensionDownloader(extension, proxy, version, destination, no_cache, False if as_json else no_print)
        res = downloader.download()
        if as_json:
            print(json.dumps(res, ensure_ascii=False))
    else:
        msg = "Please provide either an extension or a file containing extensions."
        if as_json:
            print(json.dumps({"ok": False, "error": "invalid_invocation", "message": msg}, ensure_ascii=False))
        else:
            print(msg)

if __name__ == '__main__':
    cli()
