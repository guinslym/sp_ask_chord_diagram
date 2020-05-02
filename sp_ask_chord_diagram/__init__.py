__version__ = '0.1.2'
import warnings
warnings.filterwarnings("ignore")

import lh3.api
from datetime import date
from datetime import datetime
from pprint import pprint as print
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup


from sp_ask_report_chats_per_school import get_nbr_of_chats_per_school_for_this_day
from ask_schools import queue_university, queue_simple_name
from ask_schools import get_shortname_by_full_school_name

import lh3.api
from ask_schools import school_name, find_school_by_operator_suffix
from ask_schools import find_school_by_queue_or_profile_name
from ask_schools import find_school_by_operator_suffix, school_name
from sp_ask_chats_utils import remove_practice_queues
from sp_ask_chats_utils import get_chats_answered


def remove_columns_from_df(df, columns):
    df.drop(columns, axis=1, inplace=True)
    return df


def get_chats_for_this_date_range(year, month, day, to=None):
    client = lh3.api.Client()
    chats = client.chats().list_day(year, month, day, to=to)
    chats_this_day = remove_practice_queues(chats)
    chats_answered = get_chats_answered(chats_this_day)
    df = prepare_to_dataframe(chats_answered)
    return df

def prepare_to_dataframe(chats_answered)  :  
    df = pd.DataFrame(chats_answered)
    df["guest"] = df['guest'].apply(lambda x:x[0:7])
    df["from"] = df['queue'].apply(lambda x: find_school_by_queue_or_profile_name(x))
    df["to"] = df['operator'].apply(lambda x: find_school_by_operator_suffix(x))
    df["school"] = df['to'].apply(lambda x: school_name.get(x).get('full') )
    df["short"] = df['from'].apply(lambda x: get_shortname_by_full_school_name(x) )
    columns = ['duration','reftracker_id', 'started','operator',
        'reftracker_url','desktracker_id', 'ended', 'queue',
        'desktracker_url','wait', 'profile', 'id',
        'referrer','ip','accepted','protocol']
    df = remove_columns_from_df(df, columns)
    del df["from"] 
    df.rename({'short': 'from'}, axis=1, inplace=True)
    columns = ["guest", "from", "to"]
    df = df[columns]
    df.sort_values(by=['from'])
    df = df.groupby('from')['to'].value_counts().reset_index(name='value')
    # df.to_excel("for_chordiagram.xlsx", index=False)
    # df.to_csv("for_chordiagram.csv", index=False)
    return df

def gephi_data(df):
    schools = list(set(list(df['from'].unique() )+ list(df['to'].unique())))
    nodes = pd.DataFrame({'id':np.arange(1, len(schools)+1) , 'label': schools})
    
    gephi = df.merge(nodes, left_on='from', right_on='label')
    gephi = gephi.merge(nodes, left_on='to', right_on='label')
    edges = gephi[['id_x', 'id_y']]
    edges['source'] = gephi['id_x']
    edges['target'] = gephi['id_y']
    edges['weight'] = gephi['value']

    del edges['id_x']
    del edges['id_y']
    
    return [nodes, edges]

def get_data_for_gephi(year, month, day, to=None):
    df = get_chats_for_this_date_range(2019, 9, 9, to="2020-04-30")
    data  = gephi_data(df)
    return data

def get_data_for_chord_diagram(year, month, day, to=None):
    df = get_chats_for_this_date_range(2019, 9, 9, to="2020-04-30")
    df.columns = ['from', 'to', 'value']
    return df


