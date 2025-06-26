import sys
from pathlib import Path
import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin

IMG_TYPE = { ".jpg", ".jpeg", ".png", ".gif", ".bmp" }
USAGE = '''\
------------------------------------------------------------------------------------------------------------------------
USAGE: ./spider [-r] [-l N] [-p PATH] URL
------------------------------------------------------------------------------------------------------------------------
Option:
 • -r        : recursively download the images in a URL received as parameter.
 • -l [N]    : indicates the maximum depth level of the recursive download. If not indicated, it will be 5.
 • -p [PATH] : indicates the path where the downloaded files will be saved. If not specified, [./data/] will be used.
------------------------------------------------------------------------------------------------------------------------
Supporting download the following extensions by default:  [ .jpg / .jpeg / .png / .gif / .bmp ]
------------------------------------------------------------------------------------------------------------------------
'''

# https://sparkling-zabaione-67f292.netlify.app

def main() -> int:
	if len(sys.argv) <= 1:
		print(USAGE)
		return 1
	try:
		option = option_parse(sys.argv[1:])
		if not option:
			return 1
		save_path = Path(option["path"])
		save_path.mkdir(parents=True, exist_ok=True)
		visited = set()
		if option["recusive"]:
			recursive_extract([option["url"]], option["path"], option["level"], visited)
		else:
			recursive_extract([option["url"]], option["path"], 0, visited)
		return 0
	except KeyboardInterrupt:
		return 1
	
def recursive_extract(urls: list, path: str, level: int, visited: set) -> None:
	if level < 0:
		return
	for url in urls:
		if url in visited: continue
		visited.add(url)
		print(f"[-URL-]: {url}")
		try:
			response = httpx.get(url, timeout=10)
			if response.status_code != 200:
				return
			html = BeautifulSoup(response.text, 'html.parser')
			for img in html.find_all('img'):
				image = img.get("src")
				if not image: continue
				image_type = Path(image).suffix.lower()
				if image_type in IMG_TYPE:
					file_path = get_save_path(Path(path), Path(image).name)
					image_url = urljoin(url, image)
					download_image(image_url, file_path)
			next_urls = []
			for a in html.find_all('a'):
				href = a.get("href")
				if href:
					next_url = href if href.startswith("http") else urljoin(url, href)
					next_urls.append(next_url)
			recursive_extract(next_urls, path, level - 1, visited)
		except httpx.HTTPError as exc:
			print(f"[Error]: Failed to fetch {exc.request.url!r}")

def get_save_path(directory: Path, filename: str) -> str:
	count = 1
	path = directory / filename
	while path.exists():
		path = directory / f"{Path(filename).stem}_{count}{Path(filename).suffix}"
		count += 1
	return path
 
def download_image(url: str, path: str) -> None:
	try:
		response = httpx.get(url, timeout=10)
		if "image" not in response.headers.get("Content-Type", ""):
			return
		with open(path, 'wb') as file:
			file.write(response.content)
	except httpx.HTTPError as exc:
			print(f"[Error]: cannot download {exc.request.url!r}")

def option_parse(argv: list) -> dict | None:
	index = 0;
	option = { "url": None, "level": None, "path": "./data/", "recusive": False }
	while index < len(argv):
		if argv[index] == "-r":
			option["recusive"] = True
			option["level"] =  option["level"] or 5
		elif argv[index] == "-l":
			index += 1
			if index < len(argv) and argv[index].isnumeric():
				option["level"] = int(argv[index])
			else:
				return error("Invalid depth level value.")
		elif argv[index] == "-p":
			index += 1;
			if index < len(argv):
				option["path"] = argv[index] + '/' if not argv[index].endswith('/') else argv[index]
			else:
				return error("Invalid path value.")
		elif (index == len(argv) - 1):
			option["url"] = argv[index]
		else:
			return error("Invalid flags.")
		index += 1
	if not option["url"]:
		return error("Missing URL.")
	if option["level"] and not option["recusive"]:
		return error("Invalid flags combination: -l requires -r.")
	return (option);

def error(message: str) -> None:
	print(f"[ERROR]: {message}")
	return None

if (__name__ == "__main__"):
	main()
