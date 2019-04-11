# Item Catalog Project

## Description
This program provides a list of items listed in a variety of categories.

It will also utilize a user registration and authentication system. The users will have the ability to add, update and delete their own items. 

## Quick Startup
To run this program on your machine, _FORK_ [this](https://github.com/jtruelas/Item-Catalog-Project.git) virtual machine and clone it to a local directory.
```
user ~ $ mkdir new_directory
user ~ $ git clone repo_url new_directory
user ~ $ cd new_directory
```
To log in to the vm, run the following:
```
user new_directory $ vagrant up && vagrant ssh
```
Once you are in:
```
vagrant@vagrant:~$ cd /vagrant
vagrant@vagrant:/vagrant$ python project.py
```
Now that the program is running, go in to your browser and type ```localhost:5000``` in the address bar and hit enter.

This will take you to the front page of the application allowing you to decide to browse through the catalog or create a user and post additional items.

If you are curious about the necessity of needing to create a user in order to add, edit or delete items, check out the following [paths](https://github.com/jtruelas/Item-Catalog-Project.git#paths) that are only accessible to logged in users or creators of a specific item.

## Paths
[Add](http://localhost:5000/categories/new)

[Edit](http://localhost:5000/categories/edit)

[Delete](http://localhost:5000/categories/delete)

[Edit User's Item](http://localhost:5000/1/items/1/edit)

[Delete User's Item](http://localhost:5000/1/items/1/delete)