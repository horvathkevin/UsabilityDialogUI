#!/usr/bin/env python
import os
import json

# Importing the libraries
import numpy as np
import matplotlib.pyplot as plt

from matplotlib.ticker import FuncFormatter

import csv

""" r before string converts string into raw string """
standardUIDir= r"C:\Users\kevin\Dropbox\BITI 6.Semester\BA\Testergebnisse\StandardUI"
dialogUIDir = r"C:\Users\kevin\Dropbox\BITI 6.Semester\BA\Testergebnisse\DialogUI"
 
def getMetricsForParticipant( filePath ):
   with open(filePath) as dataFile:    
    data = json.load(dataFile) 
    return data

def getMetricsForUIVersion ( dir ):
    metrics = []
    files = os.listdir(dir)
    
    for name in files:
        path = os.path.join(dir, name)
        metrics.append(getMetricsForParticipant(path))
        
    return metrics

def getTaskMetrics ( metricCollection, taskId ):
    return metricCollection[taskId];

def getDurationByTask ( metricCollection ):
    return metricCollection["_duration"];

def getActionCountByTask ( metricCollection ):
    return metricCollection["_countActionsUser"];

def getErrorRateByTask ( metricCollection ):
    return metricCollection["_errorRate"];

def getActionsByTask ( metricCollection ):
    return metricCollection["_actions"];

def getMetricSeriesForTask ( rawMetricData, taskId ):
    taskMetrics = {}
    summarizedActions = {}
    summarizedActionArray = []
    totalActions = 0
    taskDataFromCollection = list( map( lambda metricCollection : metricCollection[taskId], rawMetricData ) )
    
    taskMetrics["actionCount"] = list( map( getActionCountByTask, taskDataFromCollection) )
    taskMetrics["duration"] = list( map( getDurationByTask, taskDataFromCollection) )
    taskMetrics["errorRate"] = list( map( getErrorRateByTask, taskDataFromCollection) )

    for metricCollection in taskDataFromCollection:
        actions = metricCollection["_actions"]
        totalActions = totalActions + len(actions)
        
        for action in actions:
            actionName = action["action"]
            if actionName in summarizedActions:
                summarizedActions[actionName] = summarizedActions[actionName] + 1
            else:
                summarizedActions[actionName] = 1
                
    for action in summarizedActions:
        item = {}
        item["name"] = action
        item["value"] = summarizedActions[action] / totalActions * 100
        
        summarizedActionArray.append(item)

    summarizedActionArray.sort(key=getActionValue)
    summarizedActionArray.reverse()
    taskMetrics["actions"] = summarizedActionArray
    
    return taskMetrics


def getActionValue ( item ):
    return item["value"]



def getMetricSeriesForUIVersion ( rawMetricData ):
    summarizedMetricData = []
    
    for taskId in range(5):
        summarizedMetricData.append(getMetricSeriesForTask(rawMetricData, taskId)) 
        
    return summarizedMetricData

def toPercent(x, pos=None):
    'The two args are the value and tick position'
    return ( "%.2f" % x ) + " %"

def toSeconds(x, pos=None):
    'The two args are the value and tick position'
    return ( "%.2f" % x ) + " s"

def showBarGraphMetrics ( dataStandard, dataDialog, title, yAxisLabel, formatter ):
    xLabels = []
    fig, ax = plt.subplots()
    x = np.arange(len(dataStandard))
    width = 0.35
    
    if formatter is not None:
        ax.yaxis.set_major_formatter(FuncFormatter(formatter))        
   
    standardUISeries = plt.bar(x - width/2, dataStandard, width=width, color="#D7191C", zorder=3, label="Standard UI")
    dialogUISeries = plt.bar(x + width/2, dataDialog, width=width, color="#2C7BB6", zorder=3, label="Dialog UI")
    
    for i in x:
        xLabels.append("Proband" + str(i + 1))
    
    plt.xticks(x, xLabels)
    ax.set_ylabel(yAxisLabel)
    ax.set_title(title)
    ax.grid(zorder=0, axis="y")
    ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.075), ncol=2, fancybox=True)
     
    autoLabel(ax, standardUISeries, formatter)
    autoLabel(ax, dialogUISeries, formatter)
    
    plt.show()
    
    
    
