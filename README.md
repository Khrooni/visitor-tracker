# VisitorTracker
![alt text](img/p00-VisitorTracker.png)

# About
VisitorTracker is a Tkinter based GUI application that scrapes visitor data from a local gym's website, stores that data in a SQLite database, and draws different graphs from the collected data. This project was created as a hobby project to draw some interesting graphs and to gain some more coding experience.

VisitorTracker was designed to be compatible with multiple sources of data. Adding more data collection locations should be quite simple, requiring only to implement data scraping from a new website and adding a new option to the GUI for selecting which location to collect the data from. (I might choose to add more locations in the future if I regain my interest in this project again.)

# How to use - Demo

Example usage of the application.

**Opening screen**
![alt text](img/p01-main-menu.png)

**Use the 'Open Calendar' button to access the calendar**\
Dates with a green background indicate collected data, while non-highlighted dates have no data.
![alt text](img/p02-calendar.png)

**Use the 'Plot All Graphs' or 'Plot Graph' button to plot a graph**\
The number of graphs plotted by 'Plot All Graphs' depends on the selected 'Graph Amount' (e.g., if set to 2, only graphs 1 and 2 will be plotted). The 'Graph Amount' can be set to 1, 2, or 4.\
The 'Plot Graph' button plots only its specific graph and is disabled for tabs beyond the set 'Graph Amount' (e.g., if graph amount is set to 1, the 'Plot Graph' button for Graphs 2, 3, and 4 will be disabled).
![alt text](img/p03-plotted-1-graph.png)

**Select a graph mode, such as 'Most Visitors'**\
There are three graph modes: 'Visitors' calculates the average number of visitors for each hour, 'Most Visitors' selects the highest value for each hour, and 'Least Visitors' selects the lowest value for each hour. (Each hour may have multiple visitor readings if data was collected several times within that hour)
![alt text](img/p04-graph-mode.png)

**Plotted 'Most Visitors' graph**
![alt text](img/p05-most-visitors.png)

**Select a new Graph Amount**
![alt text](img/p06-graph-amount.png)

**4 different graphs plotted with 'Plot All Graphs' button**
![alt text](img/p07-plotted-4-graphs.png)

The graph numbers in the tabs correspond to this diagram:\
![alt text](img/square1234.png)

**2 plotted graphs**
![alt text](img/p08-plotted-2-graphs.png)

**Select a graph type, such as 'Line Graph'**
![alt text](img/p09-graph-type.png)

**Plotted Line Graph**
![alt text](img/p10-plotted-1-line-graph.png)

**Location selection**\
Multiple locations have not been implemented yet. New locations might be added in the future.
![alt text](img/p11-location.png)

**Select a time mode, such as 'Daily Average'**\
There are three time modes: 'Calendar' allows selection of a specific date, 'Daily Average' averages visitors by day of the week, and 'Time Range' allows selection of a period from the present back to various intervals, such as 48 hours, 7 days, 1 month, and so forth.
![alt text](img/p12-time-mode.png)

**Plotted 'Daily Average' graph (Monday)**
![alt text](img/p14-day.png)

**Plotted 'Daily Average' graph (Thursday)**
![alt text](img/p15-thursday.png)

**Selecting 'Time Range' as the time mode**
![alt text](img/p17-last.png)

**Plotted 'Time Range' graph (activity of last 3 months)**
![alt text](img/p18-last-3-months.png)

## Menubar

**Select 'Save Single Graph' from the 'File' dropdown**\
'Save Figure' option saves all displayed graphs as a single image. 'Save Single Graph' option opens a popup for selecting which graph to save as an image.

'Import Data' option opens the file manager to select another database (\*.db) and merges its visitor data with the current database. Initially created for debugging but I decided to keep it, can be useful for combining data from multiple devices if needed. 'Create Backup'-option creates a copy of the database file (\*.db). 'Change Database'-option lets user change the database that is used. 'Create Backup' and 'Change Database' were also both created for debugging but I decided to keep them even though they might not have that many use cases.
![alt text](img/p19-file.png)

**Select the number of the graph that you wish to save and press 'OK'**\
(The 'OK' button is hidden behind the graph number options in this picture)
![alt text](img/p20-save-single-graph.png)

## Database View

**Select 'Database' from the 'View' dropdown**\
'Graphs' option and 'Database' option open their respective pages.
![alt text](img/p21-view.png)

**Select the 'Data Collection Interval', such as 30 seconds**\
All changes made in the database page will show in the 'Database events' sidebar.
![alt text](img/p22-database.png)

**Start data collection**\
Data collection continues in the background until it is stopped or the application is closed.
![alt text](img/p23-interval.png)

**Stop data collection**
![alt text](img/p24-start.png)

**Select a different data collection interval and start collecting data**
![alt text](img/p25-stop.png)

**Collected data**
![alt text](img/p26-collect-data.png)

## Settings

**Open 'Settings'**
![alt text](img/p27-before-settings.png)

**Settings popup**\
Clicking the current database name opens a file manager to select a new database. 'Use Default Database' reverts it back to the default database.\
There are three 'Y-axis upper limit'-modes: 'Auto Limit' adjusts the upper limit across all graphs based on the highest value when a new graph is drawn, 'No Limit' lets each graph set its own upper limit, and 'Select Limit' allows user to set a fixed upper limit for all graphs.\
'Reset' restores all settings to their defaults, 'OK' saves any changes, and 'Cancel' discards them.
![alt text](img/p28-settings.png)

**Different upper limit options**
![alt text](img/p29-y-axis.png)

**Save changes by clicking 'OK'**
![alt text](img/p30-no-limit.png)

**4 graphs with Auto Limit**
![alt text](img/p31-4-graphs-auto-limit.png)

**4 graphs with No Limit**
![alt text](img/p32-4-graphs-no-limit.png)

**Select Limit**
![alt text](img/p33-select-limit.png)

**100 as the upper limit**
![alt text](img/p34-select-limit-100.png)

**Save changes**
![alt text](img/p35-limit-100.png)

**4 graphs No Limit**
![alt text](img/p36-plot-all.png)

**4 graphs Select Limit (100)**
![alt text](img/p37-4-graphs-100-limit.png)
