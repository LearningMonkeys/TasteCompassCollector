This is a project for collecting text data of restaurant review using Scrapy.
## Project structure
```plaintext
TasteCompassCollector/
│
├── setup.bat
├── setup.sh
└── tasteCompass/                # Scrapy project root directory
    │
    ├── scrapy.cfg               # Scrapy project configuration file
    └── tasteCompass/            # Scrapy project main directory
        ├── __init__.py
        ├── items.py             # Define data structure
        ├── middlewares.py       # Set middleware
        ├── pipelines.py         # Process and store the data
        ├── settings.py          # Scrapy project setting
        └── spiders/             # Spiders(crawlers) directory
            ├── __init__.py
            └── spider.py        # Spider file
```
## Getting Started
### Requirements
* Python 3.10
### Setup
Shell scripts for setup are provided as setup.sh, setup.bat.
You can use one according to your environment.
* Mac/Linux
  ```
  bash setup.sh
  ```
* Windows
  ```
  setup.bat
  ```
### Execution
* Execute spider(crawler)
  ```python
  scrapy crawl [spider_name]  # ex) scrapy crawl naver_blog
  ```