def showBarGraphActions ( data, title, yAxisLabel, formatter ):
    xLabels = []
    fig, ax = plt.subplots()
    x = np.arange(len(data))
    width = 0.35
    chartData = []
    
    for i in data:
        chartData.append(data[i]["value"])
        xLabels.append(data[i]["name"])
    
    if formatter is not None:
        ax.yaxis.set_major_formatter(FuncFormatter(formatter))        
   
    series = plt.bar(x, chartData, width=width, color="#D7191C", zorder=3, label="Aufteilung Aufgaben")
    
    plt.xticks(x, xLabels)
    ax.set_ylabel(yAxisLabel)
    ax.set_title(title)
    ax.grid(zorder=0, axis="y")
    ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.075), ncol=2, fancybox=True)
     
    autoLabel(ax, series, formatter)
    
    plt.show()
    
    
def autoLabel(ax, rects, formatter=None, xpos='center'):
    """
    Attach a text label above each bar in *rects*, displaying its height.

    *xpos* indicates which side to place the text w.r.t. the center of
    the bar. It can be one of the following {'center', 'right', 'left'}.
    """
    xpos = xpos.lower()  # normalize the case of the parameter
    ha = {'center': 'center', 'right': 'left', 'left': 'right'}
    offset = {'center': 0.5, 'right': 0.57, 'left': 0.43}  # x_txt = x + w*off

    for rect in rects:
        height = rect.get_height()
        label = height
        
        if formatter is not None:
            label = formatter(height)
        
        ax.text(rect.get_x() + rect.get_width() * offset[xpos], 1.01 * height,
                label, ha=ha[xpos], va='bottom')

def set_box_color(bp, color):
    plt.setp(bp['boxes'], color=color)
    plt.setp(bp['whiskers'], color=color)
    plt.setp(bp['caps'], color=color)
    plt.setp(bp['medians'], color=color)
    plt.setp(bp['fliers'], color=color)
    
def add_values(bp, ax, formatter = None ):
    """ This actually adds the numbers to the various points of the boxplots"""
    for element in ['whiskers', 'medians', 'caps', 'fliers']:
        for line in bp[element]:
            x_l = 0
            x_r = 0
            y = 0
            # Get the position of the element. y is the label you want
            if element == "fliers":
                xyData = line.get_xydata()
                # When there is no flier, continue
                if xyData.size == 0:
                    continue
                
                x_l = x_r = xyData[0][0] + 0.1
                y = xyData[0][1]
            else:
                (x_l, y),(x_r, _) = line.get_xydata()
            # Make sure datapoints exist 
            # (I've been working with intervals, should not be problem for this case)
            if not np.isnan(y): 
                label = y
                
                if formatter is not None:
                    label = formatter(label)  
                
                x_line_center = x_l + (x_r - x_l)/2
                y_line_center = y  # Since it's a line and it's horisontal
                # overlay the value:  on the line, from center to right
                ax.text(x_line_center, y_line_center, # Position
                        label, # Value (3f = 3 decimal float)
                        verticalalignment='center', # Centered vertically with line 
                        fontsize=14, backgroundcolor="white")
    
