import re
import requests
from PIL import Image, ImageFilter
from lxml import html 
from urllib.parse import urlparse, parse_qs, urlunparse, urlencode
from library_db.utils.db_utils import get_user_data, get_user_type, get_media_types


def is_loggedin(session):
    try:
        email = session["email"]
        pwdhash = session["pwdhash"]
    except KeyError:
        return False

    db_pwdhash = get_user_data(email).get("pwdhash")

    if not db_pwdhash:
        return False

    return db_pwdhash == pwdhash


def is_staff(session):
    if not is_loggedin(session):
        return False

    if not get_user_type(session["email"]) == "Staff":
        return False

    return True


def is_admin(session):
    if not is_loggedin(session):
        return False

    if not get_user_type(session["email"]) == "Admin":
        return False

    return True


def get_template_vars(session) -> dict:
    template_vars = {}
    template_vars["logged_in"] = is_loggedin(session)
    template_vars["is_admin"] = is_admin(session)
    template_vars["is_staff"] = is_staff(session)
    template_vars["darkmode"] = session.get("darkmode")
    template_vars["grid"] = session.get("grid", True)
    template_vars["name"] = get_user_data(session.get("email")).get("name")
    template_vars["media_types"] = get_media_types()
    return template_vars


def update_query_params(url: str, **params):
    parsed_url = urlparse(url)
    parsed_query = dict(parse_qs(parsed_url.query), **params)
    return urlunparse(
        (
            parsed_url.scheme,
            parsed_url.netloc,
            parsed_url.path,
            parsed_url.params,
            urlencode(parsed_query, doseq=True),
            parsed_url.fragment,
        )
    )


def crop_image(img: Image.Image, w: int, h: int) -> Image.Image:
    crop_w = w
    crop_h = h

    new_w = int(crop_h * (img.width / img.height))
    img_resized = img.resize((new_w, crop_h))
    img_resized = img_resized.convert('RGB')

    if img_resized.width >= crop_w:
        (left, upper) = (int(img_resized.width / 2 - crop_w / 2), 0)
        (right, lower) = (
            int(img_resized.width / 2 + crop_w / 2),
            img_resized.height,
        )

        img_cropped = img_resized.crop((left, upper, right, lower))
        return img_cropped
    else:
        img_resized = img_resized.resize((crop_w, img_resized.height))
        return img_resized


def process_cover_image(path: str):
    image = Image.open(path)
    image = crop_image(image, 270, 400)
    image.save(path, "JPEG")

def process_cd_cover(path: str):
    cover = Image.open(path)
    cover = crop_image(cover, 270, 270)

    background = Image.open(path)
    background = crop_image(background, 270, 400)
    background = background.filter(ImageFilter.GaussianBlur(8))

    background.paste(
        cover, (0, int((background.height - cover.height) / 2))
    )
    background.save(path, "JPEG")

    
def goodreads_search(query: str):
    res = requests.get(
        "https://www.goodreads.com/book/auto_complete", params={'format': 'json', 'q': query}
    )

    return ["https://www.goodreads.com" + i['bookUrl'] for i in res.json()]

def imdb_search(query: str):
    res = requests.get(f"https://v3.sg.media-imdb.com/suggestion/x/{query}.json")
    if not res.json().get("d"):
        return 0
    
    search_results = []
    for i in res.json().get("d"):
        try:
            search_results.append(i['i']['imageUrl'])
        except KeyError:
            pass

    return search_results

def scrape_goodreads_cover(goodreads_book_url: str):
    res = requests.get(goodreads_book_url)
    res_link = html.fromstring(res.text).xpath("//img[@id='coverImage'] | //img[@class='ResponsiveImage']")
    if not res_link:
        return None
    
    return res_link[0].get("src")

def download_image(url: str, path: str):
    res = requests.get(url, stream=True)
    if res.status_code == 200 or res.status_code == 302:
        with open(path, 'wb') as f:
            for chunk in res:
                f.write(chunk)
        return 1
    else:
        return 0
