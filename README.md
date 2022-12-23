# Introduction
We present an application for matching new teachers with schools based on a flexible generalisation of the gale-shapely assignment algorithm (first decribed here: https://doi.org/10.2307/2312726).

The application aims to provide users with a simple framework for configuring, running, and evaluating teacher assignments according to their needs by combining a limited set of controlling principles with the data provided for each school and teacher. 

Next are instructions to install and run, followed by a detailed guide of how to use.

## Installation
Currently the application only works for Windows. We aim to provide a standalone windows installer in the near future but the easiest way to run now is by first installing miniconda for windows from here:  
https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe  

After installing, open Anaconda prompt from the start menu and follow these instructions. In what follows, we refer to the location where you cloned this repository as `<REPO_DIR>`.

### Install
```
cd <REPO_DIR>
conda env create -f environment.yaml
conda init cmd.exe
```

### Run
Launch `<REPO_DIR>/fabmatch.bat` from file explorer.

Or from command prompt: 
```
conda activate FabMatch_SLE
python <REPO_DIR>/fabmatch_SLE.py
```

### Uninstall
```
conda deactivate
conda remove --name fabmatch_streamlit --all
```

# Usage
The application runs in a browser window controlled by a local python process. The application is organised into three pages, accessible from the sidebar at any time:
- [`Home`](#home)
    - This is the main section. From here you can run a new match and view and save the results, load and save projects, and exit the application.
- [`Import Data`](#import-data)
    - From here you can import and manage schools and teachers data to use for matching and apply filters to exclude any data from the match and from any precursory or subsequent calculations.
- [`Match Settings`](#match-settings)
    - From here you can control the settings to use for matching. These can include rules on the proportion of matches allocated to different districts or school types for example. The full range of settings can also take into consideration any of the fields in the school or teacher data and is not limited to proportions. See the dedicated [`Match Settings`](#match-settings) section for more details.

The basic order of execution is:

1. From the [`Import Data`](#import-data) page import schools and teachers data and apply any filters.
2. From the [`Match Settings`](#match-settings) page set match settings. Note that a value for the `Total cap` setting is the minimum required before any match can be run.
3. From the [`Home`](#home) page run the match and then visualise and export the results.

At any stage of the above process the current state of the project can also be saved from the [`Home`](#home) page using the `Save project` sidebar interface. This will save the imported school and teacher dataframes along with any filter options and match settings into a single project file which can be loaded from the `Load project` sidebar interface on [`Home`](#home).

Dedicated sections for each page are presented below in the order of their expected execution.

## Import Data
The main panel contains two tabs - one for [`Schools`](#schools) data and one for [`Teachers`](#teachers) data - and each of these contains a file uploading interface.

The first step is to select the data file to upload via either the `Browse files` button or the `Drag and drop files here` interface. The file must be in `.csv` format and each row should correspond to a unique school/teacher. Once the file has been selected click the `Read columns` button and two subtabs will be revealed below - [`Choose Columns`](#choose-columns) and [`Extra Options`](#extra-options).

### Choose Columns
The matching process currently requires specific fields to be present in both the schools and teachers data and this tab allows the user to select which columns from the csv to use for each field. The required fields are:

#### `Schools`:
- `Total teachers` (numerical)
    - The total numer of teachers
- `Total pupils` (numerical)
    - The total number of pupils
- `School owner` (any datatype)
    - The owner of the school (e.g. Government)
- `Approved school` (any datatype)
    - Some value indicating the approval status of the school
- `School ID` (any datatype)
    - The school's unique ID
- `School type` (any datatype)
    - The type of school (e.g. Primary)
- `District` (any datatype)
    - The school's district
- `Chiefdom` (any datatype)
    - The school's chiefdom
- `Latitude` (numerical)
    - The school's latitude
- `Longitude` (numerical)
    - The school's longitude

#### `Teachers`:
- `Gender` (any datatype)
    - The teacher's gender
- `Service years` (numerical)
    - How many years the teacher has been in service
- `Teaching qualification` (any datatype)
    - The teacher's qualification
- `Salary source` (any datatype)
    - The source of the teacher's salary (e.g. Government)
- `School ID` (any datatype)
    - The unique ID of the school that the teacher currently works at
- `School type` (any datatype)
    - The type of the school that the teacher currently works at
- `District` (any datatype)
    - The district of the school that the teacher currently works at
- `Chiefdom` (any datatype)
    - The chiefdom of the school that the teacher currently works at
- `Latitude` (numerical)
    - The latitude of the school that the teacher currently works at
- `Longitude` (numerical)
    - The longitude of the school that the teacher currently works at

For any fields that are common to both schools and teachers (e.g. `School type`), it is important that the values are in the same format for both (e.g. if the string "Primary" is used to denote a primary school in the `School type` column of the schools data, then the `School type` column of the teachers data must also use "Primary" to denote primary school). The subsequent stages in the matching process do not perform any checks for this so it is important that these checks are applied before uploading any data to the program.

Once all fields have been filled in the `Choose Columns` tab click the `Import` button to import the chosen columns from the csv into a dataframe, which is then presented below in an interactive format. Finally on this tab the `Reset Data` button can be clicked at any time to revert this import. Note that this doesn't clear any of the fields entered above.

### Extra Options
In addition to chosing the columns the `Import Data` page also allows filters to be applied to both the schools and teachers data.

#### `NOTE`:
It is important to note that filters applied here will apply to all stages of the program, including any before/after comparisons on the match results. It is not recommended to filter out "Government" paid teachers at this stage, as all subsequent before/after comparisons expect to find "Government" teachers in the data prior to the match. This particular filter could be safely applied in the [`Match Settings`](#match-settings) instead.

Once the data are imported, fields to filter by are selected from the `[Schools/Teachers] Attribute` drop-down menu in the `Extra Options` tab (note that prior to importing or after resetting the data this tab will be empty). After selecting the field, depending on whether the values in the field are numerical or not, either a range selector or a new drop-down menu will appear to the right of the `[Schools/Teachers] Attribute` menu. The range selector allows a minumum and maximum value to be set and the drop-down menu allows one or more values to be chosen. In both cases, clicking the `Add filter` button will create a new filter, selecting from either the chosen range of values or the chosen set of values. If the `Invert Selection` checkbox is checked the filter will instead select from the opposite of what is chosen. For example, to remove all schools of `School owner` "Private" from the data, you could select the value "Private" from the second drop-down and then check the `Invert Selection` box prior to clicking `Add filter`.

Once a filter has been added it will be displayed at the top of the tab along with all other added filters. Each filter can be individually removed by clicking the `Remove` button next to its display here.

Finally to apply the current set of filters to the data, click the `Apply Options` button. The filters will not be applied automatically so be careful to always click `Apply Options` whenever you change the set of filters. You can see the current state of the data at any time in the `Current data` panel below. The `global_index` field keeps a track of the index of each row in the original, pre-filtered, dataframe.

### Save project
The full data import process is quite laborious so we recommend at this stage to return to the [`Home`](#home) page and save the current project. This will allow the current project to be loaded at any time with the full data and filters that were entered above.

## Match Settings
After the data has been imported and any filters have been applied, the `Match Settings` tab is now operational. This is where the majority of the configuration for the matching procedure takes place.

The main panel contains four tabs - `Overview`, `Schools`, `Teachers`, and `Valid Pairs` - and there is also a `Reset Settings` button in the sidebar to reset all match settings to their initial (empty) values.

The `Overview` tab is where the `Total Cap` can be set and where the current state of the settings for each of the other tabs can be viewed and any specific setting can be removed from the current state if desired.

While `Total Cap` is the only setting which is strictly required for the match to be run, it is not recommended to run without adding some additional match settings. In this most basic state any teacher from the teachers data will potentially be matched with any school from the schools data. Schools with the most need will always be served first but teachers will simply be served in the order that they appear in the data. More realistically the user will want to filter and guide the matching procedure based on specific attributes of the teachers and schools. To illustrate using the `Match Settings` to achieve a particular goal, we present an example scenario:
1. Schools should be allocated teachers proportionally by school type, according to the following percentages:
    - Pre-primary: 5%
    - Primary: 70%
    - Junior Secondary: 15%
    - Senior Secondary: 10%
2. Schools that need the most teachers should have priority
3. Only teachers currently working in the school but not already on government payroll should be hired
4. Higher qualified teachers should always be hired before lower qualified
5. If two teachers are equally qualified, a female should be hired before a male
6. If two teachers are equally qualified and the same gender, the one with the longest service should be hired first

There are four main types of match settings that we can use to achieve these goals with this program:
- [Rules](#rules)
- [Preferences](#preferences)
- [Tiebreaks](#tiebreaks)
- [Valid Pairs](#valid-pairs)

Rules, Preferences, and Tiebreaks (`RPT`) can each be set separately for schools and for teachers. Valid Pairs (`VP`) are properties of schools and teachers considered together. Below we cover each in turn in the context of the above example.

### Rules
Of all the `RPT` settings, rules are the most powerful. Rules can be thought of as an ordered set of filters with associated proportions for each filter in the set. Only once the group of schools or teachers selected by a filter have been satisfied up to their proportion of the total cap can the matching process consider any schools or teachers not selected by that filter, and their matches are locked in place from that point onwards. Multiple rules applying to the same attribute are processed in sequence. Rules applying to different attributes have their filters combined by boolean `and` and their proportions combined by multiplication over all combinations of the joint filter sequences.

In the context of our example we can fully implement goal number 1 with a sequence of rules and implement a part of goal number 3 with a single rule.

For goal 1 there is a special built-in interface in the `Schools` tab to generate rules based on either School type or District (or both) proportions entered by the user. Select the `School type constraints` expander and check the `Use school type constraints` checkbox. This will open up a set of sliders which can be adjusted to match the desired proportions. Afer entering these, go back to `Overview` and in the `Schools` expander this sequence of rules will have been be added. Using `School type constraints` sliders forces the proportions to add up to 1 (or 100%) so that the order of the rule sequence will not affect the outcome.

For goal 3 we can use the `Rule` tab from within the `Teachers` tab to add a rule which filters by "Government" in `Salary source` and then set a `Proportional cap` of zero with the slider. Click `Add Teachers_Rule` and return to `Overview` to see this rule listed under the `Teachers` expander.

Finally, there is a preset set of schools rules (selectable under `Fuction name` drop-down as `WB_rules.ruleschl` when `Use preset function` is checked) which can be selected. This function applies rules on districts and school types such that the districts are proportionally distributed according to the total need over the district and school types are proportionally distributed according to the total number of pupils accross the country in each school type.

#### NOTE:
When a preset function is chosen all other school rules are ignored in the final match.

### Preferences
Preferences are the second most powerful of the `RPT` settings. Where rules split the schools/teachers data into discrete sets which are processed in order, preferences apply to all of the data at the same time (within each rule set). Schools preferences are attributes of teachers and teachers preferences are attributes of schools (unlike schools and teachers rules and tiebreaks which are attributes of schools and teachers respectively). Each preference setting takes a field of the corresponding data and converts it into a numerical value (or uses the raw value if it is already numerical). Multiple preferences over different fields are combined by summation of their values.

In the working of the algorithm each school looks for teachers in turn. The order of turns is determined by the schools' current need for new teachers (this detail guarantees that we will always implement goal 2 in our example). When a school takes its turn to look for a new teacher it processes the teachers in the order of its teacher preference. If a school's preferred teacher is already provisionally taken by another school (which had an earlier turn) then the teacher will either decide to stay where they are or accept the new school based on their school preference order, staying if they don't prefer the new school to the current one or moving otherwise. If they choose to stay then the school moves to the next teacher in the order of preference and continues in this manner until the end of its current turn, which occurs when it is no longer the school with the most need for new teachers.

In the context of our example we can implement goal number 4 with a school preference on `Teaching qualification`. From the `Pref` tab within the `Schools` tab, select `Teaching qualification` from the `Teachers Attribute` drop-down menu and then multi-select every possible value from the `Values` drop-down menu. Below this set the desired numerical value for each value of the qualification (higher values are more preferred) and then click the `Add Schools_Pref` button. Back in `Overview` the preference has now been added to the `Schools` expander under `Pref`.

### Tiebreaks
Tiebreaks are the least powerful of the `RPT` settings. In many ways they are similar to preferences but they function slightly differently. Firstly, they are only applied in the case where two schools/teachers have equal preferences (hence the name tiebreak). Secondly, they use the attributes of the same data source (i.e. school tiebreaks are attributes of schools and teacher tiebreaks are attributes of teachers). Finally, they are combined by applying in sequence, where prefrences are combined by value summation - i.e. a second tiebreak wll be applied only when the first tiebreak is equal, a third only when both the first and second are equal, etc..

In the context of our example, we can implement both goals 5 and 6 by a combination of two teacher tiebreaks - first on `Gender` and second on `Service years`. From the `Tiebreak` tab within the `Teachers` tab, select `Gender` from the `Teachers Attribute` drop-down menu and then multi-select every possible value from the `Values` drop-down menu. Below this set the desired numerical value for each value of the gender (higher values are more preferred) and then click the `Add Teachers_Tiebreak` button. Now select `Service years` from the `Teachers Attribute` drop-down menu and click the `Add Teachers_Tiebreak` button (`Service years` is numerical already so we use the raw value). Back in `Overview` the tiebreak has now been added to the `Teachers` expander under `Tiebreak`.

### Valid Pairs
The final settings type `VP` are as powerful as the rules described above but operate slightly differently. They restrict the possible matches from all pairs of schools and teachers according to some joint property of the two. There are currently two types of `VP` rule implemented in the program - `Match Key` and `Radius`. `Match Key` enforces that the only possible matches can occur between schools and teachers that share the same value in the chosen field (this also requires that both data have this field to begin with). `Radius` uses the `Latitude` and `Longitude` values in the schools and teachers data to enforce that the only possible matches can occur between schools and teachers within a given radius of each other (in km).

In the context of our example we can implement the remaining part of goal number 3 with a `Match Key` rule. From the `Valid Pairs` tab select `Match Key` from the `Rule` drop-down menu and then from the `Key` drop-down menu select `School ID`. Click `Add pairing rule` and back in `Overview` this will be displayed under the `Valid Pairs` expander.

An alternative suggestion to goal 3. might be to restrict the match to `Match key` on `School type` but enforce a 2km `Radius` restriction. This would allow for more influence of the chosen `RPT` settings, and possibly a better overall match, provided that teachers are willing and able to move to new schools up to the chosen distance.

### Save project
With that we have implemented all of the stated goals in our example and we are ready to leave the `Match Settings`. We recommended at this stage to return to the [`Home`](#home) page and save the current project. This will allow the current project to be loaded at any time with the full data and filters along with the match settings that were entered above.

## Home
Now that data have been uploaded and match settings have been set the `Home` page has full functionality. If you reached this section before reading about those pages, you are directed here: [`Import Data`](#import-data) and here: [`Match Settings`](#match-settings). The main panel contains tabs for viewing and exporting the results of a match but until the match is run it is empty.

A match can be run with the current data and settings from the sidebar button `Run match`. A progress bar will appear at the bottom of the sidebar indicating the progress of the current match. Depending on the settings and the size of the data after filtering this process may take some. On completion the main panel tabs - `Results`, `Graphs`, `Before/After`, and `Maps` - will be populated.

`Results` contains the matched schools and teachers in two separate dataframes. The same rows in each dataframe correspond to a matched pair and the columns contain the values from the imported dataframes. Notably, the `global_index` column can be used to locate the matched school or teacher in the original csv files that were provided as input. Both the schools and teachers data can be saved separately from their `Export [Schools/Teachers] results` button.

`Graphs` contains a set of bar charts depicting the number of teachers hired according to each of the attributes `Gender`, `Service years`, and `School type` and the number of teachers assigned to schools in each `District`.

`Before/After` contains various comparisons between the overall school and teacher characteristics prior to the match and after it. As well as the above mentioned `Gender`, `Service years`, `School type`, and `District`, the GPE R Squared metric is also displayed at the top along with the change in this metric.

Finally `Maps` contains two geographical scatter plot of all the schools colored by their need prior to the match and by the number of teachers that they recieved in the match. These can be switched between with the `Need` and `Received` tabs.
