# CodeForces_Ratings_Racer
This tool generates an animated race video of your and your friends' CodeForces ratings

## Sample Output
![Raings-race-video.gif](https://media.giphy.com/media/WLMIeAeC68ZMaPsTw2/giphy.gif)

## Dependencies
- [requests](https://pypi.org/project/requests/)
- [pandas](https://pypi.org/project/pandas/)
- [BeautifulSoup](https://pypi.org/project/beautifulsoup4/)
- [bar_chart_race](https://github.com/dexplo/bar_chart_race)
- [ffmpeg](https://www.ffmpeg.org/download.html)

## Installation
```sh
pip3 install requests pandas beautifulsoup4
```
```sh
python -m pip install git+https://github.com/dexplo/bar_chart_race
```
#### Note:
Don't install [bar_chart_race](https://github.com/dexplo/bar_chart_race) using pip as the version installed via pip seems to be outdated.

### [ffmpeg](https://www.ffmpeg.org/download.html) installation:
To install ffmpeg, you can go to [this site](https://ffmpeg.org/download.html).
For Windows, you can directly download zip from [here](https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip), extract it and add it to path or paste it in your System32 folder.
To understand more about the step-by-step guide on how to do this, check [this site](https://www.wikihow.com/Install-FFmpeg-on-Windows).

## Usage
Write all the CodeForces user handles in [input.txt](https://github.com/TheViking733n/CodeForces_Ratings_Racer/blob/main/input.txt) file and then run the below command:
```sh
python cf_racer.py
```
