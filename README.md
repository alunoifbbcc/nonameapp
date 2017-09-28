DB2 class project

#### HOW TO USE:

##### Clone the application and create a virtual enviroment:
```
git clone https://github.com/AmonartRolon/noname-app.git
cd noname-app
python3 -m venv venv
```
##### Activate the virtual enviroment and install the dependencies:
```
source venv/bin/activate
pip3 install -r requirements.txt
```

##### Choosing a configuration:
```
export FLASK_CONFIG=configuration_name
```
Checkout the config dictionary in the config.py file for the available configuration names 
##### Run the application:
```
./manager.py runserver
```
###### The application will start on port 3000
