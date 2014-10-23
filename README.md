dictdiff
========

Python diff / merge basic dictionaries / lists

A simple library to record changes between two simple objects and merge the changes into base object to get the changed object.
Perfect if you want to store what was changed (e.g. by storing a JSON of the resulting object) and then at a later time apply the changes back to auto-generated base data.

**Features**

* Compares two dictionary objects recursively
* Compares two lists
 * Detects item movements within compared lists based on item identifier key, e.g. "id" or "name"
* Stores comparison differences in a compact dictionary
* Supports base dictionary changes while still properly applying a previously recorded diff
* Supports merging two dictionaries to produce a result with features from both sources (see more explanation below)

**Common usage case:**

* You have a function that is able to generate the same settings dictionary over and over (*base dictionary*)
 * This function may at any time in the future generate a bit different dictionary (add or remove a few items)
* Users are able to make adjustments to this dictionary (change settings) (*target dictionary*)
* `dictdiff()` function will record these changes in a compact dictionary (*diff dictionary*)
 * You will store this dictionary as JSON string for later use
* When user requests his settings, your code will
 * Generate the *base dictionary* again
 * Load the *diff dictionary*
 * Apply the *diff* to *base* with `dictmerge()` function to obtain *target*
 * Serve the resulting dictionary to the user

Note: `dictmerge()` can directly apply *target* to *base* for situations where you find yourself unable to perform `dictdiff()` first. However, this has two shortcomings: any changes in default *base* item values will not be honoured as *target* "remembers" the values as they were at the time *target* was generated. Additionally, this method requires comparatively much more storage because *target* is stored as the complete *diff* dictionary, which is presumably larger (you don't need these functions if *target* is completely different than *base*).
