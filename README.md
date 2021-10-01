# Naver news crawling with bs4 & selenium

## Install required packages

```bash
pip install -r requirements.txt
```

## Install chromedriver

You're required to use exact version of chromedriver that matches with your local chrome.
To install chromedriver, visit [here](https://sites.google.com/chromium.org/driver/)

2021/10/01 Latest stable release: ChromeDriver 94.0.4606.61

## Crawling

```bash
chmod +x run.sh
./run.sh
```

You can modify run.sh to change search keyword and other arguments.

## Allowed press

allowed_press.txt contains journals which are allowed to crawl.
News articles released by other media channels will be discarded.
