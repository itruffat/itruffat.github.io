# Automatic GitPage Updater
## ~ By itruffat

After finding myself manually going thorugh my own github projects to add them to the GitPage updater, I could not help myself but to make it automatic. 
The `update.py` Python file here, combined with the yml file at `./github/workflows/automatic-update.yml` ensures that the gitpage will update at least once a day.
Thus won't be necessary to manually update the page when a new project is posted.


Feel free to use in your GitPage, just try to keep this `README.md` file on it as well. 
You'll need to set up your user name as a variable and create a Token that has writting rights to this repo. 
(For security reasons, I'd recommend that's the only permission it has).
Additionaly, you'll need to define a README.md.template file, with a `[REPOS-LIST]` argument in it.

The target repos must have a `.gitpage/entry.yml` file on them, with a name, a category and a description.

For example, the one on this project is:

    name: This Git Page
    category: utilities
    skip: False
    description : |
      Besides what you are reading right now, this repo contains a workflow to automatically fetch information from other github proyects on your personal git account and automatically populate your readme file.
      This section of the code was created using it. For more information on how this works, please refer to `.gitpage/README.md` .


# TODO

* Will probably try to migrate the template into Jinja2, adding more power to it as a whole.
* That power will probably correspond with other styling features.
* Might try to add an option to have some AI automatically craft the description and category, not needing you to do it by hand.

