import os
from base import sanitize_filename

def comment_html_cache_path(dest_dir,theme,title):
    title= sanitize_filename(title)
    return os.path.join(dest_dir, theme,title,f"{title}.html")