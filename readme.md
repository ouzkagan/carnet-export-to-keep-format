# Carnet to Keep/Zoho

Script to convert your Carnet notebook exports to google keep export shape. 

## Installation

Download or clone code. 

After extracting code go to the directory and install requirements by this command:

```bash
pip install -r requirements.txt
```

## Usage

1. Convert Carnet .sqd files to html and json with same names. (untitled.sqd -> untitled.html & untitled.json)
2. Move your Carnet files (html and json files) to **/carnet** directory.  
3. Put image files inside /data folder.
4. Run the script

```bash
python script.py
```
Script will create new folder called '/keep' and zip the folder automatically. You can check files inside keep directory or directly upload zip to Zoho notebooks or similar apps.

## Contributing
Pull requests are welcome. 

## License
[MIT](https://choosealicense.com/licenses/mit/)