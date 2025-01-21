# Trendy Song App

This application analyzes songs to find the most "trendy" parts using the Essentia library. It allows users to input a YouTube music link, retrieves the audio, and identifies the catchy segments of the song.

## Project Structure

```
trendy-song-app
├── src
│   ├── app.py
│   ├── audio_processing.py
│   └── utils.py
├── requirements.txt
└── README.md
```

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/trendy-song-app.git
   cd trendy-song-app
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```
   python src/app.py
   ```

2. When prompted, enter the YouTube music link.

3. The application will process the audio and return the timestamps of the most catchy parts of the song.

## Functionality

- **Audio Retrieval**: Downloads audio from a provided YouTube link.
- **Audio Analysis**: Utilizes the Essentia library to analyze the audio and find trendy segments.
- **Timestamp Output**: Displays the start and stop timestamps of the catchy parts.

## Dependencies

- `essentia`
- `pytube`
- Additional libraries as required

## Contributing

Feel free to submit issues or pull requests for improvements or bug fixes.