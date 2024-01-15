# LyricLullaby Music Streaming Application

Welcome to LyricLullaby, a robust music streaming application powered by Flask. Explore, create, and enjoy a seamless music experience!<br>
LyricLullaby: A secure and feature-rich music platform with robust authentication, user roles, and an admin dashboard for insightful statistics, ensuring a tailored experience for users, creators, and administrators while supporting multilingual song management, content diversity, and seamless .mp3 playback.

## Features

- **Robust Authentication and User Roles:**
  Ensures a secure and tailored experience for general users, creators, and administrators.

- **User-friendly Song Management:**
  Normal users can effortlessly view, rate, and create playlists with support for multiple languages.

- **Content Diversity by Creators:**
  Creators contribute to content diversity by registering and managing new songs, lyrics, and albums.

- **Admin Dashboard:**
  Admin users gain access to an insightful dashboard for statistics, content policy enforcement, removal of guideline-violating content, and management of creator blacklists/whitelists.

- **Powerful Search Functionality:**
  Explore albums based on various criteria such as song name, creator name, ratings, and genres for an enhanced music discovery experience.

- **Seamless .mp3 File Support:**
  LyricLullaby supports the seamless addition and playback of .mp3 files, elevating the auditory experience for users.

## Project Structure

The project directory is organized as follows:

- **application:** Core files for the Flask application.
- **db_directory:** SQLite database storage.
- **static:** Static assets including images, styles, and song files.
- **templates:** HTML templates for different views.

## How to Run

### Local Setup
Ensure you have Python and Flask installed on your machine.

1. Open a terminal and navigate to the project directory.
2. Run the local setup script to initialize the virtual environment and install dependencies:

    ```bash
    ./local_setup.sh
    ```

### Local Run
After the setup, run the Flask application using:

```bash
./local_run.sh
