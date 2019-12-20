'use strict';

document.addEventListener("DOMContentLoaded", function(event) { 
    var formButton = L.DomUtil.get("a-button");
    var formSelect = document.getElementById("year-select");

    formButton.addEventListener("click", function(event){
        event.preventDefault()
    });

    var map = L.map('map').setView([30.5, -0.09], 2);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    const MAX_YEAR_RANGE = 2020;
    const MIN_YEAR_RANGE = 1960;  // this can be older when paper records have been transcribed
    const YEAR_RANGE_SIZE = 5;

    // Create panes for the year_ranges
    // array of n panes -- one per year_range from min year_range to max year_range
    let panes = [];
    let n_panes = (MAX_YEAR_RANGE - MIN_YEAR_RANGE)/YEAR_RANGE_SIZE + 1;
    for( let pane_index = 0; pane_index< n_panes; pane_index++) {
        // append new pane to the array
        panes.push( map.createPane('pane'+pane_index));
    }
    //----- controls ------
    // add options to the selector for all year_ranges
    for (let year_range = MIN_YEAR_RANGE; year_range<=MAX_YEAR_RANGE; year_range += YEAR_RANGE_SIZE){
        let opt = document.createElement('option');
        let year_range_str = "" + year_range;
        opt.value = year_range_str;
        opt.innerHTML = year_range_str;
        formSelect.appendChild(opt);
    }
    formButton.onclick = function() {
        let year_range_str = formSelect.options[ formSelect.selectedIndex].text;
        let year_range = Number(year_range_str)

        if( year_range >= MAX_YEAR_RANGE) {
            year_range = MIN_YEAR_RANGE;
        } else {
            year_range += YEAR_RANGE_SIZE;
        }
        // update the selector
        formSelect.value = "" + year_range;
        revealData(year_range);
    }
    formSelect.onchange = function() {
        let year_range = this.value;
        revealData(year_range);
    }

    function hide(index) {
        // hide the markers
        panes[index].style.display = 'none';
    }
    function polyDel(){
        // delete the polylines
        for(let i in map._layers) {
            if(map._layers[i]._path != undefined) {
                try {
                    map.removeLayer(map._layers[i]);
                }
                catch(e) {
                    console.log("problem with " + e + map._layers[i]);
                }
            }
        }
    }
    // Show all the markers and polylines for the selected date range
    function show(index) {
        // show the markers
        panes[index].style.display = '';
        // create polylines
        polyWrite(index);
    }
    // Write all the polylines for the selected date range
    function polyWrite(index){
        let year_range_range = year_ranges[index];

        L.geoJSON([year_range_range], {

            style: function (feature) {
                return feature.properties && feature.properties.style;
            },

            pointToLayer: function (feature, latlng) {
                let colors = ['#0041ff', '#ff00ff', '#ff004f'];
                let dashArrays= [ "20, 5", "10, 5", "20, 1"];

                let outloan = false;
                let  inloan = false;
                if( feature.properties.popupContent) {
                    for(let key in feature.properties.popupContent) {
                        let loansdir = key.substr(0,1);
                        if( loansdir == 'O'){
                            outloan = true;
                        }
                        else if( loansdir == 'I'){
                            inloan = true;
                        }
                    }
                }
                //        inloan outloan inandout  (neither: assumed not possible)
                // colorx     0      1       2          x
                let colorx = 0;
                if(outloan){
                    colorx++;
                    if(inloan) {
                        colorx++;
                    }
                }
                // using Henry Thasler's library
                // https://www.thasler.com/leaflet.geodesic/example/interactive-noWrap.html
                // an arc from ottawa to latlng
                return L.geodesic([[[45.421, -75.697], latlng]], {
                    weight: 1 + Number(Math.log( feature.properties.magsum)),
                    opacity: 0.5,
                    color: colors[colorx],
                    dashArray: dashArrays[colorx],
                    lineCap: 'butt',
                    steps: 50,
                    wrap: false
                });
            }
        }).addTo(map);
    }
    // Hide old markers and polylines, and display new
    function revealData(year_range){
        // delete the polylines
        polyDel();

        // year_range to index
        let new_p_index = (year_range - MIN_YEAR_RANGE)/YEAR_RANGE_SIZE;
        if(new_p_index <0) {
            console.log("error new_pane_index " + new_p_index);
        }
        // hide all old marker panes
        panes.forEach( function(value, index, array) {
            if(index != new_p_index) {
                hide( index);
            }
        });
        // show new pane
        show(new_p_index);
    }

    // create popup tooltip info for each marker
    // showing city name, years and institutons
    function onEachFeature(feature, layer) {
        let popupContent = "";
        let outloanInsts = [];
        let outloanNum = [];
        let inloanInsts = [];
        let inloanNum = [];
        if (feature.properties) {
            if( feature.properties.place) {
                popupContent += feature.properties.place;
                popupContent += "<br>";
                popupContent += "years= "
                if( ! feature.properties.years){
                    console.log("no years " + feature.properties.place);
                } else {
                    feature.properties.years.forEach( function(value, index, array) {
                        popupContent += value + ", ";
                    });
                }
                popupContent += "<br>";
            }
            if( feature.properties.popupContent) {
                for(let key in feature.properties.popupContent) {
                    let loansdir = key.substr(0,1);
                    let instname = key.substr(1);
                    let quantity = feature.properties.popupContent[key];
                    if( loansdir == 'O'){
                        outloanInsts.push(instname);
                        outloanNum.push(quantity);
                    }
                    if( loansdir == 'I'){
                        inloanInsts.push(instname);
                        inloanNum.push(quantity);
                    }
                }
                if( outloanInsts.length > 0){
                    popupContent += "Loans Out:";
                    popupContent += "<br>";
                    popupContent += "<ul>";
                    outloanInsts.forEach(function(value, index, array) {
                        popupContent += "<li>";
                        popupContent += outloanNum[index];
                        popupContent += " - ";
                        popupContent += value;
                        popupContent += "</li>";
                    });
                    popupContent += "</ul>";
                }
                if( inloanInsts.length > 0){
                    popupContent += "Loans In:";
                    popupContent += "<br>";
                    popupContent += "<ul>";
                    inloanInsts.forEach(function(value, index, array) {
                        popupContent += "<li>";
                        popupContent += inloanNum[index];
                        popupContent += " - ";
                        popupContent += value;
                        popupContent += "</li>";
                    });
                    popupContent += "</ul>";
                }
            }
        }
        layer.bindTooltip(popupContent); // or bindPopup
    }

    // get the input features in a year_range,
    //   and create a feature per address which aggregates input features
    //   for all years in the year_range
    function build_year_range_range (pane_index){
        let year_range_features = {}  // accumulate the results in this

        // the date range
        let year_range_start = pane_index * YEAR_RANGE_SIZE + MIN_YEAR_RANGE;
        let year_range_end = year_range_start + YEAR_RANGE_SIZE;

        // scan the input features, looking for ones which are within the year_range
        //  TODO: scan once, not many times
        connData.features.forEach( function(feature, index, array) {
            let year = feature.properties.year;
            if(year >= year_range_start &&
               year < year_range_end ){
                let addr = feature.properties.place;
                // is this in  year_range_features? create or deep merge
                //if(!(addr in Object.keys(year_range_features))) {
                if(!(addr in year_range_features)) {
                    year_range_features[addr] = {"type": "Feature"};
                    year_range_features[addr]["properties"] = Object.assign(feature.properties);
                    year_range_features[addr].properties["years"] = [feature.properties.year];
                    year_range_features[addr].properties["magsum"] = [feature.properties.mag];
                    year_range_features[addr]["geometry"] = feature.geometry;
                } else {
                    let props = year_range_features[addr]["properties"];
                    props.years.push(feature.properties.year);
                    props.magsum += [feature.properties.mag];
                    for( let inst in feature.properties.popupContent){
                        // is this inst in year_range_features? create or sum
                        if( !(inst in props.popupContent)){
                            props.popupContent[inst] = 0;
                        }
                        props.popupContent[inst] += feature.properties.popupContent[inst];
                    }
                }
            }
        });

        let year_range_range = {
            "type": "FeatureCollection",
            "metadata": {},
            "features": []
        };
        year_range_range.metadata = connData.metadata;

        // year_range_features.forEach( function(feature, index, array) {
        for( let dec_feature in year_range_features){
            year_range_range.features.push(year_range_features[dec_feature]);
        }
        return year_range_range;
    }

    // disable the shadow
    let icon = new L.Icon.Default();
    icon.options.shadowSize = [0,0];

    // group the input features by address,year_range
    let year_ranges = [];
    year_ranges.metadata = connData.metadata;

    for( let pane_index = 0; pane_index< n_panes; pane_index++) {
        // start off with hidden markers
        panes[pane_index].style.display = 'none';

        let year_range_range = build_year_range_range (pane_index);
        // append new pane to the array
        year_ranges.push( year_range_range );

        L.geoJSON([year_range_range], {

            style: function (feature) {
                return feature.properties && feature.properties.style;
            },

            onEachFeature: onEachFeature,

            pointToLayer: function (feature, latlng) {
                let p_index = Math.floor((feature.properties.year - MIN_YEAR_RANGE)/YEAR_RANGE_SIZE);
                if(p_index <0) {
                    console.log("error p_index " + p_index);
                }
                return L.marker(latlng, {
                    icon: icon,
                    pane: panes[p_index]
                });
            }
        }).addTo(map);
    }

    // the initial load
    revealData(formSelect.options[ formSelect.selectedIndex].text);
});