def get_html_template():
    html_doc ="""
        <!DOCTYPE html>
        <html lang="en" >
        <head>
        <meta charset="UTF-8">
        <title>Ask School chord diagram</title>
        <link rel="stylesheet" href="./style.css">

        <style>
        body {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol";
        }

        body { background-color: #30303d; color: #fff; }
        #chartdiv {
        width: 100%;
        height: 800px;
        }
        </style>

        </head>
        <body>

        <!-- partial:index.partial.html -->
        <script src="https://www.amcharts.com/lib/4/core.js"></script>
        <script src="https://www.amcharts.com/lib/4/charts.js"></script>
        <script src="https://www.amcharts.com/lib/4/themes/dark.js"></script>
        <script src="https://www.amcharts.com/lib/4/themes/animated.js"></script>
        <div id="chartdiv"></div>
        <!-- partial -->
        <script>
        var data = [
            // node property fields take data from data items where they are first mentioned, that's 
            // why we add empty data items at the beginning and set colors here

                {"from":"Algoma","to":"Mentee","value":7},{"from":"Algoma","to":"Guelph","value":4},{"from":"Algoma","to":"York","value":4},{"from":"Algoma","to":"Ontario Tech","value":3},{"from":"Algoma","to":"Ryerson","value":3},{"from":"Algoma","to":"Guelph-Humber","value":2},{"from":"Algoma","to":"Lakehead","value":2},{"from":"Algoma","to":"Ottawa","value":2},{"from":"Algoma","to":"Queens","value":2},{"from":"Algoma","to":"Western","value":2},{"from":"Algoma","to":"Brock","value":1},{"from":"Algoma","to":"Carleton","value":1},{"from":"Algoma","to":"McMaster","value":1},{"from":"Brock","to":"Mentee","value":36},{"from":"Brock","to":"Brock","value":14},{"from":"Brock","to":"Guelph","value":14},{"from":"Brock","to":"Ryerson","value":10},{"from":"Brock","to":"McMaster","value":8},{"from":"Brock","to":"Queens","value":7},{"from":"Brock","to":"York","value":6},{"from":"Brock","to":"Guelph-Humber","value":5},{"from":"Brock","to":"Carleton","value":4},{"from":"Brock","to":"Ontario Tech","value":4},{"from":"Brock","to":"Ottawa","value":3},{"from":"Brock","to":"Western","value":3},{"from":"Brock","to":"Algoma","value":2},{"from":"Brock","to":"Lakehead","value":2},{"from":"Brock","to":"Laurentian","value":2},{"from":"Brock","to":"Scholars Portal","value":2},{"from":"Carleton","to":"Carleton","value":71},{"from":"Carleton","to":"Mentee","value":42},{"from":"Carleton","to":"McMaster","value":25},{"from":"Carleton","to":"Western","value":13},{"from":"Carleton","to":"York","value":11},{"from":"Carleton","to":"Scholars Portal","value":7},{"from":"Carleton","to":"Guelph","value":6},{"from":"Carleton","to":"Guelph-Humber","value":5},{"from":"Carleton","to":"Lakehead","value":4},{"from":"Carleton","to":"Ottawa","value":4},{"from":"Carleton","to":"Queens","value":4},{"from":"Carleton","to":"Ryerson","value":3},{"from":"Carleton","to":"Brock","value":1},{"from":"Guelph","to":"Guelph","value":82},{"from":"Guelph","to":"Mentee","value":65},{"from":"Guelph","to":"Guelph-Humber","value":28},{"from":"Guelph","to":"Ryerson","value":19},{"from":"Guelph","to":"York","value":18},{"from":"Guelph","to":"Carleton","value":9},{"from":"Guelph","to":"Ottawa","value":9},{"from":"Guelph","to":"Western","value":9},{"from":"Guelph","to":"McMaster","value":8},{"from":"Guelph","to":"Queens","value":7},{"from":"Guelph","to":"Lakehead","value":5},{"from":"Guelph","to":"Ontario Tech","value":4},{"from":"Guelph","to":"Toronto","value":3},{"from":"Guelph","to":"Brock","value":1},{"from":"Guelph","to":"Laurentian","value":1},{"from":"Guelph","to":"Scholars Portal","value":1},{"from":"Guelph-Humber","to":"Mentee","value":73},{"from":"Guelph-Humber","to":"Guelph","value":34},{"from":"Guelph-Humber","to":"York","value":22},{"from":"Guelph-Humber","to":"Guelph-Humber","value":9},{"from":"Guelph-Humber","to":"McMaster","value":7},{"from":"Guelph-Humber","to":"Carleton","value":6},{"from":"Guelph-Humber","to":"Queens","value":6},{"from":"Guelph-Humber","to":"Ryerson","value":3},{"from":"Guelph-Humber","to":"Brock","value":2},{"from":"Guelph-Humber","to":"Toronto","value":2},{"from":"Guelph-Humber","to":"Ontario Tech","value":1},{"from":"Guelph-Humber","to":"Ottawa","value":1},{"from":"Guelph-Humber","to":"Western","value":1},{"from":"Lakehead","to":"Mentee","value":51},{"from":"Lakehead","to":"Lakehead","value":19},{"from":"Lakehead","to":"York","value":15},{"from":"Lakehead","to":"Guelph","value":14},{"from":"Lakehead","to":"McMaster","value":12},{"from":"Lakehead","to":"Ontario Tech","value":9},{"from":"Lakehead","to":"Ryerson","value":9},{"from":"Lakehead","to":"Ottawa","value":5},{"from":"Lakehead","to":"Carleton","value":4},{"from":"Lakehead","to":"Brock","value":3},{"from":"Lakehead","to":"Laurentian","value":2},{"from":"Lakehead","to":"Scholars Portal","value":2},{"from":"Lakehead","to":"Western","value":2},{"from":"Lakehead","to":"Guelph-Humber","value":1},{"from":"Lakehead","to":"Saint-Paul","value":1},{"from":"Lakehead","to":"Toronto","value":1},{"from":"Laurentian","to":"Mentee","value":33},{"from":"Laurentian","to":"Laurentian","value":21},{"from":"Laurentian","to":"Ottawa","value":13},{"from":"Laurentian","to":"Queens","value":12},{"from":"Laurentian","to":"York","value":10},{"from":"Laurentian","to":"Guelph","value":7},{"from":"Laurentian","to":"McMaster","value":6},{"from":"Laurentian","to":"Ryerson","value":6},{"from":"Laurentian","to":"Lakehead","value":5},{"from":"Laurentian","to":"Guelph-Humber","value":4},{"from":"Laurentian","to":"Brock","value":3},{"from":"Laurentian","to":"Carleton","value":2},{"from":"Laurentian","to":"Ontario Tech","value":2},{"from":"Laurentian","to":"Saint-Paul","value":2},{"from":"Laurentian","to":"Toronto","value":1},{"from":"Laurentian","to":"Western","value":1},{"from":"McMaster","to":"McMaster","value":147},{"from":"McMaster","to":"Mentee","value":91},{"from":"McMaster","to":"Guelph","value":24},{"from":"McMaster","to":"York","value":21},{"from":"McMaster","to":"Ottawa","value":17},{"from":"McMaster","to":"Queens","value":15},{"from":"McMaster","to":"Carleton","value":13},{"from":"McMaster","to":"Ryerson","value":12},{"from":"McMaster","to":"Western","value":12},{"from":"McMaster","to":"Lakehead","value":9},{"from":"McMaster","to":"Brock","value":8},{"from":"McMaster","to":"Scholars Portal","value":8},{"from":"McMaster","to":"Ontario Tech","value":5},{"from":"McMaster","to":"Guelph-Humber","value":4},{"from":"McMaster","to":"Laurentian","value":3},{"from":"McMaster","to":"Toronto","value":2},{"from":"Ontario Tech","to":"Mentee","value":43},{"from":"Ontario Tech","to":"Ontario Tech","value":13},{"from":"Ontario Tech","to":"Guelph","value":9},{"from":"Ontario Tech","to":"McMaster","value":9},{"from":"Ontario Tech","to":"Ryerson","value":8},{"from":"Ontario Tech","to":"York","value":8},{"from":"Ontario Tech","to":"Guelph-Humber","value":7},{"from":"Ontario Tech","to":"Toronto","value":3},{"from":"Ontario Tech","to":"Carleton","value":2},{"from":"Ontario Tech","to":"Lakehead","value":2},{"from":"Ontario Tech","to":"Ottawa","value":2},{"from":"Ontario Tech","to":"Brock","value":1},{"from":"Ontario Tech","to":"Queens","value":1},{"from":"Ontario Tech","to":"Western","value":1},{"from":"Ottawa","to":"Ottawa","value":177},{"from":"Ottawa","to":"Mentee","value":83},{"from":"Ottawa","to":"Saint-Paul","value":29},{"from":"Ottawa","to":"York","value":23},{"from":"Ottawa","to":"Queens","value":14},{"from":"Ottawa","to":"Ryerson","value":13},{"from":"Ottawa","to":"Guelph","value":9},{"from":"Ottawa","to":"Carleton","value":8},{"from":"Ottawa","to":"McMaster","value":7},{"from":"Ottawa","to":"Scholars Portal","value":6},{"from":"Ottawa","to":"Laurentian","value":4},{"from":"Ottawa","to":"Western","value":4},{"from":"Ottawa","to":"Brock","value":2},{"from":"Ottawa","to":"Lakehead","value":2},{"from":"Ottawa","to":"Ontario Tech","value":2},{"from":"Ottawa","to":"Toronto","value":1},{"from":"Queens","to":"Queens","value":91},{"from":"Queens","to":"Mentee","value":51},{"from":"Queens","to":"Guelph","value":26},{"from":"Queens","to":"McMaster","value":20},{"from":"Queens","to":"Ryerson","value":19},{"from":"Queens","to":"Carleton","value":15},{"from":"Queens","to":"York","value":12},{"from":"Queens","to":"Western","value":9},{"from":"Queens","to":"Laurentian","value":7},{"from":"Queens","to":"Ottawa","value":7},{"from":"Queens","to":"Scholars Portal","value":6},{"from":"Queens","to":"Guelph-Humber","value":5},{"from":"Queens","to":"Lakehead","value":5},{"from":"Queens","to":"Ontario Tech","value":5},{"from":"Queens","to":"Algoma","value":1},{"from":"Queens","to":"Toronto","value":1},{"from":"Ryerson","to":"Ryerson","value":349},{"from":"Ryerson","to":"Mentee","value":244},{"from":"Ryerson","to":"York","value":50},{"from":"Ryerson","to":"Guelph","value":29},{"from":"Ryerson","to":"McMaster","value":25},{"from":"Ryerson","to":"Queens","value":19},{"from":"Ryerson","to":"Carleton","value":8},{"from":"Ryerson","to":"Ottawa","value":8},{"from":"Ryerson","to":"Laurentian","value":7},{"from":"Ryerson","to":"Western","value":7},{"from":"Ryerson","to":"Toronto","value":5},{"from":"Ryerson","to":"Brock","value":3},{"from":"Ryerson","to":"Guelph-Humber","value":3},{"from":"Ryerson","to":"Lakehead","value":3},{"from":"Ryerson","to":"Ontario Tech","value":3},{"from":"Ryerson","to":"Algoma","value":1},{"from":"Ryerson","to":"Saint-Paul","value":1},{"from":"Ryerson","to":"Scholars Portal","value":1},{"from":"Saint-Paul","to":"Ottawa","value":10},{"from":"Saint-Paul","to":"York","value":4},{"from":"Saint-Paul","to":"Ryerson","value":3},{"from":"Saint-Paul","to":"Guelph-Humber","value":2},{"from":"Saint-Paul","to":"Mentee","value":2},{"from":"Saint-Paul","to":"Carleton","value":1},{"from":"Saint-Paul","to":"Guelph","value":1},{"from":"Saint-Paul","to":"Queens","value":1},{"from":"Saint-Paul","to":"Saint-Paul","value":1},{"from":"Saint-Paul","to":"Western","value":1},{"from":"Scholars Portal","to":"Western","value":1},{"from":"Toronto","to":"Toronto","value":1455},{"from":"Toronto","to":"Mentee","value":64},{"from":"Toronto","to":"Guelph","value":45},{"from":"Toronto","to":"Ryerson","value":21},{"from":"Toronto","to":"York","value":17},{"from":"Toronto","to":"Queens","value":15},{"from":"Toronto","to":"Lakehead","value":14},{"from":"Toronto","to":"Ontario Tech","value":12},{"from":"Toronto","to":"Western","value":12},{"from":"Toronto","to":"McMaster","value":11},{"from":"Toronto","to":"Carleton","value":9},{"from":"Toronto","to":"Ottawa","value":8},{"from":"Toronto","to":"Guelph-Humber","value":4},{"from":"Toronto","to":"Saint-Paul","value":4},{"from":"Toronto","to":"Scholars Portal","value":4},{"from":"Toronto","to":"Laurentian","value":2},{"from":"Toronto","to":"Algoma","value":1},{"from":"Toronto","to":"Brock","value":1},{"from":"Western","to":"Western","value":435},{"from":"Western","to":"Mentee","value":195},{"from":"Western","to":"Guelph","value":44},{"from":"Western","to":"York","value":23},{"from":"Western","to":"Queens","value":20},{"from":"Western","to":"Ottawa","value":16},{"from":"Western","to":"Carleton","value":14},{"from":"Western","to":"Ryerson","value":14},{"from":"Western","to":"McMaster","value":9},{"from":"Western","to":"Ontario Tech","value":9},{"from":"Western","to":"Guelph-Humber","value":7},{"from":"Western","to":"Brock","value":4},{"from":"Western","to":"Lakehead","value":4},{"from":"Western","to":"Toronto","value":3},{"from":"Western","to":"Scholars Portal","value":2},{"from":"Western","to":"Saint-Paul","value":1},{"from":"York","to":"York","value":127},{"from":"York","to":"Mentee","value":46},{"from":"York","to":"Guelph","value":21},{"from":"York","to":"Ryerson","value":20},{"from":"York","to":"McMaster","value":14},{"from":"York","to":"Carleton","value":13},{"from":"York","to":"Ottawa","value":13},{"from":"York","to":"Western","value":12},{"from":"York","to":"Guelph-Humber","value":11},{"from":"York","to":"Ontario Tech","value":11},{"from":"York","to":"Queens","value":5},{"from":"York","to":"Scholars Portal","value":5},{"from":"York","to":"Brock","value":4},{"from":"York","to":"Saint-Paul","value":4},{"from":"York","to":"Lakehead","value":3},{"from":"York","to":"Toronto","value":2},{"from":"York","to":"Algoma","value":1},{"from":"York","to":"Laurentian","value":1}]
        </script>

        <script type="">

        // Themes begin
        am4core.useTheme(am4themes_dark);
        am4core.useTheme(am4themes_animated);
        // Themes end

        var chart = am4core.create("chartdiv", am4charts.ChordDiagram);

        // colors of main characters
        chart.colors.saturation = 1;
        chart.colors.step = 9;
        var colors = {
            MSKIX:chart.colors.next(),
            DATAIX:chart.colors.next(),
            PiterIX:chart.colors.next(),
            WIX:chart.colors.next(),
            CloudX:chart.colors.next(),
            SFOIX:chart.colors.next(),
            SeaIX:chart.colors.next(),
            RedIX:chart.colors.next(),
            SibirIX:chart.colors.next(),
            
        }

        // data was provided by: https://www.reddit.com/user/notrudedude



        chart.data = data

        chart.dataFields.fromName = "from";
        chart.dataFields.toName = "to";
        chart.dataFields.value = "value";


        chart.nodePadding = 0.5;
        chart.minNodeSize = 0.01;
        chart.startAngle = 80;
        chart.endAngle = chart.startAngle + 360;
        chart.sortBy = "value";
        chart.fontSize = 10;

        var nodeTemplate = chart.nodes.template;
        nodeTemplate.readerTitle = "Click to show/hide or drag to rearrange";
        nodeTemplate.showSystemTooltip = true;
        nodeTemplate.propertyFields.fill = "color";


        // when rolled over the node, make all the links rolled-over
        nodeTemplate.events.on("over", function(event) {    
            var node = event.target;
            node.outgoingDataItems.each(function(dataItem) {
                if(dataItem.toNode){
                    dataItem.link.isHover = true;
                    dataItem.toNode.label.isHover = true;
                }
            })
            node.incomingDataItems.each(function(dataItem) {
                if(dataItem.fromNode){
                    dataItem.link.isHover = true;
                    dataItem.fromNode.label.isHover = true;
                }
            }) 

            node.label.isHover = true;   
        })

        // when rolled out from the node, make all the links rolled-out
        nodeTemplate.events.on("out", function(event) {
            var node = event.target;
            node.outgoingDataItems.each(function(dataItem) {        
                if(dataItem.toNode){
                    dataItem.link.isHover = false;                
                    dataItem.toNode.label.isHover = false;
                }
            })
            node.incomingDataItems.each(function(dataItem) {
                if(dataItem.fromNode){
                    dataItem.link.isHover = false;
                dataItem.fromNode.label.isHover = false;
                }
            })

            node.label.isHover = false;
        })

        var label = nodeTemplate.label;
        label.relativeRotation = 90;

        label.fillOpacity = 0.4;
        let labelHS = label.states.create("hover");
        labelHS.properties.fillOpacity = 1;

        nodeTemplate.cursorOverStyle = am4core.MouseCursorStyle.pointer;
        // this adapter makes non-main character nodes to be filled with color of the main character which he/she kissed most
        nodeTemplate.adapter.add("fill", function(fill, target) {
            let node = target;
            let counters = {};
            let mainChar = false;
            node.incomingDataItems.each(function(dataItem) {
                if(colors[dataItem.toName]){
                    mainChar = true;
                }

                if(isNaN(counters[dataItem.fromName])){
                    counters[dataItem.fromName] = dataItem.value;
                }
                else{
                    counters[dataItem.fromName] += dataItem.value;
                }
            })
            if(mainChar){
                return fill;
            }

            let count = 0;
            let color;
            let biggest = 0;
            let biggestName;

            for(var name in counters){
                if(counters[name] > biggest){
                    biggestName = name;
                    biggest = counters[name]; 
                }        
            }
            if(colors[biggestName]){
                fill = colors[biggestName];
            }
        
            return fill;
        })

        // link template
        var linkTemplate = chart.links.template;
        linkTemplate.strokeOpacity = 0;
        linkTemplate.fillOpacity = 0.15;
        linkTemplate.tooltipText = "chats from {fromName} picked up by {toName} operators: {value.value}";

        var hoverState = linkTemplate.states.create("hover");
        hoverState.properties.fillOpacity = 0.7;
        hoverState.properties.strokeOpacity = 0.7;

        // data credit label
        var creditLabel = chart.chartContainer.createChild(am4core.TextLink);
        creditLabel.text = "Data source: Spizer";
        creditLabel.url = "";
        creditLabel.y = am4core.percent(99);
        creditLabel.x = am4core.percent(99);
        creditLabel.horizontalCenter = "right";
        creditLabel.verticalCenter = "bottom";

        var titleImage = chart.chartContainer.createChild(am4core.Image);
        //titleImage.href = "//www.amcharts.com/wp-content/uploads/2018/11/whokissed.png";
        titleImage.x = 30
        titleImage.y = 30;
        titleImage.width = 200;
        titleImage.height = 200;
        
        </script>

        </body>
        </html>


        """
    return html_doc


if __name__ == '__main__':
    #for Gephi
    nodes, edges = get_data_for_gephi(2019, 9, 9, to="2020-04-30")
    nodes.to_csv('nodes.csv', index=False)
    edges.to_csv('edges.csv', index=False)

    #Chord Diagram javascript
    df = get_data_for_chord_diagram(2019, 9, 9, to="2020-04-30")
    df.to_excel("data_for_chord_diagram_or_network_graph.xlsx", index=False)
    df.to_json("for_chordiagram.json",orient='records')

    #for creating Html file with JSON data
    html_template = get_html_template()
    soup = BeautifulSoup(html_template, 'html.parser')