def showBoxPlot ( dataStandard, dataDialog, title ):
    fig, ax = plt.subplots()
    fig.subplots_adjust(right=0.75)    
    ax.set_title(title)
     
    ax2 = ax.twinx()  # instantiate a second axes that shares the same x-axis
    ax3 = ax.twinx()  # instantiate a third axes that shares the same x-axis
    
    ax3.spines["right"].set_position(("axes", 1.05))
    ax3.spines["right"].set_visible(True)
    
    ax.set_ylabel("Zeitdauer in Sekunden")
    ax2.set_ylabel("Anzahl Aktionen")
    ax3.set_ylabel("Fehlerrate in %")
    
    
    standardFlierProps = dict(marker='o', markerfacecolor="#D7191C", markersize=5,
                  linestyle='none', markeredgecolor="#D7191C")
    
    dialogFlierProps = dict(marker='o', markerfacecolor="#2C7BB6", markersize=5,
                  linestyle='none', markeredgecolor="#2C7BB6")
    
    
    standardBox1 = ax.boxplot(dataStandard[0], positions = [0.5], widths = 0.2, flierprops=standardFlierProps)
    standardBox2 = ax2.boxplot(dataStandard[1], positions = [1.5], widths = 0.2, flierprops=standardFlierProps)
    standardBox3 = ax3.boxplot(dataStandard[2], positions = [2.5], widths = 0.2, flierprops=standardFlierProps)
    
    dialogBox1 = ax.boxplot(dataDialog[0], positions = [1], widths = 0.2, flierprops=dialogFlierProps)
    dialogBox2 = ax2.boxplot(dataDialog[1], positions = [2], widths = 0.2, flierprops=dialogFlierProps)
    dialogBox3 = ax3.boxplot(dataDialog[2], positions = [3], widths = 0.2, flierprops=dialogFlierProps)
    
    set_box_color(standardBox1, '#D7191C') # colors are from http://colorbrewer2.org/
    set_box_color(standardBox2, '#D7191C') # colors are from http://colorbrewer2.org/
    set_box_color(standardBox3, '#D7191C') # colors are from http://colorbrewer2.org/
           
    add_values(standardBox1, ax, toSeconds)
    add_values(standardBox2, ax2)
    add_values(standardBox3, ax3, toPercent)
    
    add_values(dialogBox1, ax, toSeconds)
    add_values(dialogBox2, ax2)
    add_values(dialogBox3, ax3, toPercent)
                  
    set_box_color(dialogBox1, '#2C7BB6')
    set_box_color(dialogBox2, '#2C7BB6')
    set_box_color(dialogBox3, '#2C7BB6')

    ax.set_xlim(0.25, 3.25)
    ax.set_xticks([0.75, 1.75, 2.75])
    ax.set_xticklabels(["Bearbeitungsdauer", "Anzahl Aktionen", "Fehlerrate"])
    
    
    ax.tick_params(axis="x", labelsize=14)
    ax.tick_params(axis="y", labelsize=14)
    ax2.tick_params(axis="y", labelsize=14)
    ax3.tick_params(axis="y", labelsize=14)
    
    # draw temporary red and blue lines and use them to create a legend
    ax.plot([], c='#D7191C', label='StandardUI')
    ax.plot([], c='#2C7BB6', label='DialogUI')
    ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.075), ncol=2, fancybox=True)
    


def showPieChart (data, title):
    labels = []
    values = []
    sum = 0
    
    fig, ax = plt.subplots(figsize=(6, 3), subplot_kw=dict(aspect="equal"))

    for item in data:
        labels.append(item["name"] + "(" + toPercent(item["value"]) + ")" )
        values.append(item["value"])
        sum = sum + item["value"]
    
    
    wedges, texts = ax.pie(values, wedgeprops=dict(width=0.3), startangle=-30)
    
    bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0.72)
    kw = dict(arrowprops=dict(arrowstyle="-"),
              bbox=bbox_props, zorder=0, va="center")
    
    for i, p in enumerate(wedges):
        ang = (p.theta2 - p.theta1)/2. + p.theta1
        y = np.sin(np.deg2rad(ang))
        x = np.cos(np.deg2rad(ang))
        horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
        connectionstyle = "angle,angleA=0,angleB={}".format(ang)
        kw["arrowprops"].update({"connectionstyle": connectionstyle})
        ax.annotate(labels[i], xy=(x, y), xytext=(1.35*np.sign(x), 1.4*y),
                    horizontalalignment=horizontalalignment, **kw)
    
    ax.set_title(title)
    
    plt.show()


    
rawStandardUIMetrics = getMetricsForUIVersion(standardUIDir);
rawDialogUIMetrics = getMetricsForUIVersion(dialogUIDir);

