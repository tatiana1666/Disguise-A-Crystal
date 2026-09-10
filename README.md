# Diguise a Crystal Demo

This is a web app that can generate a new-looking Crystallographic Information File (CIF) based on any input CIF.

## Installation
To run the application locally, follow the instructions below to set up a virtual environment, install the required dependencies, and launch the app on **Windows** or **macOS**.
### Prerequisites
Before starting, ensure you have **Python 3.8+** installed on your machine. Check your version by running `python --version` (Windows) or `python3 --version` (macOS). If Python is not installed, download it from [python.org](https://www.python.org/).

## Instructions for Windows
### Step 1: Download and Extract the Code
1. Click the **Code** button on the GitHub repository page and select **Download ZIP**.
2. Extract the downloaded `.zip` file to a location of your choice on your computer.

### Step 2: Open Command Prompt in the Project Folder
1. Open the extracted project folder.
2. Click on the address bar at the top of File Explorer, type `cmd`, and press **Enter**.

### Step 3: Run Commands
Run the following commands line-by-line to
1. create a virtual environment named `.venv`
2. activate the virtual environment
3. download necessary packages
4. and then launch the app:
```cmd
python -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
python app.py
```
Now the terminal should prompt you to go to **http://127.0.0.1:8050/** which you may open in your browser. NEW LINE
Note: If you get the error "Python was not found", a common fix is typing **py** instead of **python**.



## Instructions for macOS

### Step 1: Download and Extract the Code
1. Click the **Code** button on the GitHub repository page and select **Download ZIP**.
2. Double-click the downloaded `.zip` file to extract the project folder.

### Step 2: Open Terminal and Navigate to the Folder
Press ``Cmd + Space`` to open Spotlight, type Terminal, and press Enter.
Type ``cd `` (with a space after ``cd``).
Drag and drop the extracted project folder directly into the Terminal window, then press **Enter**.

### Step 3: Run Commands
Run the following commands line-by-line to
1. create a virtual environment named `.venv`
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```
Now the terminal should prompt you to go to **http://127.0.0.1:8050/** which you may open in your browser. 
To stop the running Dash server, press **Ctrl + C** in your terminal window.
To leave the virtual environment, run the following in the terminal:
```bash
deactivate
```

## Navigating the user interface
This app was made using [Dash App](https://dash.plotly.com/)
<br>
A summary of the following steps can be found in the web app under the **introduction** header.
### Step 1
Use the **on/off toggles** in the left most column of the blue table to select which transformations you would like to apply to your input CIF.
### Step 2
Scroll below the blue table and input your CIF in the *Input* column on the left-hand side, either by uploading your own CIF or selecting the example CIFs using the **on/off toggles**. If the CIF is correctly formatted, it will display the contents of the CIF in the *Input* column below. Please input your CIF in spacegroup P1 format, all other spacegroups will work in an upcoming update.
### Step 3
Once you are happy with the transformations you would like to apply to disguise the CIF, press the ``Generate CIF`` button in the *Output* column. The generated CIF contents will be displayed below the ``Generate`` button in the *Output* column. To see more information about which transformations were applied, refer to the right hand column of the blue table (under the heading *Advanced Info*).
You can download or change the name of the data block within the CIF using the buttons and the text box in the "Output" column.'

## License

[MIT](https://choosealicense.com/licenses/mit/)