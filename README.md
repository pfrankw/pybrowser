# PyBrowser

Ultra simple (200 lines of code) Flask application that supports HTTP 206 Partial Content requests.  
Mainly used for streaming video files instead of more complex applications like Jellyfin, Plex, etc.  
It opens `mkv` and `mp4` with VLC by default.  
Also permits to browse folders and download files.

⚠️ Not to be exposed as it has no authentication. ⚠️  

Example `docker-compose.yml`:
```yaml
services:
  pybrowser:
    image: ghcr.io/pfrankw/pybrowser:latest
    environment:
      - PORT=8080 # Default is 5000
      - DIRECTORY=/share # Default is /files
    volumes:
      - downloads:/share:ro

qbittorrent:
    image: lscr.io/linuxserver/qbittorrent:latest
    container_name: qbittorrent
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=Etc/UTC
      - WEBUI_PORT=8080
      - TORRENTING_PORT=6881
    volumes:
      - qbittorrent:/config
      - downloads:/downloads
    ports:
      - 8080:8080
      - 6881:6881
      - 6881:6881/udp
    restart: unless-stopped

volumes:
  qbittorrent:
  downloads:

```