summarizedStandardUIMetricData = getMetricSeriesForUIVersion(rawStandardUIMetrics)
summarizedDialogUIMetricData = getMetricSeriesForUIVersion(rawDialogUIMetrics)



for i in range(5):
    csvData = [
        ["Probanden", "1", "", "2", "",  "3", "",  "4", "",  "5", "",  "6", "",  "7", "",  "8", "", "9", "", "10", "", "Mittelwert Dialog", "Mittelwert Standard"],
        ["Anzahl Aktionen"],
        ["Bearbeitungszeit"],
        ["Fehlerrate"]
    ]
    
    for j in range(10):
        #add action count data
        csvData[1].append(summarizedStandardUIMetricData[i]["actionCount"][j])
        csvData[1].append(summarizedDialogUIMetricData[i]["actionCount"][j])
        
        #add duration data
        csvData[2].append(toSeconds(summarizedStandardUIMetricData[i]["duration"][j]))
        csvData[2].append(toSeconds(summarizedDialogUIMetricData[i]["duration"][j]))
        
        #error rate data
        csvData[3].append(toPercent(summarizedStandardUIMetricData[i]["errorRate"][j]))
        csvData[3].append(toPercent(summarizedDialogUIMetricData[i]["errorRate"][j]))
        
        
    #add action count means
    csvData[1].append(np.mean(summarizedStandardUIMetricData[i]["actionCount"]))
    csvData[1].append(np.mean(summarizedDialogUIMetricData[i]["actionCount"]))
    
     #add action count means
    csvData[2].append(toSeconds(np.mean(summarizedStandardUIMetricData[i]["duration"])))
    csvData[2].append(toSeconds(np.mean(summarizedDialogUIMetricData[i]["duration"])))
    
     #add action count means
    csvData[3].append(toPercent(np.mean(summarizedStandardUIMetricData[i]["errorRate"])))
    csvData[3].append(toPercent(np.mean(summarizedDialogUIMetricData[i]["errorRate"])))
    
    with open('Aufgabe_' + str(i + 1) + '.csv', mode='w') as taskFile:
        taskWriter = csv.writer(taskFile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        for row in csvData:
            taskWriter.writerow(row)
    
    dataStandard = [
        summarizedStandardUIMetricData[i]["duration"],
        summarizedStandardUIMetricData[i]["actionCount"],
        summarizedStandardUIMetricData[i]["errorRate"]
    ]
    
    dataDialog = [
        summarizedDialogUIMetricData[i]["duration"],
        summarizedDialogUIMetricData[i]["actionCount"],
        summarizedDialogUIMetricData[i]["errorRate"]
    ]
    
    
    
    #showPieChart(summarizedStandardUIMetricData[i]["actions"], "Verteilung Aktionen Standard UI Aufgabe" + str(i + 1) )
    showPieChart(summarizedDialogUIMetricData[i]["actions"], "Verteilung Aktionen Dialog UI Aufgabe" + str(i + 1) )
    
    
    """showBoxPlot( dataStandard, dataDialog, "Gegenüberstellung Metriken Aufgabe" + str(i + 1))
    
    showBarGraphMetrics(
        summarizedStandardUIMetricData[i]["duration"], 
        summarizedDialogUIMetricData[i]["duration"], 
        "Bearbeitungszeit Aufgabe" + str(i + 1), 
        "Bearbeitungszeit in s", 
        toSeconds
    )
    
    showBarGraphMetrics(
        summarizedStandardUIMetricData[i]["actionCount"],
         summarizedDialogUIMetricData[i]["actionCount"],
         "Anzahl Aktionen Aufgabe" + str(i + 1),
         "Anzahl Aktionen",
         None
     )
    
    showBarGraphMetrics(
        summarizedStandardUIMetricData[i]["errorRate"],
         summarizedDialogUIMetricData[i]["errorRate"],
         "Fehlerrate Aufgabe" + str(i + 1),
         "Fehlerrate in %",
         toPercent
     )
    """
    
    

    


