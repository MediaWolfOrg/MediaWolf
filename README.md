# MediaWolf 

🚧 **Project Status: Early Development** 🚧  

This project is still in the early stages of development and **is not yet ready for general use**.  

---

### 💡 Getting Involved  

Contributions are welcome from anyone who wants to help shape the project! Here’s how to jump in:  

> **1. Fork the repo** – Pick a section you’d like to work on and submit a Pull Request (PR) when you’re ready.  
>  
> **2. Start a discussion** – Before diving in, use the repo's Discussions tab to share what you’re planning. This helps avoid overlap and keeps everyone on the same page.  
>  
> **3. Recognition** – Contributors who handle a significant part of the work may be added as maintainers to help guide the project forward.  

**Note:** Be sure to check out [TheWicklowWolf](https://github.com/TheWicklowWolf) for reference and proof of concepts — it will serve as a guide for formats,docker builds, actions and overall structure/style.  

Thanks for your interest! 🚀  


## **🌍 Proposed Project Features:**

### Books (Readarr & Anna’s Archive)  
✅ Missing List → Read from Readarr, fetch missing books and auto-download via Anna’s Archive  
✅ Manual Search → Search Anna’s Archive and download books (user selection and defined file structure)  
✅ Recommendations → Generate book suggestions based on Readarr library (using a background tasks to scrape from Goodreads) - with options to add or dismiss suggestions including filters and sorting  

### Movies (Radarr & TMDB)  
✅ Recommendations → Read Radarr library and suggest similar movies via TMDB (with options to add or dismiss suggestions including filters and sorting)  
✅ Manual Search → Search via TMDB with option to add to Radarr

#### TV Shows (Sonarr & TMDB)  
✅ Recommendations → Read Sonarr library and suggest similar shows via TMDB (with options to add or dismiss suggestions including filters and sorting)  
✅ Manual Search → Search via TMDB with option to add to Sonarr

## Music (Lidarr, LastFM, yt-dlp, Spotify)  
✅ Manual Search → Search Spotify for music and download via spotDL (which uses yt-dlp)
✅ Recommendations → Generate artist recommendations from LastFM based on Lidarr library (with options to add or dismiss suggestions including filters and sorting)  
✅ Missing List → Read Lidarr library, fetch missing albums and download via yt-dlp  

### Downloads (via yt-dlp)  
✅ Direct Download Page → Input YouTube or Spotify link and download video/audio using spotDL or yt-dlp  

### Subscriptions (via spotdl and yt-dlp)  
✅ Schedule System → Subscribe to YouTube Channels, Spotify or YouTube Playlists and download on a schedule  


### 🛠️ **Tech Stack Overview**  

| Layer            | Technology                                             |
|------------------|--------------------------------------------------------|
| Frontend         | Bootstrap                                              |
| Backend          | Python with Flask                                      |
| Database         | SQLite (SQLAlchemy)                                    |
| Scheduler        | APScheduler (for cron-based scheduling)                |
| Downloader       | spotdl and yt-dlp                                      |
| Containerization | Docker + Docker Compose                                |


📂 **Proposed Project Structure**

```plaintext
MediaWolf/
├── backend/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── auth_api.py
│   │   ├── books_api.py
│   │   ├── downloads_api.py
│   │   ├── logs_api.py
│   │   ├── movies_api.py
│   │   ├── music_api.py
│   │   ├── settings_api.py
│   │   ├── shows_api.py
│   │   ├── subscriptions_api.py
│   │   └── tasks_api.py
│   ├── db/
│   │   ├── __init__.py
│   │   ├── database_handler.py
│   │   ├── music_db_handler.py
│   │   └── music_models.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── config_services.py
│   │   ├── lastfm_services.py
│   │   ├── lidarr_services.py
│   │   ├── radarr_services.py
│   │   ├── readarr_services.py
│   │   ├── sonarr_services.py
│   │   ├── spotdl_download_services.py
│   │   ├── spotify_services.py
│   │   ├── subscription_services.py
│   │   ├── tasks.py
│   │   └── ytdlp_services.py
│   ├── utils/
│   │   ├── __init__.py
│   │   └── string_cleaner.py
│   ├── logger.py
│   └── main.py
├── docker/
│   ├── .dockerignore
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── static/
│   │   ├── base_script.js
│   │   ├── base_style.css
│   │   ├── book_script.js
│   │   ├── favicon.png
│   │   ├── lidarr.svg
│   │   ├── logo.png
│   │   ├── logs_script.js
│   │   ├── movies_script.js
│   │   ├── music_script.js
│   │   ├── music_style.css
│   │   ├── settings_script.js
│   │   ├── shows_script.js
│   │   ├── subscriptions_script.js
│   │   ├── tasks_script.js
│   │   ├── theme_script.js
│   │   └── yt_dlp.png
│   └── templates/
│       ├── base.html
│       ├── books.html
│       ├── downloads.html
│       ├── login.html
│       ├── logs.html
│       ├── movies.html
│       ├── music.html
│       ├── settings.html
│       ├── shows.html
│       ├── subscriptions.html
│       └── tasks.html
├── docs/
│   └── screenshot.png
└── README.md
```


# 📊 Project Progress Tracker

**Books (Readarr & Anna’s Archive)**
- [ ] Readarr Missing List Scheduled Downloader -> Similar to [BookBounty](https://github.com/TheWicklowWolf/BookBounty)
- [ ] Manual Search -> Similar to [calibre-web-automated-book-downloader](https://github.com/calibrain/calibre-web-automated-book-downloader)
- [ ] Recommendations based on Readarr Book List -> Similar to [eBookBuddy](https://github.com/TheWicklowWolf/eBookBuddy)
- [ ] Download engine -> Similar to [calibre-web-automated-book-downloader](https://github.com/calibrain/calibre-web-automated-book-downloader)

**Movies (Radarr & TMDB)**
- [ ] Recommendations based on Radarr Movie List -> Similar to [RadaRec](https://github.com/TheWicklowWolf/RadaRec)
- [ ] Manual Search

**TV Shows (Sonarr & TMDB)**
- [ ] Recommendations based on Sonarr Show List -> Similar to [SonaShow](https://github.com/TheWicklowWolf/SonaShow)
- [ ] Manual Search

**Music (Lidarr, LastFM, yt-dlp, Spotify)**
- [ ] Lidarr Missing List Scheduled Downloader -> Similar to [LidaTube](https://github.com/TheWicklowWolf/LidaTube)
- [x] Manual Search
- [x] Recommendations

**Downloads**
- [ ] Download via SpotDL or yt-dlp directly

**Tasks**
- [ ] Task Manager System (Cron schedule, Manual Start, Stop and Cancel)

**Subscriptions**
- [ ] YouTube Channels (Audio, Video, Live)
- [ ] YouTube and Spotify Playlists (Audio)
- [ ] Playlist Generators (For Audio Files)

**Login Manager**
- [ ] Login and Account Manager

**Settings Manager**
- [x] Settings Loader & Saver


# 📦 Local Development Setup

**Docker Setup**

In order to quickly get started with the project you can use the docker compose file to start the project.

- Make sure you have docker and docker compose installed
- Clone the repository
- Run `docker compose up -d`
- Access the application at `http://127.0.0.1:5000`


**Manual Setup**

- Clone the repository
- create a virtual environment and activate it (You can use pyenv for ease of maintaining multiple versions)
- Run `pip install -r docker/requirements.txt`
- Run `export FLASK_APP=backend/main.py && flask run`
- Access the application at `http://127.0.0.1:5000`

**Commiting Changes**

Make sure you install the pre-commit hooks by running `pre-commit install`

- Run `git add .`
- Run `git commit -m "Commit Message"`
- Run `git push`

You might face some issues in your files with the pre-commit hooks, fix them and try again.
