# 📚 Library Website
This is a Library Website made (in making) with [Python](https://github.com/python/cpython), SQL and [Flask](https://github.com/pallets/flask) for a School Project

<details>
  <summary>Screenshot</summary>
  
![Screenshot 2022-10-26 at 22-27-19 Library - SQL Library](https://user-images.githubusercontent.com/63876564/198130318-6b565702-9bb9-452d-86b2-4eddf861c358.png)

</details>


## Setup

#### Install requirements for the Project:
```
pip install -r requirements.txt
```
#### Database:

You can either use the sample Database in  [library_db/library.db](https://github.com/sdaqo/library_website/blob/main/library_db/library.db) or create your own one with the structure given in the [db_create.sql](https://github.com/sdaqo/library_website/blob/main/db_create.sql) file and copy it to **library_db/library.db**

#### Sample Database:

Admin user Credentials:

Email: admin@admin.admin Password: admin1234

## Start

Without Debugging:
```
python wsgi.py
```

With Debugging:
```
python -m library_db.app
```
You can also specify a host and port in wsgi.py like so:
```
...
if __name__ == "__main__":
    app.run(host='<The Host>', port=<The Port>)
```
