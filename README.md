# Convenient Networking
![Screenshot 2022-10-27 204242](https://user-images.githubusercontent.com/45099803/198423345-e4f4554a-bf9e-4ce9-a4bd-4ae00d444314.png)
## This project was designed to simplify the workflow of initial device configuration process
1. Supports Telnet and SSH protocols
2. Implements connection protection for Telnet, noone will be able to kick you from device when you're working
3. Template support
4. Create Templates for any device.
   * Use variable support to make templates more agile.
   * Coming Soon share template with one-liner generate by the app.
   * Coming soon combine multiple template in one big template and push it to multiple devices 
5. Universal break function, no need to memorize different key combinations to break into rommon/loader/bios, this feature will break it automatically and stop once inside.
6. Disable AutoScrolling, helps when you want to see the output but the device is constantly outputting to the console.

## Installing

```
git clone https://github.com/MrAntonS/Convenient-Networking 
cd Convenient-Networking
python -m pip install pipenv
python -m pipenv install
```

After that you should be able to just run
```
pipenv run python ./src/main/MainWindow.py
```
Or alternatively you could compile it to exe file
```
pipenv run pyinstaller --noconfirm --onefile --windowed --specpath ./src/output/ --distpath ./src/output/ --workpath ./src/output/build -n ConvNet "./src/main/MainWindow.py"
```
## Contributing
Contributions are always welcome! To contribute potential features or bug-fixes:

1. Fork this repository
2. Apply any changes and/or additions based off an existing issue (or create a new issue for the feature/fix you are working on)
3. Create a pull request to have your changes reviewed and merged
