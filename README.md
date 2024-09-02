# Draw graph from collected data

Collects data from a gym's website about how many visitors are at the gym at any given time. Draws different graphs from the data.

# About

KORJAA!(name here) is a Tkinter based GUI application that scrapes visitor data from a local gym's website, stores that data in a SQLite database, and draws different graphs from the collected data. This project was created as a hobby project to draw some interesting graphs and to gain some more coding experience.

KORJAA!-app was designed to be compatible with multiple sources of data. Adding more data collection locations should be quite simple, requiring only to implement data scraping from a new website and adding a new option to the GUI for selecting which location to collect the data from. (I might choose to add more locations in the future if I regain my interest in this project again.)

# How to use - Demo

Example usage of the application.

**Starting screen.**
![alt text](img\p01-main-menu.png)

**Open the calendar by pressing the "Open Calendar"- button.** The dates in the calendar that are highlighted by green background signify dates with data collected and dates without the green background don't have any collected data.
![alt text](img/p02-calendar.png)

**Plot a graph by pressing "Plot All Graphs"-button or "Plot Graph"-button.** "Plot all graphs"-button will plot all graphs shown on screen (the amount of graphs depends on the selected Graph Amount: 1, 2 or 4). "Plot Graph"-button only plots its connected graph. The "Plot Graph"-button is disabled in all tabs exceeding the graph amount. (For example, if graph amount is set to 1 and user selects Graph 2,3 or 4 the "Plot Graph" button for those tabs will be disabled.)
![alt text](img/p03-plotted-1-graph.png)

**Select graph mode. Most Visitors in this case.**
![alt text](img/p04-graph-mode.png)

****
![alt text](img/p05-most-visitors.png)

![alt text](img/p06-graph-amount.png)

![alt text](img/p07-plotted-4-graphs.png)

![alt text](img/p08-plotted-2-graphs.png)

![alt text](img/p09-graph-type.png)

![alt text](img/p10-plotted-1-line-graph.png)

![alt text](img/p11-location.png)

![alt text](img/p12-time-mode.png)

![alt text](img/p13-daily-average.png)

![alt text](img/p14-weekday.png)

![alt text](img/p15-weekday-thu.png)

![alt text](img/p16-Time-range.png)

![alt text](img/p17-last.png)

![alt text](img/p18-last-3-months.png)

![alt text](img/p19-file.png)

![alt text](img/p20-save-single-graph.png)

![alt text](img/p21-view.png)

![alt text](img/p22-database.png)

![alt text](img/p23-interval.png)

![alt text](img/p24-start.png)

![alt text](img/p25-stop.png)

![alt text](img/p26-collect-data.png)

![alt text](img/p27-settings.png)

![alt text](img/p28-y-axis.png)

![alt text](img/p29-no-limit.png)

![alt text](img/p30-plot-4-no-limit.png)

![alt text](img/p31-choose-limit.png)

![alt text](img/p32-100-limit.png)

![alt text](img/p33-plot-4-limit-100.png)



